#!/usr/bin/python
from serial import *
import sys

ser = Serial(port='/dev/ttyUSB0',
             baudrate=57600,
             bytesize=EIGHTBITS,
             parity=PARITY_NONE,
             stopbits=STOPBITS_ONE,
             timeout=5)
output = open('envir.log', 'a', 1)

while True:
    try:
        input = ser.read(64)
        output.write(input)
        sys.stdout.write(input)
    except KeyboardInterrupt:
        print "Exiting."
        output.flush()
        output.close()
        sys.exit()

