import pytest

from smart_contracts.cert_board.constants import (
    STATE_DEPLOYED,
)
from smart_contracts.constants import ALGO_ASA_ID
from tests.cert_board.client_helper import CertBoardGlobalState
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH, SKIP_SAME_AS_FOR_ALGO

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "START"
TEST_ACTION_NAME = "cert_board_deploy"


# ------- Tests -------
def test_action(
    cert_board: CertBoard,
    asset: int,
) -> None:

    pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()

    # Action
    res = cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    # Check return
    assert res.return_value != 0, "App was not created."

    # Check contract state
    gs_exp = CertBoardGlobalState(
        pla_manager=cert_board.acc.address,
        expected_consensus_rate=0,
        certificate_fee=0,
        stress_test_fee_round=0,
        payment_asset=0,
        max_test_duration=0,
        max_test_blocking=0,
        stake_min=0,
        stake_max=0,
        blocked_algo=0,
        state=STATE_DEPLOYED,
    )
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    return
