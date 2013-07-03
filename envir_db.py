#!/usr/bin/env python
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
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

