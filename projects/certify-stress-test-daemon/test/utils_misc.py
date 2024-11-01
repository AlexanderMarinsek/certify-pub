"""Different helper / abstraction functions.
"""
import time
from typing import List

from algokit_utils.beta.composer import PayParams
from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils import is_localnet
from algosdk.atomic_transaction_composer import AtomicTransactionComposer, TransactionWithSigner


def send_payment(
    algorand_client: AlgorandClient, 
    sender_address: str, 
    receiver_address: str, 
    amount: int
) -> None:
    """Send a payment. 

    Args:
        sender (str): Sender address.
        receiver (str): Receiver address.
        amount (int): Amount.
    """
    algorand_client.send.payment(
        PayParams(
            sender=sender_address,
            receiver=receiver_address,
            amount=amount,
        )
    )


def create_account(
    algorand_client: AlgorandClient, 
) -> AddressAndSigner:
    """Makae a new random account and fund it.

    Args:
        algorand_client (AlgorandClient): Algorand client.

    Returns:
        AddressAndSigner: New account.
    """
    account = algorand_client.account.random()
    return account


def create_and_fund_account(
    algorand_client: AlgorandClient, 
    amount: int=40_000_000
) -> AddressAndSigner:
    """Makae a new random account and fund it.

    Args:
        algorand_client (AlgorandClient): Algorand client.

    Returns:
        AddressAndSigner: New funded account.
    """
    account = create_account(algorand_client)
    send_payment(
        algorand_client=algorand_client,
        sender_address=algorand_client.account.dispenser().address,
        receiver_address=account.address,
        amount=amount,
    )
    return account


def create_funded_account_list(
    algorand_client: AlgorandClient,
    num_of_accounts: list
) -> List[AddressAndSigner]:
    """Create a number of funded accounts.

    Args:
        algorand_client (AlgorandClient): Algorand client.
        num_of_accounts (list): Number of accounts to create.

    Returns:
        List[AddressAndSigner]: Funded accounts.
    """
    accs = []
    for i in range(num_of_accounts):
        acc = create_and_fund_account(algorand_client)
        accs.append(acc)
    return accs


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


if __name__ == '__main__':

    algorand_client = AlgorandClient.default_local_net()
    algorand_client.set_suggested_params_timeout(0)

    account = create_and_fund_account(algorand_client)
    print(account)
    from algosdk import mnemonic
    print(mnemonic.from_private_key(account.signer.private_key))

    # send_payment(
    #     algorand_client=algorand_client,
    #     sender_address=algorand_client.account.dispenser().address,
    #     receiver_address='WPONCVMVICV4DQHTE53O2BNQTWM5L57K55H3ZYRQSLHRIUOEJXNV2LW3ZQ',
    #     amount=100_000_000_000,
    # )
