# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

try:
    from ._red_team import RedTeam
    from ._attack_strategy import AttackStrategy
    from ._attack_objective_generator import RiskCategory, SupportedLanguages
    from ._red_team_result import RedTeamResult
except ImportError:
    raise ImportError(
        "Could not import Pyrit. Please install the dependency with `pip install azure-ai-evaluation[redteam]`."
    )


__all__ = [
    "RedTeam",
    "AttackStrategy",
    "RiskCategory",
    "RedTeamResult",
    "SupportedLanguages",
]
