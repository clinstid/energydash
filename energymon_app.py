#!/usr/bin/env python
from flask import Flask, render_template
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
import json
from mongoengine import *

from utc_conversion import *
from models import *
from settings import *

app = Flask(__name__)

def get_last_entry():
    connect(host=MONGO_HOST,
            db=MONGO_DATABASE_NAME)
    return EnvirReading.objects.order_by('-reading_timestamp').first()

@app.route('/')
def start_app():
    last_entry = get_last_entry()
    return render_template('index.html',
                           date=last_entry.reading_timestamp,
                           usage=last_entry.total_watts,
                           temp_f=last_entry.temp_f)

@app.route('/current_state')
def fetch_current_state():
    last_entry = get_last_entry()
    return render_template('current_state.html',
                           date=last_entry.reading_timestamp,
                           usage=last_entry.total_watts,
                           temp_f=last_entry.temp_f)

@app.teardown_request
def shutdown_session(exception=None):
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

