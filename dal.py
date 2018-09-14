"""
This thingy is Mr. DAL, everyone's favorite Data Access Layer!
"""
import datetime
from mongoengine import *

class PrintableDocument(Document):
    meta = {'abstract': True}

    def __repr__(self):
        return f'<{type(self).__name__} {self.to_mongo().to_dict()}>'

class User(PrintableDocument):
    name = StringField(required=True)
    tid = StringField(required=True, unique=True)


class Pair(PrintableDocument):
    is_active = BooleanField(default=True)
    tid1 = StringField()
    tid2 = StringField()
    confidence1 = IntField(min_value=0, max_value=100)
    confidence2 = IntField(min_value=0, max_value=100)
    round_num = IntField(required=True)
    start_time = DateTimeField(default=datetime.datetime.now())
    end_time = DateTimeField()
    turn = IntField(min_value=1, max_value=2, default=1)


class Message(PrintableDocument):
    pair = ReferenceField(Pair, required=True)
    sender = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(required=True)


def get_user_by_tid(tid):
    try:
        return User.objects(tid=str(tid))[0]
    except IndexError as e:
        return None


def get_name_by_tid(tid):
    user = get_user_by_tid(tid)
    if user is None:
        return 'John Doe'
    return user['name']


def get_pairs_containing_tid(tid, is_active=None):
    if is_active is None:
        return Pair.objects(Q(tid1=str(tid)) | Q(tid2=str(tid)))
    return Pair.objects(Q(is_active=is_active) & (Q(tid1=str(tid)) | Q(tid2=str(tid))))


def get_pair_by_tid(tid, is_active=True, round_num=None):
    if round_num is None:
        return Pair.objects(Q(is_active=is_active) & (Q(tid1=str(tid)) | Q(tid2=str(tid))))
    return Pair.objects(Q(round_num=int(round_num)) & (Q(tid1=str(tid)) | Q(tid2=str(tid))))

# establish connection to mongodb instance
db = connect('tinder_turing', host='localhost', port=27017)
