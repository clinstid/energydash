from mongoengine import *
from datetime import datetime
import pytz

class EnvirReading(Document):
    reading_timestamp = DateTimeField(required=True,
                                      default=datetime.now(tz=pytz.utc))
    receiver_days_since_birth = IntField()
    receiver_time = StringField()
    ch1_watts = IntField()
    ch2_watts = IntField()
    ch3_watts = IntField()
    total_watts = IntField(required=True)
    temp_f = FloatField()
