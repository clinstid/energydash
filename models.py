from sqlalchemy import Column, Integer, DateTime
from database import Base

class Usage(Base):
    __tablename__ = 'usage'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True))
    usage_in_watts = Column(Integer)

    def __init__(self, timestamp, usage_in_watts):
        self.timestamp = timestamp
        self.usage_in_watts = usage_in_watts

    def __repr__(self):
        return '<Usage({timestamp}, {usage_in_watts})>'.format(timestamp=self.timestamp,
                                                               usage_in_watts=self.usage_in_watts)



