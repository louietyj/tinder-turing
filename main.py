import random
from config import *
from turing_bot import *
from bot_reply import *
from dal import *

bot_reply = BotReply(CLEVERBOT_TOKEN)
turing_bot = TuringBot(BOT_TOKEN)

def pair(prob_bot=0.3):
    tids = [user['tid'] for user in db.users.find()]    # TODO: ...where 'active': False
    tids_copy = tids.copy()
    random.shuffle(tids)

    # Pair with bots
    bot_count = round(len(tids) * prob_bot)
    for _ in range(bot_count):
        db.pairs.insert_one({'tid1': tids.pop(), 'tid2': None, 'active': True})

    # Pair between players
    while len(tids) >= 2:
        tid1, tid2 = tids.pop(), tids.pop()
        tid1, tid2 = sorted((tid1, tid2))
        db.pairs.insert_one({'tid1': tid1, 'tid2': tid2, 'active': True})

    # Pair leftover guy with bot
    if tids:
        db.pairs.insert_one({'tid1': tids.pop(), 'tid2': None, 'active': True})

    msg = 'You are now connected with your partner!'
    for tid in tids_copy:
        turing_bot.bot.sendMessage(chat_id=tid, text=turing_bot._format_bot(msg))
