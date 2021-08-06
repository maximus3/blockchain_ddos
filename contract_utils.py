import json
from solcx import compile_files, set_solc_version, install_solc


def get_address(name):
    with open('address_config.json', 'r') as f:
        data = json.load(f)
    return data[name]


def compile_contract(contract_source_path='contracts/base.sol'):
    try:
        set_solc_version('0.5.17')
    except Exception:
        install_solc('0.5.17')
        set_solc_version('0.5.17')
    compiled_sol = compile_files([contract_source_path])
    contract_id, contract_interface = list(compiled_sol.items())[0]
    assert (contract_id.startswith(contract_source_path))  # TODO
    return contract_id, contract_interface


def deploy_contract(w3, contract_interface):
    tx_hash = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']).constructor().transact()

    address = w3.eth.get_transaction_receipt(tx_hash)['contractAddress']
    return address


def save_contract_data(contract_address, contract_abi, filename='contract_data.json'):
    data = {
        'address': contract_address,
        'abi': contract_abi,
    }
    with open(filename, 'w') as f:
        json.dump(data, f)


def load_contract_data(filename='contract_data.json'):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['address'], data['abi']
