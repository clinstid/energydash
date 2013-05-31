#!/usr/bin/env python
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pytz
import redis
from dateutil.relativedelta import relativedelta
import json

from utc_conversion import *
from database import db_session
from models import Usage
from settings import *
import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(SQLITE_DATABASE_PATH)
db = SQLAlchemy(app)

@app.route('/')
def start_app():

    r = redis.StrictRedis(REDIS_HOST_NAME)
    count = r.zcard(REDIS_SET_NAME)

    now = datetime.now(tz=pytz.utc)
    end = dt_to_seconds(now)
    start = dt_to_seconds(now + relativedelta(hours=-8))
    keys = r.zrangebyscore(REDIS_SET_NAME, start, end)
    pipe = r.pipeline()
    for key in keys:
        pipe.hget(REDIS_HASH_NAME, key)

    values = pipe.execute()

    print 'keys[{}], values[{}]'.format(len(keys), len(values))

    # google chart data_table
    #data_table = {'cols': [{'id': 'minute', 'label': 'Minute', 'type': 'string'},
    #                       {'id': 'watts', 'label': 'Watts', 'type': 'number'}],
    #              'rows': [] }
    #for i in range(min(len(keys), len(values))):
    #    data_table['rows'].append({'c': [{'v': str(seconds_to_dt(keys[i]))},
    #                                     {'v': int(values[i])}]})

    # jquery flot data_table
    data_table = []
    for i in range(min(len(keys), len(values))):
        data_table.append([str(seconds_to_dt(keys[i])), int(values[i])])

    return render_template('charts.html',
                           usage_data=data_table,
                           num_entries=len(keys))

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

