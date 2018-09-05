"""
This thingy is Mr. DAL, everyone's favorite Data Access Layer!
"""
import datetime
from mongoengine import *


class User(Document):
    name = StringField(required=True)
    tid = StringField(required=True, unique=True)


class Pair(Document):
    is_active = BooleanField(default=True)
    tid1 = StringField()
    tid2 = StringField()
    confidence1 = IntField(min_value=0, max_value=100)
    confidence2 = IntField(min_value=0, max_value=100)
    round_num = IntField(required=True)
    start_time = DateTimeField(default=datetime.datetime.now())
    end_time = DateTimeField()


class Message(Document):
    pair = ReferenceField(Pair, required=True)
    sender = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())


def get_user_by_tid(tid):
    return User.objects(tid=str(tid))[0]

# establish connection to mongodb instance
connect('tinder_turing', host='localhost', port=27017)
