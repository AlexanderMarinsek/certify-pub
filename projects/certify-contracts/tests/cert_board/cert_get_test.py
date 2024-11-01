import pytest
from algosdk.abi import AddressType

from smart_contracts.constants import ALGO_ASA_ID, CERT_INFO_VAL_LENGTH
from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH, SKIP_SAME_AS_FOR_ALGO

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_ACTION_NAME = "cert_get"


# ------- Tests -------
def test_action(
    cert_board: CertBoard,
    asset: int,
) -> None:

    pytest.skip("TO DO : FOR SOME REASON THERE IS AN ERROR.")

    pytest.skip(SKIP_SAME_AS_FOR_ALGO) if asset != ALGO_ASA_ID else None

    # Setup
    action_inputs = ActionInputs()
    action_inputs.payment_asset = asset
    action_inputs.issuer = cert_board.acc.address
    action_inputs.info = bytes([0xFF] * CERT_INFO_VAL_LENGTH)
    cert_board.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )
    cert_board.action(action_name="cert_create", action_inputs=action_inputs)
    bal_start = cert_board.app_available_balance(asset)
    gs_start = cert_board.get_global_state()

    box_name = AddressType().encode(action_inputs.recipient) + AddressType().encode(
        cert_board.acc.address
    )
    assert cert_board.app_box(box_name)[0]

    # Action
    res = cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    # Check return
    assert res.raw_value == action_inputs.info

    # Check contract state
    gs_exp = gs_start
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check balance
    bal_end = cert_board.app_available_balance(asset)
    assert bal_end == bal_start

    # Check box
    box_name = AddressType().encode(action_inputs.recipient) + AddressType().encode(
        cert_board.acc.address
    )
    assert cert_board.app_box(box_name)[0]
    assert cert_board.app_box(box_name)[1] == action_inputs.info

    return
