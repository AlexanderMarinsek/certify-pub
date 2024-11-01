from smart_contracts.cert_board.constants import (
    STATE_LIVE,
)
from tests.cert_board.client_helper import CertBoardGlobalState
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "DEPLOYED"
TEST_ACTION_NAME = "cert_board_set"


# ------- Tests -------
def test_action(
    cert_board: CertBoard,
    asset: int,
) -> None:

    # Setup
    action_inputs = ActionInputs()
    action_inputs.payment_asset = asset
    cert_board.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )
    cert_board.action(action_name="cert_board_optin_asa", action_inputs=action_inputs)

    # Action
    res = cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = CertBoardGlobalState(
        pla_manager=action_inputs.pla_manager,
        expected_consensus_rate=action_inputs.expected_consensus_rate,
        certificate_fee=action_inputs.certificate_fee,
        stress_test_fee_round=action_inputs.stress_test_fee_round,
        payment_asset=action_inputs.payment_asset,
        max_test_duration=action_inputs.max_test_duration,
        max_test_blocking=action_inputs.max_test_blocking,
        stake_min=action_inputs.stake_min,
        stake_max=action_inputs.stake_max,
        blocked_algo=0,
        state=STATE_LIVE,
    )

    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    return
