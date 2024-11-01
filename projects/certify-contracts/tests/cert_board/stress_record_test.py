from algokit_utils.beta.account_manager import AddressAndSigner

from smart_contracts.constants import (
    ALGO_ASA_ID,
)
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH
from tests.utils import wait_for_rounds

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_STRESS_INITIAL_STATE = "LIVE"
TEST_ACTION_NAME = "stress_record"


# ------- Tests -------
def test_action(
    cert_board: CertBoard,
    asset: int,
    user: AddressAndSigner,
) -> None:

    # Setup
    action_inputs = ActionInputs()
    action_inputs.payment_asset = asset
    action_inputs.user_address = user.address
    action_inputs.pla_manager = cert_board.acc.address
    cert_board.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )

    cert_board.acc = user
    app_id = cert_board.initialize_stress_testing_state(
        action_inputs=action_inputs,
        target_state=TEST_STRESS_INITIAL_STATE,
    )
    gs_start = cert_board.get_global_state()
    gs_st_start = cert_board.get_stress_testing_global_state(app_id)

    bal_algo_start = cert_board.app_available_balance(ALGO_ASA_ID)

    # Wait a bit to record
    rounds = 3
    wait_for_rounds(cert_board.algorand_client, rounds, cert_board.acc)

    # Action
    res = cert_board.stress_testing_action(
        app_id=app_id,
        action_name=TEST_ACTION_NAME,
        action_inputs=action_inputs,
    )

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = gs_start
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check stress testing state
    gs_exp = gs_st_start
    gs_exp.cnt_produced_blocks = 1
    gs_exp.total_stake_sum = gs_st_start.total_stake_sum * 2
    gs_exp.cnt_total_stake_sum = 2
    gs_exp.last_block = res.confirmed_round
    assert (
        cert_board.get_stress_testing_global_state(app_id) == gs_exp
    ), ERROR_GLOBAL_STATE_MISMATCH

    return
