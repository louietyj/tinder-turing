import functools
import random
import telegram
import telegram.error
import time

RETRY_FUNCS = {'sendMessage', 'send_message'}
TIMEOUT_FUNCS = {'sendMessage', 'send_message'}

def try_repeat_wrapper(func, retries=100):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except telegram.error.TimedOut as e:
                error = e
                print(error)
                time.sleep(min(32, 2 ** i + random.random()))   # Exponential backoff
        raise error
    return wrapped_func

def timeout_wrapper(func, timeout=20):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = timeout
        return func(*args, **kwargs)
    return wrapped_func

class BotWrapper:
    def __init__(self, bot):
        self._bot = bot

    def __getattr__(self, attr):
        _attr = getattr(self._bot, attr)
        if attr in RETRY_FUNCS:
            _attr = try_repeat_wrapper(_attr)
        if attr in TIMEOUT_FUNCS:
            _attr = timeout_wrapper(_attr)
        return _attr
