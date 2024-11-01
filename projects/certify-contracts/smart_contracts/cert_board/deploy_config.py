import logging
from dataclasses import dataclass

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)

PATH_TO_FRONTEND = "../certify-frontend/src/certBoardAppID.tsx"


@dataclass
class DeployConst:
    # pla_manager: str = None
    expected_consensus_rate: int = 1
    certificate_fee: int = 100_000
    stress_test_fee_round: int = 1
    payment_asset: int = 0
    max_test_duration: int = 10_000
    max_test_blocking: int = 11_000
    stake_min: int = 100_000
    stake_max: int = 10_000_000


# define deployment behavior based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    from smart_contracts.artifacts.cert_board.cert_board_client import (
        CertBoardClient,
    )

    print("----- Deploying certification board ... -----\n")
    cert_board_client = CertBoardClient(
        algod_client,
        creator=deployer.address,
        signer=deployer.signer,
        indexer_client=indexer_client,
    )

    res = cert_board_client.create_cert_board_deploy()

    print(f"Created certification board with app ID: {res.return_value}\n")

    with open(PATH_TO_FRONTEND, "w") as file:
        file.write(f"export const certBoardAppID = {res.return_value}")

    # Needs to be funded with account MBR to be able to set
    print("Funding certification board with MBR ...\n")
    algokit_utils.ensure_funded(
        algod_client,
        algokit_utils.EnsureBalanceParameters(
            account_to_fund=cert_board_client.app_address,
            min_spending_balance_micro_algos=0,
        ),
    )
    print("Funding finished.\n")

    print("Setting certification board.\n")
    # Set the platform with some predefined settings, accepting ALGO as payment
    cert_board_client.cert_board_set(
        pla_manager=deployer.address,
        expected_consensus_rate=DeployConst.expected_consensus_rate,
        certificate_fee=DeployConst.certificate_fee,
        stress_test_fee_round=DeployConst.stress_test_fee_round,
        payment_asset=DeployConst.payment_asset,
        max_test_duration=DeployConst.max_test_duration,
        max_test_blocking=DeployConst.max_test_blocking,
        stake_min=DeployConst.stake_min,
        stake_max=DeployConst.stake_max,
    )
