import base64
from typing import Literal

from algokit_utils import ABITransactionResponse, TransactionParameters
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import AlgorandClient
from algokit_utils.beta.composer import PayParams
from algosdk.abi import AddressType
from algosdk.logic import get_application_address

import tests.cert_board.stress_testing_interface as st
from smart_contracts.artifacts.cert_board.cert_board_client import (
    CertBoardClient,
    KeyRegTxnInfo,
)
from smart_contracts.cert_board.constants import (
    STATE_DEPLOYED,
    STATE_LIVE,
)
from smart_contracts.constants import (
    ALGO_ASA_ID,
    MBR_ACCOUNT,
    MBR_ASA,
    MBR_CERT_BOX,
    MBR_STRESS_BOX,
    MBR_STRESS_TESTING_CONTRACT,
)
from tests.utils import (
    available_balance,
    balance,
    create_pay_fee_txn,
    get_box,
    is_online,
    is_opted_in,
)

from .client_helper import CertBoardGlobalState
from .config import ActionInputs

POSSIBLE_STATES = Literal[
    "START",
    "DEPLOYED",
    "LIVE",
]

POSSIBLE_ACTIONS = Literal[
    "cert_board_deploy",
    "cert_board_key_reg",
    "cert_board_set",
    "cert_board_optin_asa",
    "cert_board_withdraw",
    "cert_create",
    "cert_get",
    "stress_create",
    "stress_end",
    "stress_get",
    "stress_record",
    "stress_start",
    "stress_unused",
]


