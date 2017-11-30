from PIL import Image
import random


# These are the variables that you can change without breaking anything.
divide_constant = 1200 * 30     # Size of chunks. Must be larger than shuffle_constant and less than number of pixels in the image.
shuffle_constant = 200 * 40     # Size of sub chunks. Must be larger than pattern_a's largest value.
pattern_a = [64, 80, 200]       # Size of sub sub chunks. Smallest value must be larger than pattern_b's largest value.
pattern_b = [4, 8, 12, 16]      # Size of sub sub sub chunks. Largest value must be smaller than pattern_a's largest value.
pattern_b_rule = [3, 2, 0, 1]   # Permutation order. Do NOT change values, only their order.
skip_header = 0                 # Pixels to skip at the beginning of the image
skip_footer = 0                 # Pixels to skip at the end of the image

# Constants for determining which step to carry out
SHUFFLE = 0
SHUFFLE_G = 1
PERMUTATE = 2
DIVIDE_G = 3


class Rule():
    pattern_one = []
    pattern_two = []
    method = None
    length = None

    def __init__(self, method, p = None, length = None, pattern_one = [], pattern_two = []):
        self.method = method
        if length is None:
            if p is None:
                self.pattern_one = pattern_one
                self.pattern_two = pattern_two
            else:
                self.pattern_one = p
                self.pattern_two = p
        else:
            self.length = length


class Chunk():
    ch = []

    def __init__(self):
        self.ch = []


def divide(w):
    return Rule(DIVIDE_G, length = w)
def shuffle(w):
    return Rule(SHUFFLE_G, length = w)
def shuffle_pattern(p):
    return Rule(SHUFFLE, p = p)
def permutate_pattern(p, r):
    return Rule(PERMUTATE, pattern_one = p, pattern_two = r)


# Array of rules for recursive loop in process_rules.
rules = [divide(divide_constant),                          # Divides stream into chunks
         shuffle(shuffle_constant),                        # Divides chunks into sub chunks and shuffles
         shuffle_pattern(pattern_a),                       # Divides sub chunks according to pattern and shuffles
         permutate_pattern(pattern_b, pattern_b_rule)]     # Divides sub sub chunks according to pattern and permutates


def process_rules(pix, depth):
    new_depth = depth
    result = []
    chunks = []
    if new_depth >= len(rules):
        return pix
    rule = rules[new_depth]
    if rule.method == DIVIDE_G or rule.method == SHUFFLE_G:
        position = 0
        while position < len(pix):
            chunk_length = rule.length
            if (position + chunk_length) >= len(pix):
                chunk_length = len(pix) - position
            chunk = Chunk()
            for i in range(position, position + chunk_length):
                chunk.ch.append(pix[i])
            chunks.append(chunk)
            position += chunk_length
    if rule.method == SHUFFLE_G:
        random.shuffle(chunks)
    if rule.method == SHUFFLE or rule.method == PERMUTATE:
        position = 0
        sub_position = 0
        sub_chunks = []
        while position < len(pix):
            chunk_length = rule.pattern_one[sub_position]
            if (position + rule.pattern_one[sub_position]) >= len(pix):
                chunk_length = len(pix) - position
            chunk = Chunk()
            for i in range(position, position + chunk_length):
                chunk.ch.append(pix[i])
            sub_chunks.append(chunk)
            sub_position += 1
            if sub_position == len(rule.pattern_one):
                if rule.method == SHUFFLE:
                    random.shuffle(sub_chunks)
                    chunks.extend(sub_chunks)
                if rule.method == PERMUTATE:
                    for i in rule.pattern_two:
                        chunks.append(sub_chunks[i])
                sub_chunks.clear()
                sub_position = 0
            position += chunk_length
    for chunk in chunks:
        chunk.ch = process_rules(chunk.ch, new_depth+1)
    for chunk in chunks:
        for pixel in chunk.ch:
            result.append(pixel)
    return result



def process_image(img):
    pixels = list(img.getdata())
    processed_pixels = process_rules(pixels, 0)
    finished_img = img
    finished_img.putdata(processed_pixels)
    finished_img.save(fp = "glitch.jpg")


img = Image.open("test.jpg")
process_image(img)