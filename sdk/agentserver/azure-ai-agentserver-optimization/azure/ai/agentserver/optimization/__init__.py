# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Agent Optimization — Config loader for optimization-ready hosted agents.

One import, one call::

    from azure.ai.agentserver.optimization import load_config

    config = load_config()                          # uses .agent_configs/baseline/
    config = load_config(config_dir="my_configs")   # custom directory

Resolution order (first match wins):
    1. OPTIMIZATION_CONFIG env var   → inline JSON (used by temp agent versions)
    2. OPTIMIZATION_CANDIDATE_ID + ENDPOINT → resolver API → full config + skills
    3. Local directory (config_dir or .agent_configs/)
       → metadata.yaml + instructions.md + tools.json + skills/
    4. No config found → returns ``None``.
"""

from azure.ai.agentserver.optimization._config import load_config, load_skills_from_dir
from azure.ai.agentserver.optimization._models import (
    CandidateConfig,
    OptimizationConfig,
    Skill,
)
from azure.ai.agentserver.optimization._version import VERSION

__all__ = [
    "CandidateConfig",
    "OptimizationConfig",
    "Skill",
    "load_config",
    "load_skills_from_dir",
]
__version__ = VERSION
