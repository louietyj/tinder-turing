import threading

def run_async(f, *args, **kwargs):
	threading.Thread(target=f, args=args, kwargs=kwargs).start()
