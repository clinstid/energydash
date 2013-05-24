#!/usr/bin/python
import sys
import string
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz


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
