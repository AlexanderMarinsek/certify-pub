from algosdk.atomic_transaction_composer import AtomicTransactionComposer

from tests.cert_board.utils import CertBoard
from tests.constants import ERROR_GLOBAL_STATE_MISMATCH
from tests.utils import create_pay_fee_txn

from .config import ActionInputs

# ------- Test constants -------
TEST_INITIAL_STATE = "LIVE"
TEST_ACTION_NAME = "cert_board_withdraw"


# ------- Tests -------
def test_action(
    cert_board: CertBoard,
    asset: int,
) -> None:

    # Setup
    action_inputs = ActionInputs()
    action_inputs.payment_asset = asset
    action_inputs.pla_manager = cert_board.acc.address
    cert_board.initialize_state(
        target_state=TEST_INITIAL_STATE, action_inputs=action_inputs
    )
    # Fund the application with some asset to be able to withdraw it
    action_inputs.amount = 424_242
    pay_fee_txn = create_pay_fee_txn(
        algorand_client=cert_board.algorand_client,
        asset_id=action_inputs.payment_asset,
        amount=action_inputs.amount,
        sender=cert_board.acc.address,
        signer=cert_board.acc.signer,
        receiver=cert_board.cert_board_client.app_address,
    )
    atc = AtomicTransactionComposer()
    atc.add_transaction(pay_fee_txn)
    atc.submit(cert_board.algorand_client.client.algod)
    gs_start = cert_board.get_global_state()
    bal_start = cert_board.app_available_balance(asset)

    # Action
    res = cert_board.action(action_name=TEST_ACTION_NAME, action_inputs=action_inputs)

    # Check return
    assert res.confirmed_round

    # Check contract state
    gs_exp = gs_start
    assert cert_board.get_global_state() == gs_exp, ERROR_GLOBAL_STATE_MISMATCH

    # Check balance
    bal_end = cert_board.app_available_balance(asset)
    assert bal_end + action_inputs.amount == bal_start

    return
