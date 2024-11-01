"""The Certify stress test daemon abstraction, relying on the daemon class definition.
"""
import argparse
from pathlib import Path

from algokit_utils.beta.account_manager import AddressAndSigner
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk import mnemonic, account

from .daemon_utils import init_default_file_logger, interpret_config
from .StressTestDaemon import StressTestDaemon


def run(
    config_path: str, 
    log_path: str
):

    ### Load config ####################################################################################################

    # (validator_manager_public_address,
    (validator_manager_mnemonic_str,
    app_id,
    algod_config_server,
    algod_config_token,
    indexer_config_server,
    indexer_config_token,
    kmd_config_server,
    kmd_config_token,
    loop_period_s,
    logging_level) = interpret_config(config_path)


    ### Init logger ####################################################################################################

    logger = init_default_file_logger(
        'daemon_logger', 
        Path(log_path), 
        logging_level
    )

    [logger.info('#'*120) for i in range(3)]
    logger.info(f'Started daemon. ' + '#'*105)

    logger.info(f'Serving app with ID {app_id}.')
    logger.info(f'Indexer server configured to {indexer_config_server}')


    ### Set up manager #################################################################################################

    manager_private_key = mnemonic.to_private_key(validator_manager_mnemonic_str)
    manager_address = account.address_from_private_key(manager_private_key)
    manager = AddressAndSigner(
        address=manager_address,
        signer=AccountTransactionSigner(manager_private_key)
    )    


    ### Run daemon #####################################################################################################

    daemon = StressTestDaemon(loop_period_s)

    daemon.connect_logger(logger)

    daemon.set_algorand_client_from_config_params(
        algod_config_server,
        algod_config_token,
        indexer_config_server,
        indexer_config_token,
        kmd_config_server,
        kmd_config_token,
    )

    daemon.set_validator_manager_account(manager)

    daemon.set_stress_testing_client(app_id)

    daemon.run_record_loop()    



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=f"Certify daemon.")
    parser.add_argument(
        '--config_path', type=str, help='Path to the config file',
        required=False, default=Path(*Path(__file__).parent.parts[:-1], 'daemon.config')
    )
    parser.add_argument(
        '--log_path', type=str, help='Path to the log file',
        required=False, default=Path(*Path(__file__).parent.parts[:-1], 'daemon.log')
    )
    args = parser.parse_args()

    run(args.config_path, args.log_path)
