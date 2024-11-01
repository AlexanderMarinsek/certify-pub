import pytest
from algokit_utils import LogicError
from algosdk.error import AlgodHTTPError

from smart_contracts.constants import ALGO_ASA_ID
from smart_contracts.stress_testing.constants import ERROR_TEST_CAN_FINISH_IN_TIME
from tests.constants import SKIP_SAME_AS_FOR_ALGO
from tests.stress_testing.utils import StressTesting
from tests.utils import (
    is_expected_https_error,
    is_expected_logic_error,
    wait_for_rounds,
)

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "CREATED"
TEST_ACTION_NAME = "unused"


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
        gs_start.duration_max,
        stress_testing.acc,
    )

    # Action
    res = stress_testing.action(
        action_name=TEST_ACTION_NAME, action_inputs=action_inputs
    )

    # Check return
    assert res.return_value == gs_start.stake

    # Check contract doesn't exist anymore
    with pytest.raises(AlgodHTTPError) as e:
        stress_testing.get_global_state()
    assert is_expected_https_error("application does not exist", e)

    return


def test_unused_called_too_soon(
    stress_testing: StressTesting,
    asset: int,
) -> None:

    pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()
    stress_testing.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )
    wait_for_rounds(
        stress_testing.algorand_client,
        0,
        stress_testing.acc,
    )

    # Action fail
    with pytest.raises(LogicError) as e:
        stress_testing.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    assert is_expected_logic_error(ERROR_TEST_CAN_FINISH_IN_TIME, e)

    return
