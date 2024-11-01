import dataclasses

from algosdk.abi import AddressType
from algosdk.constants import ZERO_ADDRESS

from smart_contracts.artifacts.stress_testing.stress_testing_client import (
    GlobalState,
)


@dataclasses.dataclass(kw_only=True)
class StressTestingGlobalState:
    user_address: str = ZERO_ADDRESS
    owner_address: str = ZERO_ADDRESS
    stake: int = 0
    duration: int = 0
    duration_max: int = 0
    round_created: int = 0
    round_start: int = 0
    round_end: int = 0
    round_ended: int = 100000000
    round_end_max: int = 0
    last_block: int = 0
    cnt_produced_blocks: int = 0
    total_stake_sum: int = 0
    cnt_total_stake_sum: int = 0
    state: bytes = b"\x00"

    @classmethod
    def from_global_state(cls, gs: GlobalState) -> "StressTestingGlobalState":
        return cls(
            user_address=decode_abi_address(gs.user_address.as_bytes),
            owner_address=decode_abi_address(gs.owner_address.as_bytes),
            stake=gs.stake,
            duration=gs.duration,
            duration_max=gs.duration_max,
            round_created=gs.round_created,
            round_start=gs.round_start,
            round_end=gs.round_end,
            round_ended=gs.round_ended,
            round_end_max=gs.round_end_max,
            last_block=gs.last_block,
            cnt_produced_blocks=gs.cnt_produced_blocks,
            total_stake_sum=gs.total_stake_sum,
            cnt_total_stake_sum=gs.cnt_total_stake_sum,
            state=gs.state.as_bytes,
        )

    @classmethod
    def with_defaults(cls) -> "StressTestingGlobalState":
        return cls()


def decode_abi_address(data: bytes) -> str:
    return AddressType().decode(data)
