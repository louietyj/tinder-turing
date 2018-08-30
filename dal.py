"""
This thingy is Mr. DAL, everyone's favorite Data Access Layer!
"""
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.tinder_turing


def register_user(tid):
    return


def register_pair(tid1, tid2=None):
    return


def save_message(pair, sender, message, timestamp):
    return
