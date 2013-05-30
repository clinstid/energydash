#!/usr/bin/env python
from flask import Flask
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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(SQLITE_DATABASE_PATH)
db = SQLAlchemy(app)

@app.route('/')
def start_app():

    r = redis.StrictRedis(REDIS_HOST_NAME)
    count = r.zcard(REDIS_SET_NAME)

    keys = r.zrange(REDIS_SET_NAME, 0, -1)
    pipe = r.pipeline()
    for key in keys:
        pipe.hget(REDIS_HASH_NAME, key)

    values = pipe.execute()

    print 'keys[{}], values[{}]'.format(len(keys), len(values))

    #message += '<table border="1"><tr><th>Time</th><th>Watts</th></tr>\n'

    data_table = {'cols': [{'id': 'minute', 'label': 'Minute', 'type': 'string'},
                           {'id': 'watts', 'label': 'Watts', 'type': 'number'}],
                  'rows': [] }

    for i in range(min(len(keys), len(values))):
        data_table['rows'].append({'c': [{'v': str(seconds_to_dt(keys[i]))},
                                         {'v': int(values[i])}]})

    #for entry in entries_dict['entries']:
    #    message += '<tr><td>{}</td><td>{}</td></tr>\n'.format(entry['start'], entry['usage'])

    #message += '</table>\n'
    
    message = """
      <html><head><title>energymon 1.0</title>
      <script type="text/javascript" src="https://www.google.com/jsapi"></script>'
      <script type="text/javascript">

      // Load the Visualization API and the piechart package.
      google.load('visualization', '1.0', {'packages':['corechart']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the pie chart, passes in the data and
      // draws it.
      function drawChart() {
"""
    message += 'var data = new google.visualization.DataTable(' + json.dumps(data_table) + ', 0.6)\n'
    message += """
        // Create the data table.
        // var data = new google.visualization.DataTable();

        // Set chart options
        var options = {'title':'Power Usage',
                       'width':800,
                       'height':600};

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
"""

    message += '</script>\n'
    message += '<body>\n'
    message += 'energymon 1.0<br/>\n'
    message += 'Usage entries: {}\n'.format(count)
    message += '<div id="chart_div"></div>'
    message += '</body>\n'
    message += '</html>\n'

    return message

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

