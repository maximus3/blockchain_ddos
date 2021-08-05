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
        # contract_address, contract_abi = load_contract_data()
        # w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
        # cls.contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        cls.payload = {
            'from': get_address('employer'),
            'value': 1000000,
        }

        cls.active_threads = []

        _, _, active_threads = start_service()
        for name in active_threads:
            cls.active_threads.append(active_threads[name])

        _, _, active_threads, _, _, _ = start_client()
        for name in active_threads:
            cls.active_threads.append(active_threads[name])

    def test_good(self):
        self.contract.functions.create_job('https://', 80, 1, 1, 1, 1, 1).transact(self.payload)

    def test_good_second(self):
        self.contract.functions.create_job('https://must_be_error', 80, 1, 1, 1, 1, 1).transact(self.payload)

    def test_bad(self):
        self.contract.functions.create_job('BAD', 80, 1, 1, 1, 1, 1).transact(self.payload)

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