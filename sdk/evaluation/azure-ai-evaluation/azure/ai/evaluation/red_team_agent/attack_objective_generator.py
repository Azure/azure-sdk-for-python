# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum
from typing import List

class RiskCategory(str, Enum):
    """Risk categories for attack objectives."""
    HateUnfairness = "hate_unfairness"
    Violence = "violence"
    Sexual = "sexual"
    SelfHarm = "self_harm"

class AttackObjectiveGenerator:
    """Generator for creating attack objectives.

    :param risk_categories: List of risk categories to generate attack objectives for
    :type risk_categories: List[RiskCategory]
    """
    def __init__(self, risk_categories: List[RiskCategory], num_objectives: int = 10):
        self.risk_categories = risk_categories
        self.num_objectives = num_objectives