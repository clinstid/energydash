#!/usr/bin/env python
from datetime import datetime, timedelta
import pytz
import threading
from time import sleep
from dateutil.relativedelta import relativedelta
import sys

from models import Usage
from database import db_session
from energymon_app import app

class ReadingPeriod(object):
    """ 
    Defines a list of readings in watts over a time period denoted by start
    and end. Stores an average over this time period.
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.readings = []
        self.timestamps = []
        self.average = 0.0
        self.reading_total = 0
        self.min_reading = 0
        self.max_reading = 0
    
    def add_reading(self, reading):
        if reading.timestamp not in self.timestamps:
            self.readings.append(reading.usage_in_watts)
            self.timestamps.append(reading.timestamp)
            #print ">> Adding reading {}".format(reading)

    def update_stats(self):
        self.reading_total = sum(self.readings)
        self.reading_count = len(self.readings)
        self.average = self.reading_total/self.reading_count 
        self.min_reading = min(self.readings)
        self.max_reading = max(self.readings)
        #print ">>        count {} avg {} min {} max {} total {}".format(self.reading_count,
        #                                                                self.average,
        #                                                                self.min_reading,
        #                                                                self.max_reading,
        #                                                                self.reading_total)
        #for timestamp in self.timestamps:
        #    print ">>    {}".format(timestamp)

class ReadingPeriods(object):
    def __init__(self):
        self.rp_list = []

    def dump_timestamps(self):
        rp_count = 0
        for rp in self.rp_list:
            print ">>    {}".format(rp_count)
            for timestamp in rp.timestamps:
                print ">>        {}".format(timestamp)
            rp_count += 1

    def find_reading_period(self, start_time):
        #print ">> Looking for reading period for {}".format(start_time)
        if not self.rp_list or len(self.rp_list) == 0:
            #print ">> self.rp_list is empty"
            return None

        current_rp_index = 0
        while current_rp_index < len(self.rp_list):
            #print ">> Trying {} - {} --> {}".format(current_rp_index, 
            #                                        self.rp_list[current_rp_index].start,
            #                                        self.rp_list[current_rp_index].end)
            if (start_time >= self.rp_list[current_rp_index].start and 
                start_time < self.rp_list[current_rp_index].end):
                #print ">> Found reading period at {}".format(current_rp_index)
                return self.rp_list[current_rp_index]
            else:
                current_rp_index += 1

        #print ">> No matching ReadingPeriod was found."
        return None

    def update_stats(self):
        self.reading_total = 0
        self.min_reading = sys.maxint
        self.max_reading = 0
        self.reading_count = 0
        self.average = 0

        for rp in self.rp_list:
            rp.update_stats()
            self.min_reading = min(self.min_reading, rp.min_reading)
            self.max_reading = max(self.max_reading, rp.max_reading)
            self.reading_total += rp.reading_total 
            self.reading_count += rp.reading_count

        if self.reading_count == 0:
            return

        self.average = float(self.reading_total)/float(self.reading_count)

        print ">>    count {} avg {} min {} max {} total {}".format(self.reading_count,
                                                                    self.average,
                                                                    self.min_reading,
                                                                    self.max_reading,
                                                                    self.reading_total)
    def update_cache(self, now, query_start):
        # Clean up our list to remove old values and figure out where we left off
        if self.rp_list:
            last_period = None
            print ">>    Cleanup - start count {}".format(len(self.rp_list))
            self.rp_list[:] = filter(lambda x: x.start >= query_start,
                                     self.rp_list)
            print ">>    Cleanup - end count {}".format(len(self.rp_list))
            if len(self.rp_list) > 0:
                last_period = self.rp_list[-1]
            if last_period is not None:
                query_start = last_period.start

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

        for entry in entries:
            if entry.timestamp.tzinfo is None:
                entry.timestamp = pytz.utc.localize(entry.timestamp)

            rp = self.find_reading_period(start_time=entry.timestamp)
            if not rp:
                start = self.get_period_start_for_entry(entry) 
                end = self.get_period_end_from_start(start) 
                rp = ReadingPeriod(start=start, end=end)
                #print ">> Created ReadingPeriod for {} --> {}".format(start, end)
                self.rp_list.append(rp)
                                       
            rp.add_reading(entry)

        self.update_stats()
        
class MinuteReadingPeriods(ReadingPeriods):
    def __init__(self, minutes):
        ReadingPeriods.__init__(self)
        self.minutes = minutes

    def get_period_end_from_start(self, start):
        return start + relativedelta(minutes=+self.minutes)

    @staticmethod
    def get_period_start_for_entry(entry):
        return datetime(year=entry.timestamp.year,
                        month=entry.timestamp.month,
                        day=entry.timestamp.day,
                        hour=entry.timestamp.hour,
                        minute=entry.timestamp.minute,
                        second=0,
                        tzinfo=pytz.utc)

class HourReadingPeriods(ReadingPeriods):
    def __init__(self, hours):
        ReadingPeriods.__init__(self)
        self.hours = hours

    def get_period_end_from_start(self, start):
        return start + relativedelta(hours=+self.hours)

    @staticmethod
    def get_period_start_for_entry(entry):
        return datetime(year=entry.timestamp.year,
                        month=entry.timestamp.month,
                        day=entry.timestamp.day,
                        hour=entry.timestamp.hour,
                        minute=0,
                        second=0,
                        tzinfo=pytz.utc)

class DayReadingPeriods(ReadingPeriods):
    def __init__(self, days):
        ReadingPeriods.__init__(self)
        self.days = days

    def get_period_end_from_start(self, start):
        return start + relativedelta(days=+self.days)

    @staticmethod
    def get_period_start_for_entry(entry):
        return datetime(year=entry.timestamp.year,
                        month=entry.timestamp.month,
                        day=entry.timestamp.day,
                        hour=0,
                        minute=0,
                        second=0,
                        tzinfo=pytz.utc)

class MonthReadingPeriods(ReadingPeriods):
    def __init__(self, months):
        ReadingPeriods.__init__(self)
        self.months = months

    def get_period_end_from_start(self, start):
        return start + relativedelta(months=+self.months)

    @staticmethod
    def get_period_start_for_entry(entry):
        return datetime(year=entry.timestamp.year,
                        month=entry.timestamp.month,
                        day=1,
                        hour=0,
                        minute=0,
                        second=0,
                        tzinfo=pytz.utc)

class Cache(object):
    def __init__(self):
        self.minutes_from_last_hour = MinuteReadingPeriods(minutes=1)
        self.hours_from_last_24_hours = HourReadingPeriods(hours=1)
        self.four_hours_from_last_7_days = HourReadingPeriods(hours=4)
        self.four_hours_from_last_30_days = HourReadingPeriods(hours=4)
        self.days_from_last_3_months = DayReadingPeriods(days=1)
        self.months_from_last_year = MonthReadingPeriods(months=1)

    def cleanup(self):
        pass

    def run(self):
        print ">> Starting energymon_cache."
        while True:
            now = datetime.now(tz=pytz.utc)
            print ">> Updating last hour"
            self.minutes_from_last_hour.update_cache(now=now,
                                                     query_start=now+relativedelta(hours=-1))
            #self.minutes_from_last_hour.dump_timestamps()
            print ">> Updating last 24 hours"
            self.hours_from_last_24_hours.update_cache(now=now,
                                                       query_start=now+relativedelta(hours=-24))
            print ">> Updating last 7 days"
            self.four_hours_from_last_7_days.update_cache(now=now,
                                                          query_start=now+relativedelta(days=-7))
            print ">> Updating last 30 days"
            self.four_hours_from_last_30_days.update_cache(now=now,
                                                          query_start=now+relativedelta(days=-30))
            print ">> Updating last 3 months"
            self.days_from_last_3_months.update_cache(now=now,
                                                      query_start=now+relativedelta(months=-30))
            print ">> Updating last year"
            self.months_from_last_year.update_cache(now=now,
                                                    query_start=now+relativedelta(years=-1))
            sleep(30)

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
