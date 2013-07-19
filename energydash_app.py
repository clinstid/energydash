#!/usr/bin/env python

################################################################################
# file:        energydash_app.py
# description: energydash web application
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

from flask import Flask, render_template
from datetime import datetime, timedelta
import pytz
import json
import pymongo
import logging
import urllib
import sys

from utc_conversion import *
from settings import *

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stream=sys.stderr))
mongo_uri = 'mongodb://{user}:{password}@{host}/{database}'.format(user=urllib.quote(MONGO_USER),
                                                                   password=urllib.quote(MONGO_PASSWORD),
                                                                   host=MONGO_HOST,
                                                                   database=MONGO_DATABASE_NAME)
client = pymongo.MongoReplicaSetClient(hosts_or_uri=mongo_uri,
                                       replicaSet=MONGO_REPLICA_SET,
                                       read_preference=pymongo.read_preferences.ReadPreference.NEAREST)
db = client[MONGO_DATABASE_NAME]
readings = db.envir_reading
hours = db.hours
bookmarks = db.bookmarks

day_map = {
           'Mon': 1,
           'Tue': 2,
           'Wed': 3,
           'Thu': 4,
           'Fri': 5,
           'Sat': 6,
           'Sun': 7
           }

def get_min(entries, key):
    return min(map(lambda entry: entry[key], entries)) 

def get_max(entries, key):
    return max(map(lambda entry: entry[key], entries))

def get_avg(entries, key):
    key_entries = map(lambda entry: entry[key], entries)
    return sum(key_entries) / len(key_entries)

def get_last_entry():
    return bookmarks.find_one({'_id': 'seconds'})

def get_last_hour():
    now = datetime.now(tz=pytz.utc)
    one_hour_ago = now - timedelta(hours=1)
    readings.ensure_index('reading_timestamp', pymongo.ASCENDING)
    cursor = readings.find({'reading_timestamp': {'$gte': one_hour_ago}})
    cursor = cursor.sort('reading_timestamp', pymongo.ASCENDING)
    return map(lambda reading: [int(dt_to_seconds(reading['reading_timestamp']))*1000, 
                                reading['total_watts']], 
               cursor) 

@app.route('/')
def start_app():
    last_entry = get_last_entry()
    return render_template('index.html',
                           local_timezone=LOCAL_TIMEZONE,
                           date=local_str_from_naive_utc_dt(last_entry['timestamp'],
                                                            LOCAL_TIMEZONE),
                           usage=last_entry['usage'],
                           temp_f=last_entry['tempf'])

@app.route('/current_chart')
def fetch_current_chart():
    last_hour = get_last_hour()
    logger = logging.getLogger('current_chart')
    logger.info('{} entries from the last hour: {} --> {}.'.format(len(last_hour), 
                                                                   last_hour[0][0], 
                                                                   last_hour[-1][0]))
    logger.debug(last_hour)
    return json.dumps(last_hour)

@app.route('/current_state')
def fetch_current_state():
    last_entry = get_last_entry()
    return json.dumps({
                       'date': local_str_from_naive_utc_dt(last_entry['timestamp'],
                                                           LOCAL_TIMEZONE),
                       'usage': last_entry['usage'],
                       'temp_f': last_entry['tempf']
                      })

@app.route('/hod')
def hours_of_day():
    hours_in_day = db.hours_in_day
    cursor = hours_in_day.find({}, {'_id': 1, 'average_usage': 1, 'average_tempf': 1})
    usage_list = []
    tempf_list = []
    for hour in cursor:
        usage_list.append([int(hour['_id']), hour['average_usage']])
        tempf_list.append([int(hour['_id']), hour['average_tempf']])
    hours_list = [
             {
              'label': 'Usage (watts)',
              'data': sorted(usage_list, key=lambda hour: hour[0]),
              'yaxis': 1
             },
             {
              'label': 'Temperature (&#176; F)',
              'data': sorted(tempf_list, key=lambda hour: hour[0]),
              'yaxis': 2
             }
            ]
    return json.dumps(hours_list)

@app.route('/last_24_hours')
def last_24_hours():
    now = datetime.now(tz=pytz.utc)
    start = now - timedelta(hours=24)
    usage_list = []
    tempf_list = []
    cursor = hours.find({'_id': {'$gte': start}},
                        {
                            '_id': 1,
                            'average_usage': 1,
                            'average_tempf': 1
                        })
    for hour in cursor: 
        usage_list.append([int(dt_to_seconds(hour['_id']))*1000,
                           hour['average_usage']])
        tempf_list.append([int(dt_to_seconds(hour['_id']))*1000,
                           hour['average_tempf']])

    hours_list = [
                  {
                   'label': 'Usage (watts)',
                   'data': sorted(usage_list, key=lambda hour: hour[0]),
                   'yaxis': 1
                   },
                  {
                   'label': 'Temperature (&#176; F)',
                   'data': sorted(tempf_list, key=lambda hour: hour[0]),
                   'yaxis': 2
                   }
                  ]
    obj = {
           'chart_data': hours_list,
           'min_usage': round(get_min(usage_list, 1), 2),
           'max_usage': round(get_max(usage_list, 1), 2),
           'avg_usage': round(get_avg(usage_list, 1), 2),
           'min_tempf': round(get_min(tempf_list, 1), 2),
           'max_tempf': round(get_max(tempf_list, 1), 2),
           'avg_tempf': round(get_avg(tempf_list, 1), 2)
           }
    return json.dumps(obj)

def get_dow():
    day_map = {
               'Mon': 1,
               'Tue': 2,
               'Wed': 3,
               'Thu': 4,
               'Fri': 5,
               'Sat': 6,
               'Sun': 7
               }
    hours_per_dow = db.hours_per_dow
    cursor = hours_per_dow.find({},
                                {
                                    '_id': 1,
                                    'hours': 1
                                })
    days = [] 
    for day in cursor:
        hour_list = []
        for hour, data in day['hours'].iteritems():
            hour_list.append([int(hour), data['average_usage']])
        hour_list = sorted(hour_list, key=lambda hour: hour[0])
        days.append({ 
                     'label': day['_id'],
                     'data': hour_list
                    })
        days = sorted(days, key=lambda day: day_map[day['label']])

    return days

@app.route('/dow')
def days_of_week():
    return json.dumps(get_dow())

@app.teardown_request
def shutdown_session(exception=None):
    pass

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s/%(name)s]: %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger('main')
    app.run(host='0.0.0.0', debug=True)

