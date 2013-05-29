#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pytz

from database import db_session
from models import Usage
from settings import SQLITE_DATABASE_PATH

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(SQLITE_DATABASE_PATH)
db = SQLAlchemy(app)

@app.route('/')
def start_app():
    message = 'energymon 1.0<br/>\n'
    count = 0
    retries = 5
    while retries > 0:
        try:
            count = db_session.query(Usage).count()
            break
        except OperationalError as e:
            print "Count failed [{}], retries left {}.".format(e, retries)
            retries -= 1

    message += 'Usage entries: {}<br/>\n'.format(count)

    return message

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

