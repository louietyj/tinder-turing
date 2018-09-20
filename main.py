import math
import random
import report
from config import *
from turing_bot import *
from bot_reply import *
from dal import *

INITIAL_HELLO = 'Hello!'
INITIAL_BOT_HELLOS = ['Hello!', 'Hi.', 'Hey there.', 'Good afternoon.', 'Hello?',
                      'Greetings!', 'Salutations!', 'Howdy!']

bot_reply = BotReply(CLEVERBOT_TOKEN)
turing_bot = TuringBot(BOT_TOKEN, bot_reply)

def pair_all(round_num, prob_bot=0.5):
    # Make sure there is no inactive pair with this round number
    if Pair.objects(round_num=round_num, is_active=False).first():
        while True:
            cmd = input('[Warn] There is an inactive pair with this round number. Continue? (y/n) ')
            if cmd.lower() == 'y':
                break
            if cmd.lower() == 'n':
                return

    # Get unpaired tids
    tids = set(User.objects.distinct('tid'))
    tids -= set(Pair.objects(is_active=True).distinct('tid1'))
    tids -= set(Pair.objects(is_active=True).distinct('tid2'))
    tids = list(tids)
    random.shuffle(tids)

    # Pair between players
    human_count = math.ceil(len(tids) * (1 - prob_bot))
    if human_count % 2 == 1:
        human_count = human_count + 1 if human_count < len(tids) else human_count - 1
    for _ in range(human_count // 2):
        init_pair(round_num, tids.pop(), tids.pop())

    # Pair with bots
    while tids:
        init_pair(round_num, tids.pop(), None)

def init_pair(round_num, tid1, tid2):
    msg1 = (
        f'Round {round_num}: You are now connected with your partner! It is your turn to speak, '
         'and you must say "Hello!", so we have already done that for you.'
    )
    msg2 = (
        f'Round {round_num}: You are now connected with your partner! It is your partner\'s turn '
         'to speak, and he must say "Hello!"'
    )
    turn = random.randint(1, 2)
    start_tid, other_tid = (tid1, tid2) if turn == 2 else (tid2, tid1)
    pair = Pair(round_num=round_num, tid1=tid1, tid2=tid2, turn=turn).save()
    if start_tid:
        # send the "it's ur turn" message to the starter (if it's a human)
        run_async(turing_bot.bot.sendMessage, chat_id=start_tid, text=turing_bot._format_bot(msg1))

    sender_tid = None if start_tid is None else str(start_tid)
    if other_tid:
        # receiving end is human
        run_async(turing_bot.bot.sendMessage, chat_id=other_tid, text=turing_bot._format_bot(msg2))
        run_async_after(1, turing_bot.bot.sendMessage, chat_id=other_tid, text=INITIAL_HELLO)
    else:
        # receiving end is a bot
        run_async_after(1, turing_bot.await_bot_reply, pair, start_tid, random.choice(INITIAL_BOT_HELLOS))
    Message(pair=pair, sender=sender_tid, message=INITIAL_HELLO).save()  # log initial hello message

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
        run_async(turing_bot.bot.sendMessage, chat_id=tid, text=turing_bot._format_bot(msg))
