import dataclasses

from smart_contracts.stress_testing.constants import (
    STATE_NONE,
)


# ------- Data classes -------
@dataclasses.dataclass(kw_only=True)
class ActionInputs:

    user_address: str | None = (
        "3SQSQFXED5D3BRFGIIPVEBCI7ZHBSKKRSIZJ6MYLIUPE57CWP6KUR7363A"
    )
    owner_address: str | None = (
        "4VF26D5AH5FA5CEP3XMSIX2C5BU2HQAGZX2YVUV3C3PPVVFWRG3DFKACSU"
    )
    stake: int | None = 1_000_000
    duration: int | None = 42
    duration_max: int | None = 101

    state: bytes = STATE_NONE

    receiver: str | None = None
    amount: int | None = None

    key_reg_vote_first: int | None = None
    key_reg_vote_last: int | None = None
    key_reg_vote_key_dilution: int | None = 4
    key_reg_selection: str | None = "TyPKJHa8IcFFwJ0xvx4/uUeGgVk4pp8r90S5J/xya4M="
    key_reg_vote: str | None = "CrPTVLdfR0z5U5Vx2MbcY8pMM8MDq7uSmKL8YJgGwuw="
    key_reg_state_proof: str | None = (
        "wcT8pSuOGU84gHJr67NiasgsMpr5pFir6wnzYCmEddnsp5Ys7mh9zWZ6jJJY7VK8jM3FsBoEnHFboYci8VbNpQ=="
    )
    key_reg_sender: str | None = None