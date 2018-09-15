import threading
import time

def run_async(f, *args, **kwargs):
    threading.Thread(target=f, args=args, kwargs=kwargs).start()

def run_async_after(wait_time, f, *args, **kwargs):
    def wrapped_f(*args, **kwargs):
        time.sleep(wait_time)
        return f(*args, **kwargs)
    threading.Thread(target=wrapped_f, args=args, kwargs=kwargs).start()
