import pytest

from smart_contracts.constants import ALGO_ASA_ID
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH, SKIP_SAME_AS_FOR_ALGO
from tests.stress_testing.utils import StressTesting
from tests.utils import (
    wait_for_rounds,
)

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_ACTION_NAME = "record"


# ------- Tests -------
def test_action(
    stress_testing: StressTesting,
    asset: int,
) -> None:

    pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()
    stress_testing.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )
    gs_start = stress_testing.get_global_state()
    wait_for_rounds(
        stress_testing.algorand_client,
        1,
        stress_testing.acc,
    )

    # Action
    res = stress_testing.action(
        action_name=TEST_ACTION_NAME, action_inputs=action_inputs
    )

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = gs_start
    gs_exp.last_block = res.confirmed_round
    gs_exp.cnt_produced_blocks = 1
    gs_exp.total_stake_sum = 2 * 42000042
    gs_exp.cnt_total_stake_sum = 2
    assert stress_testing.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    return
