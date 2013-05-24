#!/usr/bin/env python
from serial import *
import sys
import pika

ser = Serial(port='/dev/ttyUSB0',
             baudrate=57600,
             bytesize=EIGHTBITS,
             parity=PARITY_NONE,
             stopbits=STOPBITS_ONE,
             timeout=5)
output = open('envir.log', 'a', 1)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
QUEUE_NAME = 'envir'
channel.queue_declare(queue=QUEUE_NAME)

while True:
    try:
        message = ser.read(64)
        channel.basic_publish(exchange='',
                              routing_key=QUEUE_NAME,
                              body=message)
        output.write(message)
        sys.stdout.write(message)
    except KeyboardInterrupt:
        print "Caught keyboard interrupt, exiting."
        output.flush()
        output.close()
        sys.exit()

