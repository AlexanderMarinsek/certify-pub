# pyright: reportMissingModuleSource=false
from algopy import (
    ARC4Contract,
    Bytes,
    Global,
    Txn,
    UInt64,
    arc4,
    gtxn,
    itxn,
)

from ..common import KeyRegTxnInfo, ReturnStressTestingEnd
from ..constants import CONSENSUS_STAKE_ROUND_DELAY
from .constants import (
    ERROR_ACCOUNT_CANNOT_TERMINATE_TEST,
    ERROR_AMOUNT,
    ERROR_BLOCKS_AFTER_END_DONT_COUNT,
    ERROR_CALLED_BY_NOT_CREATOR,
    ERROR_DURATION_WILL_NOT_WORK,
    ERROR_INCORRECT_DURATION,
    ERROR_INCORRECT_USER,
    ERROR_NOT_STATE_CREATED,
    ERROR_NOT_STATE_LIVE,
    ERROR_NOTHING_TO_RECORD,
    ERROR_RECEIVER,
    ERROR_TEST_CAN_FINISH_IN_TIME,
    ERROR_TEST_NOT_SOON_ENOUGH,
    STATE_CREATED,
    STATE_LIVE,
    STATE_NONE,
)


class StressTesting(ARC4Contract):
    """
    Escrow to be put online for the stress test by the user.
    It allows counting of produced blocks.

    Global state
    ------------

    user_address : arc4.Address
        Account of user that requested the test.
    owner_address : arc4.Address
        Account of owner of the funds used in the stress test.

    stake : UInt64
        Amount of stake used in the stress test.
        The value is expressed in microALGO.

    duration : UInt64
        Number of rounds for the stress test.
        The actual duration of the block recording is 320 rounds shorter due to consensus trailing.
    duration_max : UInt64
        Maximum number of rounds allocated for the test, i.e. blocking of funds.
        This is to take into account key generation time after the stress testing contract has been created.
    round_created : UInt64
        Round number when the request for the stress test is created.
    round_start : UInt64
        Round number when the actual participation in consensus starts.
    round_end : UInt64
        Round number when test should end.
    round_ended : UInt64
        Round number at which the contract ended.
        Can be smaller than round_end in case of early test termination.
    round_end_max : UInt64
        Round number by which the stress test will be completed at the latest.

    last_block : UInt64
        Last block number that this contract account produced.
    cnt_produced_blocks : UInt64
        Counter of produced blocks.

    total_stake_sum : UInt64
        Sum for calculating the average of total online stake during the test.
    cnt_total_stake_sum : UInt64
        Counter for calculating the average of total online stake during the test.

    state : Bytes
        State of the contract. Can be one of the following:
            CREATED - contract has been created.
            LIVE - contract is live.

    Methods
    -------
    create(
        user_address: arc4.Address,
        owner_address: arc4.Address,
        stake: UInt64,
        duration: UInt64,
        round_end_max: UInt64,
    ) -> arc4.UInt64:
        Creates a new contract for stress testing.

    start(
        user_address: arc4.Address,
        key_reg_info: KeyRegTxnInfo,
        txn: gtxn.PaymentTransaction,
    ) -> None:
        Starts the stress test.

    end(
        user_address: arc4.Address,
    ) -> ReturnStressTestingEnd:
        Ends the stress test.

    record(
    ) -> None:
        Records a produced block during the stress test.

    unused(
    ) -> None:
        Records a produced block during the stress test.


    """

    def __init__(self) -> None:
        """
        Define smart contract's global storage.
        """

        self.user_address = Global.zero_address
        self.owner_address = Global.zero_address

        self.stake = UInt64(0)

        self.duration = UInt64(0)
        self.duration_max = UInt64(0)
        self.round_created = UInt64(0)
        self.round_start = UInt64(0)
        self.round_end = UInt64(0)
        self.round_ended = UInt64(0)
        self.round_end_max = UInt64(0)

        self.last_block = UInt64(0)
        self.cnt_produced_blocks = UInt64(0)

        self.total_stake_sum = UInt64(0)
        self.cnt_total_stake_sum = UInt64(1)

        self.state = Bytes(STATE_NONE)

    @arc4.abimethod(create="require")
    def create(
        self,
        user_address: arc4.Address,
        owner_address: arc4.Address,
        stake: UInt64,
        duration: UInt64,
        duration_max: UInt64,
    ) -> arc4.UInt64:
        """
        Creates a new contract for stress testing.

        Parameters
        ----------
        user_address : arc4.Address
            Account of user that requested the test.
        owner_address : arc4.Address
            Account of owner of the funds used in the stress test.
        stake : UInt64
            Amount of stake used in the stress test.
            The value is expressed in microALGO.
        duration : UInt64
            Number of rounds for the stress test.
            The actual duration of the block recording is 320 rounds shorter due to consensus trailing.
        duration_max : UInt64
            Maximum number of rounds allocated for the test, i.e. blocking of funds.
            This is to take into account key generation time after the stress testing contract has been created.

        Returns
        -------
        app_id : Application
            App ID of the created application.
        """

        self.user_address = user_address.native
        self.owner_address = owner_address.native
        self.stake = stake
        self.duration = duration
        self.duration_max = duration_max

        self.round_ended = UInt64(100000000)
        self.cnt_produced_blocks = UInt64(0)
        # self.total_stake_sum = Global.online_stake
        self.total_stake_sum = UInt64(42000042)
        self.cnt_total_stake_sum = UInt64(1)

        self.state = Bytes(STATE_CREATED)

        self.round_created = Global.round
        self.round_end_max = self.round_created + self.duration_max

        assert self.duration < self.duration_max, ERROR_INCORRECT_DURATION
        assert self.duration > UInt64(
            CONSENSUS_STAKE_ROUND_DELAY
        ), ERROR_DURATION_WILL_NOT_WORK

        return arc4.UInt64(Global.current_application_id.id)

    @arc4.abimethod()
    def start(
        self,
        user_address: arc4.Address,
        key_reg_info: KeyRegTxnInfo,
        txn: gtxn.PaymentTransaction,
    ) -> None:
        """
        Starts the stress test.

        Parameters
        ----------
        user_address : arc4.Address
            Account of user that requested the test.
        key_reg_info : KeyRegTxnInfo
            Key registration information to use.
        txn : gtxn.PaymentTransaction
            Payment transaction for transfer of the requested stake and for covering
            the fee for reward registration.
        """

        assert Txn.sender == Global.creator_address, ERROR_CALLED_BY_NOT_CREATOR
        assert self.state == Bytes(STATE_CREATED), ERROR_NOT_STATE_CREATED
        assert self.user_address == user_address.native, ERROR_INCORRECT_USER

        self.round_end = Global.round + self.duration

        assert self.round_end < self.round_end_max, ERROR_TEST_NOT_SOON_ENOUGH

        assert txn.receiver == Global.current_application_address, ERROR_RECEIVER
        amt = self.stake + UInt64(0)  # TO DO : + Global.fee_reg_rewards
        assert txn.amount == amt, ERROR_AMOUNT

        self.round_start = Global.round + UInt64(CONSENSUS_STAKE_ROUND_DELAY)
        self.last_block = self.round_start

        # Check participation keys info
        assert key_reg_info.vote_first.native == self.round_created
        assert key_reg_info.vote_last.native == self.round_end_max
        assert key_reg_info.sender.native == Global.current_application_address

        # Send part key txn
        itxn.KeyRegistration(
            vote_key=key_reg_info.vote_pk.bytes,
            selection_key=key_reg_info.selection_pk.bytes,
            vote_first=key_reg_info.vote_first.native,
            vote_last=key_reg_info.vote_last.native,
            vote_key_dilution=key_reg_info.vote_key_dilution.native,
            state_proof_key=key_reg_info.state_proof_pk.bytes,
            sender=key_reg_info.sender.native,
            fee=0,  # TO DO : Global.fee_reg_rewards,
        ).submit()

        self.state = Bytes(STATE_LIVE)

        return

    @arc4.abimethod(allow_actions=["DeleteApplication"])
    def end(
        self,
        user_address: arc4.Address,
    ) -> ReturnStressTestingEnd:
        """
        Ends the stress test.

        Parameters
        ----------
        user_address : arc4.Address
            Account that requested the test to end.
        """

        assert Txn.sender == Global.creator_address, ERROR_CALLED_BY_NOT_CREATOR
        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        self.round_ended = Global.round

        success = False
        if user_address.native == self.owner_address:
            if self.round_ended < self.round_end:
                success = False
            else:
                success = True
        else:
            if self.round_ended < self.round_end:
                success = False
                assert False, ERROR_ACCOUNT_CANNOT_TERMINATE_TEST  # noqa: B011
            else:
                success = True

        # Closes account to creator
        itxn.Payment(
            receiver=Global.creator_address,
            amount=0,
            close_remainder_to=Global.creator_address,
        ).submit()

        # TO DO : change sum_total_stake to wide to prevent overflows (for large stake tests)
        avr_online_stake = self.total_stake_sum // self.cnt_total_stake_sum

        return ReturnStressTestingEnd(
            success=arc4.Bool(success),
            avr_online_stake=arc4.UInt64(avr_online_stake),
            cnt_produced_block=arc4.UInt64(self.cnt_produced_blocks),
            round_start=arc4.UInt64(self.round_start),
            round_end=arc4.UInt64(self.round_end),
            round_ended=arc4.UInt64(self.round_ended),
            stake=arc4.UInt64(self.stake),
            user_address=arc4.Address(self.user_address),
        )

    @arc4.abimethod()
    def record(
        self,
    ) -> None:
        """
        Records a produced block during the stress test.
        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE
        assert Global.round < self.round_ended  # Not reachable

        # TO DO : Global.current_application_address.last_block_produced
        last_block = Global.round

        assert last_block < self.round_end, ERROR_BLOCKS_AFTER_END_DONT_COUNT
        if self.last_block < last_block:
            self.cnt_produced_blocks += UInt64(1)
            self.last_block = last_block
            # self.total_stake_sum = Global.online_stake
            self.total_stake_sum += UInt64(42000042)
            self.cnt_total_stake_sum += UInt64(1)
        else:
            assert False, ERROR_NOTHING_TO_RECORD  # noqa: B011

        return

    @arc4.abimethod(allow_actions=["DeleteApplication"])
    def unused(
        self,
    ) -> arc4.UInt64:
        """
        Records a produced block during the stress test.
        """

        assert Txn.sender == Global.creator_address, ERROR_CALLED_BY_NOT_CREATOR
        assert self.state == Bytes(STATE_CREATED), ERROR_NOT_STATE_CREATED

        assert (
            Global.round + self.duration > self.round_end_max
        ), ERROR_TEST_CAN_FINISH_IN_TIME

        # Closes account to creator
        itxn.Payment(
            receiver=Global.creator_address,
            amount=0,
            close_remainder_to=Global.creator_address,
        ).submit()

        return arc4.UInt64(self.stake)
