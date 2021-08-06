from web3 import Web3
import json

from contract_utils import save_contract_data, deploy_contract, compile_contract, get_address, load_contract_data


def make_accounts(w3):
    accounts = w3.eth.accounts[:]
    acc_data = {
        'service': accounts.pop(0),
        'employer': accounts.pop(0)
    }
    for i, acc in enumerate(accounts):
        acc_data[f'client{i + 1}'] = acc
    with open('address_config.json', 'w') as f:
        json.dump(acc_data, f)


def start_app():
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    make_accounts(w3)
    w3.eth.default_account = get_address('service')

    contract_id, contract_interface = compile_contract()
    address = deploy_contract(w3, contract_interface)
    print(f'Deployed {contract_id} to: {address}\n')
    contract = w3.eth.contract(address=address, abi=contract_interface["abi"])

    save_contract_data(contract.address, contract.abi)

    return w3, contract


def load_app():
    contract_address, contract_abi = load_contract_data()
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    w3.eth.default_account = get_address('service')
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    return w3, contract


if __name__ == '__main__':
    w3, contract = start_app()
