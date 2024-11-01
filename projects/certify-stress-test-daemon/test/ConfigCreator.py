"""Create node config file programatically.
"""
from pathlib import Path


class ConfigCreator(object):
    """Create node config file programatically.
    """

    def __init__(self):
        self.config = None

    def create_config(
        self, 
        validator_manager_mnemonic: str,
        stress_test_app_id: str,
        algod_config_server: str='http://localhost:4001',
        algod_config_token: str='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        indexer_config_server: str='http://localhost:8980',
        indexer_config_token: str='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        kmd_config_server: str='http://localhost:4002',
        kmd_config_token: str='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        loop_period_s: int=1,
        logging_level: str='DEBUG'
    ) -> str:
        """Create the config text.

        Args:
            validator_manager_mnemonic (str):  
            stress_test_app_id (int):  
            algod_config_server (_type_, optional): Defaults to 'http://localhost:4001'.
            algod_config_token (str, optional): Defaults to 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'.
            indexer_config_server (_type_, optional): Defaults to 'http://localhost:8980'.
            indexer_config_token (str, optional): Defaults to 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'.
            kmd_config_server (_type_, optional): Defaults to 'http://localhost:4002'.
            kmd_config_token (str, optional): Defaults to 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'.
            loop_period_s (int, optional): Loop time. Defaults to 1.
            logging_level (str, optional): Defaults to 'DEBUG'.

        Returns:
            str: Config text.
        """
        self.config = \
        '[validator_manager_config] ####################################################################################################' + '\n' + \
        '\n' + \
        f'validator_manager_mnemonic = {validator_manager_mnemonic}' + '\n' + \
        '\n\n' + \
        '[certify_config] ####################################################################################################' + '\n' + \
        '\n' + \
        f'stress_test_app_id = {stress_test_app_id}' + '\n' + \
        '\n\n' + \
        '[daemon_config] ##########################################################################################################' + '\n' + \
        '\n' + \
        f'loop_period_s = {loop_period_s}' + '\n' + \
        f'logging_level = {logging_level}' + '\n' + \
        '\n\n' + \
        '[algo_client_config] ###################################################################################################' + '\n' + \
        '\n' + \
        f'algod_config_server = {algod_config_server}' + '\n' + \
        f'algod_config_token = {algod_config_token}' + '\n' + \
        f'indexer_config_server = {indexer_config_server}' + '\n' + \
        f'indexer_config_token = {indexer_config_token}' + '\n' + \
        f'kmd_config_server = {kmd_config_server}' + '\n' + \
        f'kmd_config_token = {kmd_config_token}' + '\n'
        return self.config


    def save_to_file(
        self, 
        filepath: Path
    ) -> None:
        """Save the pre-generated config to a file.

        Args:
            filepath (Path): Path, incuding filename.
        """
        with open(filepath, 'w') as f:
            f.write(self.config)


if __name__ == '__main__':

    from algokit_utils.beta.algorand_client import AlgorandClient
    from algosdk import mnemonic

    from utils_misc import create_and_fund_account


    algorand_client = AlgorandClient.default_local_net()
    algorand_client.set_suggested_params_timeout(0)

    stress_test_app_id = 9999
    validator_ad_manager = create_and_fund_account(algorand_client)

    mne = mnemonic.from_private_key(validator_ad_manager.signer.private_key)

    cc = ConfigCreator()
    cc.create_config(
        validator_manager_mnemonic=mne,
        stress_test_app_id=stress_test_app_id
    )
    cc.save_to_file(Path(Path(__file__).parent, 'test.config'))
