from algokit_utils.beta.account_manager import AddressAndSigner
from algosdk.abi import AddressType

from smart_contracts.constants import ALGO_ASA_ID
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_STRESS_INITIAL_STATE = "CREATED"
TEST_ACTION_NAME = "stress_start"


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
    cert_board.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )

    cert_board.acc = user
    app_id = cert_board.initialize_stress_testing_state(
        action_inputs=action_inputs,
        target_state=TEST_STRESS_INITIAL_STATE,
    )
    gs_start = cert_board.get_global_state()

    bal_algo_start = cert_board.app_available_balance(ALGO_ASA_ID)

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

    # Check balance
    bal_algo_end = cert_board.app_available_balance(ALGO_ASA_ID)
    assert bal_algo_end + action_inputs.stake == bal_algo_start

    # Check created box
    box_name = AddressType().encode(action_inputs.user_address) + app_id.to_bytes(
        8, byteorder="big"
    )
    box = cert_board.app_box(box_name)
    assert box[1]
    assert box[0] == bytes(len(box[0]))

    return
