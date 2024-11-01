import pytest
from algokit_utils import LogicError

from smart_contracts.constants import ALGO_ASA_ID
from smart_contracts.stress_testing.constants import (
    ERROR_INCORRECT_DURATION,
    STATE_CREATED,
)
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH, SKIP_SAME_AS_FOR_ALGO
from tests.stress_testing.client_helper import StressTestingGlobalState
from tests.stress_testing.utils import StressTesting
from tests.utils import is_expected_logic_error

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "START"
TEST_ACTION_NAME = "create"


# ------- Tests -------
def test_action(
    stress_testing: StressTesting,
    asset: int,
) -> None:

    pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()

    # Action
    res = stress_testing.action(
        action_name=TEST_ACTION_NAME, action_inputs=action_inputs
    )

    # Check return
    assert res.return_value != 0, "App was not created."

    # Check contract state
    gs_exp = StressTestingGlobalState(
        user_address=action_inputs.user_address,
        owner_address=action_inputs.owner_address,
        stake=action_inputs.stake,
        duration=action_inputs.duration,
        duration_max=action_inputs.duration_max,
        state=STATE_CREATED,
        round_created=res.confirmed_round,
        round_end_max=res.confirmed_round + action_inputs.duration_max,
        total_stake_sum=42000042,
        cnt_total_stake_sum=1,
    )
    assert stress_testing.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    return


def test_wrong_duration(
    stress_testing: StressTesting,
    asset: int,
) -> None:

    pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()
    action_inputs.duration_max = action_inputs.duration - 1

    # Action fail
    with pytest.raises(LogicError) as e:
        stress_testing.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    assert is_expected_logic_error(ERROR_INCORRECT_DURATION, e)

    return
