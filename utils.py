import threading
import time

def run_async(f, *args, **kwargs):
	threading.Thread(target=f, args=args, kwargs=kwargs).start()

def run_async_after(wait_time, f, *args, **kwargs):
	time.sleep(wait_time)
	threading.Thread(target=f, args=args, kwargs=kwargs).start()
