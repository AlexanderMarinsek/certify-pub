import dataclasses

from algosdk.abi import AddressType, TupleType, UintType
from algosdk.constants import ZERO_ADDRESS

from smart_contracts.artifacts.cert_board.cert_board_client import (
    GlobalState,
    StressTestInfo,
)


@dataclasses.dataclass(kw_only=True)
class CertBoardGlobalState:
    pla_manager: str = ZERO_ADDRESS
    expected_consensus_rate: int = 0
    certificate_fee: int = 0
    stress_test_fee_round: int = 0
    payment_asset: int = 0
    max_test_duration: int = 0
    max_test_blocking: int = 0
    stake_min: int = 0
    stake_max: int = 0
    blocked_algo: int = 0
    state: bytes = b"\x00"

    @classmethod
    def from_global_state(cls, gs: GlobalState) -> "CertBoardGlobalState":
        return cls(
            pla_manager=decode_abi_address(gs.pla_manager.as_bytes),
            expected_consensus_rate=gs.expected_consensus_rate,
            certificate_fee=gs.certificate_fee,
            stress_test_fee_round=gs.stress_test_fee_round,
            payment_asset=gs.payment_asset,
            max_test_duration=gs.max_test_duration,
            max_test_blocking=gs.max_test_blocking,
            stake_min=gs.stake_min,
            stake_max=gs.stake_max,
            blocked_algo=gs.blocked_algo,
            state=gs.state.as_bytes,
        )

    @classmethod
    def with_defaults(cls) -> "CertBoardGlobalState":
        return cls()


def decode_abi_address(data: bytes) -> str:
    return AddressType().decode(data)


def decode_stress_test_info(data: bytes) -> StressTestInfo:
    stress_test_info_type = TupleType(
        [
            UintType(64),  # avr_online_stake
            UintType(64),  # cnt_produced_block
            UintType(64),  # round_start
            UintType(64),  # round_end
            UintType(64),  # stake
        ]
    )

    decoded_tuple = stress_test_info_type.decode(data)

    stress_test_info = StressTestInfo(
        avr_online_stake=decoded_tuple[0],
        cnt_produced_block=decoded_tuple[1],
        round_start=decoded_tuple[2],
        round_end=decoded_tuple[3],
        stake=decoded_tuple[4],
    )

    return stress_test_info