class CertBoard:
    def __init__(
        self,
        cert_board_client: CertBoardClient,
        algorand_client: AlgorandClient,
        acc: AddressAndSigner,
    ):
        self.cert_board_client = cert_board_client
        self.algorand_client = algorand_client
        self.acc = acc

    def action(
        self,
        action_name: POSSIBLE_ACTIONS,
        action_inputs: ActionInputs,
    ) -> ABITransactionResponse:
        """
        Executes a particular action on the CertBoard instance (on its current state).
        """
        if action_name == "cert_board_deploy":
            sp = self.algorand_client.client.algod.suggested_params()

            res = self.cert_board_client.create_cert_board_deploy(
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                ),
            )

            # Fund the application with MBR
            self.algorand_client.send.payment(
                PayParams(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    receiver=self.cert_board_client.app_address,
                    amount=MBR_ACCOUNT,
                )
            )

        elif action_name == "cert_board_key_reg":
            # Transfer amount for key reg fee
            pay_fee_txn = create_pay_fee_txn(
                algorand_client=self.algorand_client,
                asset_id=ALGO_ASA_ID,
                amount=0,  # REWARDS_OPT_IN_FEE
                sender=self.acc.address,
                signer=self.acc.signer,
                receiver=self.cert_board_client.app_address,
            )

            # Increase fee for inner key reg txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            res = self.cert_board_client.cert_board_key_reg(
                key_reg_info=KeyRegTxnInfo(
                    vote_first=action_inputs.key_reg_vote_first,
                    vote_last=action_inputs.key_reg_vote_last,
                    vote_key_dilution=action_inputs.key_reg_vote_key_dilution,
                    vote_pk=base64.b64decode(action_inputs.key_reg_vote),
                    selection_pk=base64.b64decode(action_inputs.key_reg_selection),
                    state_proof_pk=base64.b64decode(action_inputs.key_reg_state_proof),
                    sender=self.cert_board_client.app_address,
                ),
                txn=pay_fee_txn,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                ),
            )

        elif action_name == "cert_board_set":
            foreign_assets = (
                []
                if action_inputs.payment_asset == ALGO_ASA_ID
                else [action_inputs.payment_asset]
            )

            res = self.cert_board_client.cert_board_set(
                pla_manager=action_inputs.pla_manager,
                expected_consensus_rate=action_inputs.expected_consensus_rate,
                certificate_fee=action_inputs.certificate_fee,
                stress_test_fee_round=action_inputs.stress_test_fee_round,
                payment_asset=action_inputs.payment_asset,
                max_test_duration=action_inputs.max_test_duration,
                max_test_blocking=action_inputs.max_test_blocking,
                stake_min=action_inputs.stake_min,
                stake_max=action_inputs.stake_max,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    foreign_assets=foreign_assets,
                ),
            )

        elif action_name == "cert_board_optin_asa":
            if action_inputs.payment_asset == ALGO_ASA_ID:
                res = None
                pass
            else:
                # Transfer amount for MBR opt-in for ASA
                pay_fee_txn = create_pay_fee_txn(
                    algorand_client=self.algorand_client,
                    asset_id=ALGO_ASA_ID,
                    amount=MBR_ASA,
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    receiver=self.cert_board_client.app_address,
                )

                # Increase fee for inner asa opt-in txn
                sp = self.algorand_client.client.algod.suggested_params()
                sp.fee = 2 * sp.min_fee
                sp.flat_fee = True

                res = self.cert_board_client.cert_board_optin_asa(
                    asa=action_inputs.payment_asset,
                    sender=self.cert_board_client.app_address,
                    txn=pay_fee_txn,
                    transaction_parameters=TransactionParameters(
                        sender=self.acc.address,
                        signer=self.acc.signer,
                        suggested_params=sp,
                    ),
                )

        elif action_name == "cert_board_withdraw":
            # Increase fee for inner withdrawal txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            asset_id = action_inputs.payment_asset
            foreign_assets = [] if asset_id == ALGO_ASA_ID else [asset_id]

            res = self.cert_board_client.cert_board_withdraw(
                amount=action_inputs.amount,
                asset_id=asset_id,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                    foreign_assets=foreign_assets,
                ),
            )

        elif action_name == "cert_create":
            # Transfer amount for payment for certificate
            pay_fee_txn = create_pay_fee_txn(
                algorand_client=self.algorand_client,
                asset_id=action_inputs.payment_asset,
                amount=action_inputs.certificate_fee,
                sender=self.acc.address,
                signer=self.acc.signer,
                receiver=self.cert_board_client.app_address,
            )

            # Transfer amount for payment of MBR increase
            mbr_txn = create_pay_fee_txn(
                algorand_client=self.algorand_client,
                asset_id=ALGO_ASA_ID,
                amount=MBR_CERT_BOX,
                sender=self.acc.address,
                signer=self.acc.signer,
                receiver=self.cert_board_client.app_address,
            )

            # Increase fee for inner asa opt-in txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            recipient = action_inputs.recipient
            box_name = AddressType().encode(recipient) + AddressType().encode(
                self.acc.address
            )
            boxes = [
                [
                    0,
                    box_name,
                ]
            ]

            res = self.cert_board_client.cert_create(
                recipient=recipient,
                info=action_inputs.info,
                mbr_txn=mbr_txn,
                txn=pay_fee_txn,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                    boxes=boxes,
                ),
            )

        elif action_name == "cert_get":
            issuer = (
                action_inputs.issuer
                if action_inputs.issuer is not None
                else self.acc.address
            )

            recipient = action_inputs.recipient
            box_name = AddressType().encode(recipient) + AddressType().encode(issuer)
            boxes = [
                [
                    0,
                    box_name,
                ],
            ]

            res = self.cert_board_client.cert_get(
                recipient=recipient,
                issuer=issuer,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                ),
            )

        elif action_name == "stress_create":
            # Fund the CertBoard with additional stake that can be used for the test
            self.algorand_client.send.payment(
                PayParams(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    receiver=self.cert_board_client.app_address,
                    amount=action_inputs.cert_board_top_up_stake,
                )
            )

            gs = self.get_global_state()

            # Transfer amount for payment for stress test
            amount = action_inputs.duration_max * gs.stress_test_fee_round
            pay_fee_txn = create_pay_fee_txn(
                algorand_client=self.algorand_client,
                asset_id=action_inputs.payment_asset,
                amount=amount,
                sender=self.acc.address,
                signer=self.acc.signer,
                receiver=self.cert_board_client.app_address,
            )

            # Transfer amount for payment of ALGO due to MBR increase,
            # online fee, and potential reward loss
            potential_loss = (
                gs.expected_consensus_rate
                * action_inputs.stake
                * action_inputs.duration_max
            )
            amount = potential_loss + MBR_STRESS_TESTING_CONTRACT
            algo_txn = create_pay_fee_txn(
                algorand_client=self.algorand_client,
                asset_id=ALGO_ASA_ID,
                amount=amount,
                sender=self.acc.address,
                signer=self.acc.signer,
                receiver=self.cert_board_client.app_address,
            )

            # Increase fee for inner txn to create stress testing contract
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            res = self.cert_board_client.stress_create(
                stake=action_inputs.stake,
                duration=action_inputs.duration,
                duration_max=action_inputs.duration_max,
                algo_txn=algo_txn,
                txn=pay_fee_txn,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                ),
            )

        elif action_name == "stress_get":
            recipient = action_inputs.recipient
            box_name = AddressType().encode(
                recipient
            ) + action_inputs.stress_test_id.to_bytes(8, byteorder="big")
            boxes = [
                [
                    0,
                    box_name,
                ],
            ]

            res = self.cert_board_client.cert_get(
                recipient=recipient,
                issuer=issuer,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    boxes=boxes,
                ),
            )

        else:
            raise ValueError(f"Invalid action name {action_name}")

        return res

    def stress_testing_action(
        self,
        app_id: int,
        action_name: POSSIBLE_ACTIONS,
        action_inputs: ActionInputs,
    ) -> ABITransactionResponse:
        """
        Executes a particular action on the StressTesting instance (on its current state).
        """
        if action_name == "stress_start":
            stress_testing_app_address = get_application_address(app_id)
            gs_st = self.get_stress_testing_global_state(app_id)

            vote_first = (
                action_inputs.key_reg_vote_first
                if action_inputs.key_reg_vote_first is not None
                else gs_st.round_created
            )
            vote_last = (
                action_inputs.key_reg_vote_last
                if action_inputs.key_reg_vote_last is not None
                else gs_st.round_end_max
            )

            user_address = self.acc.address
            box_name = AddressType().encode(user_address) + app_id.to_bytes(
                8, byteorder="big"
            )
            boxes = [
                [
                    0,
                    box_name,
                ],
            ]
            foreign_apps = [app_id]

            mbr_txn = create_pay_fee_txn(
                algorand_client=self.algorand_client,
                asset_id=ALGO_ASA_ID,
                amount=MBR_STRESS_BOX,
                sender=self.acc.address,
                signer=self.acc.signer,
                receiver=self.cert_board_client.app_address,
            )

            # Increase fee for forwarding the method call to StressTesting contract,
            # for transferring the stake to it, and its inner key reg txn call
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 4 * sp.min_fee
            sp.flat_fee = True

            res = self.cert_board_client.stress_start(
                stress_test_id=app_id,
                key_reg_info=KeyRegTxnInfo(
                    vote_first=vote_first,
                    vote_last=vote_last,
                    vote_key_dilution=action_inputs.key_reg_vote_key_dilution,
                    vote_pk=base64.b64decode(action_inputs.key_reg_vote),
                    selection_pk=base64.b64decode(action_inputs.key_reg_selection),
                    state_proof_pk=base64.b64decode(action_inputs.key_reg_state_proof),
                    sender=stress_testing_app_address,
                ),
                mbr_txn=mbr_txn,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                    foreign_apps=foreign_apps,
                    boxes=boxes,
                ),
            )

        elif action_name == "stress_end":
            gs_st = self.get_stress_testing_global_state(app_id)
            user_address = (
                action_inputs.user_address
                if action_inputs.user_address is not None
                else gs_st.user_address
            )

            box_name = AddressType().encode(user_address) + app_id.to_bytes(
                8, byteorder="big"
            )
            boxes = [
                [
                    0,
                    box_name,
                ],
            ]
            foreign_apps = [app_id]

            # Increase fee for forwarding to stress testing contract and its inner account close txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 3 * sp.min_fee
            sp.flat_fee = True

            res = self.cert_board_client.stress_end(
                user_address=user_address,
                stress_test_id=app_id,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                    foreign_apps=foreign_apps,
                    boxes=boxes,
                ),
            )

        elif action_name == "stress_record":
            gs_st = self.get_stress_testing_global_state(app_id)
            user_address = (
                action_inputs.user_address
                if action_inputs.user_address is not None
                else gs_st.user_address
            )

            box_name = AddressType().encode(user_address) + app_id.to_bytes(
                8, byteorder="big"
            )
            boxes = [
                [
                    0,
                    box_name,
                ],
            ]
            foreign_apps = [app_id]

            # Increase fee for forwarding to stress testing contract
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            res = self.cert_board_client.stress_record(
                user_address=user_address,
                stress_test_id=app_id,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                    foreign_apps=foreign_apps,
                    boxes=boxes,
                ),
            )

        elif action_name == "stress_unused":
            gs_st = self.get_stress_testing_global_state(app_id)
            user_address = (
                action_inputs.user_address
                if action_inputs.user_address is not None
                else gs_st.user_address
            )

            box_name = AddressType().encode(user_address) + app_id.to_bytes(
                8, byteorder="big"
            )
            boxes = [
                [
                    0,
                    box_name,
                ],
            ]
            foreign_apps = [app_id]

            # Increase fee for forwarding to stress testing contract and its inner account close txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 3 * sp.min_fee
            sp.flat_fee = True

            res = self.cert_board_client.stress_unused(
                user_address=user_address,
                stress_test_id=app_id,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                    foreign_apps=foreign_apps,
                    boxes=boxes,
                ),
            )

        else:
            raise ValueError(f"Invalid action name {action_name}")

        return res

    def get_global_state(self) -> CertBoardGlobalState:
        if self.cert_board_client.app_id == 0:
            return None
        else:
            return CertBoardGlobalState.from_global_state(
                self.cert_board_client.get_global_state()
            )

    def get_state(self) -> POSSIBLE_STATES:
        gs = self.get_global_state()
        if gs is None:
            state = "START"

        else:
            state_enc = gs.state

            if state_enc == STATE_DEPLOYED:
                state = "DEPLOYED"
            elif state_enc == STATE_LIVE:
                state = "LIVE"
            else:
                raise ValueError(f"Unknown state: {state_enc}")

        return state

    def initialize_state(
        self,
        target_state: POSSIBLE_STATES,
        action_inputs: ActionInputs,
        current_state: POSSIBLE_STATES | None = None,
    ):
        """
        Moves a CertBoard instance from its current state to the target_state,
        while applying action_inputs to the actions that lead to that state.
        """

        if current_state is None:
            _current_state = self.get_state()
        else:
            _current_state = current_state

        if target_state == "START":
            return

        # Transition to the target state step by step
        path_to_state = self.get_path_to_state(
            target_state=target_state,
            current_state=_current_state,
        )

        for action_name in path_to_state:
            self.action(action_name, action_inputs)

    def get_path_to_state(
        self,
        target_state: POSSIBLE_STATES,
        current_state: POSSIBLE_STATES | None = None,
    ) -> list[str]:
        """
        Returns a list of actions that transition from the start to the target state.
        """
        to_start = []
        to_deployed = [*to_start, "cert_board_deploy"]
        to_live = [*to_deployed, "cert_board_optin_asa", "cert_board_set"]

        state_transitions = {
            "START": to_start,
            "DEPLOYED": to_deployed,
            "LIVE": to_live,
        }

        if target_state not in state_transitions:
            raise ValueError(f"Unknown target state: {target_state}")

        if current_state is not None:
            path = [
                item
                for item in state_transitions[target_state]
                if item not in state_transitions[current_state]
            ]
        else:
            path = state_transitions[target_state]

        return path

    def get_stress_testing_global_state(
        self, app_id: int
    ) -> st.StressTestingGlobalState | None:
        if app_id == 0:
            res = None
        else:
            try:
                stress_testing = st.StressTesting(
                    stress_testing_client=st.StressTestingClient(
                        algod_client=self.algorand_client.client.algod,
                        app_id=app_id,
                    ),
                    algorand_client=self.algorand_client,
                    acc=self.acc,
                )
                res = stress_testing.get_global_state()
            except Exception as e:
                print(str(e))
                res = None
        return res

    def get_stress_testing_state(self, app_id: int) -> st.POSSIBLE_STATES:
        gs = self.get_stress_testing_global_state(app_id)
        if gs is None:
            state = "START"

        else:
            state_enc = gs.state

            if state_enc == st.STATE_CREATED:
                state = "CREATED"
            elif state_enc == st.STATE_LIVE:
                state = "LIVE"
            else:
                raise ValueError(f"Unknown state: {state_enc}")

        return state

    def initialize_stress_testing_state(
        self,
        action_inputs: ActionInputs,
        app_id: int = 0,
        target_state: st.POSSIBLE_STATES = "LIVE",
        current_state: st.POSSIBLE_STATES | None = None,
    ) -> int:
        """
        Moves a StressTesting that is part of CertBoard from its current state to the target_state,
        while applying action_inputs to the actions that lead to that state.
        """

        if app_id != 0:
            if current_state is None:
                _current_state = self.get_stress_testing_state()
            else:
                _current_state = current_state
        else:
            _current_state = "START"

        if target_state == "START":
            return

        # Transition to the target state step by step
        path_to_state = self.get_stress_testing_path_to_state(
            target_state=target_state,
            current_state=_current_state,
        )

        application_id = app_id
        for action_name in path_to_state:
            if action_name == "stress_create":
                res = self.action(action_name, action_inputs)
                application_id: int = res.return_value
            else:
                self.stress_testing_action(
                    app_id=application_id,
                    action_name=action_name,
                    action_inputs=action_inputs,
                )

        return application_id

    def get_stress_testing_path_to_state(
        self,
        target_state: st.POSSIBLE_STATES,
        current_state: st.POSSIBLE_STATES | None = None,
    ) -> list[str]:
        """
        Returns a list of actions that transition from the start to the target state.
        """
        to_start = []
        to_created = [*to_start, "stress_create"]
        to_live = [*to_created, "stress_start"]

        state_transitions = {
            "START": to_start,
            "CREATED": to_created,
            "LIVE": to_live,
        }

        if target_state not in state_transitions:
            raise ValueError(f"Unknown target state: {target_state}")

        if current_state is not None:
            path = [
                item
                for item in state_transitions[target_state]
                if item not in state_transitions[current_state]
            ]
        else:
            path = state_transitions[target_state]

        return path

    def app_is_opted_in(
        self,
        asset_id: int,
    ) -> bool | None:
        return is_opted_in(
            algorand_client=self.algorand_client,
            address=self.cert_board_client.app_address,
            asset_id=asset_id,
        )

    def app_balance(
        self,
        asset_id: int,
    ) -> bool | None:
        return balance(
            algorand_client=self.algorand_client,
            address=self.cert_board_client.app_address,
            asset_id=asset_id,
        )

    def app_available_balance(
        self,
        asset_id: int,
    ) -> int:
        return available_balance(
            algorand_client=self.algorand_client,
            address=self.cert_board_client.app_address,
            asset_id=asset_id,
        )

    def app_is_online(self) -> bool:
        return is_online(
            algorand_client=self.algorand_client,
            address=self.cert_board_client.app_address,
        )

    def app_box(
        self,
        box_name: bytes,
    ) -> tuple[bytes, bool]:
        return get_box(
            algorand_client=self.algorand_client,
            box_name=box_name,
            app_id=self.cert_board_client.app_id,
        )
