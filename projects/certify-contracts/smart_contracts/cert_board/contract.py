from algopy import (
    Account,
    Application,
    ARC4Contract,
    Asset,
    Box,
    BoxMap,
    Bytes,
    Global,
    TransactionType,
    Txn,
    UInt64,
    arc4,
    gtxn,
    itxn,
    op,
    subroutine,
)

from ..common import (
    CertInfo,
    KeyRegTxnInfo,
    StressTest,
    StressTestInfo,
)
from ..constants import ALGO_ASA_ID
from ..stress_testing.contract import StressTesting
from .constants import (
    ERROR_AMOUNT,
    ERROR_AMOUNT_ASA_OPTIN_MBR,
    ERROR_ASSET_ID,
    ERROR_CALLED_BY_NOT_PLA_MANAGER,
    ERROR_CALLED_BY_NOT_PLA_MANAGER_OR_CREATOR,
    ERROR_MAX_DURATION_LARGER_THAN_MAX_BLOCKED,
    ERROR_MAX_STAKE_SMALLER_THAN_MIN,
    ERROR_NOT_ENOUGH_ALGO_TO_WITHDRAW,
    ERROR_NOT_OPTED_INTO_ASSET,
    ERROR_NOT_PAYMENT_OR_XFER,
    ERROR_NOT_STATE_LIVE,
    ERROR_RECEIVER,
    ERROR_REQUESTED_STAKE_TOO_LARGE,
    ERROR_REQUESTED_STAKE_TOO_SMALL,
    ERROR_STRESS_TEST_FINISHED,
    ERROR_UNKNOWN_STRESS_TEST,
    STATE_DEPLOYED,
    STATE_LIVE,
    STATE_NONE,
)


