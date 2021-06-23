import os
import sys


def compress(file: bytes, show_percentage=False):
    # Convert to string
    string = file.decode("latin")

    # Make a dict for each caracter and sort them by their frequency
    chars = dict()
    for ch in string:
        if ch in chars.values():
            continue
        chars[ch] = string.count(ch)

    sorted_chars = {k: v for k, v in sorted(chars.items(), key=lambda item: item[1], reverse=True)}
    bin_sorted_chars = dict()
    for i in range(len(sorted_chars)):
        k = list(sorted_chars.keys())[i]
        bin_sorted_chars[k] = bin(i)[2:]

    # Set bin char value
    max_len = len(bin_sorted_chars[list(bin_sorted_chars.keys())[-1]])
    for k, v in bin_sorted_chars.items():
        bin_sorted_chars[k] = ("0" * (max_len - len(v))) + v

    # Add char length header
    bin_string = bin(len(bin_sorted_chars[list(bin_sorted_chars.keys())[0]]))[2:]
    bin_string = ("0" * (8 - len(bin_string))) + bin_string

    # Add char definition
    char_def = ""
    for k, v in bin_sorted_chars.items():
        bin_k = bin(bytearray(k, "utf-8")[0])[2:]
        char_def += (("0" * (8 - len(bin_k))) + bin_k) + bin_sorted_chars[k]
    bin_string += char_def

    # Add char definition length header
    bin_char_def_length = bin(len(char_def))[2:]
    bin_string = (("0" * (16 - len(bin_char_def_length))) + bin_char_def_length) + bin_string

    # Add message trad
    for ch in string:
        bin_string += bin_sorted_chars[ch]

    # Add missing char header
    missing_chars = 8 - (len(bin_string) % 8)
    bin_string += "0" * missing_chars

    bin_missing_chars = bin(missing_chars)[2:]
    bin_missing_chars = ("0" * (8 - len(bin_missing_chars))) + bin_missing_chars

    bin_string = bin_missing_chars + bin_string

    # Convert bin to bytes
    compressed_bytes = bytearray()
    for b in [bin_string[i:i+8] for i in range(0, len(bin_string), 8)]:
        b_int = int(b, 2)
        compressed_bytes.append(b_int)
    compressed_bytes = bytes(compressed_bytes)

    if show_percentage:
        percentage = (len(bin_string) * 100) / len(''.join(format(x, 'b') for x in bytearray(file.decode("latin"), 'utf-8')))
        print(f"Compressed version : {-(round(percentage) - 100)}% gained")

    return compressed_bytes


def decompress(file: bytes):
    # Convert bytes to bin
    compressed_bin = ""
    for b in file:
        bin_b = bin(b)[2:]
        compressed_bin += ("0" * (8 - len(bin_b))) + bin_b

    # Remove the overflow
    overflow = int(compressed_bin[:8], 2)
    compressed_bin = compressed_bin[8:-overflow]

    # Parse char definition
    chars = dict()
    char_def_length = int(compressed_bin[:16], 2)
    compressed_bin = compressed_bin[16:]
    char_length = int(compressed_bin[:8], 2)
    compressed_bin = compressed_bin[8:]
    char_def = compressed_bin[:char_def_length]
    msg = compressed_bin[char_def_length:]
    for ch_def in [char_def[i:i+(char_length + 8)] for i in range(0, len(char_def), (char_length + 8))]:
        ch = int(ch_def[:8], 2)
        ch = ch.to_bytes((ch.bit_length() + 7) // 8, sys.byteorder).decode("latin")
        chars[ch_def[8:]] = ch

    decoded_string = ""
    for ch_bin in [msg[i:i + char_length] for i in range(0, len(msg), char_length)]:
        decoded_string += chars[ch_bin]

    return decoded_string.encode()


if len(sys.argv) < 2:
    print("You must specify a file to compress")
    sys.exit()

if not os.path.isfile(sys.argv[1]):
    print("This file doesn't exists")
    sys.exit()

with open(sys.argv[1], "rb") as f:
    compressed_data = compress(f.read(), True)

with open(os.getcwd() + "/compressed.cmprs", "wb") as f:
    f.write(compressed_data)

with open(os.getcwd() + "/decompressed.idklol", "wb") as f:
    f.write(decompress(compressed_data))
