# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Strategy mapping utilities for PyRIT FoundryScenario integration."""

from typing import Dict, Optional

try:
    from pyrit.scenario.scenarios.foundry_scenario import FoundryStrategy
except ImportError:
    # Fallback for environments where PyRIT 0.10.0+ is not available
    FoundryStrategy = None

from .._attack_strategy import AttackStrategy


# Mapping table: azure-sdk AttackStrategy → PyRIT FoundryStrategy
# Note: PAIR strategy is not present in current AttackStrategy enum
ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY: Dict[AttackStrategy, Optional[str]] = {
    # Baseline (no modifications)
    AttackStrategy.Baseline: None,  # Special case - handled separately
    
    # Single-turn converter strategies (easy)
    AttackStrategy.ROT13: "ROT13" if FoundryStrategy is None else FoundryStrategy.ROT13,
    AttackStrategy.Base64: "Base64" if FoundryStrategy is None else FoundryStrategy.Base64,
    
    # Multi-turn attack strategies (difficult)
    AttackStrategy.MultiTurn: "MultiTurn" if FoundryStrategy is None else FoundryStrategy.MultiTurn,
    AttackStrategy.Crescendo: "Crescendo" if FoundryStrategy is None else FoundryStrategy.Crescendo,
    
    # Jailbreak strategy
    AttackStrategy.Jailbreak: "Jailbreak" if FoundryStrategy is None else FoundryStrategy.Jailbreak,
}


def convert_attack_strategy_to_foundry(strategy: AttackStrategy) -> Optional[str]:
    """
    Convert azure-sdk-for-python AttackStrategy to PyRIT FoundryStrategy.
    
    Args:
        strategy: The attack strategy to convert
        
    Returns:
        Corresponding FoundryStrategy, or None for baseline
        
    Raises:
        ValueError: If strategy is not supported in FoundryScenario
    """
    if strategy == AttackStrategy.Baseline:
        return None  # Baseline handled separately
        
    if strategy not in ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY:
        raise ValueError(
            f"Attack strategy {strategy} is not supported with FoundryScenario. "
            f"Supported strategies: {list(ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY.keys())}"
        )
    
    return ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY[strategy]


def is_foundry_supported(strategy: AttackStrategy) -> bool:
    """
    Check if an attack strategy is supported by FoundryScenario.
    
    Args:
        strategy: The attack strategy to check
        
    Returns:
        True if supported, False otherwise
    """
    return strategy in ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY
