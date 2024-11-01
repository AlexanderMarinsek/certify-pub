# ------- Definition of constants -------
"""
Possible states of the contract:
    DEPLOYED - contract has been created.
    LIVE - contract is live.
"""
STATE_NONE = b"\x00"
STATE_DEPLOYED = b"\x01"
STATE_LIVE = b"\x02"


BOX_STRESS_TEST_KEY = b"_stress_"
"""
BOX_STRESS_TEST_KEY : bytes
    Prefix for the boxes of stress test results at the platform.
"""

STRESS_TEST_IN_PROGRESS = b"IN_PROGRESS"

CERT_INFO_VAL_LENGTH = 1024


# Errors
ERROR_CALLED_BY_NOT_PLA_MANAGER = "Can only be called by platform manager."
ERROR_RECEIVER = "Transaction must be to this contract."
ERROR_CALLED_BY_NOT_PLA_MANAGER_OR_CREATOR = (
    "Can only be called by platform manager or creator."
)
ERROR_NOT_OPTED_INTO_ASSET = "Not opted into asset."
ERROR_MAX_STAKE_SMALLER_THAN_MIN = "Max stake must be larger than min."
ERROR_MAX_DURATION_LARGER_THAN_MAX_BLOCKED = (
    "Max duration must be smaller than max requests block rounds."
)
ERROR_AMOUNT_ASA_OPTIN_MBR = (
    "Sent amount doesn't match the MBR increase for opting into an ASA."
)
ERROR_NOT_ENOUGH_ALGO_TO_WITHDRAW = "There is not enough available ALGO for withdrawal."
ERROR_NOT_STATE_LIVE = "Cannot be called from other state than LIVE."
ERROR_AMOUNT = "Sent amount doesn't match the agreed one."
ERROR_NOT_PAYMENT_OR_XFER = "Transaction type must be either Payment or AssetTransfer."
ERROR_REQUESTED_STAKE_TOO_LARGE = (
    "Requested stake for the stress test is larger than allowed."
)
ERROR_REQUESTED_STAKE_TOO_SMALL = (
    "Requested stake for the stress test is smaller than allowed."
)
ERROR_ASSET_ID = "Sent asset doesn't match the agreed one."
ERROR_UNKNOWN_STRESS_TEST = (
    "User address and stress test ID combination are not found at the platform."
)
ERROR_STRESS_TEST_FINISHED = "Stress test has already finished."
