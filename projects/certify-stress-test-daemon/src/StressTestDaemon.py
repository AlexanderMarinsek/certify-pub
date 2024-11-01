"""The Certify stress test daemon class definion.
"""
import time
import logging

from algokit_utils import TransactionParameters
from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.network_clients import AlgoClientConfig, AlgoClientConfigs

from .StressTestingClient import StressTestingClient


class StressTestDaemon(object):
    """Deamon for Certify stress test.

    Args:
        loop_period_s (float): Period at which record loop is called.
    """

    def __init__(
        self, 
        loop_period_s: float
    ) -> None:
        """Initialize stress test daemon.

        Args:
            loop_period_s (float): Period at which record loop is called.
        """
        self.loop_period_s = loop_period_s

    def connect_logger(
        self, 
        logger: logging.Logger
    ) -> None:
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.Logger()
            self.logger.setLevel('debug')

    def set_algorand_client_from_config_params(
        self,
        algod_config_server: str,
        algod_config_token: str,
        indexer_config_server: str,
        indexer_config_token: str,
        kmd_config_server: str,
        kmd_config_token: str
    ) -> None:
        """Set up Algorand client.

        Args:
            algod_config_server (str): URL of the algod.
            algod_config_token (str): Token for algod access.
            indexer_config_server (str): URL of the indexer.
            indexer_config_token (str): Token for indexer access.
            kmd_config_server (str): URL of the KMD.
            kmd_config_token (str): Token for KMD access.
        """
        algod_config = AlgoClientConfig(
            server=algod_config_server,
            token=algod_config_token
        )
        indexer_config = AlgoClientConfig(
            server=indexer_config_server,
            token=indexer_config_token
        )
        kmd_config = AlgoClientConfig(
            server=kmd_config_server,
            token=kmd_config_token
        )
        algorand_client = AlgorandClient(
            AlgoClientConfigs(
                algod_config=algod_config,
                indexer_config=indexer_config,
                kmd_config=kmd_config,
            )
        )
        self.set_algorand_client(algorand_client)

    def set_algorand_client(
        self, 
        algorand_client: AlgorandClient
    ) -> None:        
        """Set up Algorand client.

        Args:
            algorand_client (AlgorandClient): Initialized client.
        """
        self.algorand_client = algorand_client
        self.algorand_client.set_suggested_params_timeout(0)

    # def set_app_id(
    #     self,
    #     app_id: int,
    # ):
    #     self.app_id = app_id

    def set_validator_manager_account(
        self,
        manager_account: AddressAndSigner
    ) -> None:
        """Set the validator manager account.

        Args:
            manager_account (AddressAndSigner): Validator manager account.
        """
        self.manager_account = manager_account

    def set_stress_testing_client(
        self,
        app_id: int,
    ) -> None:
        """Set the smart contract client.

        Args:
            app_id (int): Stress test application ID.
        """
        self.stress_testing_client = StressTestingClient(
            algod_client=self.algorand_client.client.algod,
            app_id=app_id
        )

    def run_record_loop(
        self
    ) -> None:
        """Run the daemon, periodically calling the smart contract record function.
        """
        while True:
            start_time_s = time.time()
            try:
                res = self.stress_testing_client.record(
                    transaction_parameters=TransactionParameters(
                        sender=self.manager_account.address,
                        signer=self.manager_account.signer,
                    ),
                )
                self.logger.log(
                    logging.DEBUG, 
                    'Recorded block.'
                    )
            except Exception as e:
                self.logger.log(
                    logging.DEBUG, 
                    f'Tried recording block without success. Error: {e}'
                )
            try:
                time.sleep(start_time_s + self.loop_period_s - time.time())
            except:
                self.logger.log(
                    logging.WARNING, 
                    f'Could not sleep for {self.loop_period_s} s (negative sleep time).'
                )
