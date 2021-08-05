from threading import Lock


class LockObj:
    def __init__(self, lock_obj):
        self.lock = Lock()
        self._obj = lock_obj

    def __enter__(self):
        self.lock.acquire()
        return self._obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
        if exc_val:
            raise
