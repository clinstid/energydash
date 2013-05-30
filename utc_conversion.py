from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

def seconds_to_dt(seconds):
    return (datetime(year=1970, month=1, day=1, tzinfo=pytz.utc) + 
            relativedelta(seconds=+int(seconds)))

def dt_to_seconds(utc_dt):
    return ((utc_dt - 
             datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)).total_seconds())


