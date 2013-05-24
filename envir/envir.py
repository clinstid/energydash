#!/usr/bin/env python
import sys
import string
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz
import pika

from envir_settings import *

class Envir:
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
                          tzinfo=pytz.timezone(ENVIR_BIRTH_TZ))

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=ENVIR_MSG_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=ENVIR_QUEUE_NAME, durable=True)
        self.channel.basic_consume(Envir.handle_message,
                                   queue=ENVIR_QUEUE_NAME,
                                   no_ack=False)

    def start(self):
        self.channel.start_consuming()

    @staticmethod
    def handle_message(ch, method, properties, body):
        try:
            msg = Msg(body)
        except ET.ParseError as e:
            print "Skipping '{}': {}".format(body, repr(e))
            return

        msg.print_csv(sys.stdout)
        ch.basic_ack(delivery_tag=method.delivery_tag)

class MsgException(Exception):
    pass

class Msg(object):

    def __init__(self, body):
        root = ET.fromstring(body)

        if not root.tag == Envir.MSG_TAG:
            raise MsgException('Unexpected tag "{}" encountered. Expected "{}"'.format(root.tag,
                                                                                       Envir.MSG_TAG))

        self.src = root.findtext(Envir.SRC_TAG)
        self.dsb = Msg.get_text_as_int(root, Envir.DAYS_SINCE_BIRTH_TAG)
        self.time24 = root.findtext(Envir.TIME_TAG)
        self.temp_c = Msg.get_text_as_float(root, Envir.TEMP_C_TAG)
        self.temp_f = Msg.get_text_as_float(root, Envir.TEMP_F_TAG)
        self.radio_id = Msg.get_text_as_int(root, Envir.RADIO_ID_TAG)
        self.sensor_type = Msg.get_text_as_int(root, Envir.TYPE_TAG)

        self.ch1_watts = 0
        self.ch2_watts = 0
        self.ch3_watts = 0

        ch1 = root.find(Envir.CH1_TAG)
        if ch1 is not None:
            self.ch1_watts = Msg.get_text_as_int(ch1, Envir.WATTS_TAG)

        ch2 = root.find(Envir.CH2_TAG)
        if ch2 is not None:
            self.ch2_watts = Msg.get_text_as_int(ch2, Envir.WATTS_TAG)

        ch3 = root.find(Envir.CH3_TAG)
        if ch3 is not None:
            self.ch3_watts = Msg.get_text_as_int(ch3, Envir.WATTS_TAG)

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
        self.timestamp = Envir.birth_date + time_delta_since_birth

    def print_csv(self, output_file):
         output_file.write('"{timestamp}",{total_watts}\n'.format(timestamp=self.timestamp, total_watts=self.total_watts))

    @staticmethod
    def get_text_as_float(elem, tag):
        text = elem.findtext(tag)
        if text:
            return float(text)
        else:
            return text

    @staticmethod
    def get_text_as_int(elem, tag):
        text = elem.findtext(tag)
        if text:
            return int(text)
        else:
            return text

def main():
    envir = Envir()
    try:
        envir.start()
    except KeyboardInterrupt:
        print "Caught keyboard interrupt, exiting."
        sys.exit()

if __name__ == '__main__':
    main()
