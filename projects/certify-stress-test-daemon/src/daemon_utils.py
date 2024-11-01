"""Different utils and helpers for the daemon.
"""
import sys
import logging
import configparser
from pathlib import Path


def init_default_file_logger(
    logger_name: str, 
    log_path: Path, 
    logging_level: str='INFO'
) -> logging.Logger:
    """Initialize a logger, pointing to a file.

    Args:
        logger_name (str): Name.
        log_path (Path): Path.
        logging_level (str): Level. Default is `"INFO"`.

    Returns:
        logging.Logger: Logger.
    """
    # Initialize logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(eval(f'logging.{logging_level}'))
    # Create file handler which logs messages
    fh = logging.FileHandler(log_path)
    fh.setLevel(eval(f'logging.{logging_level}'))
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # Add the handlers to the logger
    logger.addHandler(fh)
    return logger


def init_default_stdout_logger(
    logger_name: str, 
    logging_level
) -> logging.Logger:
    """Initialize a logger, pointing to STDOUT.

    Args:
        logger_name (str): Name.
        logging_level (str): Level. Default is `"INFO"`.

    Returns:
        logging.Logger: Logger.
    """
    # Initialize logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(eval(f'logging.{logging_level}'))
    # Create stream handler to log messages to stdout
    sh = logging.StreamHandler(sys.stdout)  # Set to output to stdout
    sh.setLevel(eval(f'logging.{logging_level}'))
    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(sh)
    return logger


def interpret_config(
    config_path: Path
) -> tuple:
    """Interpret and load up the daemon config.

    Args:
        config_path (Path): Path.

    Raises:
        ValueError: non-existent config.

    Returns:
        tuple: Config parameters.
    """

    # Catch non-existent file
    if not config_path.is_file():
        raise ValueError(f'Can\'t find the provided config file at {str(config_path)}')
    
    config = configparser.RawConfigParser(defaults=None, strict=False, allow_no_value=True)
    config.read(config_path)

    # validator_manager_public_address = str(config.get('validator_manager_config', 'validator_manager_public_address'))
    validator_manager_mnemonic_str = str(config.get('validator_manager_config', 'validator_manager_mnemonic'))

    app_id = int(config.get('certify_config', 'stress_test_app_id'))

    algod_config_server =   str(config.get('algo_client_config', 'algod_config_server'))
    algod_config_token =    str(config.get('algo_client_config', 'algod_config_token'))
    indexer_config_server = str(config.get('algo_client_config', 'indexer_config_server'))
    indexer_config_token =  str(config.get('algo_client_config', 'indexer_config_token'))
    kmd_config_server =     str(config.get('algo_client_config', 'kmd_config_server'))
    kmd_config_token =      str(config.get('algo_client_config', 'kmd_config_token'))

    loop_period_s = float(config.get('daemon_config', 'loop_period_s'))
    logging_level = str(config.get('daemon_config', 'logging_level')).upper()

    return (
        # validator_manager_public_address,
        validator_manager_mnemonic_str,
        app_id,
        algod_config_server,
        algod_config_token,
        indexer_config_server,
        indexer_config_token,
        kmd_config_server,
        kmd_config_token,
        loop_period_s,
        logging_level
    )
