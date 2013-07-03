#!/usr/bin/env python
from flask import Flask, render_template
from datetime import datetime, timedelta
import pytz
import json
import pymongo
import logging

from utc_conversion import *
from settings import *

app = Flask(__name__)
client = pymongo.MongoClient(host=MONGO_HOST)
db = client[MONGO_DATABASE_NAME]
readings = db.envir_reading

def get_last_entry():
    return readings.find().sort('reading_timestamp', pymongo.DESCENDING).limit(1)[0]

def get_last_hour():
    now = datetime.now(tz=pytz.utc)
    one_hour_ago = now - timedelta(hours=1)
    cursor = readings.find({'reading_timestamp': {'$gte': one_hour_ago}})
    return map(lambda reading: [int(dt_to_seconds(reading['reading_timestamp']))*1000, 
                                reading['total_watts']], 
               cursor) 

@app.route('/')
def start_app():
    last_entry = get_last_entry()
    return render_template('index.html',
                           local_timezone=LOCAL_TIMEZONE,
                           date=local_str_from_naive_utc_dt(last_entry['reading_timestamp'],
                                                            LOCAL_TIMEZONE),
                           usage=last_entry['total_watts'],
                           temp_f=last_entry['temp_f'])

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
                       'date': local_str_from_naive_utc_dt(last_entry['reading_timestamp'],
                                                           LOCAL_TIMEZONE),
                       'usage': last_entry['total_watts'],
                       'temp_f': last_entry['temp_f']
                      })

@app.teardown_request
def shutdown_session(exception=None):
    pass

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s/%(name)s]: %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger('main')
    app.run(host='0.0.0.0', debug=True)

