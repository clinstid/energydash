#!/usr/bin/env python
from serial import *
import sys
import amqplib.client_0_8 as amqp

from envir_settings import *

def main():
    print ">> Opening serial port."
    ser = Serial(port=ENVIR_SERIAL_PORT,
                 baudrate=ENVIR_SERIAL_BAUDRATE,
                 bytesize=ENVIR_SERIAL_BYTESIZE,
                 parity=ENVIR_SERIAL_PARITY,
                 stopbits=ENVIR_SERIAL_STOPBITS,
                 timeout=ENVIR_SERIAL_TIMEOUT)

    # TODO - Need to use a logger!
    output = open('envir.log', 'a', 1)

    print ">> Establishing AMQP connection to {}.".format(ENVIR_MSG_HOST)
    connection = amqp.Connection(host=ENVIR_MSG_HOST)
    print ">> Opening channel."
    channel = connection.channel()
    channel.access_request('/data', active=True, write=True)
    print ">> Declaring exchange '{}'".format(ENVIR_EXCHANGE_NAME)
    channel.exchange_declare(exchange=ENVIR_EXCHANGE_NAME, 
                             type='direct',
                             auto_delete=False,
                             durable=True)
    print ">> Declaring queue '{}'".format(ENVIR_MSG_QUEUE_NAME)
    channel.queue_declare(queue=ENVIR_MSG_QUEUE_NAME,
                          durable=True,
                          auto_delete=False)
    print ">> Binding queue to exchange."
    channel.queue_bind(queue=ENVIR_MSG_QUEUE_NAME,
                       exchange=ENVIR_EXCHANGE_NAME)

    print ">> Waiting for data..."
    while True:
        try:
            line = ser.readline()
            if len(line) > 0:
                output.write(line)
                print ">> Received line: {}\n".format(line.rstrip())
                message = amqp.Message(body=line.rstrip(),
                                       content_type='text/plain',
                                       delivery_mode=2)
                channel.basic_publish(msg=message,
                                      exchange=ENVIR_EXCHANGE_NAME,
                                      routing_key=ENVIR_MSG_QUEUE_NAME)
                print ">> Queued message."
        except KeyboardInterrupt:
            print "Caught keyboard interrupt, exiting."
            output.flush()
            output.close()
            channel.close()
            connection.close()
            ser.close()
            sys.exit()

if __name__ == '__main__':
    main()
