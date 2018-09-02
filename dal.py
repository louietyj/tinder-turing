"""
This thingy is Mr. DAL, everyone's favorite Data Access Layer!
"""
import datetime
import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client.tinder_turing

# prevent duplicate documents from being inserted
# all users must have unique Telegram IDs
db.users.create_index([('tid', 1)], unique=True)

# this enforces all pairs to be unique
# disabled, because bot IDs will be repeated
# db.pairs.create_index([('pair', 1)], unique=True)


def register_user(tid, name):
    """
    Registers a user into the database.
    :param tid: Telegram ID
    :param name: Name of user
    :return: True if registration succeeded; False otherwise
    """
    document = {'name': name, 'tid': tid}
    try:
        result = db.users.insert_one(document)
    except (pymongo.errors.DuplicateKeyError, pymongo.errors.WriteError):
        return False
    return True


def get_user_name(tid):
    """
    Get a user's registered name by their Telegram ID
    :param tid:
    :return: name if found; None otherwise
    """
    result = db.users.find_one({'tid': tid}, {'name': True})
    if result is not None:
        return result['name']
    return None


def register_pair(tid1, tid2=None):
    """
    Registers a pair into the database. Every pair must be unique.

    The pair list is always sorted in ascending order.

    :param tid1: first Telegram ID
    :param tid2: second Telegram ID
    :return: True if registration succeeded; False otherwise
    """
    document = {'pair': sorted([tid1, tid2])}
    try:
        result = db.pairs.insert_one(document)
    except pymongo.errors.WriteError:
        return False
    return True


def get_pair(tid):
    """
    Retrieves the pair that a given Telegram ID is assigned to.
    :param tid: target Telegram ID
    :return: list of pairs if any; None if tid does not exist in any pair
    """
    pattern = {'pair': tid}

    cursor = db.pairs.find(pattern, {'pair': True})
    if cursor is None:
        return None

    pairs = []
    for result in cursor:
        pairs.append(result['pair'])
    return pairs


def save_message(pair, sender, message, timestamp=datetime.datetime.utcnow()):
    """
    Saves a message to the database.
    :param pair:
    :param sender:
    :param message:
    :param timestamp:
    :return: True if save succeeded; False otherwise
    """
    document = {'pair': pair, 'sender': sender, 'message': message, 'timestamp': timestamp}
    try:
        result = db.messages.insert_one(document)
    except pymongo.errors.WriteError:
        return False
    return True
