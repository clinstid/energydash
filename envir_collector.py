#!/usr/bin/env python
from serial import *
import sys
import amqplib.client_0_8 as amqp

from envir_settings import *

ser = Serial(port=ENVIR_SERIAL_PORT,
             baudrate=ENVIR_SERIAL_BAUDRATE,
             bytesize=ENVIR_SERIAL_BYTESIZE,
             parity=ENVIR_SERIAL_PARITY,
             stopbits=ENVIR_SERIAL_STOPBITS,
             timeout=ENVIR_SERIAL_TIMEOUT)

# TODO - Need to use a logger!
output = open('envir.log', 'a', 1)

connection = amqp.Connection(host=ENVIR_MSG_HOST)
channel = connection.channel()
channel.access_request('/data', active=True, write=True)
channel.exchange_declare(exchange=ENVIR_EXCHANGE_NAME, 
                         type='direct',
                         auto_delete=False,
                         durable=True)
channel.queue_declare(queue=ENVIR_MSG_QUEUE_NAME,
                      durable=True,
                      auto_delete=False)

while True:
    try:
        line = ser.readline()
        if len(line) > 0:
            message = amqp.Message(body=line.rstrip(),
                                   content_type='text/plain')
            channel.basic_publish(msg=message,
                                  exchange=ENVIR_EXCHANGE_NAME,
                                  routing_key=ENVIR_MSG_QUEUE_NAME)
            self.channel.queue_bind(queue=ENVIR_MSG_QUEUE_NAME,
                                    exchange=ENVIR_EXCHANGE_NAME)
            output.write(line)
            sys.stdout.write('"{}"\n'.format(line))
    except KeyboardInterrupt:
        print "Caught keyboard interrupt, exiting."
        output.flush()
        output.close()
        channel.close()
        connection.close()
        sys.exit()

