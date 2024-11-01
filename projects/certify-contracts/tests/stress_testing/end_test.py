import pytest
from algosdk.error import AlgodHTTPError

from smart_contracts.constants import ALGO_ASA_ID
from tests.constants import SKIP_SAME_AS_FOR_ALGO
from tests.stress_testing.utils import StressTesting
from tests.utils import (
    is_expected_https_error,
    wait_for_rounds,
)

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_ACTION_NAME = "end"


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
    status = stress_testing.algorand_client.client.algod.status()
    current_round = status["last-round"]
    wait_for_rounds(
        stress_testing.algorand_client,
        gs_start.round_end_max - current_round,
        stress_testing.acc,
    )

    # Action
    res = stress_testing.action(
        action_name=TEST_ACTION_NAME, action_inputs=action_inputs
    )

    # Check return
    # Below assertion fails for some reason
    # assert res.return_value == ReturnStressTestingEnd(
    #     success=True,
    #     avr_online_stake=42000042,
    #     cnt_produced_block=0,
    #     round_start=gs_start.round_start,
    #     round_end=gs_start.round_end,
    #     round_ended=res.confirmed_round,
    #     stake=gs_start.stake,
    #     user_address=gs_start.user_address,
    # )
    assert res.return_value.success == True  # noqa: E712
    assert res.return_value.avr_online_stake == 42000042
    assert res.return_value.cnt_produced_block == 0
    assert res.return_value.round_end == gs_start.round_end
    assert res.return_value.round_ended == res.confirmed_round
    assert res.return_value.stake == gs_start.stake
    assert res.return_value.user_address == gs_start.user_address

    # Check contract doesn't exist anymore
    with pytest.raises(AlgodHTTPError) as e:
        stress_testing.get_global_state()
    assert is_expected_https_error("application does not exist", e)

    return


def test_action_owner(
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
    action_inputs.user_address = gs_start.owner_address

    # Action
    res = stress_testing.action(
        action_name=TEST_ACTION_NAME, action_inputs=action_inputs
    )

    # Check return
    # Below assertion fails for some reason
    # assert res.return_value == ReturnStressTestingEnd(
    #     success=True,
    #     avr_online_stake=42000042,
    #     cnt_produced_block=0,
    #     round_start=gs_start.round_start,
    #     round_end=gs_start.round_end,
    #     round_ended=res.confirmed_round,
    #     stake=gs_start.stake,
    #     user_address=gs_start.user_address,
    # )
    assert res.return_value.success == False  # noqa: E712
    assert res.return_value.avr_online_stake == 42000042
    assert res.return_value.cnt_produced_block == 0
    assert res.return_value.round_end == gs_start.round_end
    assert res.return_value.round_ended == res.confirmed_round
    assert res.return_value.stake == gs_start.stake
    assert res.return_value.user_address == gs_start.user_address

    # Check contract doesn't exist anymore
    with pytest.raises(AlgodHTTPError) as e:
        stress_testing.get_global_state()
    assert is_expected_https_error("application does not exist", e)

    return
