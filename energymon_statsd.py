#!/usr/bin/env python
import pymongo
import logging
from time import sleep
from datetime import datetime, timedelta
import pytz

from settings import *
from utc_conversion import *

class Stats(object):
    def __init__(self):
        self.stopping = False
        self.client = pymongo.MongoClient(host=MONGO_HOST)
        self.db = self.client[MONGO_DATABASE_NAME]
        self.logger = logging.getLogger('Stats')

    def stop(self):
        self.client.disconnect()
        self.stopping = True

    def update_stats(self):
        readings = self.db.envir_reading
        hours = self.db.hours
        days = self.db.days
        months = self.db.months
        watermarks = self.db.watermarks
        logger = self.logger

        # Figure out where we left off by finding the timestamp of the last
        # watermark.
        last_watermark = 0
        if watermarks.count() > 0:
            cursor = watermarks.find({}, {'_id': 0, 'timestamp': 1})
            cursor = cursor.sort('timestamp', pymongo.DESCENDING).limit(1)
            for watermark in cursor:
                last_watermark = watermark['timestamp']
        else:
            last_watermark = epoch

        logger.info('Last watermark was {}'.format(last_watermark))

        logger.info('{} total readings.'.format(readings.count()))
        cursor = readings.find({'reading_timestamp': {'$gt': last_watermark}})
        logger.info('{} new readings since last watermark.'.format(cursor.count()));

        current_hour = None
        current_day = None
        current_month = None
        new_watermark = last_watermark
        for reading in cursor:
            if reading['total_watts'] == 0 or reading['temp_f'] == 0:
                continue

            timestamp = pytz.utc.localize(reading['reading_timestamp'])
            if not current_hour or timestamp >= current_hour['_id'] + timedelta(hours=1):
                if current_hour:
                    hours.save(current_hour)

                current_hour_start = datetime(year=timestamp.year,
                                              month=timestamp.month,
                                              day=timestamp.day,
                                              hour=timestamp.hour,
                                              tzinfo=pytz.utc)
                current_hour = readings.find_one({'_id': current_hour_start})

                if current_hour is None:
                    current_hour = {'_id': current_hour_start,
                                    'count': 0,
                                    'average_usage': 0,
                                    'average_tempf': 0,
                                    'timestamps': []
                                   }
                    logger.info('Adding hour: {}'.format(current_hour_start))

            if timestamp not in current_hour['timestamps']:
                current_hour['average_usage'] = ((current_hour['average_usage'] * 
                                                  current_hour['count'] + reading['total_watts']) /
                                                 (current_hour['count'] + 1))
                current_hour['average_tempf'] = ((current_hour['average_tempf'] * 
                                                  current_hour['count'] + reading['temp_f']) /
                                                 (current_hour['count'] + 1))
                current_hour['count'] += 1;
                current_hour['timestamps'].append(timestamp)

            new_watermark = timestamp 

        # record our last watermark
        watermarks.insert({'timestamp': new_watermark})

    def run(self):
        while not self.stopping:
            self.update_stats()
            sleep(360)

def main():
    logging.basicConfig(format='[%(asctime)s/%(name)s]: %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger('main')
    if DEBUG:
        logger.setLevel(logging.DEBUG)

    stats = Stats()
    while not stats.stopping:
        try:
            stats.run()
        except KeyboardInterrupt:
            logger.info('Ctrl-C received, exiting.')
            stats.stop()
        except Exception as e:
            logger.error('Caught unhandled exception: {}'.format(e))
            stats.stop()
            raise

    logger.info('Exiting.')

if __name__ == '__main__':
    main()
