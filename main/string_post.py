# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 13:27:49 2019

@author: Bart Dring

This imports a result file from the MatLab output.

https://github.com/Exception1984/StringArt

Usage: string_post.py pin_file_name
Example string_post.py einstein.pins


"""


import sys
import math
from pathlib import Path

y_in_val = 28.0 # желаемое положение Y внутри рабочей зоны
y_out_val = 0.0 # желаемое положение Y вне рабочей зоны
pin_count = 256
radius = 11.75 # radius of pins...used to calculate thread length
thread_length = 0.0 # the length of each line of string is added to this
line_count = 0 # общее количество линий

# create the input file as a command line parameter
input_filename = Path(sys.argv[1])
if not input_filename.is_file():
    sys.exit("Error: The input file %s does not exist" % input_filename)

    print("Input File: " + input_filename)

p = Path(input_filename)
output_filename = str(p.parent) + '\\' + Path(input_filename).stem + ".nc"


print("Output File: " + output_filename)


def pin_wrap_gcode(pin_number):
    gcode = f'G0 X{pin_number + 0.5:.2f} Y{y_in_val:.2f}\n'
    gcode += f'G0 Y{y_out_val:.2f}\n'
    gcode += f'G0 X{pin_number - 0.5:.2f}\n'
    gcode += f'G0 Y{y_in_val:.2f}\n'
    return gcode


gcode_out_line = ""
gcode_out_list = []


from_pin = 0
to_pin = 0

# input_filename = Path(sys.argv[1])
# output_filename = input_filename.stem + ".nc"

f = open(input_filename, "r")
f_gcode = open(output_filename, "w")





f_gcode.write("G90\n") # absolute positioning mode
f_gcode.write("G21\n") # metric mode
f_gcode.write(f'G0 Y{y_in_val:.2f}\n') # move the needle into the work

line_number = 0

rad_per_delta = math.pi / 128

for line in f:
    line.strip()  # remove whitespace at ends

    pin_data = line.split()

    if line != "" and line_number != 0:
        if (line_number == 1):
            from_pin = int(pin_data[0]) # only in the first case bacause we may be >256 or < 0 later
            f_gcode.write(f'G10 L20 P0 X{from_pin:d}\n') #Set the current pin as the start pin.

        to_pin = int(pin_data[1])

        delta = to_pin - (from_pin % pin_count)

        if delta != 0:
            chord_len = 2.0 * radius * math.sin((rad_per_delta*abs(delta))/2.0)
            thread_length = thread_length + chord_len

        f_gcode.write("; ...Go from " +pin_data[0] + " to " + pin_data[1] + "\n")
        if abs(delta) < (pin_count/2): # we need to make sure we never move more than than half turn
            to_pin = from_pin + delta


        else: # need to another way
            if (delta > 0):
                # print("subtract")
                to_pin = from_pin - (pin_count - abs(delta))
            else:
                # print("add")
                to_pin = from_pin + (pin_count - (from_pin % pin_count)) + to_pin

        f_gcode.write(pin_wrap_gcode(to_pin))




        from_pin = to_pin

        line_count = line_count + 1

    line_number = line_number + 1
f.close
f_gcode.close

print(f'Line count: {(line_count):d} Lines')
print(f'Chord Length: {(thread_length/12):.2f} Feet, {(thread_length/36):.2f} Yards')
