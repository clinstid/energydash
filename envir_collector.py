#!/usr/bin/env python
from serial import *
import sys
from threading import Thread
import logging
from datetime import datetime
import pytz

from envir_settings import *
from envir_db import Envir

work_queue = Queue()

def collect():
    global work_queue
    logger = logging.getLogger('collector')
    logger.info('Opening serial port.')
    ser = Serial(port=ENVIR_SERIAL_PORT,
                 baudrate=ENVIR_SERIAL_BAUDRATE,
                 bytesize=ENVIR_SERIAL_BYTESIZE,
                 parity=ENVIR_SERIAL_PARITY,
                 stopbits=ENVIR_SERIAL_STOPBITS,
                 timeout=ENVIR_SERIAL_TIMEOUT)

    logger.info('Waiting for data...')
    while True:
        try:
            line = ser.readline()
            if len(line) > 0:
                logger.info('Received line: {}'.format(line.rstrip()))
                work_queue.put((datetime.now(tz=pytc.utc), line.rstrip()))
                logger.info('Queued message.')
        except KeyboardInterrupt:
            logger.info('Caught keyboard interrupt, exiting.')
            output.flush()
            output.close()
            channel.close()
            connection.close()
            ser.close()
            sys.exit()

def write_to_db():
    global work_queue
    logger = logging.getLogger('writer')
    while(True):
        (timestamp, line) = work_queue.get()
        logger.info('Received: {} - {}'.format(timstamp, line))

def main():
    logger = logging.getLogger(__name__)
    collector = Thread(target=collect)
    writer = Thread(target=write_to_db)
    collector.start()
    writer.start()
    collector.join()
    writer.join()

if __name__ == '__main__':
    main()
