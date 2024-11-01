import argparse
from pathlib import Path

from src.daemon import run


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=f"Certify stress test daemon.")
    parser.add_argument(
        '--config_path', type=str, help='Path to the config file',
        required=False, default=Path(Path(__file__).parent, 'daemon.config')
    )
    parser.add_argument(
        '--log_path', type=str, help='Path to the log file',
        required=False, default=Path(Path(__file__).parent, 'daemon.log')
    )
    args = parser.parse_args()

    run(Path(args.config_path), Path(args.log_path))
