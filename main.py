import sys

from PIL import Image
import numpy as np
from bitstring import BitArray

# -----The verification matrix is of the order of 3----- #
H3 = [[0, 0, 0, 1, 1, 1, 1],
      [0, 1, 1, 0, 0, 1, 1],
      [1, 0, 1, 0, 1, 0, 1]]

# -----The verification matrix is of the order of 4----- #
H4 = [[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
      [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
      [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
      [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]]

# -----The verification matrix is of the order of 5----- #
H5 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
      [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
      [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
      [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
      [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]]


# -----Array of the least bits in pixel from the main image----- #
def get_least_bits_of_pixel(array):
    bits_array = []
    for i in range(0, len(array)):
        for j in range(0, len(array[i])):
            for k in range(0, 3):
                bits_array.append(array[i, j][k] % 2)
    return bits_array


# -----Array of bits in pixel from the message image----- #
def get_bits_array_of_message(mess_arr):
    bits_array = []
    for i in range(0, len(mess_arr)):
        for j in range(0, len(mess_arr[i])):
            for k in range(0, 3):
                x = '{0:08b}'.format(mess_arr[i, j][k])
                arr = list(x)
                for q in range(0, len(arr)):
                    bits_array.append(int(arr[q]))
    return bits_array


# -----Splitting an array into blocks----- #
def chunk_array(array, chunk):
    chunked_array = []
    for i in range(0, len(array), chunk):
        chunked_array.append(array[i:i + chunk])
    while len(chunked_array[len(chunked_array) - 1]) < chunk:
        chunked_array[len(chunked_array) - 1].append(0)
    return chunked_array


# -----Calculation and modification of the syndrome----- #
def syndrome(chunked_main_arr, chunked_mess_arr, H):
    for p in range(0, len(chunked_mess_arr)):
        s = np.dot(H, np.transpose(chunked_main_arr[p]))
        s = np.mod(s, 2)
        b = BitArray(s).uint
        if b != 0:
            chunked_main_arr[p][b - 1] = int(not (chunked_main_arr[p][b - 1]))
        b = BitArray(chunked_mess_arr[p]).uint
        if b != 0:
            chunked_main_arr[p][b - 1] = int(not (chunked_main_arr[p][b - 1]))


# -----Combining a partitioned array into a single array----- #
def comb_array(array):
    result = []
    for i in range(0, len(array)):
        for j in range(0, len(array[i])):
            result.append(array[i][j])
    return result


# -----Hiding a message image in the main image----- #
def hide_message(main_arr, bits):
    ind = 0
    for i in range(0, len(main_arr)):
        for j in range(0, len(main_arr[i])):
            for k in range(0, 3):
                main_arr[i, j][k] += -(main_arr[i, j][k] % 2) + bits[ind]
                ind += 1


def save_image(im_array, filename):
    im = Image.fromarray(im_array)
    im.save(filename)


def recover_message_bits(chunked_array, H):
    res_arr = []
    for i in range(0, len(chunked_array)):
        s = np.dot(H, np.transpose(chunked_array[i]))
        s = list(np.mod(s, 2))
        for j in range(0, len(s)):
            res_arr.append(s[j])
    return res_arr


# -----Recover an array of message image pixels----- #
def recover_array_of_pixels(w, h, array):
    result = np.array([[[0 for i in range(0, 3)] for i in range(0, h)] for i in range(0, w)])
    ind = 0
    for p in range(0, w):
        for q in range(0, h):
            for i in range(0, 3):
                result[p][q][i] = np.uint8(BitArray(array[ind]).uint)
                ind += 1
    return result.astype(np.uint8)


# ----------------------------------Main---------------------------------- #
Hn = input('Enter the order of the verification matrix 3, 4 or 5:')
N = 0
if Hn == '3':
    H = H3
    N = 7
    K = 3
elif Hn == '4':
    H = H4
    N = 15
    K = 4
elif Hn == '5':
    H = H5
    N = 31
    K = 5
else:
    print("Error!")
    sys.exit()

main_filename = 'main_img.jpg'
main_im = Image.open(main_filename)
main_im.convert("RGB")
main_array = np.array(main_im)

message_file = 'message_img.jpg'
message_im = Image.open(message_file)
message_im.convert("RGB")
message_array = np.array(message_im)
width, height = message_im.size

# -----Hiding a message image----- #
main_bits_array = get_least_bits_of_pixel(main_array)
message_bits_array = get_bits_array_of_message(message_array)

chunked_main_array = chunk_array(main_bits_array, N)
chunked_message_array = chunk_array(message_bits_array, K)

if len(chunked_main_array) < len(chunked_message_array):
    print('The message is too large!')
    sys.exit()

syndrome(chunked_main_array, chunked_message_array, H)

res_bits = comb_array(chunked_main_array)

hide_message(main_array, res_bits)

save_image(main_array, 'out.png')

# -----Decoding----- #
out_filename = 'out.png'
out_im = Image.open(out_filename)
out_im.convert("RGB")
out_array = np.array(out_im)

out_bits_array = get_least_bits_of_pixel(out_array)

chunked_out_array = chunk_array(out_bits_array, N)

recover_array = recover_message_bits(chunked_out_array, H)

chunked_recover_array = chunk_array(recover_array, 8)

recover_message = recover_array_of_pixels(width, height, chunked_recover_array)

save_image(recover_message, 'result.png')
