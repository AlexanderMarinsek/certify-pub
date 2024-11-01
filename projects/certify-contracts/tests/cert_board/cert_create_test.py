from algosdk.abi import AddressType

from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_ACTION_NAME = "cert_create"


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
    bal_start = cert_board.app_available_balance(asset)
    gs_start = cert_board.get_global_state()

    # Action
    res = cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = gs_start
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check balance
    bal_end = cert_board.app_available_balance(asset)
    assert bal_end == bal_start + action_inputs.certificate_fee

    # Check created box
    box_name = AddressType().encode(action_inputs.recipient) + AddressType().encode(
        cert_board.acc.address
    )
    assert cert_board.app_box(box_name)[1]
    assert cert_board.app_box(box_name)[0] == action_inputs.info

    return
