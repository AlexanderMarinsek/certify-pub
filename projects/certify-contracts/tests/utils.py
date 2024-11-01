import base64
import time

from algokit_utils import (
    LogicError,
    is_localnet,
)
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils.beta.composer import AssetTransferParams, PayParams
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionSigner,
    TransactionWithSigner,
)
from algosdk.error import AlgodHTTPError
from pytest import ExceptionInfo

from smart_contracts.constants import ALGO_ASA_ID


# ------- Functions -------
def wait_for_rounds(
    algorand_client: AlgorandClient,
    num_rounds: int,
    acc: AddressAndSigner | None = None,
) -> None:
    """
    Waits for rounds to pass.
    If on localnet, this is done by sending individual zero payment transactions.
    If on other networks, wait for more rounds to pass.

    Parameters
    ----------
    algorand_client: AlgorandClient
        Algorand client for the network connection.
    acc : AddressAndSigner
        Account with signer that is sending transactions.
    num_rounds : int
        Number of rounds to progress.

    """

    if is_localnet(algorand_client.client.algod):
        if acc is None:
            raise Exception("For progressing rounds on localnet an account is needed.")
        for _ in range(num_rounds):
            # Send the transaction
            txn = TransactionWithSigner(
                algorand_client.transactions.payment(
                    PayParams(
                        sender=acc.address,
                        receiver=acc.address,
                        amount=0,
                        extra_fee=0,
                    )
                ),
                signer=acc.signer,
            )

            atc = AtomicTransactionComposer()
            atc.add_transaction(txn)

            res = atc.execute(algorand_client.client.algod, 0)  # noqa: F841
            # print(f"Transaction sent with txID: {res.tx_ids}")
    else:
        status = algorand_client.client.algod.status()
        current_round = status["last-round"]
        while (
            current_round + num_rounds
            > algorand_client.client.algod.status()["last-round"]
        ):
            time.sleep(3)

    return


def is_expected_logic_error(
    error_code: str,
    e: ExceptionInfo[LogicError],
) -> bool:
    return "assert // " + error_code + "\t\t<-- Error" in str(e.value)


def is_expected_https_error(
    error_code: str,
    e: ExceptionInfo[LogicError],
) -> bool:
    return error_code in str(e.value)


def is_opted_in(
    algorand_client: AlgorandClient,
    address: str,
    asset_id: int,
) -> bool | None:
    if asset_id != ALGO_ASA_ID:
        opted_in = (
            True if balance(algorand_client, address, asset_id) is not None else None
        )
    else:
        opted_in = None

    return opted_in


def is_online(
    algorand_client: AlgorandClient,
    address: str,
) -> bool:
    online = (
        algorand_client.client.algod.account_info(
            address=address,
        )["status"]
        == "Online"
    )

    return online


def balance(
    algorand_client: AlgorandClient,
    address: str,
    asset_id: int,
) -> int | None:
    try:
        if asset_id != ALGO_ASA_ID:
            bal = algorand_client.client.algod.account_asset_info(
                address=address,
                asset_id=asset_id,
            )["asset-holding"]["amount"]
        else:
            bal = algorand_client.client.algod.account_info(
                address=address,
            )["amount"]
    except Exception as e:
        print(e)
        bal = None

    return bal


def available_balance(
    algorand_client: AlgorandClient,
    address: str,
    asset_id: int,
) -> int:
    if asset_id == ALGO_ASA_ID:
        bal = balance(algorand_client, address, asset_id)
        mbr = get_mbr(algorand_client, address)
        bal -= mbr
    else:
        frozen = is_frozen(algorand_client, address, asset_id)
        if frozen:
            bal = 0
        else:
            bal = balance(algorand_client, address, asset_id)

    return bal


def get_box(
    algorand_client: AlgorandClient,
    box_name: bytes,
    app_id: int,
) -> tuple[bytes, bool]:

    exists = False
    box_raw = b""

    try:
        box_raw = algorand_client.client.algod.application_box_by_name(
            application_id=app_id,
            box_name=box_name,
        )
        box_raw = base64.b64decode(box_raw["value"])
        exists = True
    except AlgodHTTPError:
        pass
    except Exception as e:
        print(e)

    return [box_raw, exists]


def get_mbr(
    algorand_client: AlgorandClient,
    address: str,
) -> int:
    try:
        mbr = algorand_client.client.algod.account_info(
            address=address,
        )["min-balance"]
    except Exception as e:
        print(e)
        mbr = None

    return mbr


def is_frozen(
    algorand_client: AlgorandClient,
    address: str,
    asset_id: int,
) -> bool | None:
    try:
        if asset_id != ALGO_ASA_ID:
            frozen = algorand_client.client.algod.account_asset_info(
                address=address,
                asset_id=asset_id,
            )["asset-holding"]["is-frozen"]
        else:
            frozen = False
    except Exception as e:
        print(e)
        frozen = None

    return frozen


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
