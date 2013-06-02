################################################################################
# Local settings
################################################################################
DEBUG=True
LOCAL_TIMEZONE='America/New_York'

################################################################################
# MongoDB settings
################################################################################
MONGO_HOST='quigon'
MONGO_DATABASE_NAME='energymon'

################################################################################
# redis settings
################################################################################
#REDIS_HOST_NAME='revan'
#REDIS_HOST_NAME='localhost'
#REDIS_SET_NAME='energymon_set'
#REDIS_HASH_NAME='energymon_hash'
#SQLITE_DATABASE_PATH='/home/clinstid/src/energymon/energymon.sqlite3'

################################################################################
# EnviR settings
################################################################################
#ENVIR_MSG_HOST = 'malak'
#ENVIR_EXCHANGE_NAME = 'envir'
#ENVIR_MSG_QUEUE_NAME = 'envir'

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
