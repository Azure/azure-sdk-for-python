"""Configuration types for Azure Cosmos DB availability strategies."""

from typing import Dict

from typing_extensions import Literal, TypedDict


class CrossRegionHedgingStrategyConfig(TypedDict, total=False):
    """Configuration for cross-region request hedging strategy.

    :ivar type: Type of strategy, must be "CrossRegionHedging"
    :vartype type: str
    :ivar threshold_ms: Time in ms before routing to alternate region (default: 500)
    :vartype threshold_ms: int
    :ivar threshold_steps_ms: Time interval between routing attempts (default: 100)
    :vartype threshold_steps_ms: int
    """
    type: Literal["CrossRegionHedging"]
    threshold_ms: int
    threshold_steps_ms: int

def _validate_hedging_config(config: CrossRegionHedgingStrategyConfig) -> CrossRegionHedgingStrategyConfig:
    """Validate and create a CrossRegionHedgingStrategyConfig.
    
    :param config: Dictionary containing configuration values
    :type config: Dict[str, Any]
    :returns: Validated configuration
    :rtype: CrossRegionHedgingStrategyConfig
    :raises ValueError: If configuration is invalid
    """
        
    threshold_ms = config.get("threshold_ms", 500)
    threshold_steps_ms = config.get("threshold_steps_ms", 100)
    
    if not isinstance(threshold_ms, int):
        raise ValueError("threshold_ms must be an integer")
    if not isinstance(threshold_steps_ms, int):
        raise ValueError("threshold_steps_ms must be an integer")
        
    if threshold_ms <= 0:
        raise ValueError("threshold_ms must be positive")
    if threshold_steps_ms <= 0:
        raise ValueError("threshold_steps_ms must be positive")

    return CrossRegionHedgingStrategyConfig(
        type="CrossRegionHedging",
        threshold_ms=threshold_ms,
        threshold_steps_ms=threshold_steps_ms
    )