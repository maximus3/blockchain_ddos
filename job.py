class JobDoneInfo:
    def __init__(self, event_args):
        self._job_id = event_args.job_id
        self._worker = event_args.worker
        self._success = event_args.success
        self._MTRoot = event_args.MTRoot
        self._proofs = event_args.proof

    def save_repr(self):
        return {
            '_value': self._value,
            '_job_id': self._job_id,
            '_worker': self._worker,
            '_success': self._success,
            '_MTRoot': self._MTRoot,
            '_proofs': self._proofs
        }

    def __str__(self):
        return f'job_id: {self._job_id}, worker: {self._worker}'


class JobInfo:
    def __init__(self, data=None, event_args=None):
        if data:
            self.id = data[0]
            self.host = data[1]
            self.port = data[2]
            self.reward_per_query = data[3]
            self.max_queries_per_worker = data[4]
            self.test_start_time = data[5]
            self.test_end_time = data[6]
            self.reg_end_time = data[7]
            self.owner = data[8]
        elif event_args:
            self.id = None
            self.host = event_args.host
            self.port = event_args.port

            self.value = event_args.value
            self.needed_queries = event_args.needed_queries

            self.reward_per_query = int(self.value / self.needed_queries)
            self.max_queries_per_worker = event_args.max_queries_per_worker
            self.test_start_time = event_args.test_start_time
            self.test_end_time = event_args.test_end_time
            self.reg_end_time = event_args.reg_end_time
            self.owner = event_args.job_owner
        else:
            raise RuntimeError('One of argument data or event_args must be not None')

        self.worker_reward = int(self.reward_per_query * self.max_queries_per_worker)
