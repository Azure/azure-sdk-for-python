# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Agent Optimization — Config loader for optimization-ready hosted agents.

One import, one call::

    from azure.ai.agentserver.optimization import load_config

    config = load_config(default_instructions="You are a helpful assistant.")
    # config.instructions        — optimized or default
    # config.model              — optimized or default
    # config.temperature        — optimized or default
    # config.skills             — learned skills (empty list if none)
    # config.tool_descriptions  — optimized tool descriptions (empty dict if none)
    # config.source             — "env:OPTIMIZATION_CONFIG", "api:candidate:abc", "local:<path>", or "defaults"

Resolution order (first match wins):
    1. OPTIMIZATION_CONFIG env var   → inline JSON (used by temp agent versions)
    2. OPTIMIZATION_CANDIDATE_ID + JOB_ID + ENDPOINT → resolver API → full config + skills
    3. Local directory (.agent_configs/) → metadata.yaml + instructions.md + tools.json + skills/
    4. Defaults                      → your hardcoded values (agent works normally)
"""

from azure.ai.agentserver.optimization._config import load_config, load_skills_from_dir
from azure.ai.agentserver.optimization._models import (
    CandidateConfig,
    OptimizationConfig,
    Skill,
    ToolDescription,
)
from azure.ai.agentserver.optimization._version import VERSION

__all__ = [
    "CandidateConfig",
    "OptimizationConfig",
    "Skill",
    "ToolDescription",
    "load_config",
    "load_skills_from_dir",
]
__version__ = VERSION
