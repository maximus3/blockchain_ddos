from web3 import Web3
from threading import Condition, Thread

from contract_utils import load_contract_data, get_address
from threads import EventSearcherWrapper, JobThreadWrapper
from job import JobInfo
from utils import LockObj


def print_job_info(job_id, jobs_locked):
    with jobs_locked as jobs:
        job = jobs.get(job_id)
    if job is None:
        print(f'CLIENT_LOG: Job {job_id} not found')
        return
    print(f'CLIENT_LOG: {job.host}:{job.port} from {job.owner}')
    print(f'CLIENT_LOG: {job.reward_per_query} wei for 1 query')
    print(f'CLIENT_LOG: {job.max_queries_per_worker} queries')
    print(f'CLIENT_LOG: From {job.test_start_time} to {job.test_end_time}')
    print(f'CLIENT_LOG: Registration before {job.reg_end_time}')


def handler_on_new_job(name, event, contract, do_job_cv, jobs_locked, jobs_to_do, SEND_TO_WORK):
    job_id = event.args.id
    job = JobInfo(contract.functions.get_job_info(job_id).call())
    with jobs_locked as jobs:
        jobs[job_id] = job
    print(name, f'Found new job {job.id}')
    if SEND_TO_WORK:
        with do_job_cv:
            jobs_to_do.append(job_id)
            do_job_cv.notify()


def start_client(send_to_work=True, client_name=''):
    client_name = 'CLIENT' + client_name
    contract_address, contract_abi = load_contract_data()
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    w3.eth.default_account = get_address(client_name.lower())
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    jobs_locked = LockObj(dict())
    do_job_cv = Condition()
    jobs_to_do = []

    active_threads = {}

    name = client_name + ':JobCreated'
    event_filter = contract.events.JobCreated.createFilter(fromBlock='latest')
    searcher = EventSearcherWrapper(event_filter, handler_on_new_job, name,
                                    handler_args=(contract, do_job_cv, jobs_locked, jobs_to_do, send_to_work))
    active_threads[name] = searcher

    name = client_name + ':JobThread'
    active_threads[name] = JobThreadWrapper(do_job_cv, jobs_to_do, jobs_locked, w3, contract, client_name)

    for name in active_threads:
        active_threads[name].start_thread()

    return w3, contract, active_threads, do_job_cv, jobs_locked, jobs_to_do


if __name__ == '__main__':
    w3, contract, active_threads, do_job_cv, jobs_locked, jobs_to_do = start_client()

    while True:
        command = input()
        if command == 'stop':
            for name in active_threads:
                active_threads[name].stop_thread(wait=False)
            for name in active_threads:
                active_threads[name].stop_thread(wait=True)
            break
        elif command.startswith('get') and len(command.split()) == 2:
            job_id = command.split()[-1]
            if not job_id.isdigit():
                print(f'{job_id} is not a digit')
                continue
            print_job_info(int(job_id), jobs_locked)
        elif command.startswith('make') and len(command.split()) == 2:
            job_id = command.split()[-1]
            if not job_id.isdigit():
                print(f'{job_id} is not a digit')
                continue
            with do_job_cv:
                jobs_to_do.append(int(job_id))
                do_job_cv.notify()
        else:
            print('Command not found')