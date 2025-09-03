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


class CrossRegionHedgingStrategy:
    """Configuration for cross-region request routing using availability thresholds.

    Controls whether and how requests are routed across regions for improved availability
    and latency. Uses time-based thresholds to determine when to route requests to alternate
    regions. Can be configured at the client level and overridden per request.
    """

    threshold_ms: int
    """Wait time in milliseconds before routing to alternate region. Default value is 500."""
    threshold_steps_ms: int
    """Time interval in milliseconds between subsequent region routing attempts. Default value is 100."""

    
    def __init__(
        self,
        threshold_ms: int = 500,
        threshold_steps_ms: int = 100
    ) -> None:
        """Initialize availability strategy with specified configuration."""
        if threshold_ms <= 0:
            raise ValueError("threshold must be positive when enabled is True")
        if threshold_steps_ms <= 0:
            raise ValueError("threshold_steps must be positive when enabled is True")

        self.threshold_ms = threshold_ms
        self.threshold_steps_ms = threshold_steps_ms
