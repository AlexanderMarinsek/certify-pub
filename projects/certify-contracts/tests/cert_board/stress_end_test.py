from algokit_utils.beta.account_manager import AddressAndSigner
from algosdk.abi import AddressType

from smart_contracts.artifacts.cert_board.cert_board_client import (
    StressTestInfo,
)
from smart_contracts.constants import (
    ALGO_ASA_ID,
    MBR_STRESS_BOX,
    MBR_STRESS_TESTING_CONTRACT,
)
from tests.cert_board.client_helper import decode_stress_test_info
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH
from tests.utils import wait_for_rounds

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_STRESS_INITIAL_STATE = "LIVE"
TEST_ACTION_NAME = "stress_end"


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

    # Wait until stress testing ends
    rounds = (
        gs_st_start.round_end_max
        - cert_board.algorand_client.client.algod.status()["last-round"]
    )
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
    gs_exp.blocked_algo = gs_start.blocked_algo - gs_st_start.stake
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check balance
    bal_algo_end = cert_board.app_available_balance(ALGO_ASA_ID)
    assert (
        bal_algo_end
        == bal_algo_start + action_inputs.stake + MBR_STRESS_TESTING_CONTRACT
    )

    # Check the box contents
    box_name = AddressType().encode(action_inputs.user_address) + app_id.to_bytes(
        8, byteorder="big"
    )
    box = cert_board.app_box(box_name)
    assert box[1]
    box_val = decode_stress_test_info(box[0])
    assert box_val == StressTestInfo(
        avr_online_stake=42000042,
        cnt_produced_block=0,
        round_start=gs_st_start.round_start,
        round_end=gs_st_start.round_end,
        stake=gs_st_start.stake,
    )

    return


def test_action_early_end(
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

    pla_manager = cert_board.acc
    cert_board.acc = user
    app_id = cert_board.initialize_stress_testing_state(
        action_inputs=action_inputs,
        target_state=TEST_STRESS_INITIAL_STATE,
    )
    gs_start = cert_board.get_global_state()
    gs_st_start = cert_board.get_stress_testing_global_state(app_id)

    bal_algo_start = cert_board.app_available_balance(ALGO_ASA_ID)

    # Platform manager ends the test early
    cert_board.acc = pla_manager

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
    gs_exp.blocked_algo = gs_start.blocked_algo - gs_st_start.stake
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check balance
    bal_algo_end = cert_board.app_available_balance(ALGO_ASA_ID)
    assert (
        bal_algo_end
        == bal_algo_start
        + action_inputs.stake
        + MBR_STRESS_BOX
        + MBR_STRESS_TESTING_CONTRACT
    )

    # Check the box was deleted
    box_name = AddressType().encode(action_inputs.user_address) + app_id.to_bytes(
        8, byteorder="big"
    )
    box = cert_board.app_box(box_name)
    assert not box[1]

    return
