#!/usr/bin/env python
from flask import Flask, render_template
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
import json
from mongoengine import *
import logging

from utc_conversion import *
from models import *
from settings import *

app = Flask(__name__)

def local_str_from_naive_utc_dt(naive_utc_dt):
    local_tz = pytz.timezone(LOCAL_TIMEZONE)
    local_time = pytz.utc.localize(naive_utc_dt).astimezone(local_tz)
    return local_time.strftime("%a %b %d %H:%M %Z")


def get_last_entry():
    connect(host=MONGO_HOST,
            db=MONGO_DATABASE_NAME)
    return EnvirReading.objects.order_by('-reading_timestamp').first()

def get_last_hour():
    now = datetime.now(tz=pytz.utc)
    one_hour_ago = now - timedelta(hours=1)
    connect(host=MONGO_HOST,
            db=MONGO_DATABASE_NAME)
    query = EnvirReading.objects(reading_timestamp__gte=one_hour_ago)
    return map(lambda reading: [int(dt_to_seconds(reading.reading_timestamp))*1000, 
                                reading.total_watts], 
               query) 

@app.route('/')
def start_app():
    last_entry = get_last_entry()
    return render_template('index.html',
                           local_timezone=LOCAL_TIMEZONE,
                           date=local_str_from_naive_utc_dt(last_entry.reading_timestamp),
                           usage=last_entry.total_watts,
                           temp_f=last_entry.temp_f)

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
                       'date': local_str_from_naive_utc_dt(last_entry.reading_timestamp),
                       'usage': last_entry.total_watts,
                       'temp_f': last_entry.temp_f
                      })

@app.teardown_request
def shutdown_session(exception=None):
    pass

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s/%(name)s]: %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger('main')
    app.run(host='0.0.0.0', debug=True)

