#!/usr/bin/env python
from serial import *
import sys
import pika

from envir_settings import *

ser = Serial(port=ENVIR_SERIAL_PORT,
             baudrate=ENVIR_SERIAL_BAUDRATE,
             bytesize=ENVIR_SERIAL_BYTESIZE,
             parity=ENVIR_SERIAL_PARITY,
             stopbits=ENVIR_SERIAL_STOPBITS,
             timeout=ENVIR_SERIAL_TIMEOUT)

# TODO - Need to use a logger!
output = open('envir.log', 'a', 1)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=ENVIR_MSG_HOST))
channel = connection.channel()
channel.queue_declare(queue=ENVIR_QUEUE_NAME, durable=True)

while True:
    try:
        message = ser.readline()
        channel.basic_publish(exchange='',
                              routing_key=ENVIR_QUEUE_NAME,
                              body=message,
                              properties=pika.BasicProperties(delivery_mode=2))
        output.write(message)
        sys.stdout.write('"{}"'.format(message))
    except KeyboardInterrupt:
        print "Caught keyboard interrupt, exiting."
        output.flush()
        output.close()
        sys.exit()

