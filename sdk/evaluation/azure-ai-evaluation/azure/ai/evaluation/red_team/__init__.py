# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

_PYRIT_INSTALLED = False

try:
    from ._red_team import RedTeam
    from ._attack_strategy import AttackStrategy
    from ._attack_objective_generator import RiskCategory, SupportedLanguages
    from ._red_team_result import RedTeamResult

    _PYRIT_INSTALLED = True
except ImportError:
    # When pyrit is not installed, provide placeholder classes for documentation
    # This allows sphinx autodoc to document the module without the optional dependency
    import sys

    # Check if we're being imported by sphinx for documentation
    _is_sphinx = "sphinx" in sys.modules

    if not _is_sphinx:
        raise ImportError(
            "Could not import Pyrit. Please install the dependency with `pip install azure-ai-evaluation[redteam]`."
        )

    # Provide placeholder docstrings for sphinx
    class RedTeam:  # type: ignore[no-redef]
        """Red team testing orchestrator. Requires pyrit: `pip install azure-ai-evaluation[redteam]`."""

        pass

    class AttackStrategy:  # type: ignore[no-redef]
        """Attack strategy enumeration. Requires pyrit: `pip install azure-ai-evaluation[redteam]`."""

        pass

    class RiskCategory:  # type: ignore[no-redef]
        """Risk category enumeration. Requires pyrit: `pip install azure-ai-evaluation[redteam]`."""

        pass

    class SupportedLanguages:  # type: ignore[no-redef]
        """Supported languages enumeration. Requires pyrit: `pip install azure-ai-evaluation[redteam]`."""

        pass

    class RedTeamResult:  # type: ignore[no-redef]
        """Red team result container. Requires pyrit: `pip install azure-ai-evaluation[redteam]`."""

        pass


__all__ = [
    "RedTeam",
    "AttackStrategy",
    "RiskCategory",
    "RedTeamResult",
    "SupportedLanguages",
]
