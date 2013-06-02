from datetime import datetime, timedelta
import pytz

epoch = datetime.fromtimestamp(0, tzinfo=pytz.utc)

def seconds_to_dt(seconds):
    return (epoch + timedelta(seconds=seconds))

def dt_to_seconds(utc_dt):
    return ((utc_dt - epoch).total_seconds())


