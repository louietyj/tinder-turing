import eliza
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

    def get_reply(self, tid, message):
        cleverbot = self._init_cleverbot(tid)
        try:
            return cleverbot.say(message)
        except:
            return eliza.analyze(message)
