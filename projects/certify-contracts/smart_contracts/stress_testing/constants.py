# ------- Definition of constants -------
"""
Possible states of the contract:
    CREATED - contract has been created.
    LIVE - contract is live.
"""
STATE_NONE = b"\x00"
STATE_CREATED = b"\x01"
STATE_LIVE = b"\x02"

# Errors
ERROR_INCORRECT_DURATION = "Maximum end round must be larger than requested duration."
ERROR_CALLED_BY_NOT_CREATOR = "Can only be called by smart contract creator."
ERROR_NOT_STATE_CREATED = "Cannot be called from other state than CREATED."
ERROR_INCORRECT_USER = "User does not match the stress test user."
ERROR_TEST_NOT_SOON_ENOUGH = "Test was not started soon enough."
ERROR_RECEIVER = "Transaction must be to this contract."
ERROR_AMOUNT = "Sent amount doesn't match the agreed one."
ERROR_NOT_STATE_LIVE = "Cannot be called from other state than LIVE."
ERROR_ACCOUNT_CANNOT_TERMINATE_TEST = (
    "This account is not allowed to terminate the test."
)
ERROR_BLOCKS_AFTER_END_DONT_COUNT = (
    "Blocks produced after test end shouldn't be counted."
)
ERROR_NOTHING_TO_RECORD = "There is no new produced block to record."
ERROR_TEST_CAN_FINISH_IN_TIME = (
    "Cannot claim the test as unused because there is still enough time to finish it."
)
ERROR_DURATION_WILL_NOT_WORK = "Duration is too short due to consensus delay."
