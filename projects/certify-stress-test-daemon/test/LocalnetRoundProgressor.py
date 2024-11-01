import sys
import time
import logging

from algokit_utils.beta.algorand_client import AlgorandClient

from utils_misc import wait_for_rounds, create_and_fund_account


class LocalnetRoundProgressor(object):
    
    def __init__(
        self,
        round_time_s: int=3
    ) -> None:
        self.round_time_s = round_time_s
        # self._set_logger()

    def set_logger(self, logger):
        self.logger = logger
        # self.logger = logging.Logger(__name__)
        # self.logger.setLevel(logging.DEBUG)
        # # Add a handler to output to stdout
        # handler = logging.StreamHandler(sys.stdout)
        # self.logger.addHandler(handler)

    def run(self):
        self.logger.log(logging.DEBUG, f'Start progressing localnet with a round time of {self.round_time_s} seconds')
        algorand_client = AlgorandClient.default_local_net()
        algorand_client.set_suggested_params_timeout(0)
        acc = create_and_fund_account(algorand_client)
        while True:
            start_time_s = time.time()
            wait_for_rounds(
                algorand_client,
                1,
                acc
            )
            self.logger.log(logging.INFO, f'New round at {start_time_s}')
            try:
                time.sleep(start_time_s + self.round_time_s - time.time())
            except:
                pass


if __name__ == '__main__':

    lrp = LocalnetRoundProgressor()
    logger = logging.Logger(__name__)
    logger.setLevel(logging.DEBUG)
    # Add a handler to output to stdout
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    lrp.set_logger(logger)
    lrp.run()
