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

from typing import Optional, Any, Union

# Default values for cross-region hedging strategy
DEFAULT_THRESHOLD_MS = 500
DEFAULT_THRESHOLD_STEPS_MS = 100


class CrossRegionHedgingStrategy:
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
            self.threshold_ms = DEFAULT_THRESHOLD_MS
            self.threshold_steps_ms = DEFAULT_THRESHOLD_STEPS_MS
        else:
            self.threshold_ms = config.get("threshold_ms", DEFAULT_THRESHOLD_MS)
            self.threshold_steps_ms = config.get("threshold_steps_ms", DEFAULT_THRESHOLD_STEPS_MS)

        if self.threshold_ms <= 0:
            raise ValueError("threshold_ms must be positive")
        if self.threshold_steps_ms <= 0:
            raise ValueError("threshold_steps_ms must be positive")


def _validate_request_hedging_strategy(
        config: Optional[Union[bool, dict[str, Any]]]
) -> Union[CrossRegionHedgingStrategy, bool, None]:
    """Validate and create a CrossRegionHedgingStrategy for a request.
    
    :param config: Configuration for availability strategy. Can be:
        - None: Returns None (no strategy, uses client default if available)
        - True: Returns strategy with default values (threshold_ms=500, threshold_steps_ms=100)
        - False: Returns False (explicitly disabled, overrides client configs)
        - dict: Returns strategy with values from dict, using defaults for missing keys
    :type config: Optional[Union[bool, Dict[str, Any]]]
    :returns: Validated configuration object, False if explicitly disabled, or None
    :rtype: Union[CrossRegionHedgingStrategy, bool, None]
    """
    if isinstance(config, dict):
        # Validate dict values by attempting to create a strategy object
        return CrossRegionHedgingStrategy(config)
    # For bool and None, no validation needed as they are handled in the request object's `set_availability_strategy`
    return config


def validate_client_hedging_strategy(
        config: Union[bool, dict[str, Any]]
) -> Union[CrossRegionHedgingStrategy, None]:
    """Validate and create a CrossRegionHedgingStrategy for the client.

    :param config: Configuration for availability strategy. Can be:
        - True: Returns strategy with default values (threshold_ms=500, threshold_steps_ms=100)
        - False: Returns False (default, explicitly disabled)
        - dict: Returns strategy with values from dict, using defaults for missing keys
    :type config: Union[bool, Dict[str, Any]]
    :returns: Validated configuration object, False if explicitly disabled, or None
    :rtype: Union[CrossRegionHedgingStrategy, None]
    """

    if isinstance(config, bool):
        if config:
            # True -> use default values
            return CrossRegionHedgingStrategy()
        # False -> nothing set by client, return None to allow request level override or default to no strategy
        return None

    # dict -> use values from dict
    return CrossRegionHedgingStrategy(config)
