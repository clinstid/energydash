#!/usr/bin/env python
# 
# envir_settings.py
#
# This file contains settings for an EnviR power monitor feed into a collector.
# Make sure you share the settings for both the collector and the receiver.
import serial
from settings import LOCAL_TIMEZONE

# Settings for rabbitmq 
ENVIR_MSG_HOST = 'revan'
ENVIR_QUEUE_NAME = 'envir'

# The XML provided by the EnviR includes "days since birth" so we need to know
# the "birth date" so we can calculate the actual timestamp for each message.
ENVIR_BIRTH_YEAR = 2013
ENVIR_BIRTH_MONTH = 5
ENVIR_BIRTH_DAY = 18
ENVIR_BIRTH_TZ_NAME = LOCAL_TIMEZONE

# Serial port options
ENVIR_SERIAL_PORT = '/dev/ttyUSB0'
ENVIR_SERIAL_BAUDRATE = 57600
ENVIR_SERIAL_BYTESIZE = serial.EIGHTBITS
ENVIR_SERIAL_PARITY = serial.PARITY_NONE
ENVIR_SERIAL_STOPBITS = serial.STOPBITS_ONE
ENVIR_SERIAL_TIMEOUT = 1
