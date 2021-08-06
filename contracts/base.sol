pragma solidity >=0.5.0 <0.6.0;

import "./ownable.sol";

contract BaseContract is Ownable {
    struct JobInfo {
        /*
        Info about new job
        */
        string host;
        uint16 port;

        uint256 total_reward;
        uint64 reward_per_query;

        uint64 needed_queries;
        uint64 max_queries_per_worker;
        uint64 cnt_queries;

        uint64 test_start_time;
        uint64 test_end_time;
        uint64 reg_end_time;  // TODO: use it

        uint64 cnt_registered;

        address owner;
    }

    struct JobDoneInfo {
        /*
        Info about job done
        */
        uint job_id;
        address worker;
        uint64 success;
        string MTRoot;
        string proofs;
    }

    JobInfo[] private _jobs;
    JobDoneInfo[] public jobs_done;
    uint64 private delta = 100000;

    event JobCreated(uint id);
    event JobCheck(string host, uint16 port, uint value, uint64 needed_queries, uint64 max_queries_per_worker,
                   uint64 test_start_time, uint64 test_end_time, uint64 reg_end_time, address job_owner); // TODO: Is string in event ok?
    event JobDone(uint job_id, address worker, uint64 success, string MTRoot, string proof);
    event WorkChecked(bool approved, address worker);

    function create_job (string calldata _host,
                         uint16 _port,
                         uint64 _needed_queries,
                         uint64 _max_queries_per_worker,
                         uint64 _test_start_time,
                         uint64 _test_end_time,
                         uint64 _reg_end_time) external payable {
        require(msg.value > _needed_queries + delta); // TODO: delta is commission
        emit JobCheck(_host, _port, msg.value, _needed_queries, _max_queries_per_worker,
                      _test_start_time, _test_end_time, _reg_end_time, msg.sender);
    }

    function get_job_info(uint _id) external view returns(uint, string memory, uint16, uint64, uint64,
                                                     uint64, uint64, uint64, address) {
        JobInfo storage job = _jobs[_id];
        return (_id, job.host, job.port, job.reward_per_query, job.max_queries_per_worker,
                job.test_start_time, job.test_end_time, job.reg_end_time, job.owner);
    }

    function approve_job (string calldata _host,
                          uint16 _port,
                          uint _total_reward,
                          uint64 _reward_per_query,
                          uint64 _needed_queries,
                          uint64 _max_queries_per_worker,
                          uint64 _test_start_time,
                          uint64 _test_end_time,
                          uint64 _reg_end_time,
                          address _job_owner) external onlyOwner {
        uint _id = _jobs.push(JobInfo(_host,
                                      _port,
                                      _total_reward,
                                      _reward_per_query,
                                      _needed_queries,
                                      _max_queries_per_worker,
                                      0, // cnt_queries
                                      _test_start_time,
                                      _test_end_time,
                                      _reg_end_time,
                                      0, // cnt_registered
                                      _job_owner // owner
        )) - 1;

        emit JobCreated(_id);
    }

    function cancel_job(address payable _job_owner, uint _value) external onlyOwner {
        _job_owner.transfer(_value);
    }

    function get_balance() external view onlyOwner returns(uint) {
        return address(this).balance;
    }

    function check_job(uint _job_id, uint64 _success, string calldata _MTRoot, string calldata _proofs) external {
        emit JobDone(_job_id, msg.sender, _success, _MTRoot, _proofs);
    }

    function job_result_ok(uint _value, uint _job_id, address payable _worker, uint64 _success, string calldata _MTRoot, string calldata _proofs) external onlyOwner payable {
        jobs_done.push(JobDoneInfo(
            _job_id,
            address(_worker),
            _success,
            _MTRoot,
            _proofs
        ));
        _worker.transfer(_value);
        emit WorkChecked(true, address(_worker)); // TODO: who?
    }

    function job_result_error(address _worker) external onlyOwner {
        emit WorkChecked(false, address(_worker)); // TODO: reason?
    }

    // TODO: send money back if deposit not empty
}