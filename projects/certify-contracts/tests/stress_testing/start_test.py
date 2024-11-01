import pytest
from algokit_utils import LogicError

from smart_contracts.constants import ALGO_ASA_ID, CONSENSUS_STAKE_ROUND_DELAY
from smart_contracts.stress_testing.constants import (
    ERROR_TEST_NOT_SOON_ENOUGH,
    STATE_LIVE,
)
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH, SKIP_SAME_AS_FOR_ALGO
from tests.stress_testing.utils import StressTesting
from tests.utils import is_expected_logic_error, wait_for_rounds

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "CREATED"
TEST_ACTION_NAME = "start"


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

    # Action
    res = stress_testing.action(
        action_name=TEST_ACTION_NAME, action_inputs=action_inputs
    )

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = gs_start
    gs_exp.round_end = res.confirmed_round + gs_start.duration
    gs_exp.round_start = res.confirmed_round + CONSENSUS_STAKE_ROUND_DELAY
    gs_exp.last_block = gs_exp.round_start
    gs_exp.state = STATE_LIVE
    assert stress_testing.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check account is online
    assert stress_testing.app_is_online()

    return


def test_too_late(
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
    status = stress_testing.algorand_client.client.algod.status()
    current_round = status["last-round"]
    wait_for_rounds(
        stress_testing.algorand_client,
        gs_start.round_end_max - current_round,
        stress_testing.acc,
    )

    # Action fail
    with pytest.raises(LogicError) as e:
        stress_testing.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    assert is_expected_logic_error(ERROR_TEST_NOT_SOON_ENOUGH, e)

    return
