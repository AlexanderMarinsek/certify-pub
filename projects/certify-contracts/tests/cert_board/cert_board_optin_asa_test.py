import pytest

from smart_contracts.constants import ALGO_ASA_ID
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH, SKIP_NOT_APPLICABLE_TO_ALGO

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "DEPLOYED"
TEST_ACTION_NAME = "cert_board_optin_asa"


# ------- Tests -------
def test_action(
    cert_board: CertBoard,
    asset: int,
) -> None:

    pytest.skip(SKIP_NOT_APPLICABLE_TO_ALGO) if asset == ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()
    action_inputs.payment_asset = asset
    cert_board.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )
    gs_start = cert_board.get_global_state()

    # Action
    res = cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = gs_start

    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # If asset ID is not zero (i.e. ALGO), check if contract opted-in to it.
    if asset != ALGO_ASA_ID:
        assert cert_board.app_is_opted_in(asset)

    return
