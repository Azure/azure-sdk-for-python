# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Agent Optimization — Config loader for optimization-ready hosted agents.

One import, one call::

    from azure.ai.agentserver.optimization import load_config

    config = load_config()                          # uses .agent_configs/baseline/
    config = load_config(config_dir="my_configs")   # custom directory
    config = load_config(candidate_id="abc-123")    # from request header
    config = load_config(required=False)            # returns None fields instead of raising

Resolution order (first match wins):
    1. OPTIMIZATION_CONFIG env var   → inline JSON (used by temp agent versions)
    2. candidate_id param or OPTIMIZATION_CANDIDATE_ID env var + ENDPOINT → resolver API → full config + skills
    3. Local directory (config_dir or .agent_configs/) → metadata.yaml + instructions.md + tools.json + skills/
    4. No config found → raises ValueError (or returns empty config if required=False)
"""

from azure.ai.agentserver.optimization._config import (
    OPTIMIZATION_CANDIDATE_HEADER,
    load_config,
    load_skills_from_dir,
)
from azure.ai.agentserver.optimization._models import (
    CandidateConfig,
    OptimizationConfig,
    Skill,
)
from azure.ai.agentserver.optimization._version import VERSION

__all__ = [
    "CandidateConfig",
    "OPTIMIZATION_CANDIDATE_HEADER",
    "OptimizationConfig",
    "Skill",
    "load_config",
    "load_skills_from_dir",
]
__version__ = VERSION
