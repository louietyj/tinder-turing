import eliza
import random
import time
from cleverwrap import CleverWrap
from threading import RLock

class BotReply():
    def __init__(self, cleverbot_token):
        self.cleverbot_token = cleverbot_token
        self.cleverbots = {}
        self.cleverbots_lock = RLock()

    def _init_cleverbot(self, tid):
        with self.cleverbots_lock:
            if tid in self.cleverbots:
                return self.cleverbots[tid]
            cleverbot = CleverWrap(self.cleverbot_token)
            self.cleverbots[tid] = cleverbot
            return cleverbot

    @staticmethod
    def _reply_time(message, delay=2, cpm=500, noise=3):
        typing_time = 60 / cpm * len(message)
        noise_time = random.random() * noise
        return delay + typing_time + noise_time

    def _compute_reply(self, tid, message):
        cleverbot = self._init_cleverbot(tid)
        try:
            return cleverbot.say(message)
        except:
            return eliza.analyze(message)

    def get_reply(self, tid, message):
        received = time.time()
        reply = self._compute_reply(tid, message)
        reply_time = self._reply_time(reply)
        wait_time = received + reply_time - time.time()
        print(reply)
        print(f'Expected reply time: {reply_time}, wait time: {wait_time}')
        if wait_time > 0:
            time.sleep(wait_time)
        return reply
