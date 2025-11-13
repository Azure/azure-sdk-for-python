"""
Utility functions for handling attack objectives in Red Team Agent.
"""

import uuid
from typing import Dict, Optional


def extract_risk_subtype(objective: Dict) -> Optional[str]:
    """Extract risk-subtype from an objective's target_harms metadata.

    Searches through the target_harms list in the objective's metadata to find
    the first non-empty risk-subtype value.

    :param objective: The objective dictionary containing metadata with target_harms
    :type objective: Dict
    :return: The risk-subtype value if found, None otherwise
    :rtype: Optional[str]
    """
    target_harms = objective.get("metadata", {}).get("target_harms", [])
    if target_harms and isinstance(target_harms, list):
        for harm in target_harms:
            if isinstance(harm, dict) and "risk-subtype" in harm:
                subtype_value = harm.get("risk-subtype")
                if subtype_value:
                    return subtype_value
    return None


def get_objective_id(objective: Dict) -> str:
    """Get a unique identifier for an objective.

    Uses the objective's 'id' field if available. If not present, generates
    a UUID-based identifier to ensure uniqueness. This avoids using Python's
    id() which returns memory addresses that can be reused after garbage collection.

    :param objective: The objective dictionary
    :type objective: Dict
    :return: A unique identifier for the objective
    :rtype: str
    """
    obj_id = objective.get("id")
    if obj_id is not None:
        return str(obj_id)
    # Generate a random UUID-based identifier if no 'id' field exists
    return f"generated-{uuid.uuid4()}"
