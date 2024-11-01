# Constants
from .cert_board.constants import CERT_INFO_VAL_LENGTH

CONSENSUS_STAKE_ROUND_DELAY = 1  # 320  # TO DO : Check if this will be exposed in AVM
ALGO_ASA_ID = 0

MBR_ACCOUNT = 100_000
"""
MBR_ACCOUNT : int
    Minimum balance requirement for a valid account.
    In microAlgo.
"""

MBR_ASA = 100_000
"""
MBR_ASA : int
    Minimum balance requirement increase when opting into an ASA.
    In microAlgo.
"""

REWARDS_OPT_IN_FEE = 2_000_000
"""
REWARDS_OPT_IN_FEE : int
    Fee required to opt-in to rewards - to get access to last_block fields.
    In microAlgo.
"""

MBR_CERT_BOX = 2_500 + 400 * (2 * 32 + CERT_INFO_VAL_LENGTH)
"""
MBR_CERT_BOX : int
    Minimum balance requirement increase due to box for certificate at CertBoard.
    In microAlgo.
    The box consists of 2*32 bytes for key and 1024 bytes for the contents.
"""

MBR_STRESS_BOX = 2_500 + 400 * (32 + 8 + 40)
"""
MBR_STRESS_BOX : int
    Minimum balance requirement increase due to box for stress testing results at CertBoard.
    In microAlgo.
    The box consists of 32 bytes (user address) + 8 bytes (stress test app ID) for key and
    len(StressTestInfo) = 40 bytes for the contents.
"""

MBR_STRESS_TESTING_CONTRACT = 592_000
"""
MBR_STRESS_TESTING_CONTRACT : int
    Minimum balance requirement increase due to creation of a StressTesting contract.
    In microAlgo.
"""
