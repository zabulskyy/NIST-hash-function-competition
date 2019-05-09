import sys

def split_str(string, n):
    return [string[i:i+n] for i in range(0, len(string), n)]

def left_rotate(b, n):
    return ((b << n) | (b >> (32 - n))) & 0xffffffff

def extend_by_80(chunk):
    for i in range(16, 80):
        word1 = chunk[i - 3]
        word2 = chunk[i - 8]
        word3 = chunk[i - 14]
        word4 = chunk[i - 16]

        xor1 = bin(int(word1, 2) ^ int(word2, 2))
        xor2 = bin(int(xor1, 2) ^ int(word3, 2))
        xor3 = bin(int(xor2, 2) ^ int(word4, 2))

        new_word = bin(left_rotate(int(xor3, 2), 1))
        chunk.append(new_word)
    return chunk

def proceed_chunk(chunk, h):
    a, b, c, d, e = h
    h0, h1, h2, h3, h4 = h
    for i in range(80):
        f = None
        k = None
        if i < 20:
            f = d ^ (b & (c ^ d))
            k = 0x5A827999
        elif i < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        word = chunk[i]
        temp_a = left_rotate(a, 5) + f
        temp_b = temp_a + e
        temp_c = temp_b + k
        
        temp = temp_c + int(word, 2)
        temp = temp & 0xffffffff

        e = d
        d = c
        c = left_rotate(b, 30)
        b = a
        a = temp

    h0 = hex((h0 + a) & 0xffffffff)[2:]
    h1 = hex((h1 + b) & 0xffffffff)[2:]
    h2 = hex((h2 + c) & 0xffffffff)[2:]
    h3 = hex((h3 + d) & 0xffffffff)[2:]
    h4 = hex((h4 + e) & 0xffffffff)[2:]

    return ''.join([h0, h1, h2, h3, h4])

def run(text):
    text = list(map(ord, list(text)))
    text = list(map(bin, text))
    text = [str(x)[2:] for x in text]
    text = [x.zfill(8) for x in text]

    binary_length = bin(len(''.join(text)))[2:]
    binary_length = binary_length.zfill(64)

    text = "".join(text) + "1"
    while len(text) % 512 != 448:
        text += "0"

    text += binary_length
    text_chunks = split_str(text, 512)
    text_chunks = [split_str(s, 32) for s in text_chunks]

    h = ( 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)

    for i in range(len(text_chunks)):
        text_chunks[i] = extend_by_80(text_chunks[i])
        h = proceed_chunk(text_chunks[i], h)
    return h

if __name__ == "__main__":
    key = sys.argv[1]
    res = run(key)
    print(res)