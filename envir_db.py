#!/usr/bin/env python
import sys
import string
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import pytz
from time import sleep
import logging
import amqplib.client_0_8 as amqp

from envir_settings import *
from database import db_session
from models import Usage
from settings import LOCAL_TIMEZONE

LOGGER = logging.getLogger(__name__)

class Envir(object):
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

    def __init__(self):
        print ">> Connecting to rabbitmq {}".format(ENVIR_MSG_HOST)
        self.connection = amqp.Connection(host=ENVIR_MSG_HOST)
        self.channel = self.connection.channel()
        self.channel.access_request('/data', active=True, read=True) 
        self.channel.exchange_declare(exchange=ENVIR_EXCHANGE_NAME, 
                                      type='fanout',
                                      auto_delete=False,
                                      durable=True)
        self.channel.queue_declare(queue=ENVIR_MSG_QUEUE_NAME,
                                   durable=True,
                                   auto_delete=False)
        self.channel.queue_bind(queue=ENVIR_MSG_QUEUE_NAME,
                                exchange=ENVIR_EXCHANGE_NAME)
        self.channel.basic_consume(ENVIR_MSG_QUEUE_NAME, callback=Envir.handle_message)

    def cleanup(self):
        self.channel.close()
        self.connection.close()

    def run(self):
        print ">> envir running"
        while self.channel.callbacks:
            self.channel.wait()

    @staticmethod
    def handle_message(message):
        try:
            msg = Msg(message.body)
            msg.print_csv(sys.stdout)
            usage = Usage(timestamp=msg.timestamp.astimezone(pytz.utc), usage_in_watts=msg.total_watts)
            db_session.add(usage)
            db_session.commit()
        except ET.ParseError as e:
            print "Invalid XML, skipping '{}': {}".format(message.body, repr(e))

        message.channel.basic_ack(message.delivery_tag)

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
        self.received_timestamp = datetime.now(tz=pytz.timezone(LOCAL_TIMEZONE))

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
        envir.run()
    except KeyboardInterrupt:
        print "Caught keyboard interrupt, exiting."
        envir.cleanup()
        sys.exit()

if __name__ == '__main__':
    main()
