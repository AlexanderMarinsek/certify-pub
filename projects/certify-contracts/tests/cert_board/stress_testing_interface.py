from typing import Literal  # noqa: I001, RUF100

from smart_contracts.artifacts.stress_testing.stress_testing_client import (
    StressTestingClient,  # noqa: F401
)
from smart_contracts.stress_testing.constants import (  # noqa: F401
    STATE_CREATED,
    STATE_LIVE,
)
from tests.stress_testing.client_helper import StressTestingGlobalState  # noqa: F401
from tests.stress_testing.utils import StressTesting  # noqa: F401

POSSIBLE_STATES = Literal[
    "START",
    "READY",
    "SUBMITTED",
    "ENDED_CANNOT_PAY",
    "ENDED_EXPIRED",
    "ENDED_LIMITS",
    "ENDED_NOT_CONFIRMED",
    "ENDED_NOT_SUBMITTED",
    "ENDED_UPTIME",
    "ENDED_WITHDREW",
    "LIVE",
]
