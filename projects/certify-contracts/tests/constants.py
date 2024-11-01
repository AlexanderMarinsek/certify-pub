# pyright: reportMissingModuleSource=false


# ------- Error messages -------
ERROR_GLOBAL_STATE_MISMATCH = "Contract state does not match expected one."
ERROR_DELEGATOR_WRONG_DEPOSIT_RETURNED = "Expected deposit was not returned."
ERROR_DELEGATOR_WRONG_DEPOSIT_AND_EARNINGS_RETURNED = "Expected deposit and earnings were not returned."
ERROR_DELEGATOR_SETUP_FEE_NOT_REMAINING = "Contract should have setup fee remaining."
ERROR_DELEGATOR_OPERATIONAL_FEE_NOT_REMAINING = "Contract should have full operational fee remaining."
ERROR_TEST_ERROR = "Error in test!"
ERROR_MBR_INCORRECTLY_SPENT = "MBR was incorrectly accounted for."

# ------- Test skip messages -------
SKIP_SAME_AS_FOR_ALGO = "Identical test as for ALGO_ASA_ID."
SKIP_SAME_AS_FOR_AD_LIVE = "Identical test as for live=True."
SKIP_SAME_AS_FOR_AD_READY = "Identical test as for ready=True."
SKIP_SAME_AS_FOR_AD_STATE_READY = "Identical test as for state READY."
SKIP_SAME_AS_FOR_ASA = "Identical test as for ASA."
SKIP_VAL_OR_DEL_NEEDED = "Cannot be tested because ValidatorAd and/or Noticeboard needed."
SKIP_NOT_APPLICABLE_TO_ALGO = "Test not applicable to ALGO_ASA_ID."
