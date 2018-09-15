import random
from config import *
from turing_bot import *
from bot_reply import *
from dal import *
import report

bot_reply = BotReply(CLEVERBOT_TOKEN)
turing_bot = TuringBot(BOT_TOKEN, bot_reply)

def pair_all(round_num, prob_bot=0.5):
    # Get unpaired tids
    tids = set(User.objects.distinct('tid'))
    tids -= set(Pair.objects(is_active=True).distinct('tid1'))
    tids -= set(Pair.objects(is_active=True).distinct('tid2'))
    tids = list(tids)
    random.shuffle(tids)

    tids1 = []  # Their turn
    tids2 = []  # Not their turn

    # Pair with bots
    bot_count = round(len(tids) * prob_bot)
    for _ in range(bot_count):
        tid = tids.pop()
        tids1.append(tid)
        Pair(round_num=round_num, tid1=tid, tid2=None, start_time=datetime.datetime.now()).save()

    # Pair between players
    while len(tids) >= 2:
        tid1, tid2 = tids.pop(), tids.pop()
        tids1.append(tid1)
        tids2.append(tid2)
        Pair(round_num=round_num, tid1=tid1, tid2=tid2, start_time=datetime.datetime.now()).save()

    # Pair leftover guy with bot
    if tids:
        tid = tids.pop()
        tids1.append(tid)
        Pair(round_num=round_num, tid1=tid, tid2=None, start_time=datetime.datetime.now()).save()

    msg = f'Round {round_num}: You are now connected with your partner! It is your turn to speak.'
    for tid in tids1:
        turing_bot.bot.sendMessage(chat_id=tid, text=turing_bot._format_bot(msg))

    msg = f'Round {round_num}: You are now connected with your partner! It is your partner\'s turn to speak.'
    for tid in tids2:
        turing_bot.bot.sendMessage(chat_id=tid, text=turing_bot._format_bot(msg))

def unpair_all():
    for pair in Pair.objects(is_active=True):
        unpair(pair)

def unpair(pair):
    if not pair.is_active:
        return
    pair.is_active = False
    pair.end_time = datetime.datetime.now()
    pair.save()
    for tid in (pair.tid1, pair.tid2):
        if tid is None:
            continue
        msg = f'Round {pair.round_num}: The round has ended and you are now disconnected. Remember to register your confidence!'
        turing_bot.bot.sendMessage(chat_id=tid, text=turing_bot._format_bot(msg))
