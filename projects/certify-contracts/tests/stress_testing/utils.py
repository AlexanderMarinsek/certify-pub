import base64
from typing import Literal

from algokit_utils import ABITransactionResponse, TransactionParameters
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import AlgorandClient

from smart_contracts.artifacts.stress_testing.stress_testing_client import (
    KeyRegTxnInfo,
    StressTestingClient,
)
from smart_contracts.constants import ALGO_ASA_ID
from smart_contracts.stress_testing.constants import (
    STATE_CREATED,
    STATE_LIVE,
)
from tests.utils import (
    available_balance,
    balance,
    create_pay_fee_txn,
    is_online,
    is_opted_in,
)

from .client_helper import StressTestingGlobalState
from .config import ActionInputs

POSSIBLE_STATES = Literal[
    "START",
    "CREATED",
    "LIVE",
]

POSSIBLE_ACTIONS = Literal[
    "create",
    "start",
    "end",
    "record",
    "unused",
]


class StressTesting:
    def __init__(
        self,
        stress_testing_client: StressTestingClient,
        algorand_client: AlgorandClient,
        acc: AddressAndSigner,
    ):
        self.stress_testing_client = stress_testing_client
        self.algorand_client = algorand_client
        self.acc = acc

    def action(
        self,
        action_name: POSSIBLE_ACTIONS,
        action_inputs: ActionInputs,
    ) -> ABITransactionResponse:
        """
        Executes a particular action on the StressTesting instance (on its current state).
        """
        if action_name == "create":
            sp = self.algorand_client.client.algod.suggested_params()

            res = self.stress_testing_client.create_create(
                user_address=action_inputs.user_address,
                owner_address=action_inputs.owner_address,
                stake=action_inputs.stake,
                duration=action_inputs.duration,
                duration_max=action_inputs.duration_max,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                ),
            )

        elif action_name == "start":
            receiver = (
                action_inputs.receiver
                if action_inputs.receiver is not None
                else self.stress_testing_client.app_address
            )

            gs = self.get_global_state()
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
                else self.stress_testing_client.app_address
            )

            # Transfer amount
            pay_fee_txn = create_pay_fee_txn(
                algorand_client=self.algorand_client,
                asset_id=ALGO_ASA_ID,
                amount=amount,
                sender=self.acc.address,
                signer=self.acc.signer,
                receiver=receiver,
            )

            # Increase fee for inner key reg txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            res = self.stress_testing_client.start(
                user_address=user_address,
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
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                ),
            )

        elif action_name == "end":
            gs = self.get_global_state()
            user_address = (
                action_inputs.user_address
                if action_inputs.user_address is not None
                else gs.user_address
            )

            # Increase fee for inner account close txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            res = self.stress_testing_client.delete_end(
                user_address=user_address,
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                ),
            )

        elif action_name == "record":
            res = self.stress_testing_client.record(
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                ),
            )

        elif action_name == "unused":
            # Increase fee for inner account close txn
            sp = self.algorand_client.client.algod.suggested_params()
            sp.fee = 2 * sp.min_fee
            sp.flat_fee = True

            res = self.stress_testing_client.delete_unused(
                transaction_parameters=TransactionParameters(
                    sender=self.acc.address,
                    signer=self.acc.signer,
                    suggested_params=sp,
                ),
            )

        else:
            raise ValueError(f"Invalid action name {action_name}")

        return res

    def get_global_state(self) -> StressTestingGlobalState:
        if self.stress_testing_client.app_id == 0:
            return None
        else:
            return StressTestingGlobalState.from_global_state(
                self.stress_testing_client.get_global_state()
            )

    def get_state(self) -> POSSIBLE_STATES:
        gs = self.get_global_state()
        if gs is None:
            state = "START"

        else:
            state_enc = gs.state

            if state_enc == STATE_CREATED:
                state = "CREATED"
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
        Moves a StressTesting instance from its current state to the target_state,
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
        to_created = [*to_start, "create"]
        to_live = [*to_created, "start"]

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
            address=self.stress_testing_client.app_address,
            asset_id=asset_id,
        )

    def app_balance(
        self,
        asset_id: int,
    ) -> bool | None:
        return balance(
            algorand_client=self.algorand_client,
            address=self.stress_testing_client.app_address,
            asset_id=asset_id,
        )

    def app_available_balance(
        self,
        asset_id: int,
    ) -> int:
        return available_balance(
            algorand_client=self.algorand_client,
            address=self.stress_testing_client.app_address,
            asset_id=asset_id,
        )

    def app_is_online(self) -> bool:
        return is_online(
            algorand_client=self.algorand_client,
            address=self.stress_testing_client.app_address,
        )
