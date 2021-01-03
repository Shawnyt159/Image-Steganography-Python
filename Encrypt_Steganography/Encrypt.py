import os
from PIL import Image
import cv2
import glob
from subprocess import call


# Convert encoding data into 8-bit binary
# form using ASCII value of characters
def generate_message_to_binary(message):
    new_message = []

    for character in message:
        new_message.append(format(ord(character), '08b'))
    return new_message


def modify_pixel_lsb_image(pixels, message):
    # Message turned to binary
    message_list = generate_message_to_binary(message)

    # Length of message.
    message_length = len(message_list)

    # Iterator for the pixels in the image.
    iterator_of_pixel = iter(pixels)

    # Iterating over the characters in the message length
    for character in range(message_length):

        # taking 3 pixels at a time.
        pixel = [value for value in iterator_of_pixel.__next__()[:3] +
                 iterator_of_pixel.__next__()[:3] +
                 iterator_of_pixel.__next__()[:3]]

        # changing the least significant bit to 1 or 0 based on the binary of the current character.
        for j in range(0, 8):
            if message_list[character][j] == '0' and pixel[j] % 2 != 0:
                pixel[j] -= 1
            elif message_list[character][j] == '1' and pixel[j] % 2 == 0:
                if pixel[j] != 0:
                    pixel[j] -= 1
                else:
                    pixel[j] += 1

        # Deciding if it should end in a 1 or 0 to determine if it should continue or not.
        if character == message_length - 1:
            if pixel[-1] % 2 == 0:
                if pixel[-1] != 0:
                    pixel[-1] -= 1
                else:
                    pixel[-1] += 1
        else:
            if pixel[-1] % 2 != 0:
                pixel[-1] -= 1

        # Yielding three pixels at a time.
        pixel = tuple(pixel)
        yield pixel[0:3]
        yield pixel[3:6]
        yield pixel[6:9]

        # Skipping the third pixel.
        pixel = iterator_of_pixel.__next__()[:3]
        yield pixel


def encode_message_image(new_image, message):
    # getting the number of x coordinates from the image size at index 0.
    number_of_x_cords = new_image.size[0]
    x, y = 0, 0

    # for every pixel that is yielded from modify_pixel_lsb_image(), modifies the new pixel.
    for pixel in modify_pixel_lsb_image(new_image.getdata(), message):
        new_image.putpixel((x, y), pixel)
        if x == number_of_x_cords - 1:
            x = 0
            y += 1
        else:
            x += 1


def encode_message_two_input_cipher(message):
    # encoding the message with a two input cipher
    ascii_values_message = []
    for character in message:
        ascii_values_message.append(ord(character))

    encoded_message = ''
    for ascii_value in ascii_values_message:
        if ascii_value+5 > 255:
            encoded_character_one = ascii_value-4
            encoded_character_two = ascii_value - 255
            encoded_character_two = encoded_character_two + 5
        elif ascii_value-4 < 0:
            encoded_character_one = ascii_value+255
            encoded_character_one = encoded_character_one-4
            encoded_character_two = ascii_value+5
        else:
            encoded_character_one = ascii_value-4
            encoded_character_two = ascii_value+5

        encoded_message += chr(encoded_character_one)
        encoded_message += chr(encoded_character_two)
    return encoded_message


def encode_lsb_image():
    image = None
    img_file_name = ''
    while img_file_name == '':
        img_file_name = input("Enter image with extension: ")
        if img_file_name == '':
            print("Please enter a valid response: ")
    try:
        image = Image.open(img_file_name, "r")
    except FileNotFoundError:
        print("Image not found")
        exit(2)

    message = ''
    while message == '':
        message = input("Enter the message you wish to encrypt: ")
        if message == '':
            print("No message entered.")

    message = encode_message_two_input_cipher(message)
    new_image = image.copy()

    encode_message_image(new_image, message)
    new_image_name = ''
    while new_image_name == '' or not"." in new_image_name:
        new_image_name = input("Enter the name for the encoded image with png extension: ")
        if new_image_name == '' or not".png" in new_image_name:
            print("You haven't entered a new image name that is compatible: ")
    new_image.save(new_image_name, str(new_image_name.split(".")[1].upper()))
    print("Process complete.")


def decode_message_two_input_cipher(message):
    decoded_message = ''
    ascii_values_message = []

    for character in message:
        ascii_values_message.append(ord(character))

    character_number = 1
    for ascii_value in ascii_values_message:
        if character_number % 2 == 1:
            if ascii_value+4 > 255:
                ascii_value = ascii_value-255
                ascii_value = ascii_value+4
            elif ascii_value-4 < 0:
                ascii_value = ascii_value+255
                ascii_value = ascii_value-4
            else:
                ascii_value = ascii_value+4

            decoded_message += chr(ascii_value)
        character_number = character_number + 1

    return decoded_message


