from pathlib import Path

import pytest
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils.beta.composer import AssetCreateParams
from dotenv import load_dotenv


# ------- Constants -------
class TestConsts:
    acc_dispenser_amt = 400_000_000
    acc_dispenser_asa_amt = 1000_000_000


# ------- Fixtures -------
@pytest.fixture(scope="session")
def dispenser(algorand_client: AlgorandClient) -> AddressAndSigner:
    return algorand_client.account.dispenser()


@pytest.fixture(scope="session")
def asa(algorand_client: AlgorandClient) -> int:
    _dispenser = algorand_client.account.dispenser()
    # Dispenser also creates an ASA to be used during the tests
    res = algorand_client.send.asset_create(
        AssetCreateParams(
            sender=_dispenser.address,
            total=42_000_000_000,
            decimals=6,
            default_frozen=False,
            manager=_dispenser.address,
            reserve=_dispenser.address,
            freeze=_dispenser.address,
            clawback=_dispenser.address,
            unit_name="T0",
            asset_name="TEST_TOKEN_0",
        )
    )

    asa_id = res["confirmation"]["asset-index"]

    return asa_id


@pytest.fixture(scope="session")
def algorand_client() -> AlgorandClient:
    client = AlgorandClient.default_local_net()
    client.set_suggested_params_timeout(0)
    return client


@pytest.fixture(scope="session")
def test_consts() -> TestConsts:
    return TestConsts


@pytest.fixture(autouse=True, scope="session")
def environment_fixture() -> None:
    env_path = Path(__file__).parent.parent / ".env.localnet"
    load_dotenv(env_path)
