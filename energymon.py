#!/usr/bin/env python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from database import db_session
from models import Usage

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/clinstid/src/energymon/energymon.sqlite3'
db = SQLAlchemy(app)

@app.route('/')
def start_app():
    message = 'energymon 1.0\n'
    message += 'Usage entries: {}\n'.format(db_session.query(Usage).count())
    return message

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)

