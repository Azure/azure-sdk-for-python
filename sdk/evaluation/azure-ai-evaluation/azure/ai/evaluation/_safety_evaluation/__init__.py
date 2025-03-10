# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from ._red_team_agent import RedTeamAgent, AttackStrategy

class RiskCategory(str, Enum):
    """Risk categories for attack objectives."""
    HateUnfairness = "HateUnfairness"
    Violence = "Violence"
    Sexual = "Sexual"
    SelfHarm = "SelfHarm" 
    ProtectedMaterial = "ProtectedMaterial"
    IndirectJailbreak = "IndirectJailbreak"
    DirectJailbreak = "DirectJailbreak"
    CodeVulnerability = "CodeVulnerability"
    InferenceSensitiveAttributes = "InferenceSensitiveAttributes"

class AttackObjectiveGenerator:
    """Generator for creating attack objectives.

    :param risk_categories: List of risk categories to generate attack objectives for
    :type risk_categories: List[RiskCategory]
    """

    # TODO num objectives here to replace num_rows in red team agent
    # Q: Should this be total or per category?
    def __init__(self, risk_categories):
        self.risk_categories = risk_categories

__all__ = ["RedTeamAgent", "AttackStrategy", "RiskCategory", "AttackObjectiveGenerator"]
