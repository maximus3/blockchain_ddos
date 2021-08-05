from web3 import Web3

from contract_utils import load_contract_data, get_address
from threads import EventSearcherWrapper
from job import JobInfo, JobDoneInfo


def check_job_done(job, job_done):
    # TODO: check job done
    if job_done._success > job.max_queries_per_worker:
        return False
    return True


def handler_on_job_done(event, contract):
    job_done = JobDoneInfo(event.args)
    job = JobInfo(contract.functions.get_job_info(job_done._job_id).call())
    job_done._value = job.worker_reward
    print(f'SERVICE_LOG', f'New job done {job_done}')

    if check_job_done(job, job_done):
        contract.functions.job_result_ok(**job_done.save_repr()).transact()
        print(f'SERVICE_LOG', f'Job done {job_done} OK')
    else:
        contract.functions.job_result_error(job_done._worker).transact()
        print(f'SERVICE_LOG', f'Job done {job_done} ERROR')


def check_job(job):
    # TODO: check job
    if not job.host.startswith('https://'):
        return False
    return True


def handler_check_job(event, contract):
    job = JobInfo(event_args=event.args)

    if check_job(job):
        contract.functions.approve_job(job.host, job.port, job.value, job.reward_per_query, job.needed_queries,
                                       job.max_queries_per_worker, job.test_start_time, job.test_end_time,
                                       job.reg_end_time, job.owner).transact()
        print(f'SERVICE_LOG: Job {job.host}:{job.port} from {job.owner} approved')
    else:
        contract.functions.cancel_job(job.owner, job.value).transact()
        print(f'SERVICE_LOG: Job {job.host}:{job.port} from {job.owner} cancelled')


def start_service():
    contract_address, contract_abi = load_contract_data()
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    w3.eth.default_account = get_address('service')
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    active_threads = {}

    name = 'JobDone'
    event_filter = contract.events.JobDone.createFilter(fromBlock='latest')
    active_threads[name] = EventSearcherWrapper(event_filter, handler_on_job_done, name, handler_args=(contract,))

    name = 'JobCheck'
    event_filter = contract.events.JobCheck.createFilter(fromBlock='latest')
    active_threads[name] = EventSearcherWrapper(event_filter, handler_check_job, name, handler_args=(contract,))

    for name in active_threads:
        active_threads[name].start_thread()

    return w3, contract, active_threads


if __name__ == '__main__':
    w3, contract, active_threads = start_service()

    while True:
        command = input()
        if command == 'stop':
            for name in active_threads:
                active_threads[name].stop_thread(wait=False)
            for name in active_threads:
                active_threads[name].stop_thread(wait=True)
            break
        else:
            print('Command not found')