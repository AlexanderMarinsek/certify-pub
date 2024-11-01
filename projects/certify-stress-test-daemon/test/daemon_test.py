"""Script for testing the daemon. 

Creates validator hot wallet account and stress test smart contract.
A config file is created and populated with the above, before running the daemon.
The stress test is started and the chain is progressed by one block, allowing the daemon to record it.
Running on localnet will make the daemon itself progress the chain each time it records a new block.
There is no need to additionally move the chain forwards.

Presumptions:
    - The certboard is deployed through the CLI
    - The above deployment is done according to the addresses in `ActionInputs`
"""
import sys
import time
import logging
import threading
from pathlib import Path

from algosdk import mnemonic
from ConfigCreator import ConfigCreator
from algokit_utils.beta.algorand_client import AlgorandClient

from ActionInputs import ActionInputs
# from LocalnetRoundProgressor import LocalnetRoundProgressor
from utils_misc import create_and_fund_account, wait_for_rounds
from utils_setup import create_stress_test, start_stress_test

sys.path.append(str(Path(*Path(__file__).parent.parts[:-1])))
from src.StressTestDaemon import StressTestDaemon
from src import daemon
from src.daemon_utils import init_default_stdout_logger


def launch_daemon_thread( # In no way connected to certify daemon
    **kwargs
) -> None:
    """Launch a daemon thread, which terminates when the program terminates (or pauses on debug).
    """
    thread = threading.Thread( **kwargs )
    thread.daemon = True  # Make it a daemon thread
    thread.start()


def log_stress_test_state(
        client: StressTestDaemon, 
        logger: logging.Logger, 
        message: str=''
    ) -> None:
    """Log the stress test contract parameters.

    Args:
        client (StressTestDaemon): .
        logger (logging.Logger): .
        message (str, optional): Initial message, before the parameters. Defaults to ''.
    """
    gs = client.get_global_state()
    keys = (
        'cnt_produced_blocks',
        'cnt_total_stake_sum',
        'duration',
        'duration_max',
        'last_block',
        'owner_address',
        'round_created',
        'round_end',
        'round_end_max',
        'round_ended',
        'round_start',
        'stake',
        'state',
        'total_stake_sum',
        'user_address'
    )
    txt = f'{message}'
    for k in keys:
        # txt += f'\n{k}: {gs[k]}'
        txt += f'\n {k}: {getattr(gs, k, "Attribute not found")}'
    logger.log(
        logging.DEBUG,
        txt
    )


### Init stdout logger
test_logger = init_default_stdout_logger( 'test_logger', 'DEBUG')


### Config block round, daemon loop, and checking period duration
round_loop_period_s = 1


### Prepare paths
daemon_config_path = Path(Path(__file__).parent, 'tmp', 'daemon.config')
daemon_log_path = Path(Path(__file__).parent, 'tmp', 'daemon.log')
lrp_log_path = Path(Path(__file__).parent, 'tmp', 'lrp.log')
test_log_path = Path(Path(__file__).parent, 'tmp', 'test.log')


### Initialize localnet client and (funded) signer
algorand_client = AlgorandClient.default_local_net()
algorand_client.set_suggested_params_timeout(0)
# Anyone can call the record function (in the daemon) - can use entirely account
creator = create_and_fund_account(algorand_client)


### Initialize localnet round progressor
# lrp = LocalnetRoundProgressor( round_time_s=round_loop_period_s )
# lrp.set_logger( init_default_file_logger('lrp_logger', lrp_log_path, 'DEBUG') )
# launch_daemon_thread( target=lrp.run )


### Create stress test
stress_testing_client = create_stress_test(algorand_client, creator, ActionInputs)
app_id = stress_testing_client.app_id
log_stress_test_state(stress_testing_client, test_logger, 'Created stress test')


### Generate daemon config
cc = ConfigCreator()
cc.create_config(
    validator_manager_mnemonic=mnemonic.from_private_key(creator.signer.private_key),
    stress_test_app_id=app_id,
    loop_period_s=round_loop_period_s,
)
cc.save_to_file(daemon_config_path)


### Run daemon
launch_daemon_thread(target=daemon.run, args=(daemon_config_path, daemon_log_path))


### Start stress test
stress_testing_client = start_stress_test(algorand_client, creator, ActionInputs, stress_testing_client)
test_logger.log(
    logging.DEBUG, 
    f'Block number on start: {stress_testing_client.get_global_state().last_block}'
)
log_stress_test_state(stress_testing_client, test_logger, 'Started stress test')


### Move chain forwards
# Progress by one round, so that the daemon starts recording new blocks.
# New blocks will automatically get created due to the successful record transactions.
wait_for_rounds(
    algorand_client,
    1,
    creator
)
test_logger.log(
    logging.DEBUG, 
    f'Progressed by 1 block'
)


### Check on the progress
test_logger.log(
    logging.DEBUG, 
    f'Start checking with a loop period of {round_loop_period_s} seconds.'
)
while True:
    log_stress_test_state(stress_testing_client, test_logger, 'New loop')
    time.sleep(round_loop_period_s)