class CertBoard(ARC4Contract):
    """
    Certification Board servers as decentralized registrar for certificates to build trust in
    the node running capabilities of an entity.
    It supports issuing of attestations according to applicable node running standards by any entity.
    Moreover, it supports generation of on-chain produced proofs of an entity's node running
    capabilities through self-initiated stress tests, which get recorded as another certificate type.

    Global state
    ------------

    pla_manager : Account
        Platform manager account.

    expected_consensus_rate : UInt64
        Expected consensus reward rate.
        Expressed as percentage per year.

    certificate_fee : UInt64
        Fee charged by the platform for issuing of a certificate by anyone.
        Note: MBR increase is paid separately.
    stress_test_fee_round : UInt64
        Amount charged per round of the stress test.
    payment_asset : UInt64
        Payment method for the stress test and certificate fee.

    max_test_duration : UInt64
        Maximum allowed duration for a stress test.
    max_test_blocking : UInt64
        Maximum amount of rounds allowed to reserve for a stress test.

    stake_min : UInt64
        Minimum stake allowed to be used for a stress test.
    stake_max : UInt64
        Maximum stake allowed to be used for a stress test.

    blocked_algo: UInt64
        Amount of ALGO currently blocked and awaiting to be used in started stress test(s) requests.

    state : Bytes
        State of the contract. Can be one of the following:
            DEPLOYED - CertBoard has been created.
            LIVE - CertBoard is live.

    Methods
    -------
    cert_board_deploy(
    ) -> arc4.UInt64:
        Creates a new CertBoard.

    cert_board_key_reg(
        key_reg_info: KeyRegTxnInfo,
        txn: gtxn.PaymentTransaction,
    ) -> None:
        Issues a key (de)registration transaction by the platform.

    cert_board_set(
        pla_manager: arc4.Address,
        expected_consensus_rate: UInt64,
        certificate_fee: UInt64,
        stress_test_fee_round: UInt64,
        payment_asset: UInt64,
        max_test_duration: UInt64,
        max_test_blocking: UInt64,
        stake_min: UInt64,
        stake_max: UInt64,
    ) -> None:
        Sets platform parameters (anew).

    cert_board_optin_asa(
        asa: Asset,
        sender: Account,
        txn: gtxn.PaymentTransaction,
    ) -> None:
        Opts the platform address in to an ASA.

    cert_board_withdraw(
        amount: UInt64,
        asset_id: UInt64,
    ) -> None:
        Platform owner withdraws amount of asset from the platform.

    cert_create(
        recipient: arc4.Address,
        info: CertInfo,
        mbr_txn: gtxn.PaymentTransaction,
        txn: gtxn.Transaction,
    ) -> None:
        An issuer creates a certificate stored on the platform.

    cert_get(
        recipient: arc4.Address,
        issuer: arc4.Address,
    ) -> CertInfo:
        Returns the certificate issued by issuer to the recipient.

    stress_create(
        stake: UInt64,
        duration: UInt64,
        round_end_max: UInt64,
        algo_txn: gtxn.PaymentTransaction,
        txn: gtxn.Transaction,
    ) -> arc4.UInt64:
        Creates a stress test.

    stress_end(
        user_address: arc4.Address,
        stress_test_id: UInt64,
    ) -> None:
        Ends a stress test.

    stress_get(
        recipient: arc4.Address,
        stress_test_id: UInt64,
    ) -> StressTestInfo:
        Gets information about a successfully finished stress test.

    stress_record(
        user_address: arc4.Address,
        stress_test_id: UInt64,
    ) -> None:
        Records a produced block of during the stress test.

    stress_start(
        stress_test_id: UInt64,
        key_reg_info: KeyRegTxnInfo,
    ) -> None:
        Starts a created test.

    stress_unused(
        user_address: arc4.Address,
        stress_test_id: UInt64,
    ) -> None:
        Ends a not used stress test.

    """

    def __init__(self) -> None:
        """
        Define smart contract's global and box storage.
        """

        self.pla_manager = Global.zero_address

        self.expected_consensus_rate = UInt64(0)

        self.certificate_fee = UInt64(0)
        self.stress_test_fee_round = UInt64(0)
        self.payment_asset = UInt64(0)

        self.max_test_duration = UInt64(0)
        self.max_test_blocking = UInt64(0)

        self.stake_min = UInt64(0)
        self.stake_max = UInt64(0)

        self.blocked_algo = UInt64(0)

        self.state = Bytes(STATE_NONE)

        self.stress_tests = BoxMap(StressTest, StressTestInfo, key_prefix=b"")

    @arc4.abimethod(create="require")
    def cert_board_deploy(
        self,
    ) -> arc4.UInt64:
        """
        Creates a new CertBoard.

        Returns
        -------
        app_id : arc4.UInt64
            App ID of the created application.
        """

        self.pla_manager = Global.creator_address

        # Change state to DEPLOYED
        self.state = Bytes(STATE_DEPLOYED)

        return arc4.UInt64(Global.current_application_id.id)

    @arc4.abimethod()
    def cert_board_key_reg(
        self,
        key_reg_info: KeyRegTxnInfo,
        txn: gtxn.PaymentTransaction,
    ) -> None:
        """
        Issues a key (de)registration transaction by the platform.

        Parameters
        ----------
        key_reg_info : KeyRegTxnInfo
            Key registration information to send.
        txn : gtxn.PaymentTransaction
            Payment transaction to cover costs for the key (de)registration fee.
        """

        assert Txn.sender == self.pla_manager, ERROR_CALLED_BY_NOT_PLA_MANAGER

        # Check if payment for covering the fee was made to this contract
        assert txn.receiver == Global.current_application_address, ERROR_RECEIVER
        key_reg_txn_fee = txn.amount

        # Issue the key registration transaction
        itxn.KeyRegistration(
            vote_key=key_reg_info.vote_pk.bytes,
            selection_key=key_reg_info.selection_pk.bytes,
            vote_first=key_reg_info.vote_first.native,
            vote_last=key_reg_info.vote_last.native,
            vote_key_dilution=key_reg_info.vote_key_dilution.native,
            state_proof_key=key_reg_info.state_proof_pk.bytes,
            sender=key_reg_info.sender.native,
            fee=key_reg_txn_fee,
        ).submit()

        return

    @arc4.abimethod()
    def cert_board_set(
        self,
        pla_manager: arc4.Address,
        expected_consensus_rate: UInt64,
        certificate_fee: UInt64,
        stress_test_fee_round: UInt64,
        payment_asset: UInt64,
        max_test_duration: UInt64,
        max_test_blocking: UInt64,
        stake_min: UInt64,
        stake_max: UInt64,
    ) -> None:
        """
        Sets platform parameters (anew).

        Parameters
        ----------
        pla_manager : Account
            Platform manager account.

        expected_consensus_rate : UInt64
            Expected consensus reward rate.
            Expressed as percentage per year.

        certificate_fee : UInt64
            Fee charged by the platform for issuing of a certificate by anyone.
            Note: MBR increase is paid separately.
        stress_test_fee_round : UInt64
            Amount charged per round of the stress test.
        payment_asset : UInt64
            Payment method for the stress test and certificate fee.

        max_test_duration : UInt64
            Maximum allowed duration for a stress test.
        max_test_blocking : UInt64
            Maximum amount of rounds allowed to reserve for a stress test.

        stake_min : UInt64
            Minimum stake allowed to be used for a stress test.
        stake_max : UInt64
            Maximum stake allowed to be used for a stress test.

        """

        assert (
            Txn.sender == self.pla_manager or Txn.sender == Global.creator_address
        ), ERROR_CALLED_BY_NOT_PLA_MANAGER_OR_CREATOR

        self.pla_manager = pla_manager.native

        self.expected_consensus_rate = expected_consensus_rate

        self.certificate_fee = certificate_fee
        self.stress_test_fee_round = stress_test_fee_round
        self.payment_asset = payment_asset

        self.max_test_duration = max_test_duration
        self.max_test_blocking = max_test_blocking

        self.stake_min = stake_min
        self.stake_max = stake_max

        # Sanity check on parameters
        assert self.stake_min < self.stake_max, ERROR_MAX_STAKE_SMALLER_THAN_MIN
        assert (
            self.max_test_duration < self.max_test_blocking
        ), ERROR_MAX_DURATION_LARGER_THAN_MAX_BLOCKED
        if payment_asset != UInt64(ALGO_ASA_ID):
            assert Global.current_application_address.is_opted_in(
                Asset(payment_asset)
            ), ERROR_NOT_OPTED_INTO_ASSET

        self.state = Bytes(STATE_LIVE)

        return

    @arc4.abimethod()
    def cert_board_optin_asa(
        self,
        asa: Asset,
        sender: Account,
        txn: gtxn.PaymentTransaction,
    ) -> None:
        """
        Opts the platform address in to an ASA.

        Parameters
        ----------
        asa : Asset
            Asset to opt into.
        sender : Account
            Account to opt into the asa.
        txn : gtxn.PaymentTransaction
            Payment transaction to cover MBR increase.
        """

        assert Txn.sender == self.pla_manager, ERROR_CALLED_BY_NOT_PLA_MANAGER

        # Check if payment for covering the MBR increase was made to this contract
        assert txn.receiver == Global.current_application_address, ERROR_RECEIVER
        assert txn.amount == Global.asset_opt_in_min_balance, ERROR_AMOUNT_ASA_OPTIN_MBR

        # Opt in to the asset
        itxn.AssetTransfer(
            sender=sender,
            xfer_asset=asa,
            asset_receiver=sender,
            asset_amount=0,
        ).submit()

        return

    @arc4.abimethod()
    def cert_board_withdraw(
        self,
        amount: UInt64,
        asset_id: UInt64,
    ) -> None:
        """
        Platform owner withdraws amount of asset from the platform.

        Parameters
        ----------
        amount : UInt64
            Amount to withdraw from the platform.
        asset_id : UInt64
            ID of the asset to withdraw, i.e. ASA ID or 0 for ALGO.
        """

        assert Txn.sender == self.pla_manager, ERROR_CALLED_BY_NOT_PLA_MANAGER

        if asset_id != UInt64(ALGO_ASA_ID):
            itxn.AssetTransfer(
                xfer_asset=asset_id,
                asset_receiver=self.pla_manager,
                asset_amount=amount,
            ).submit()
        else:
            available_balance = (
                Global.current_application_address.balance
                - Global.current_application_address.min_balance
                - self.blocked_algo
            )
            assert available_balance >= amount, ERROR_NOT_ENOUGH_ALGO_TO_WITHDRAW
            itxn.Payment(
                receiver=self.pla_manager,
                amount=amount,
            ).submit()

        return

    @arc4.abimethod()
    def cert_create(
        self,
        recipient: arc4.Address,
        info: CertInfo,
        mbr_txn: gtxn.PaymentTransaction,
        txn: gtxn.Transaction,
    ) -> None:
        """
        An issuer creates a certificate stored on the platform.

        Parameters
        ----------
        recipient: arc4.Address
            Recipient of the certificate.
        info : CertInfo
            Information to be recorded in the certificate.
        mbr_txn : gtxn.PaymentTransaction
            Payment transaction for the payment of the increase of platform MBR due to creation of the certificate.
        txn : gtxn.Transaction
            Transaction for the payment of the certificate issuance fee.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        mbr_cur = Global.current_application_address.min_balance

        box_name = recipient.native.bytes + Txn.sender.bytes

        certificate = Box(CertInfo, key=box_name)
        certificate.value = info.copy()

        # Check if the input MBR payment transaction was sufficient for increase the MBR
        mbr_new = Global.current_application_address.min_balance
        amt = mbr_new - mbr_cur
        assert mbr_txn.receiver == Global.current_application_address, ERROR_RECEIVER
        assert mbr_txn.amount == amt, ERROR_AMOUNT

        # Check payment for certificate issuance
        if txn.type == TransactionType.Payment:
            assert self.payment_asset == UInt64(ALGO_ASA_ID), ERROR_ASSET_ID
            assert txn.receiver == Global.current_application_address, ERROR_RECEIVER
            assert txn.amount == self.certificate_fee, ERROR_AMOUNT
        elif txn.type == TransactionType.AssetTransfer:
            assert self.payment_asset == txn.xfer_asset.id, ERROR_ASSET_ID
            assert (
                txn.asset_receiver == Global.current_application_address
            ), ERROR_RECEIVER
            assert txn.asset_amount == self.certificate_fee, ERROR_AMOUNT
        else:
            assert False, ERROR_NOT_PAYMENT_OR_XFER  # noqa: B011

        return

    @arc4.abimethod(readonly=True)
    def cert_get(
        self,
        recipient: arc4.Address,
        issuer: arc4.Address,
    ) -> CertInfo:
        """
        Returns the certificate issued by issuer to the recipient.

        Parameters
        ----------
        recipient: arc4.Address
            Recipient of the certificate.
        issuer: arc4.Address
            Issuer of the certificate.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        box_name = recipient.native.bytes + issuer.native.bytes

        certificate = Box(CertInfo, key=box_name)

        return certificate.value

    @arc4.abimethod()
    def stress_create(
        self,
        stake: UInt64,
        duration: UInt64,
        duration_max: UInt64,
        algo_txn: gtxn.PaymentTransaction,
        txn: gtxn.Transaction,
    ) -> arc4.UInt64:
        """
        Creates a stress test.

        Parameters
        ----------
        stake : UInt64
            Amount of stake used in the stress test.
            The value is expressed in microALGO.
        duration : UInt64
            Number of rounds for the stress test.
            The actual duration of the block recording is 320 rounds shorter due to consensus trailing.
        duration_max : UInt64
            Maximum number of rounds allocated for the test, i.e. blocking of funds.
            This is to take into account key generation time after the stress testing contract has been created.
        algo_txn : gtxn.PaymentTransaction
            Payment transaction for the payment of:
            1) the increase of platform MBR due to creation of the stress test,
            2) the fee for making the stress test contract opt-in to rewards with later key reg, and
            3) the fee charged for the potential loss of platforms consensus rewards due to the stress test.
        txn : gtxn.Transaction
            Transaction for the payment of the stress test fee.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        assert self.stake_max > stake, ERROR_REQUESTED_STAKE_TOO_LARGE
        assert self.stake_min < stake, ERROR_REQUESTED_STAKE_TOO_SMALL

        mbr_cur = Global.current_application_address.min_balance

        user_address = arc4.Address(Txn.sender)
        create_result, txn_create = arc4.arc4_create(
            StressTesting.create,
            user_address,
            arc4.Address(self.pla_manager),
            stake,
            duration,
            duration_max,
        )

        service_fee = duration_max * self.stress_test_fee_round

        # Check payment for the stress test
        if txn.type == TransactionType.Payment:
            assert self.payment_asset == UInt64(ALGO_ASA_ID), ERROR_ASSET_ID
            assert txn.receiver == Global.current_application_address, ERROR_RECEIVER
            assert txn.amount == service_fee, ERROR_AMOUNT
        elif txn.type == TransactionType.AssetTransfer:
            assert self.payment_asset == txn.xfer_asset.id, ERROR_ASSET_ID
            assert (
                txn.asset_receiver == Global.current_application_address
            ), ERROR_RECEIVER
            assert txn.asset_amount == service_fee, ERROR_AMOUNT
        else:
            assert False, ERROR_NOT_PAYMENT_OR_XFER  # noqa: B011

        # Check if the input ALGO payment transaction was sufficient for increase of the MBR,
        # payment of online registration transaction fee, and potential loss of rewards
        potential_loss = self.expected_consensus_rate * stake * duration_max
        mbr_new = Global.current_application_address.min_balance
        amt = potential_loss + (mbr_new - mbr_cur)  # + Global.fee_reg_rewards
        assert algo_txn.receiver == Global.current_application_address, ERROR_RECEIVER
        assert algo_txn.amount == amt, ERROR_AMOUNT

        # Check if there is enough stake to reserve for the test
        assert (
            self.blocked_algo
            < Global.current_application_address.balance
            - Global.current_application_address.min_balance
        )
        self.blocked_algo += stake + potential_loss  # + Global.fee_reg_rewards

        return create_result

    @arc4.abimethod()
    def stress_end(
        self,
        user_address: arc4.Address,
        stress_test_id: UInt64,
    ) -> None:
        """
        Ends a stress test.

        Parameters
        ----------
        user_address : UInt64
            Address of the user that initiated the stress test.
        stress_test_id : UInt64
            App ID of the stress test to end.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        stress_test = StressTest(user_address, arc4.UInt64(stress_test_id))
        assert stress_test in self.stress_tests, ERROR_UNKNOWN_STRESS_TEST
        assert (
            self.stress_tests[stress_test] == _get_stress_test_info_init()
        ), ERROR_STRESS_TEST_FINISHED

        # bal_cur = Global.current_application_address.balance

        end_result, txn_app = arc4.abi_call(
            StressTesting.end,
            arc4.Address(Txn.sender),
            app_id=stress_test_id,
        )

        # # TO DO : Return the difference between generated and target rewards
        # bal_new = Global.current_application_address.balance
        # gen_rewards = bal_new - bal_cur

        self.blocked_algo -= end_result.stake.native

        if end_result.success:
            self.stress_tests[stress_test] = StressTestInfo(
                avr_online_stake=end_result.avr_online_stake,
                cnt_produced_block=end_result.cnt_produced_block,
                round_start=end_result.round_start,
                round_end=end_result.round_end,
                stake=end_result.stake,
            )
        else:
            assert op.Box.delete(stress_test.bytes)

        return

    @arc4.abimethod(readonly=True)
    def stress_get(
        self,
        recipient: arc4.Address,
        stress_test_id: UInt64,
    ) -> StressTestInfo:
        """
        Gets information about a successfully finished stress test.

        Parameters
        ----------
        recipient: arc4.Address
            Recipient of the certificate.
        stress_test_id : UInt64
            App ID of the stress test to end.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        stress_test = StressTest(recipient, arc4.UInt64(stress_test_id))
        stress_test_info = self.stress_tests[stress_test].copy()

        return stress_test_info.copy()

    @arc4.abimethod()
    def stress_record(
        self,
        user_address: arc4.Address,
        stress_test_id: UInt64,
    ) -> None:
        """
        Records a produced block of during the stress test.

        Parameters
        ----------
        user_address : UInt64
            Address of the user that initiated the stress test.
        stress_test_id : UInt64
            App ID of the stress test to end.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        stress_test = StressTest(user_address, arc4.UInt64(stress_test_id))
        assert stress_test in self.stress_tests, ERROR_UNKNOWN_STRESS_TEST
        assert (
            self.stress_tests[stress_test] == _get_stress_test_info_init()
        ), ERROR_STRESS_TEST_FINISHED

        arc4.abi_call(
            StressTesting.record,
            app_id=stress_test_id,
        )

        return

    @arc4.abimethod()
    def stress_start(
        self,
        stress_test_id: UInt64,
        key_reg_info: KeyRegTxnInfo,
        mbr_txn: gtxn.PaymentTransaction,
    ) -> None:
        """
        Starts a created test.

        Parameters
        ----------
        user_address : UInt64
            Address of the user that initiated the stress test.
        stress_test_id : UInt64
            App ID of the stress test to end.
        mbr_txn : gtxn.PaymentTransaction
            Payment transaction for the payment of the increase of platform MBR due to
            creation of the box to record the stress test.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        mbr_cur = Global.current_application_address.min_balance

        user_address = arc4.Address(Txn.sender)
        stress_test_app = Application(stress_test_id)

        user_address_get = op.AppGlobal.get_ex_bytes(stress_test_app, b"user_address")
        assert user_address_get[1]
        assert user_address_get[0] == user_address.native.bytes
        assert stress_test_app.creator == Global.current_application_address

        stress_test = StressTest(user_address, arc4.UInt64(stress_test_id))
        self.stress_tests[stress_test] = _get_stress_test_info_init()

        stake_get = op.AppGlobal.get_ex_uint64(stress_test_app, b"stake")
        assert stake_get[1]

        txn = itxn.Payment(
            receiver=stress_test_app.address,
            amount=stake_get[0],  # + Global.fee_reg_rewards
        )

        arc4.abi_call(
            StressTesting.start,
            user_address,
            key_reg_info.copy(),
            txn,
            app_id=stress_test_id,
        )
        # Check if the input ALGO payment transaction was sufficient for increase of the MBR
        # due to box creation
        mbr_new = Global.current_application_address.min_balance
        amt = mbr_new - mbr_cur
        assert mbr_txn.receiver == Global.current_application_address, ERROR_RECEIVER
        assert mbr_txn.amount == amt, ERROR_AMOUNT

        return

    @arc4.abimethod()
    def stress_unused(
        self,
        user_address: arc4.Address,
        stress_test_id: UInt64,
    ) -> None:
        """
        Ends a not used stress test.

        Parameters
        ----------
        user_address : UInt64
            Address of the user that initiated the stress test.
        stress_test_id : UInt64
            App ID of the stress test to end.

        """

        assert self.state == Bytes(STATE_LIVE), ERROR_NOT_STATE_LIVE

        user_address = arc4.Address(Txn.sender)
        stress_test_app = Application(stress_test_id)

        user_address_get = op.AppGlobal.get_ex_bytes(stress_test_app, b"user_address")
        assert user_address_get[1]
        assert user_address_get[0] == user_address.native.bytes
        assert stress_test_app.creator == Global.current_application_address

        res, txn_app = arc4.abi_call(
            StressTesting.unused,
            app_id=stress_test_id,
        )

        self.blocked_algo -= res.native

        return


@subroutine
def _get_stress_test_info_init() -> StressTestInfo:
    return StressTestInfo(
        avr_online_stake=arc4.UInt64(0),
        cnt_produced_block=arc4.UInt64(0),
        round_start=arc4.UInt64(0),
        round_end=arc4.UInt64(0),
        stake=arc4.UInt64(0),
    )
