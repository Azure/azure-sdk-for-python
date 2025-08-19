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

Example:
    ```python
    from azure.cosmos import CosmosClient
    from azure.cosmos._availability_strategy import CrossRegionHedgingStrategy, DisabledStrategy
    from datetime import timedelta

    # Configure hedging strategy with initial threshold and fixed step
    strategy = CrossRegionHedgingStrategy(
        threshold=timedelta(milliseconds=100),  # Wait 100ms before first hedged request
        threshold_steps=timedelta(milliseconds=50)  # Wait 50ms between each subsequent request
    )

    # Create client with configured strategy
    client = CosmosClient(url, credential, availability_strategy=strategy)
    container = client.get_container_client("dbname", "containername")

    # Strategy will be used automatically for read operations
    items = list(container.read_all_items())

    # Override strategy for a specific request
    custom_strategy = CrossRegionHedgingStrategy(
        threshold=timedelta(milliseconds=50),
        threshold_steps=[0.5]
    )
    items = list(container.read_all_items(availability_strategy=custom_strategy))

    # Disable hedging for a specific request
    items = list(container.read_all_items(availability_strategy=DisabledStrategy()))
    ```
"""

import abc
from datetime import timedelta

class AvailabilityStrategy(abc.ABC):
    """Abstract base class for availability strategies.

    This class defines the interface that all availability strategies must implement.
    Strategies can modify how requests are executed to improve availability and latency.
    Strategies can be configured at the client level and overridden per request.
    """


class DisabledStrategy(AvailabilityStrategy):
    """Strategy that disables request hedging.

    This strategy executes requests directly without any hedging.
    It can be used to disable hedging for specific requests when a client
    has a default hedging strategy configured.

    Example:
        ```python
        # Disable hedging for a specific request
        items = container.read_all_items(
            availability_strategy=DisabledStrategy()
        )
        ```
    """

class CrossRegionHedgingStrategy(AvailabilityStrategy):
    """Strategy that implements cross-region request hedging.

    This strategy improves tail latency by sending duplicate requests to other regions
    after configured time thresholds. When the first successful response arrives,
    any pending requests are cancelled.

    The strategy uses two timing parameters:
    - threshold: Initial wait time before sending the first hedged request
    - threshold_steps: Fixed wait time between each subsequent request

    For example, with threshold=100ms and threshold_steps=50:
    - Original request sent at t=0
    - Second request at t=100ms (initial threshold)
    - Third request at t=150ms (after 50ms step)
    - Fourth request at t=200ms (after 50ms step)

    :param threshold: Initial wait before first hedged request
    :type threshold: timedelta
    :param threshold_steps: Fixed time interval between subsequent requests
    :type threshold_steps: timedelta
    :raises ValueError: If threshold is negative or threshold_steps is invalid
    """

    def __init__(self, threshold: timedelta, threshold_steps: timedelta) -> None:
        """Initialize the cross-region hedging strategy.

        :param threshold: Initial wait before first hedged request
        :type threshold: timedelta
        :param threshold_steps: Fixed time interval between subsequent requests
        :type threshold_steps: timedelta
        :raises ValueError: If threshold or threshold_steps is negative
        """
        if threshold.total_seconds() < 0:
            raise ValueError("Threshold must be non-negative")
        if threshold_steps.total_seconds() < 0:
            raise ValueError("Threshold steps must be non-negative")

        self._threshold = threshold
        self._threshold_steps = threshold_steps

    @property
    def threshold(self) -> timedelta:
        """Get the base threshold before sending hedged requests.

        :return: Base threshold
        :rtype: timedelta
        """
        return self._threshold

    @property
    def threshold_steps(self) -> timedelta:
        """Get the fixed time interval between requests.

        :return: Time interval
        :rtype: timedelta
        """
        return self._threshold_steps