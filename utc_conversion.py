from datetime import datetime, timedelta
import pytz

epoch = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)

def local_str_from_naive_utc_dt(naive_utc_dt, local_timezone):
    local_tz = pytz.timezone(local_timezone)
    local_time = pytz.utc.localize(naive_utc_dt).astimezone(local_tz)
    return local_time.strftime("%a %b %d %H:%M.%S %Z")

def seconds_to_dt(seconds):
    return (epoch + timedelta(seconds=seconds))

def dt_to_seconds(utc_dt):
    if not utc_dt.tzinfo:
        utc_dt = pytz.utc.localize(utc_dt)
    return int(round(((utc_dt - epoch).total_seconds())))
