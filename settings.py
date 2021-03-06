################################################################################
# file:        settings.py
# description: energydash settings
################################################################################
# Copyright 2013 Chris Linstid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

################################################################################
# Local settings
################################################################################
DEBUG=True
LOCAL_TIMEZONE='America/New_York'

################################################################################
# MongoDB settings
################################################################################
MONGO_DATABASE_NAME='energydash'

# Host name, user name and password are defined in a file NOT in revision
# control.
import mongodb_secret 
MONGO_USER=mongodb_secret.MONGO_USER
MONGO_PASSWORD=mongodb_secret.MONGO_PASSWORD
MONGO_HOST=mongodb_secret.MONGO_HOST
MONGO_REPLICA_SET=mongodb_secret.MONGO_REPLICA_SET

# The XML provided by the EnviR includes "days since birth" so we need to know
# the "birth date" so we can calculate the actual timestamp for each message.
ENVIR_BIRTH_YEAR = 2013
ENVIR_BIRTH_MONTH = 5
ENVIR_BIRTH_DAY = 18
ENVIR_BIRTH_TZ_NAME = LOCAL_TIMEZONE

# Serial port options
ENVIR_SERIAL_PORT = '/dev/ttyUSB0'
ENVIR_SERIAL_BAUDRATE = 57600
import serial
ENVIR_SERIAL_BYTESIZE = serial.EIGHTBITS
ENVIR_SERIAL_PARITY = serial.PARITY_NONE
ENVIR_SERIAL_STOPBITS = serial.STOPBITS_ONE
ENVIR_SERIAL_TIMEOUT = 1
