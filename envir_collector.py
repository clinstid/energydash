#!/usr/bin/env python
from serial import *
import sys
from threading import Thread
import logging
from datetime import datetime
import pytz
from mongoengine import *
from Queue import Queue
from time import sleep

from settings import *
from envir_db import EnvirMsg
from models import *


class Collector(Thread):
    def __init__(self, work_queue):
        Thread.__init__(self)
        self.daemon = True
        self.exiting = False
        self.work_queue = work_queue

    def run(self):
        logger = logging.getLogger('collector')
        logger.info('Opening serial port.')
        ser = Serial(port=ENVIR_SERIAL_PORT,
                     baudrate=ENVIR_SERIAL_BAUDRATE,
                     bytesize=ENVIR_SERIAL_BYTESIZE,
                     parity=ENVIR_SERIAL_PARITY,
                     stopbits=ENVIR_SERIAL_STOPBITS,
                     timeout=ENVIR_SERIAL_TIMEOUT)

        logger.info('Waiting for data...')

        while not self.exiting:
                line = ser.readline()
                if len(line) > 0:
                    logger.debug('Received line: {}'.format(line.rstrip()))
                    self.work_queue.put((datetime.now(tz=pytz.utc), line.rstrip()))
                    logger.debug('Queued message (size={}).'.format(self.work_queue.qsize()))

        logger.info('Closing serial port.')
        ser.close()

class Writer(Thread):
    def __init__(self, work_queue):
        Thread.__init__(self)
        self.daemon = True
        self.exiting = False
        self.work_queue = work_queue

    def run(self):
        logger = logging.getLogger('writer')
        while not self.exiting:
            try:
                logger.info('Connecting to database {}@{}...'.
                            format(MONGO_DATABASE_NAME,
                                   MONGO_HOST))
                connect(host=MONGO_HOST,
                        db=MONGO_DATABASE_NAME)

            except Exception as e:
                logger.error('Unhandled exception from database: {}'.format(e))
                raise

            logger.info('Wating for work...')

            while not self.exiting:
                (timestamp, line) = self.work_queue.get()
                logger.debug('Received: {}: - {} (size={})'.format(timestamp, 
                                                                  line, 
                                                                  self.work_queue.qsize()))
                msg = EnvirMsg(timestamp, line)
                try:
                    EnvirReading(reading_timestamp=msg.reading_timestamp,
                                 receiver_days_since_birth=msg.dsb,
                                 receiver_time=msg.time24,
                                 ch1_watts=msg.ch1_watts,
                                 ch2_watts=msg.ch2_watts,
                                 ch3_watts=msg.ch3_watts,
                                 total_watts=msg.total_watts,
                                 temp_f=msg.temp_f).save()
                except Exception as e:
                    logger.error('Unhandled exception from db save: {}'.format(e))

        logger.info('Exiting.')

def main():
    logging.basicConfig(format='[%(asctime)s/%(name)s]: %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger('main')
    if DEBUG:
        logger.setLevel(logging.DEBUG)

    work_queue = Queue()
    logger.info('Starting collector.')
    collector = Collector(work_queue)
    collector.start()
    logger.info('Starting writer.')
    writer = Writer(work_queue)
    writer.start()

    while (collector is not None and collector.isAlive() and
           writer is not None and writer.isAlive()):
        try:
            collector.join(1)
            writer.join(1)
        except KeyboardInterrupt:
            logger.info('Ctrl-C received, exiting.')
            collector.exiting = True
            writer.exiting = True

    logger.info('Exiting.')

if __name__ == '__main__':
    main()