def decode_lsb_image():
    img_file_name = input("Enter image with message to decrypt: ")
    image = Image.open(img_file_name, "r")

    encoded_message = ''
    image_data = image.getdata()
    pixel_iterator = iter(image_data)

    while True:

        pixels = [value for value in pixel_iterator.__next__()[:3] +
                  pixel_iterator.__next__()[:3] +
                  pixel_iterator.__next__()[:3]]

        binary_string = ''
        for color_value in pixels[:8]:
            if color_value % 2 == 0:
                binary_string += '0'
            else:
                binary_string += '1'
        character_to_add = chr(int(binary_string, 2))
        encoded_message += character_to_add
        if pixels[-1] % 2 != 0:
            return encoded_message

        pixels = pixel_iterator.__next__()[:3]


def delete_video_frames_directory(path):
    for file_name in glob.glob(path+'/*'):
        try:
            os.remove(file_name)
        except OSError as e:
            print("Error: %s : %s" % (file_name, e.strerror))
    os.rmdir(path)


def save_frames_as_video(path, new_video_name):
    video_frames_directory = "video_frames/video_frame%d.jpg"
    call(["ffmpeg", "-i", video_frames_directory, "-vcodec", "jpeg2000", new_video_name + ".avi", "-y"])
    delete_video_frames_directory(path)


def extract_frames_from_video_and_encode_message(video, message, new_video_name):
    directory = "video_frames"
    parent_directory = os.getcwd() + "/"
    path = os.path.join(parent_directory, directory)
    os.mkdir(path)

    frame_number = 0
    while video.isOpened():
        retrieved_frame, frame = video.read()
        if not retrieved_frame:
            break
        cv2.imwrite(os.path.join(path, 'video_frame'+str(frame_number)+'.jpg'), frame)
        frame_number += 1

    video.release()
    cv2.destroyAllWindows()
    file = path+'/video_frame0.jpg'
    first_frame = Image.open(file, "r")

    # Encoding the message as cipher text.
    message = encode_message_two_input_cipher(message)
    # Encoding the message in the first frame.
    encode_message_image(first_frame, message)
    first_frame.save(file)
    # Saving the frames as a video.
    save_frames_as_video(path, new_video_name)


def encode_lsb_video():
    video_name = input("Enter the video with extension: ")
    video = cv2.VideoCapture(video_name)
    message = input("Enter the message you wish to encrypt: ")
    new_video_name = input("Enter the name of the new video you wish without extension: ")
    extract_frames_from_video_and_encode_message(video, message, new_video_name)


def decode_lsb_image_no_input(img_file_name):
    image = Image.open(img_file_name, "r")

    encoded_message = ''
    image_data = image.getdata()
    pixel_iterator = iter(image_data)

    while True:

        pixels = [value for value in pixel_iterator.__next__()[:3] +
                  pixel_iterator.__next__()[:3] +
                  pixel_iterator.__next__()[:3]]

        binary_string = ''
        for color_value in pixels[:8]:
            if color_value % 2 == 0:
                binary_string += '0'
            else:
                binary_string += '1'
        character_to_add = chr(int(binary_string, 2))
        encoded_message += character_to_add
        if pixels[-1] % 2 != 0:
            return encoded_message

        pixels = pixel_iterator.__next__()[:3]


def decode_lsb_video():
    video_name = input("Enter the video you wish to decode: ")
    video = cv2.VideoCapture(video_name)
    retrieved_frame, frame = video.read()
    first_frame = 'video_frame0.jpg'
    if not retrieved_frame:
        return "No frames found in video"
    cv2.imwrite(first_frame, frame)
    message = decode_lsb_image_no_input(first_frame)
    print(message)


def main():
    print("Welcome to steganography, pick your option: ")
    encode_or_decode = input("Enter the number that corresponds:\n"
                             "1.) Encode\n"
                             "2.) Decode\n"
                             "3.) Exit\n"
                             ": ")
    if encode_or_decode == '1':
        print("Pick your method: ")
        encode_method = input("Enter the number that corresponds:\n"
                              "1.) Least Significant Bit image\n"
                              "2.) Least Significant Bit video\n"
                              "3.) Exit\n"
                              ": ")
        if encode_method == '1':
            encode_lsb_image()
            print('Success.')
        elif encode_method == '2':
            encode_lsb_video()
            print('Success.')
        else:
            print("Thanks for using the program!\n")
            exit(1)
    elif encode_or_decode == '2':
        print("Pick your method: ")
        decode_method = input("Enter the number that corresponds:\n"
                              "1.) Least Significant Bit image\n"
                              "2.) Least Significant Bit video\n"
                              "3.) Exit\n"
                              ": ")
        if decode_method == '1':
            encoded_message = decode_lsb_image()
            readable_message = decode_message_two_input_cipher(encoded_message)
            print(readable_message)
        elif decode_method == '2':
            decode_lsb_video()
        else:
            print("Thanks for using the program!\n")
            exit(1)
    else:
        print("Thanks for using the program!\n")
        exit(1)


if __name__ == '__main__':
    main()
