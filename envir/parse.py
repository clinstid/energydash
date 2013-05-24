#!/usr/bin/python
import sys
import string
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz

class EnviR:
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

    birth_tz = pytz.timezone('America/New_York')
    birth_date = datetime(year=2013, month=5, day=18, tzinfo=birth_tz)

class Msg(object):

    def __init__(self, root):
        self.src = root.findtext(EnviR.SRC_TAG)
        self.dsb = Msg.get_text_as_int(root, EnviR.DAYS_SINCE_BIRTH_TAG)
        self.time24 = root.findtext(EnviR.TIME_TAG)
        self.temp_c = Msg.get_text_as_float(root, EnviR.TEMP_C_TAG)
        self.temp_f = Msg.get_text_as_float(root, EnviR.TEMP_F_TAG)
        self.radio_id = Msg.get_text_as_int(root, EnviR.RADIO_ID_TAG)
        self.sensor_type = Msg.get_text_as_int(root, EnviR.TYPE_TAG)

        self.ch1_watts = 0
        self.ch2_watts = 0
        self.ch3_watts = 0

        ch1 = root.find(EnviR.CH1_TAG)
        if ch1 is not None:
            self.ch1_watts = Msg.get_text_as_int(ch1, EnviR.WATTS_TAG)

        ch2 = root.find(EnviR.CH2_TAG)
        if ch2 is not None:
            self.ch2_watts = Msg.get_text_as_int(ch2, EnviR.WATTS_TAG)

        ch3 = root.find(EnviR.CH3_TAG)
        if ch3 is not None:
            self.ch3_watts = Msg.get_text_as_int(ch3, EnviR.WATTS_TAG)

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
        self.timestamp = EnviR.birth_date + time_delta_since_birth

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
    if len(sys.argv) < 2:
        print "Usage: {} <xml-file> [<output-csv-file>]".format(sys.argv[0])
        sys.exit()

    xml_file = open(sys.argv[1])
    xml = xml_file.read()

    clean_xml = filter(lambda x: x in string.printable, xml)

    # List of messages
    messages = []

    for xml_line in clean_xml.splitlines():
        #print xml_line
        try:
            tree = ET.fromstring(xml_line)
        except:
            print "Skipping:", xml_line
            continue

        if tree.tag == EnviR.MSG_TAG:
            messages.append(Msg(tree))

    output_file = sys.stdout
    if len(sys.argv) == 3:
        output_file = open(sys.argv[2], 'w')

    for message in messages:
        message.print_csv(output_file)

    output_file.close()

if __name__ == '__main__':
    main()
