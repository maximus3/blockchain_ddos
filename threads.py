import random
from threading import Thread, Lock
import time

from merkle_tree import MerkleTree
from make_ddos import make_ddos


class BaseThread(Thread):
    def __init__(self):
        super().__init__()
        self.isRunning = True
        self.lock = Lock()

        self.logger_name = 'BaseThread:Log'

    def stop(self):
        with self.lock:
            self.isRunning = False


class BaseWrapper:
    def __init__(self, ThreadClass, cv=None, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.thread = None
        self.ThreadClass = ThreadClass
        self.cv = cv
        if self.cv is not None:
            self.args = (self.cv,) + self.args

        self.logger_name = 'BaseWrapper:Log'

    def start_thread(self):
        if self.thread is not None and self.thread.is_alive():
            print(self.logger_name, 'Current thread is working, stop it before run new one')
            return
        self.thread = self.ThreadClass(*self.args, **self.kwargs)
        self.thread.start()

    def stop_thread(self, wait=False):
        if self.thread is None:
            print(self.logger_name, 'No active thread found')
            return
        self.thread.stop()
        if self.cv is not None:
            with self.cv:
                self.cv.notify_all()
        if wait:
            print(self.logger_name, 'Waiting thread join...')
            self.thread.join()


class JobThread(BaseThread):
    def __init__(self, cv, jobs_to_do, jobs_locked, w3, contract, name=''):
        super().__init__()
        self.cv = cv
        self.jobs_to_do = jobs_to_do
        self.jobs_locked = jobs_locked
        self.w3 = w3
        self.contract = contract
        self.need_bad = False  # For tests
        self.name = name

        self.logger_name = 'JobThread:' + name + ':LOG'

    def run(self):
        print(self.logger_name, f'Search for new jobs started')
        with self.cv:
            while True:
                if len(self.jobs_to_do) == 0:
                    self.cv.wait()
                with self.lock:
                    if not self.isRunning:
                        break
                if len(self.jobs_to_do) == 0:
                    continue
                job_id = self.jobs_to_do.pop(0)
                with self.jobs_locked as jobs:
                    job = jobs.get(job_id)
                if job is None:
                    print(self.logger_name, f'Job {job_id} not found')
                    continue

                suc_count, responses = make_ddos(job)

                merkel_tree = MerkleTree()
                merkel_root = merkel_tree.make_tree(responses)

                if self.need_bad:
                    merkel_root = list(merkel_root)
                    random.shuffle(merkel_root)
                    merkel_root = ''.join(merkel_root)

                print(self.logger_name, f'Job {job_id} {job.host} done! Success: {suc_count}, MTRoot: {merkel_root}')

                report = {
                    '_job_id': job_id,
                    '_success': suc_count,
                    '_MTRoot': merkel_root,
                    '_proofs': merkel_tree.get_proofs(),
                }

                self.contract.functions.check_job(**report).transact()

                # TODO: start new thread waiting job approve

        print(self.logger_name, 'Search for new jobs stopped')


class EventSearcherThread(BaseThread):
    def __init__(self, event_filter, event_handler, name='', handler_args=(), poll_interval=10):
        super().__init__()
        self.event_filter = event_filter
        self.poll_interval = poll_interval
        self.event_handler = event_handler
        self.name = name
        self.handler_args = handler_args

        self.logger_name = 'EventSearcherThread:' + name + ':LOG'

    def run(self):
        print(self.logger_name, f'Search for new events {self.name} started')
        while True:
            with self.lock:
                if not self.isRunning:
                    break
            for event in self.event_filter.get_new_entries():
                self.event_handler(self.name, event, *self.handler_args)
            time.sleep(self.poll_interval)
        print(self.logger_name, f'Search for new events {self.name} stopped')


class JobThreadWrapper(BaseWrapper):
    def __init__(self, cv, *args, **kwargs):
        super().__init__(JobThread, cv, *args, **kwargs)
        self.logger_name = 'JobThreadWrapper:Log'


class EventSearcherWrapper(BaseWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(EventSearcherThread, None, *args, **kwargs)
        self.logger_name = 'EventSearcherWrapper:Log'


