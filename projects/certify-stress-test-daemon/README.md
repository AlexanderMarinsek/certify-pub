# Certify Stress Test Daemon

The Certify Stress Test Daemon periodically checks whether a new block has been proposed by the validator. It runs on the node under test (NUT) and relies on the [Certify StressTesting smart contract](../certify-contracts/docs/stress_testing_specs.md), where it regularly calls the `record` function in a transaction. This allows the validator to conduct self-reporting, including an on-chain verification.



## Usage

### Short Foreword on Wallets and Payments

A validator conducting a stress test must connect a wallet to the daemon in order to cover running costs. We strongly recommend using a hot wallet, i.e., a throwaway wallet with minimal funds, for security reasons.

The funds are required in order to cover the fees of successful transactions following a `record` function call. This transaction is successful if a new block is recorded, therefore charging the validator a transaction fee of 0.001 ALGO. This fee is not charged in case of a failed transaction, for example, if the stress test is not live (active).


### Overal Procedure Overview

The below points outline the validator flow in the current implementation. 
After cloning this repository, the validator:
1. Opens the Certify app ([front-end](../front-end)) and creates a [StressTesting smart contract](../certify-contracts/docs/stress_testing_specs.md).
2. Adds the (hot) wallet mnemonic and the ID of the created StressTesting smart contract to the daemon's configuration, before running the daemon.
3. Generates a participation key for the delegator, for example, using [the goal CLI command](https://developer.algorand.org/docs/run-a-node/participate/generate_keys/). The delegator's address, indicated during contract creation, must be used for generating the participation key.
4. Adds the participation key parameters to the StressTesting smart contract using the Certify app and starts the contract.


### Environment and Daemon Setup

The Certify Stress Test Daemon can be run using the project's virtual environment or a custom Python envrionment can be used. In the latter case, please install the dependencies listed in [requirements.txt](requirements.txt).

The daemon is configured via the [daemon.config](daemon.config) file. The validator must enter the mnemonic of the wallet that will be covering the transaction costs during the stress test `validator_manager_mnemonic = <mnemonic>` and the ID of the created StressTesting smart contract `stress_test_app_id = <ID>`.


### Running

The Certify Stress Test Daemon is run from the base directory where this readme resides using `python run_daemon.py`, assuming `python` invokes the correctly-configured Python envrionment.

The Daemon will automatically output a log to the file `daemon.log`. An alternative configuration and log file can be provided through arguments `config_path` and `log_path`, respectively. This would alter the run command accordingly `python run_daemon.py --config_path <path/to/the.config> --log_path <path/to/the.log>`


## Testing

A manual test is provided in [test/daemon_test.py](./test/daemon_test.py). The test programmatically executes the steps mentioned in [the above overview section](#overal-procedure-overview).

The generated config and log files are stored in [test/tmp/](./test/tmp/), while [test/daemon_test.py](./test/daemon_test.py) outputs the state of the StressTesting smart contract to STDOUT. This includes the last observed round, start/end roung, etc.

