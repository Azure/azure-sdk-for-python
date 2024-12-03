# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azure.ai.ml._utils._experimental import experimental


@experimental
class EndpointRequestSettings:
    def __init__(self, *, request_batch_size: Optional[int] = None, min_endpoint_success_ratio: Optional[float] = None):
        """Initialize EndpointRequestSettings.

        :param request_batch_size: The number of requests to send to the teacher model endpoint as a batch,
            defaults to None
        :type request_batch_size: typing.Optional[int], optional
        :param min_endpoint_success_ratio: The ratio of (successful requests / total requests) needed for the
            data generation step to be considered successful. Must be a value between 0 and 1 inclusive,
            defaults to None
        :type min_endpoint_success_ratio: typing.Optional[float], optional
        """
        self._request_batch_size = request_batch_size
        self._min_endpoint_success_ratio = min_endpoint_success_ratio

    @property
    def request_batch_size(self) -> Optional[int]:
        """Get the number of inference requests to send to the teacher model as a batch.

        :return: The number of inference requests to send to the teacher model as a batch.
        :rtype: typing.Optional[int]
        """
        return self._request_batch_size

    @request_batch_size.setter
    def request_batch_size(self, value: Optional[int]) -> None:
        """Set the number of inference requests to send to the teacher model as a batch.

        :param value: The number of inference requests to send to the teacher model as a batch.
        :type value: typing.Optional[int]
        """
        self._request_batch_size = value

    @property
    def min_endpoint_success_ratio(self) -> Optional[float]:
        """Get the minimum ratio of successful inferencing requests.

        :return: The minimum ratio of successful inferencing requests.
        :rtype: typing.Optional[float]
        """
        return self._min_endpoint_success_ratio

    @min_endpoint_success_ratio.setter
    def min_endpoint_success_ratio(self, ratio: Optional[float]) -> None:
        """Set the minimum ratio of successful inferencing requests.

        :param ratio: The minimum ratio of successful inferencing requests.
        :type ratio: typing.Optional[float]
        """
        self._min_endpoint_success_ratio = ratio

    def items(self):
        return self.__dict__.items()

    def __eq__(self, other: object) -> bool:
        """Returns True if both instances have the same values.

        This method check instances equality and returns True if both of
            the instances have the same attributes with the same values.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        if not isinstance(other, EndpointRequestSettings):
            return False
        return (
            self.request_batch_size == other.request_batch_size
            and self.min_endpoint_success_ratio == other.min_endpoint_success_ratio
        )

    def __ne__(self, other: object) -> bool:
        """Check inequality between two EndpointRequestSettings objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
