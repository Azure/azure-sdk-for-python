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

import os
from typing import Optional, Any, Union

# Default values for cross-region hedging strategy
DEFAULT_THRESHOLD_MS = 500
DEFAULT_THRESHOLD_STEPS_MS = 100

# Defaults for cold-start metadata cache hedging. These are SDK-derived and not
# customer-configurable. The threshold is an aggressive tail-latency trigger: metadata
# (control-plane) reads use a short read timeout (DBAReadTimeout, 3s by default), so the
# 1.5s hedge fires well before the primary's own timeout, giving a slow region a chance
# to be raced by a second region while the primary attempt is still outstanding. The
# concurrency budget caps the number of in-flight metadata hedges per client.
DEFAULT_METADATA_HEDGING_THRESHOLD_MS = 1500
DEFAULT_METADATA_HEDGING_THRESHOLD_STEPS_MS = 500
DEFAULT_METADATA_HEDGING_CONCURRENCY_BUDGET = 8

# Operator kill-switch (parity with the .NET AZURE_COSMOS_METADATA_HEDGING_ENABLED env var).
# When set to a recognized truthy/falsy value it overrides both the customer opt-in and the
# account PPAF state.
METADATA_HEDGING_ENABLED_ENV_VAR = "AZURE_COSMOS_METADATA_HEDGING_ENABLED"


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


class MetadataCrossRegionHedgingStrategy(CrossRegionHedgingStrategy):
    """Cold-start metadata cache cross-region hedging configuration.

    Unlike :class:`CrossRegionHedgingStrategy`, the metadata hedging threshold is a
    fixed, SDK-derived value and is not customer-configurable. The strategy is bounded
    to the primary request plus a single cross-region hedge.
    """

    def __init__(self) -> None:
        super().__init__(
            {
                "threshold_ms": DEFAULT_METADATA_HEDGING_THRESHOLD_MS,
                "threshold_steps_ms": DEFAULT_METADATA_HEDGING_THRESHOLD_STEPS_MS,
            }
        )


def _parse_metadata_hedging_env_override() -> Optional[bool]:
    """Parse the ``AZURE_COSMOS_METADATA_HEDGING_ENABLED`` env var into a tri-state bool.

    :returns: ``True``/``False`` when the env var is set to a recognized value, else ``None``.
    :rtype: Optional[bool]
    """
    raw = os.environ.get(METADATA_HEDGING_ENABLED_ENV_VAR)
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in ("true", "1", "yes"):
        return True
    if value in ("false", "0", "no"):
        return False
    return None


def resolve_metadata_hedging_opt_in(opt_in: Optional[bool], ppaf_enabled: bool) -> bool:
    """Resolve the tri-state cold-start metadata hedging opt-in to a concrete bool.

    When the customer leaves the opt-in ``None`` (the default), cold-start metadata
    hedging follows the account's PPAF (Per-Partition Automatic Failover) state: it is
    enabled when PPAF is enabled and disabled otherwise. An explicit ``True`` enables
    hedging even when PPAF is disabled, and an explicit ``False`` disables it regardless
    of PPAF. The ``AZURE_COSMOS_METADATA_HEDGING_ENABLED`` environment variable, when set to a
    recognized truthy/falsy value, overrides both the customer opt-in and the account PPAF
    state (operator kill-switch, parity with the .NET SDK).

    :param opt_in: The customer-supplied tri-state opt-in (True/False/None).
    :type opt_in: Optional[bool]
    :param ppaf_enabled: Whether Per-Partition Automatic Failover is enabled for the account.
    :type ppaf_enabled: bool
    :returns: True if cold-start metadata hedging should be applied, False otherwise.
    :rtype: bool
    """
    env_override = _parse_metadata_hedging_env_override()
    if env_override is not None:
        return env_override
    if opt_in is None:
        return ppaf_enabled
    return opt_in


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
