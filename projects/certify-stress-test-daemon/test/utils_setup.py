"""Environment setup utilities, sourced from smart contract tests.
"""
import sys
import base64
from pathlib import Path

from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils import TransactionParameters
from algokit_utils.beta.composer import AssetTransferParams, PayParams
from algosdk.atomic_transaction_composer import TransactionSigner, TransactionWithSigner

from utils_misc import create_and_fund_account
from ActionInputs import ActionInputs

sys.path.append(str(Path(*Path(__file__).parent.parts[:-1])))
from src.StressTestingClient import StressTestingClient, KeyRegTxnInfo


ALGO_ASA_ID = 0


def create_pay_fee_txn(
    algorand_client: AlgorandClient,
    asset_id: int,
    amount: int,
    sender: str,
    signer: TransactionSigner,
    receiver: str,
    extra_fee: int = 0,
) -> TransactionWithSigner:
    if asset_id == ALGO_ASA_ID:
        txn = TransactionWithSigner(
            algorand_client.transactions.payment(
                PayParams(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    extra_fee=extra_fee,
                )
            ),
            signer=signer,
        )
    else:
        txn = TransactionWithSigner(
            algorand_client.transactions.asset_transfer(
                AssetTransferParams(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    extra_fee=extra_fee,
                    asset_id=asset_id,
                )
            ),
            signer=signer,
        )

    return txn


def set_up_cert_board():
    pass


def create_stress_test(algorand_client, creator, action_inputs):
    stress_testing_client = StressTestingClient(
        algorand_client.client.algod,
        creator=creator.address,
        signer=creator.signer,
        indexer_client=algorand_client.client.indexer,
    )
    sp = algorand_client.client.algod.suggested_params()
    res = stress_testing_client.create_create(
        user_address=action_inputs.user_address,
        owner_address=action_inputs.owner_address,
        stake=action_inputs.stake,
        duration=action_inputs.duration,
        duration_max=action_inputs.duration_max,
        transaction_parameters=TransactionParameters(
            sender=creator.address,
            signer=creator.signer,
            suggested_params=sp,
        ),
    )
    sp = algorand_client.client.algod.suggested_params()
    res = stress_testing_client.create_create(
        user_address=action_inputs.user_address,
        owner_address=action_inputs.owner_address,
        stake=action_inputs.stake,
        duration=action_inputs.duration,
        duration_max=action_inputs.duration_max,
        transaction_parameters=TransactionParameters(
            sender=creator.address,
            signer=creator.signer,
            suggested_params=sp,
        ),
    )
    return stress_testing_client


def start_stress_test(algorand_client, creator, action_inputs, stress_testing_client):
    # Increase fee for inner key reg txn
    sp = algorand_client.client.algod.suggested_params()
    sp.fee = 2 * sp.min_fee
    sp.flat_fee = True
    receiver = (
        action_inputs.receiver
        if action_inputs.receiver is not None
        else stress_testing_client.app_address
    )
    gs = stress_testing_client.get_global_state()
    user_address = (
        action_inputs.user_address
        if action_inputs.user_address is not None
        else gs.user_address
    )
    calc_amt = gs.stake + 0  # REWARDS_OPT_IN_FEE
    amount = (
        action_inputs.amount if action_inputs.amount is not None else calc_amt
    )
    vote_first = (
        action_inputs.key_reg_vote_first
        if action_inputs.key_reg_vote_first is not None
        else gs.round_created
    )
    vote_last = (
        action_inputs.key_reg_vote_last
        if action_inputs.key_reg_vote_last is not None
        else gs.round_end_max
    )
    key_sender = (
        action_inputs.key_reg_sender
        if action_inputs.key_reg_sender is not None
        else stress_testing_client.app_address
    )
    # Transfer amount
    pay_fee_txn = create_pay_fee_txn(
        algorand_client=algorand_client,
        asset_id=ALGO_ASA_ID,
        amount=amount,
        sender=creator.address,
        signer=creator.signer,
        receiver=receiver,
    )
    res = stress_testing_client.start(
        user_address=ActionInputs.user_address,
        key_reg_info=KeyRegTxnInfo(
            vote_first=vote_first,
            vote_last=vote_last,
            vote_key_dilution=action_inputs.key_reg_vote_key_dilution,
            vote_pk=base64.b64decode(action_inputs.key_reg_vote),
            selection_pk=base64.b64decode(action_inputs.key_reg_selection),
            state_proof_pk=base64.b64decode(action_inputs.key_reg_state_proof),
            sender=key_sender,
        ),
        txn=pay_fee_txn,
        transaction_parameters=TransactionParameters(
            sender=creator.address,
            signer=creator.signer,
            suggested_params=sp,
        ),
    )
    return stress_testing_client


if __name__ == '__main__':

    algorand_client = AlgorandClient.default_local_net()
    algorand_client.set_suggested_params_timeout(0)
    creator = create_and_fund_account(algorand_client)

    stress_testing_client = create_stress_test(algorand_client, creator, ActionInputs)
    stress_testing_client = start_stress_test(algorand_client, creator, ActionInputs, stress_testing_client)
