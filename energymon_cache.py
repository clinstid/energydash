#!/usr/bin/env python
from datetime import datetime, timedelta
import pytz
import threading
from time import sleep
from dateutil.relativedelta import relativedelta
import sys
from collections import OrderedDict
import redis

from models import Usage
from database import db_session
from energymon_app import app
from settings import REDIS_HOST_NAME, REDIS_SET_NAME, REDIS_HASH_NAME
from utc_conversion import *

class Minute(object):
    def __init__(self, dt_in_minute):
        self.dt = datetime(year=dt_in_minute.year, 
                           month=dt_in_minute.month, 
                           day=dt_in_minute.day, 
                           hour=dt_in_minute.hour,
                           minute=dt_in_minute.minute,
                           second=0,
                           tzinfo=pytz.utc)
        self.end_dt = self.dt + relativedelta(minutes=+1)
        self.seconds_since_epoch = int(round(dt_to_seconds(self.dt)))
        self.average = 0
        self.reading_count = 0
        print ">>    Minute: {}".format(self.dt)

    def dt_in_this_minute(self, dt):
        return (dt >= self.dt and dt < self.end_dt)

    def add_reading(self, reading):
        total = float(self.average * self.reading_count)
        total += reading
        self.reading_count += 1
        self.average = int(round(total/self.reading_count))
        print ">>        {} watts".format(reading)
        
class Cache(object):
    def __init__(self):
        self.readings = OrderedDict()
        self.red = redis.StrictRedis(host=REDIS_HOST_NAME)

    def cleanup(self):
        pass

    def update_cache(self, now):
        result = self.red.zrange(REDIS_SET_NAME, -1, -1, withscores=True)
        query_start = now + relativedelta(years=-1)
        if len(result) > 0:
            query_start = max(query_start, seconds_to_dt(int(result[0][1])))
        
        print ">>    Querying from {} to {}".format(query_start, now)
        query_complete = False
        query_retries = 5
        while not query_complete and not query_retries == 0:
            try:
                entries = db_session.query(Usage).filter(Usage.timestamp > query_start)
                query_complete = True
            except sqlalchemy.exc.OperationalError as e:
                query_retries -= 1
                print ">> Query failed: [{}], {} retries left.".format(e, query_retries)
                sleep(1)

        if entries.count() == 0:
            return None

        current_minute = None
        for entry in entries:
            if entry.timestamp.tzinfo is None:
                entry.timestamp = pytz.utc.localize(entry.timestamp)

            if current_minute is None:
                current_minute = Minute(entry.timestamp)
            elif not current_minute.dt_in_this_minute(entry.timestamp):
                self.red.zadd(REDIS_SET_NAME, 
                              current_minute.seconds_since_epoch, 
                              str(current_minute.seconds_since_epoch))
                self.red.hset(REDIS_HASH_NAME, 
                              str(current_minute.seconds_since_epoch), 
                              current_minute.average)
                current_minute = Minute(entry.timestamp)

            current_minute.add_reading(entry.usage_in_watts)

    def run(self):
        print ">> Starting energymon_cache."
        while True:
            now = datetime.now(tz=pytz.utc)
            self.update_cache(now)
            sleep(60)

def main():
    cache = Cache()
    try:
        cache.run()
    except KeyboardInterrupt:
        print "Caught keyboard interrupt, exiting."
        cache.cleanup()
        sys.exit()

if __name__ == '__main__':
    main()
