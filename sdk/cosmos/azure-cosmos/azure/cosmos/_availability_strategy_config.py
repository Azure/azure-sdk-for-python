# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Configuration types for Azure Cosmos DB availability strategies."""

from typing import Dict, Optional

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

def _validate_hedging_config(config: Optional[CrossRegionHedgingStrategyConfig])\
        -> Optional[CrossRegionHedgingStrategyConfig]:
    """Validate and create a CrossRegionHedgingStrategyConfig.
    
    :param config: Dictionary containing configuration values
    :type config: Dict[str, Any]
    :returns: Validated configuration
    :rtype: CrossRegionHedgingStrategyConfig
    :raises ValueError: If configuration is invalid
    """

    if config is None:
        return config

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
