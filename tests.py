import unittest
from web3 import Web3
import time

from contract_utils import load_contract_data, get_address

from service import start_service
from client import start_client
from main import start_app


class AllTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w3, cls.contract = start_app()
        cls.payload = {
            'from': get_address('employer'),
            'value': 1000000,
        }

        cls.active_threads = []

        _, _, active_threads = start_service()
        for name in active_threads:
            cls.active_threads.append(active_threads[name])

        _, _, active_threads, _, _, _ = start_client(client_name='1')
        for name in active_threads:
            cls.active_threads.append(active_threads[name])

        _, _, active_threads, _, _, _ = start_client(client_name='2')
        for name in active_threads:
            if name.endswith('JobThread'):
                active_threads[name].thread.need_bad = True
            cls.active_threads.append(active_threads[name])

    def test_add_jobs(self):
        self.contract.functions.create_job('https://api.github.com', 443, 50, 20, 1, 1, 1).transact(self.payload)
        time.sleep(5)
        self.contract.functions.create_job('https://yandex.ru', 443, 50, 20, 1, 1, 1).transact(self.payload)
        time.sleep(5)
        self.contract.functions.create_job('BAD', 443, 100, 20, 1, 1, 1).transact(self.payload)
        time.sleep(5)
        self.contract.functions.create_job('https://google.ru', 443, 100, 20, 1, 1, 1).transact(self.payload)
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        time.sleep(60)
        for searcher in cls.active_threads:
            searcher.stop_thread(wait=False)
        for searcher in cls.active_threads:
            searcher.stop_thread(wait=True)
        print('Balance:', cls.contract.functions.get_balance().call())
        # sys.stdout.close()
        # sys.stdout = sys.__stdout__


if __name__ == "__main__":
    unittest.main()