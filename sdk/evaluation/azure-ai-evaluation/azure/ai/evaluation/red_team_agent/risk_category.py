# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

class RiskCategory(str, Enum):
    """Risk categories for attack objectives."""
    HateUnfairness = "hate_unfairness"
    Violence = "violence"
    Sexual = "sexual"
    SelfHarm = "self_harm"