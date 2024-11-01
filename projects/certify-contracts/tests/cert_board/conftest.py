import pytest
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils.beta.composer import AssetTransferParams, PayParams
from algokit_utils.config import config

from smart_contracts.artifacts.cert_board.cert_board_client import (
    CertBoardClient,
)
from smart_contracts.constants import ALGO_ASA_ID
from tests.cert_board.utils import CertBoard
from tests.conftest import TestConsts


@pytest.fixture(scope="package", params=[ALGO_ASA_ID, "asa"])
def asset(request: pytest.FixtureRequest, asa: int) -> int:
    if request.param == "asa":
        return asa
    else:
        return request.param


@pytest.fixture(scope="package")
def creator(
    algorand_client: AlgorandClient,
    dispenser: AddressAndSigner,
    asset: int,
) -> AddressAndSigner:
    acc = algorand_client.account.random()
    algorand_client.send.payment(
        PayParams(
            sender=dispenser.address,
            receiver=acc.address,
            amount=TestConsts.acc_dispenser_amt,
        )
    )

    if asset != ALGO_ASA_ID:
        # Opt-in to ASA
        algorand_client.send.asset_transfer(
            AssetTransferParams(
                sender=acc.address,
                receiver=acc.address,
                amount=0,
                asset_id=asset,
                signer=acc.signer,
            )
        )

        # Get some ASA
        algorand_client.send.asset_transfer(
            AssetTransferParams(
                sender=dispenser.address,
                receiver=acc.address,
                amount=TestConsts.acc_dispenser_asa_amt,
                asset_id=asset,
            )
        )

    return acc


@pytest.fixture(scope="function")
def cert_board_client(
    algorand_client: AlgorandClient,
    creator: AddressAndSigner,
) -> CertBoardClient:
    """
    Create a new CertBoard client.

    Parameters
    ----------
    algorand_client : AlgorandClient

    creator : AddressAndSigner

    Returns
    -------
    cert_board_client : CertBoardClient
        CertBoard app client.
    """

    config.configure(
        debug=True,
        # trace_all=True,
    )

    cert_board_client = CertBoardClient(
        algorand_client.client.algod,
        creator=creator.address,
        signer=creator.signer,
        indexer_client=algorand_client.client.indexer,
    )

    return cert_board_client


@pytest.fixture(scope="function")
def cert_board(
    cert_board_client: CertBoardClient,
    algorand_client: AlgorandClient,
    creator: AddressAndSigner,
) -> CertBoard:

    return CertBoard(
        cert_board_client=cert_board_client,
        algorand_client=algorand_client,
        acc=creator,
    )


@pytest.fixture(scope="module")
def user(
    algorand_client: AlgorandClient,
    dispenser: AddressAndSigner,
    asset: int,
) -> AddressAndSigner:
    acc = algorand_client.account.random()
    algorand_client.send.payment(
        PayParams(
            sender=dispenser.address,
            receiver=acc.address,
            amount=TestConsts.acc_dispenser_amt,
        )
    )

    if asset != ALGO_ASA_ID:
        # Opt-in to ASA
        algorand_client.send.asset_transfer(
            AssetTransferParams(
                sender=acc.address,
                receiver=acc.address,
                amount=0,
                asset_id=asset,
                signer=acc.signer,
            )
        )

        # Get some ASA
        algorand_client.send.asset_transfer(
            AssetTransferParams(
                sender=dispenser.address,
                receiver=acc.address,
                amount=TestConsts.acc_dispenser_asa_amt,
                asset_id=asset,
            )
        )

    return acc
