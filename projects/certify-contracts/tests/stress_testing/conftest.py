import pytest
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils.beta.composer import AssetTransferParams, PayParams
from algokit_utils.config import config

from smart_contracts.artifacts.stress_testing.stress_testing_client import (
    StressTestingClient,
)
from smart_contracts.constants import ALGO_ASA_ID
from tests.conftest import TestConsts
from tests.stress_testing.utils import StressTesting


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
def stress_testing_client(
    algorand_client: AlgorandClient,
    creator: AddressAndSigner,
) -> StressTestingClient:
    """
    Create a new StressTesting client.

    Parameters
    ----------
    algorand_client : AlgorandClient

    creator : AddressAndSigner

    Returns
    -------
    stress_testing_client : StressTestingClient
        StressTesting app client.
    """

    config.configure(
        debug=True,
        # trace_all=True,
    )

    stress_testing_client = StressTestingClient(
        algorand_client.client.algod,
        creator=creator.address,
        signer=creator.signer,
        indexer_client=algorand_client.client.indexer,
    )

    return stress_testing_client


@pytest.fixture(scope="function")
def stress_testing(
    stress_testing_client: StressTestingClient,
    algorand_client: AlgorandClient,
    creator: AddressAndSigner,
) -> StressTesting:

    return StressTesting(
        stress_testing_client=stress_testing_client,
        algorand_client=algorand_client,
        acc=creator,
    )
