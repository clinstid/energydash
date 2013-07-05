#!/usr/bin/env python
from serial import *
from threading import Thread
import logging
from datetime import datetime, timedelta
import pytz
from Queue import Queue
from time import sleep
import xml.etree.ElementTree as ET
import pymongo
from dateutil.tz import tzlocal

from settings import *

class MsgException(Exception):
    pass

def get_text_as_float(elem, tag):
    text = elem.findtext(tag)
    if text:
        return float(text)
    else:
        return text

def get_text_as_int(elem, tag):
    text = elem.findtext(tag)
    if text:
        return int(text)
    else:
        return text

class EnvirMsg(object):
    MSG_TAG = 'msg'
    SRC_TAG = 'src'
    DAYS_SINCE_BIRTH_TAG = 'dsb'
    TIME_TAG = 'time'
    TEMP_C_TAG = 'tmpr'
    TEMP_F_TAG = 'tmprF'
    RADIO_ID_TAG = 'id'
    TYPE_TAG = 'type'
    CH1_TAG = 'ch1'
    CH2_TAG = 'ch2'
    CH3_TAG = 'ch3'
    WATTS_TAG = 'watts'

    birth_date = datetime(year=ENVIR_BIRTH_YEAR, 
                          month=ENVIR_BIRTH_MONTH, 
                          day=ENVIR_BIRTH_DAY, 
                          tzinfo=tzlocal())

    def __init__(self, timestamp, body):
        self.reading_timestamp = timestamp
        root = ET.fromstring(body)

        if not root.tag == EnvirMsg.MSG_TAG:
            raise MsgException('Unexpected tag "{}" encountered. Expected "{}"'.format(root.tag,
                                                                                       EnvirMsg.MSG_TAG))

        self.src = root.findtext(EnvirMsg.SRC_TAG)
        self.dsb = get_text_as_int(root, EnvirMsg.DAYS_SINCE_BIRTH_TAG)
        self.time24 = root.findtext(EnvirMsg.TIME_TAG)
        self.temp_c = get_text_as_float(root, EnvirMsg.TEMP_C_TAG)
        self.temp_f = get_text_as_float(root, EnvirMsg.TEMP_F_TAG)
        self.radio_id = get_text_as_int(root, EnvirMsg.RADIO_ID_TAG)
        self.sensor_type = get_text_as_int(root, EnvirMsg.TYPE_TAG)

        self.ch1_watts = 0
        self.ch2_watts = 0
        self.ch3_watts = 0

        ch1 = root.find(EnvirMsg.CH1_TAG)
        if ch1 is not None:
            self.ch1_watts = get_text_as_int(ch1, EnvirMsg.WATTS_TAG)

        ch2 = root.find(EnvirMsg.CH2_TAG)
        if ch2 is not None:
            self.ch2_watts = get_text_as_int(ch2, EnvirMsg.WATTS_TAG)

        ch3 = root.find(EnvirMsg.CH3_TAG)
        if ch3 is not None:
            self.ch3_watts = get_text_as_int(ch3, EnvirMsg.WATTS_TAG)

        if not self.ch1_watts:
            self.ch1_watts = 0

        if not self.ch2_watts:
            self.ch2_watts = 0

        if not self.ch3_watts:
            self.ch3_watts = 0

        self.total_watts = self.ch1_watts + self.ch2_watts + self.ch3_watts
        
        time_split = self.time24.split(':')
        hours = int(time_split[0])
        minutes = int(time_split[1])
        seconds = int(time_split[2])
        time_delta_since_birth = timedelta(days=self.dsb, seconds=seconds, minutes=minutes, hours=hours)
        self.timestamp = EnvirMsg.birth_date + time_delta_since_birth

    def get_db_document(self):
        return { 
                'reading_timestamp': self.reading_timestamp,
                'receiver_days_since_birth': self.dsb,
                'receiver_time': self.time24,
                'ch1_watts': self.ch1_watts,
                'ch2_watts': self.ch2_watts,
                'ch3_watts': self.ch3_watts,
                'total_watts': self.total_watts,
                'temp_f': self.temp_f 
               }

    def print_csv(self, logger):
         logger.info('"{timestamp}",{total_watts}'.format(timestamp=self.reading_timestamp, 
                                                          total_watts=self.total_watts))

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
        self.client = pymongo.MongoClient(host=MONGO_HOST)
        self.db = self.client[MONGO_DATABASE_NAME]
        self.readings = self.db.envir_reading

    def run(self):
        logger = logging.getLogger('writer')
        while not self.exiting:
            logger.info('Waiting for work...')

            while not self.exiting:
                (timestamp, line) = self.work_queue.get()
                logger.debug('Received: {}: - {} (size={})'.format(timestamp, 
                                                                  line, 
                                                                  self.work_queue.qsize()))
                try:
                    msg = EnvirMsg(timestamp, line)
                except ET.ParseError as pe:
                    logger.error('XML parsing failed: {}'.format(pe))
                    continue
                except MsgException as me:
                    logger.error('EnvirMsg error: {}'.format(me))
                    continue
                except Exception as e:
                    logger.error('Unhandled exception while building EnvirMsg: {}'.format(e))
                    logger.error('  Line was: {}'.format(line.rstrip()))
                    continue

                # Skip 0 readings
                if msg.total_watts == 0:
                    continue

                reading = msg.get_db_document()
                logger.info('{} watts, {} F'.format(reading['total_watts'], reading['temp_f']))

                saved = False
                while not saved:
                    try:
                        self.readings.save(reading)
                        saved = True
                    except Exception as e:
                        logger.error('Unhandled exception from db save: {}'.format(e))
                        sleep(1)

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
