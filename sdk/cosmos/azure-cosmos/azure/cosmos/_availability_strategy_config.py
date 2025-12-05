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

from typing import Optional, Any


class CrossRegionHedgingStrategyConfig:
    """Configuration for cross-region request hedging strategy.

    :param config: Dictionary containing configuration values, defaults to None
    :type config: Optional[Dict[str, Any]]
    :raises ValueError: If configuration values are invalid
    
    The config dictionary can contain:
    - threshold_ms: Time in ms before routing to alternate region (default: 500)
    - threshold_steps_ms: Time interval between routing attempts (default: 100)
    """
    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        if config is None:
            self.threshold_ms = 500
            self.threshold_steps_ms = 100
        else:
            self.threshold_ms = config.get("threshold_ms", 500)
            self.threshold_steps_ms = config.get("threshold_steps_ms", 100)

        if self.threshold_ms <= 0:
            raise ValueError("threshold_ms must be positive")
        if self.threshold_steps_ms <= 0:
            raise ValueError("threshold_steps_ms must be positive")

def _validate_hedging_config(config: Optional[dict[str, Any]]) -> Optional[CrossRegionHedgingStrategyConfig]:
    """Validate and create a CrossRegionHedgingStrategyConfig.
    
    :param config: Dictionary containing configuration values
    :type config: Optional[Dict[str, Any]]
    :returns: Validated configuration object
    :rtype: Optional[CrossRegionHedgingStrategyConfig]
    """
    if config is None:
        return None

    return CrossRegionHedgingStrategyConfig(config)
