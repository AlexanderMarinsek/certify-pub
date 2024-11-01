import typing as t

from algopy import (
    arc4,
)

# ------- Definition of types -------
CertInfo: t.TypeAlias = arc4.StaticArray[arc4.Byte, t.Literal[1024]]
"""
CertInfo: t.TypeAlias = arc4.StaticArray[arc4.Byte, t.Literal[1024]]
    Certificate contents to publish.
    For simplicity, only info is limited to 1024 B to be able to fit in one log call.
"""

SelPk: t.TypeAlias = arc4.StaticArray[arc4.Byte, t.Literal[32]]
"""
SelPk : arc4.StaticArray[arc4.Byte, t.Literal[32]]
    Selection public key of a participation key.
"""

VotePk: t.TypeAlias = arc4.StaticArray[arc4.Byte, t.Literal[32]]
"""
VotePk : arc4.StaticArray[arc4.Byte, t.Literal[32]]
    Vote public key of a participation key.
"""

StateProofPk: t.TypeAlias = arc4.StaticArray[arc4.Byte, t.Literal[64]]
"""
StateProofPk : arc4.StaticArray[arc4.Byte, t.Literal[64]]
    State proof public key of a participation key.
"""


# ------- Definition of structs -------
class KeyRegTxnInfo(arc4.Struct):
    """
    All relevant parameters of a key registration transaction.

    Fields
    ------
    vote_first : arc4.UInt64
        First round of validity of a participation key.
    vote_last : arc4.UInt64
        Last round of validity of a participation key.
    vote_key_dilution : arc4.UInt64
        Vote key dilution parameter of a participation key.
    vote_pk : VotePk
        Vote public key of a participation key.
    selection_pk : SelPk
        Selection public key of a participation key.
    state_proof_pk : StateProofPk
        State proof public key of a participation key.
    sender : arc4.Address
        Sender of the key registration transaction.
    """

    vote_first: arc4.UInt64
    vote_last: arc4.UInt64
    vote_key_dilution: arc4.UInt64
    vote_pk: VotePk
    selection_pk: SelPk
    state_proof_pk: StateProofPk
    sender: arc4.Address


class ReturnStressTestingEnd(arc4.Struct):
    """
    Information returned by `end` method of StressTesting contract.

    Fields
    ------
    success : arc4.Bool
        Whether the stress testing finished successfully (True) or prematurely (False).
    avr_online_stake : arc4.UInt64
        Average online stake during the test duration.
    cnt_produced_block : arc4.UInt64
        Number of produced blocks during the test duration.
    round_start : arc4.UInt64
        Start round number of participation in consensus for the test.
    round_end : arc4.UInt64
        End round number of the test.
    round_ended : arc4.UInt64
        Actual round number when the test ended.
    stake : arc4.UInt64
        Stake amount used during the test.
    user_address : arc4.Address
        Account of user that requested the test.
    """

    success: arc4.Bool
    avr_online_stake: arc4.UInt64
    cnt_produced_block: arc4.UInt64
    round_start: arc4.UInt64
    round_end: arc4.UInt64
    round_ended: arc4.UInt64
    stake: arc4.UInt64
    user_address: arc4.Address


class StressTestInfo(arc4.Struct):
    """
    Information recorded in successful stress test certificate for user.

    Fields
    ------
    avr_online_stake : arc4.UInt64
        Average online stake during the test duration.
    cnt_produced_block : arc4.UInt64
        Number of produced blocks during the test duration.
    round_start : arc4.UInt64
        Start round number of participation in consensus for the test.
    round_end : arc4.UInt64
        End round number of the test.
    stake : arc4.UInt64
        Stake amount used during the test.
    """

    avr_online_stake: arc4.UInt64
    cnt_produced_block: arc4.UInt64
    round_start: arc4.UInt64
    round_end: arc4.UInt64
    stake: arc4.UInt64


class StressTest(arc4.Struct):
    user: arc4.Address
    id: arc4.UInt64
