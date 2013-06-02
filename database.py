from mongoengine import *

from setings import MONGO_HOST, MONGO_DATABASE_NAME 

db = connect(name=MONGO_DATABASE_NAME, host=MONGO_HOST)

