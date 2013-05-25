#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from database import db_session
from models import Usage
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/clinstid/src/energymon/energymon.sqlite3'
db = SQLAlchemy(app)

@app.route('/')
def start_app():
    message = 'energymon 1.0<br/>\n'
    message += 'Usage entries: {}<br/>\n'.format(db_session.query(Usage).count())
    #now = datetime.now(tz=pytz.timezone('America/New_York'))
    #twenty_four_hours_ago = now - timedelta(days=0, hours=24)
    #one_hour_ago = now - timedelta(days=0, hours=1)
    #last_24_hours = get_last_24_hours()db_session.query(Usage).filter(Usage.timestamp > twenty_four_hours_ago)
    #last_hour = db_session.query(Usage).filter(Usage.timestamp > one_hour_ago)
    #for usage in last_hour:
    #    message += repr(usage) + '<br/>\n'

    return message

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)

