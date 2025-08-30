# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

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

"""Availability strategy for the Azure Cosmos database service.

This module provides availability strategies that can be used to improve request latency and
availability in multi-region deployments. Strategies can be configured at the client level
and overridden per request.
"""

from datetime import timedelta

class CrossRegionHedgingStrategy:
    """Configuration for cross-region request routing using availability thresholds.
    
    Controls whether and how requests are routed across regions for improved availability
    and latency. Uses time-based thresholds to determine when to route requests to alternate
    regions. Can be configured at the client level and overridden per request.
    
    :param enabled: Whether cross-region request routing is enabled, defaults to True
    :type enabled: bool
    :param threshold: Time to wait before routing to an alternate region, defaults to 500ms
    :type threshold: ~datetime.timedelta
    :param threshold_steps: Time interval between subsequent region routing attempts, defaults to 100ms
    :type threshold_steps: ~datetime.timedelta
    
    Example:
        ```python
        from datetime import timedelta
        
        # Enable cross-region routing with default settings
        strategy = CrossRegionHedgingStrategy()
        
        # Disable cross-region routing
        strategy = CrossRegionHedgingStrategy(enabled=False)
        
        # Custom routing thresholds
        strategy = CrossRegionHedgingStrategy(
            enabled=True,
            threshold=timedelta(milliseconds=500),  # Try alternate region after 500ms
            threshold_steps=timedelta(milliseconds=100)  # Wait 100ms between region attempts
        )
        
        # Set at client level
        client = CosmosClient(
            url,
            key,
            availability_strategy=strategy
        )
        
        # Override per request
        container.read_item(
            item="id1",
            partition_key="pk1",
            availability_strategy=strategy
        )
        ```
    """
    
    def __init__(
        self,
        enabled: bool = True,
        threshold: timedelta = timedelta(milliseconds=500),
        threshold_steps: timedelta = timedelta(milliseconds=100)
    ) -> None:
        """Initialize availability strategy with specified configuration."""
        if enabled:
            if threshold.total_seconds() <= 0:
                raise ValueError("threshold must be positive when enabled is True")
            if threshold_steps.total_seconds() <= 0:
                raise ValueError("threshold_steps must be positive when enabled is True")
                
        self._enabled = enabled
        self._threshold = threshold
        self._threshold_steps = threshold_steps
    
    @property
    def enabled(self) -> bool:
        """Whether cross-region request routing is enabled."""
        return self._enabled
        
    @property
    def threshold(self) -> timedelta:
        """Wait time before routing to alternate region."""
        return self._threshold
        
    @property
    def threshold_steps(self) -> timedelta:
        """Time interval between subsequent region routing attempts."""
        return self._threshold_steps
