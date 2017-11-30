import PIL.Image
from PIL import ImageGrab
from tkinter import *
import math
import random

LINEAR = 0
POWER = 1
POLAR = 2
SINUSOIDAL = 3

RED = 0
GREEN = 1
BLUE = 2
HUE = 3
SATURATION = 4
BRIGHTNESS = 5
NRED = 6
NGREEN = 7
NBLUE = 8
NHUE = 9
NSATURATION = 10
NBRIGHTNESS = 11

filename = "test.jpg"
lens_filename = None
img = PIL.Image.open(filename)
pixels = list(img.getdata())
limg = img
tk = Tk()
buffer = Canvas(master = tk, width = img.width, height = img.height)
buffer.configure(cursor = "crosshair")
max_display_size = 750

pattern_factor = 4.1
bend_x = 0.1
bend_y = 0.1
power_vals = [2, 0.5]
types = [LINEAR, POWER]
channels = [BRIGHTNESS, SATURATION]
use_cl_pattern = False

interactive = 0
facts = [None, None]


def remap( x, o_min, o_max, n_min, n_max ):

    #range check
    if o_min == o_max:
        return None

    if n_min == n_max:
        return None

    #check reversed input range
    reverse_input = False
    old_min = min( o_min, o_max )
    old_max = max( o_min, o_max )
    if not old_min == o_min:
        reverse_input = True

    #check reversed output range
    reverse_output = False
    new_min = min( n_min, n_max )
    new_max = max( n_min, n_max )
    if not new_min == n_min :
        reverse_output = True

    portion = (x - old_min) * (new_max - new_min) / (old_max - old_min)
    if reverse_input:
        portion = (old_max-x)*(new_max-new_min)/(old_max-old_min)

    result = portion + new_min
    if reverse_output:
        result = new_max - portion

    return result


def get_channel(pixel, channel):
    if channel > 5:
        ch = channel - 6
    else:
        ch = channel
    cc = 0
    if ch == RED or ch == HUE:
        cc = pixel[0]
    elif ch == GREEN or ch == SATURATION:
        cc = pixel[1]
    else:
        cc = pixel[2]
    if channel > 5:
        return 255 - cc
    else:
        return cc


def get_shift(pixel, position):
    cc = get_channel(pixel, channels[position])
    if types[position] == LINEAR:
        return int(facts[position] * cc / 255)
    elif types[position] == POWER:
        return int(facts[position] * remap(pow(cc / 255, power_vals[position]),
                                           0, 1, -1, 1))
    elif types[position] == SINUSOIDAL:
        return int(facts[position] * math.sin(remap(cc, 0, 255, -math.pi, math.pi)))
    else:
        if position == 0:
            c1 = cc
        else:
            c1 = get_channel(pixel, channels[1])
        if position == 1:
            c2 = cc
        else:
            c2 = get_channel(pixel, channels[0])
        angle = remap(c1, 0, 255, 0, 2 * math.pi)
        r = remap(c2, 0, 255, 0, facts[0])
        if position == 0:
            return int(r*math.cos(angle))
        else:
            return int(r*math.sin(angle))


def draw_me():
    buffer.config(background = "black")
    for x in range(0, img.width - 1):
        if use_cl_pattern is True:
            lx = int(x * pattern_factor) % img.width
        else:
            lx = int(remap(x, 0, img.width - 1, 0, limg.width - 1))
        for y in range(0, img.height - 1):
            if use_cl_pattern is True:
                ly = int(y * pattern_factor) % img.height
            else:
                ly = int(remap(y, 0, img.height - 1, 0, limg.height - 1))
            c = pixels[lx + ly + limg.width]
            x_position = (x + get_shift(c, 0) + 2 * img.width) % img.width
            y_position = (y + get_shift(c, 1) + 2 * img.height) % img.height
            n = pixels[x_position + y_position * img.width]
            buffer.create_rectangle(x, y, x+1, y+1, fill = str('#%02x%02x%02x' % n), width = 0)
    buffer.pack()


def draw():
    if interactive is True:
        facts[0] = int(remap(tk.winfo_pointerx(), 0, buffer.winfo_width(), 0, img.width))
        facts[1] = int(remap(tk.winfo_pointery(), 0, buffer.winfo_height(), 0, img.height))
        draw_me()


def mouse_clicked(event):
    power_vals[0] = random.uniform(0, 8)
    power_vals[1] = random.uniform(0, 8)
    channels[0] = int(random.uniform(0,12))
    channels[1] = int(random.uniform(0,12))
    types[0] = int(random.uniform(0,4))
    types[1] = int(random.uniform(0,4))
    facts[0] = int(remap(tk.winfo_pointerx(), 0, buffer.winfo_width(), 0, img.width))
    facts[1] = int(remap(tk.winfo_pointery(), 0, buffer.winfo_height(), 0, img.height))
    draw_me()
    print("mouse clicked")

def change_interactivity(event):
    print("Pressed enter")
    # if interactive == 0:
    #     interactive = 1
    # if interactive == 1:
    #     interactive = 0


def save_canvas(event):
    x = tk.winfo_rootx() + buffer.winfo_x()
    y = tk.winfo_rooty() + buffer.winfo_y()
    x1 = x + buffer.winfo_width()
    y1 = y + buffer.winfo_height()
#    ImageGrab.grab().crop((x, y, x1, y1)).save("glitch.jpg")


# def get_cl_pattern():
#     n = int(random.uniform(1,4719052))
#     pad = ""
#     if n < 1000:
#         pad = "0"
#     else:
#         nn = ""+str(n)
#         pad = nn[0:len(nn) - 3]
#     clname = "http://colourlovers.com.s3.amazonaws.com/images/patterns/"+pad+"/"+n+".png"
#     try:
#         limg.open(fp = clname)
#     finally:
#         get_cl_pattern()
#
#     if limg.width <= 0:
#         get_cl_pattern()



# def apply_clpattern(event):
#     get_cl_pattern()
#     draw_me()

buffer.focus_set()
buffer.bind("<Return>", change_interactivity)
buffer.bind("<Enter>", change_interactivity)
buffer.bind("32", save_canvas)
# buffer.bind("c" and use_cl_pattern == True, apply_clpattern())
buffer.bind("<Button-1>", mouse_clicked)


def setup():
    if lens_filename is not None:
        limg = PIL.Image.open(lens_filename)
    else:
        limg = img

    ratio = img.width / img.height
    if ratio < 1.0:
        neww = int(max_display_size * ratio)
        newh = max_display_size
    else:
        neww = max_display_size
        newh = int(max_display_size / ratio)
    buffer.config(width = neww, height = newh)
    if use_cl_pattern is True:
        get_cl_pattern()
    facts[0] = bend_x * img.width
    facts[1] = bend_y * img.height
    draw_me()

setup()
tk.mainloop()