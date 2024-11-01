import pytest

from smart_contracts.constants import ALGO_ASA_ID
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH, SKIP_SAME_AS_FOR_ALGO

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "DEPLOYED"
TEST_ACTION_NAME = "cert_board_key_reg"


# ------- Tests -------
def test_action(
    cert_board: CertBoard,
    asset: int,
) -> None:

    pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()
    cert_board.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )
    gs_start = cert_board.get_global_state()
    action_inputs.key_reg_vote_first = 1
    action_inputs.key_reg_vote_last = (
        cert_board.algorand_client.client.algod.status()["last-round"] + 100
    )

    # Action
    res = cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = gs_start
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check account is online
    assert cert_board.app_is_online()

    return


# def test_wrong_duration(
#     cert_board: CertBoard,
#     asset: int,
# ) -> None:

#     pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

#     # Setup
#     action_inputs = ActionInputs()
#     action_inputs.duration_max = action_inputs.duration - 1

#     # Action fail
#     with pytest.raises(LogicError) as e:
#         cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

#     assert is_expected_logic_error(ERROR_INCORRECT_DURATION, e)

#     return
