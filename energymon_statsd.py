#!/usr/bin/env python
import pymongo
import logging
from time import sleep
from datetime import datetime, timedelta
import pytz
import urllib

from settings import *
from utc_conversion import *

def update_average(old_average, old_count, new_value):
    '''
    Update an existing average using the old average, the old count, and the
    new value. The result is returned in a tuple: (new_average, new_count)
    '''
    new_count = old_count + 1
    new_average = ((old_average * old_count) + new_value) / new_count
    return (new_average, new_count)

class Stats(object):
    def __init__(self):
        self.stopping = False
        mongo_uri = 'mongodb://{user}:{password}@{host}/{database}'.format(user=urllib.quote(MONGO_USER),
                                                                           password=urllib.quote(MONGO_PASSWORD),
                                                                           host=MONGO_HOST,
                                                                           database=MONGO_DATABASE_NAME)
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[MONGO_DATABASE_NAME]
        self.logger = logging.getLogger('Stats')

    def stop(self):
        self.client.disconnect()
        self.stopping = True

    def update_hours_from_readings(self):
        '''
        This method updates the hours collection with documents that contain
        the average usage and temp_f by hour for all of the data available from
        the envir_reading collection.

        Collections used:
            1. envir_reading: Collection of readings from energy monitor
               receiver every 6 seconds.

            2. hours: Collection of usage and temp_f averages for each hour
               over all of the collected data.
        '''

        readings = self.db.envir_reading
        hours = self.db.hours
        bookmarks = self.db.bookmarks
        logger = self.logger

        logger.info('Updating hours from envir_reading.')

        # Figure out where we left off by finding the timestamp of the last
        # bookmark.
        reading_bookmark = bookmarks.find_one({'_id': 'envir_reading'})
        if reading_bookmark is None:
            reading_bookmark = { 
                                     '_id': 'envir_reading',
                                     'timestamp': epoch 
                                    }

        logger.info('Last bookmark was {}'.format(reading_bookmark))

        logger.info('{} total readings.'.format(readings.count()))
        cursor = readings.find({'reading_timestamp': {'$gt': reading_bookmark['timestamp']}})
        logger.info('{} new readings since last bookmark.'.format(cursor.count()));

        current_hour = None
        for reading in cursor:
            if reading['total_watts'] == 0 or reading['temp_f'] == 0:
                continue

            timestamp = reading['reading_timestamp']
            if not current_hour or timestamp >= (current_hour['_id'] + timedelta(hours=1)):
                if current_hour:
                    new_id = hours.save(current_hour)
                    logger.info("Moving to new hour {}".format(new_id))

                current_hour_start = datetime(year=timestamp.year,
                                              month=timestamp.month,
                                              day=timestamp.day,
                                              hour=timestamp.hour)
                logger.debug('Looking for hour at {}'.format(current_hour_start))
                current_hour = hours.find_one({'_id': current_hour_start})

                if current_hour is None:
                    current_hour = {
                                    '_id': current_hour_start,
                                    'count': 0,
                                    'average_usage': 0,
                                    'average_tempf': 0,
                                    'timestamps': []
                                   }
                    logger.debug('Creating hour document: {}'.format(current_hour_start))

            if timestamp not in current_hour['timestamps']:
                (current_hour['average_usage'], temp_count) = update_average(
                    old_average=current_hour['average_usage'],
                    old_count=current_hour['count'],
                    new_value=reading['total_watts'])
                (current_hour['average_tempf'], current_hour['count']) = update_average(
                    old_average=current_hour['average_tempf'],
                    old_count=current_hour['count'],
                    new_value=reading['temp_f'])

                current_hour['timestamps'].append(timestamp)

            reading_bookmark['timestamp'] = timestamp 

        if current_hour:
            new_id = hours.save(current_hour)
            logger.debug('Saved hour document {}'.format(new_id))
        if reading_bookmark:
            bookmarks.save(reading_bookmark)
            logger.info('Saved bookmark at {}.'.format(reading_bookmark))

    def update_hours_per_day_from_hours(self):
        '''
        This method updates two different collections:
            1. Update averages for each hour in any day, so we should have 24
               documents per collection that we updated.

            2. Update averages for each hour for each day of the week, so we
               should have 7 documents with 24 averages per day (both usage and
               temp_f).

        Collections used:
            1. hours: Collection of usage and temp_f averages for each hour
               over all of the collected data.

            2. hours_per_dow: Collection of usage and temp_f averages for each
               hour of each day of the week.

            3. hours_in_day: Collection of usage and temp_f averages for each
               hour in any day.
        '''
        logger = self.logger
        hours = self.db.hours
        hours_per_dow = self.db.hours_per_dow
        hours_in_day = self.db.hours_in_day
        bookmarks = self.db.bookmarks

        logger.info('Updating hours per day/dow from hours collection.')
        
        # We use a single bookmark for both hours per day of week and hours in
        # day because we're building those off of the same collection of hours.
        hour_bookmark = bookmarks.find_one({'_id': 'hours'})
        if hour_bookmark is None:
            hour_bookmark = {
                             '_id': 'hours',
                             'timestamp': epoch
                            }

        current_dow = None
        current_hour_of_day = None
        hours_cache = {}
        days_cache = {}
        local_tz = pytz.timezone(LOCAL_TIMEZONE)

        # We want $gte for finding our bookmark because we may have more values
        # in the last hour we processed that weren't there when we processed
        # them last.
        cursor = hours.find({'_id': {'$gte': hour_bookmark['timestamp']}})
        for hour in cursor:
            # We use a localized datetime for building these collections
            # because the day of the week values are really only relevant to
            # the timezone where the data is being collected. The hours in a
            # day don't really matter because they could be shifted by the
            # timezone offset of the browser, but again, the hours make more
            # sense when they're in the timezone of the collector. On top of
            # that, because we're localizing, we can compensate for DST since
            # we have the date.
            local_timestamp = pytz.utc.localize(hour['_id']).astimezone(local_tz)
            current_hour_num = str(local_timestamp.hour)
            logging.debug('Updating hour {}.'.format(current_hour_num))

            # Find the current_hour_of_day document to update.
            #
            # First check the current hour of day to see if it's what we want.
            if not current_hour_of_day or current_hour_of_day['_id'] != current_hour_num:
                # Next check in the hours cache
                if current_hour_num in hours_cache:
                    current_hour_of_day = hours_cache[current_hour_num]
                else:
                    # Next we go to the DB
                    current_hour_of_day = hours_in_day.find_one({'_id': current_hour_num})

                    if not current_hour_of_day:
                        # Not in the DB either, so we need to create a new document.
                        current_hour_of_day = {
                                               '_id': current_hour_num,
                                               'timezone': local_tz.zone,
                                               'average_usage': 0,
                                               'average_tempf': 0,
                                               'count': 0,
                                               'timestamps': []
                                              }

                    # Add the document (either what we pulled from the DB or
                    # just created) to the cache. We'll update the DB later
                    # when we're done processing the hours documents that we
                    # pulled from the DB.
                    hours_cache[current_hour_num] = current_hour_of_day

            if not hour['_id'] in current_hour_of_day['timestamps']:
                # Update the usage average.
                (current_hour_of_day['average_usage'], temp_count) = update_average(
                    old_average=current_hour_of_day['average_usage'],
                    old_count=current_hour_of_day['count'],
                    new_value=hour['average_usage'])

                # Update the tempf average.
                (current_hour_of_day['average_tempf'], current_hour_of_day['count']) = update_average(
                    old_average=current_hour_of_day['average_tempf'],
                    old_count=current_hour_of_day['count'],
                    new_value=hour['average_tempf'])

                current_hour_of_day['timestamps'].append(hour['_id'])

            # Find the current day of the week document to update. These are
            # indexed by the abbreviated day name (probably could have used day
            # of week number, but the day name is easier to read and can be
            # passed straight to whoever asks for it).
            day_name = local_timestamp.strftime('%a')
            logging.debug('Updating {}.'.format(day_name))
            # Same dance as the hours, check if the current dow is the right one.
            if not current_dow or current_dow['_id'] != day_name:
                # Check the days cache next.
                if day_name in days_cache:
                    current_dow = days_cache[day_name]
                else:
                    # Check the DB
                    current_dow = hours_per_dow.find_one({'_id': day_name})

                    if not current_dow:
                        # Create a new document.
                        current_dow = {
                                       '_id': day_name,
                                       'timezone': local_tz.zone,
                                       'hours': {},
                                      }

                    # Add the new/pulled from DB document to the cache.
                    days_cache[day_name] = current_dow

            if current_hour_num in current_dow['hours']:
                current_hour_of_dow = current_dow['hours'][current_hour_num]
            else:
                current_hour_of_dow = {
                                       'average_usage': 0,
                                       'average_tempf': 0,
                                       'count': 0,
                                       'timestamps': []
                                       }
                current_dow['hours'][current_hour_num] = current_hour_of_dow

            if not hour['_id'] in current_hour_of_dow['timestamps']:
                # Update the usage average.
                (current_hour_of_dow['average_usage'], temp_count) = update_average(
                    old_average=current_hour_of_dow['average_usage'],
                    old_count=current_hour_of_dow['count'],
                    new_value=hour['average_usage'])

                # Update the tempf average.
                (current_hour_of_dow['average_tempf'], current_hour_of_dow['count']) = update_average(
                    old_average=current_hour_of_dow['average_tempf'],
                    old_count=current_hour_of_dow['count'],
                    new_value=hour['average_tempf'])

            # Update the naive (UTC) datetime bookmark
            hour_bookmark['timestamp'] = hour['_id']

        # Save our updates to the DB
        for hour, doc in hours_cache.iteritems():
            hours_in_day.save(doc)
            logger.info('Saved hour {}.'.format(hour))

        for day, doc in days_cache.iteritems():
            hours_per_dow.save(doc)
            logger.info('Saved day {}.'.format(day))

        # Save the last bookmark we processed.
        bookmarks.save(hour_bookmark)
        logger.info('Saved bookmark {}'.format(hour_bookmark))

    def update_stats(self):
        self.update_hours_from_readings()
        self.update_hours_per_day_from_hours()

    def run(self):
        while not self.stopping:
            self.update_stats()
            sleep(60)

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
