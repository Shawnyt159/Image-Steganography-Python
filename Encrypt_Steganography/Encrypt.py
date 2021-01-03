import sys
from PIL import Image


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


def encode_lsb_image(image_file_name, new_image_file):
    image = None
    try:
        image = Image.open(image_file_name, "r")
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
    new_image.save(new_image_file, str(new_image_file.split(".")[1].upper()))
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


def decode_lsb_image(image_file_name):
    image = Image.open(image_file_name, "r")

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
            encoded_message = decode_message_two_input_cipher(encoded_message)
            return encoded_message

        pixel_iterator.__next__()[:3]


def main():

    if len(sys.argv) == 5 and sys.argv[1] == '-i' and sys.argv[3] == '-o':
        encode_lsb_image(sys.argv[2], sys.argv[4])
    elif len(sys.argv) == 3 and sys.argv[1] == '-d':
        print('Message: ' + decode_lsb_image(sys.argv[2]))
    else:
        print('Incorrect argument format, Encrypt: -i input_file -o output_file')
        print('Decrypt: -d input_file')


if __name__ == '__main__':
    main()
