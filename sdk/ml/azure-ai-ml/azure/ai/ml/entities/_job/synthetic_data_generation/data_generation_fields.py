# # ---------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._mixins import RestTranslatableMixin


@experimental
class EndpointName(RestTranslatableMixin):
    """Endpoint name of teacher model for synthetic data generation"""

    def __init__(self, *, teacher_model_endpoint_name: str):
        """Initialize Endpoint Information.

        param teacher_model_endpoint_name: Name of the endpoint of the teacher model
        type teacher_model_endpoint_name: str
        """
        self._teacher_model_endpoint_name = teacher_model_endpoint_name

    @property
    def teacher_model_endpoint_name(self) -> str:
        """Get the name of the teacher model endpoint
        :return: The name of the teacher model endpoint
        :rtype: str
        """
        return self._teacher_model_endpoint_name

    @teacher_model_endpoint_name.setter
    def teacher_model_endpoint_name(self, value: str) -> None:
        """Set the name of the teacher model endpoint.
        :param value: The name of the teacher model endpoint
        :type value: str
        """
        self._teacher_model_endpoint_name = value


@experimental
class EndpointUri(RestTranslatableMixin):
    """Endpoint url and key."""

    def __init__(self, *, uri: str, key: str):
        """Initialize the endpoint consumption information.

        param uri: The endpoint uri to send requests to
        type batch_size: str
        param key: The endpoint authentication key
        type min_endpoint_success_ratio: str
        """
        self._uri = uri
        self._key = key

    @property
    def uri(self) -> str:
        """Get the endpoint uri
        :return: The endpoint uri
        :rtype: str
        """
        return self._uri

    @uri.setter
    def uri(self, value: str) -> None:
        """Set the endpoint uri.

        :param value: The endpoint uri
        :type value: str

        :return: None
        """
        self._uri = value

    @property
    def key(self) -> str:
        """The endpoint authentication key.
        :return: Endpoint Authentication key
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        """Set the endpoint authentication key.

        :param value: The endpoint authentication key
        :type value: str

        :return: None
        """
        self._key = value


@experimental
class EndpointRequestSettings(RestTranslatableMixin):
    """Endpoint request settings."""

    def __init__(self, *, request_batch_size: Optional[int], min_endpoint_success_ratio: Optional[float]):
        """Initialize Endpoint Request Settings.

        param request_batch_size: Number of requests to send to the endpoint at once
        type batch_size: Optional[int]
        param min_endpoint_success_ratio: The minimum ratio required where the endpoint
                                          successfully returned a response.
        type min_endpoint_success_ratio: Optional[float]
        """
        self._request_batch_size = request_batch_size
        self._min_endpoint_success_ratio = min_endpoint_success_ratio

    @property
    def request_batch_size(self) -> Optional[int]:
        """Get the batch size for requests.
        :return: The batch size
        :rtype: Optional[int]
        """
        return self._request_batch_size

    @request_batch_size.setter
    def request_batch_size(self, value: Optional[int]) -> None:
        """Set the number of requests to batch together.

        :param value: The batch size number
        :type value: Optional[int]

        :return: None
        """
        self._request_batch_size = value

    @property
    def min_endpoint_success_ratio(self) -> Optional[float]:
        """Get the minimum ratio of responses required to return successfully.
        :return: The minimum ratio of responses required to process successfully
        :rtype: Optional[float]
        """
        return self._min_endpoint_success_ratio

    @min_endpoint_success_ratio.setter
    def min_endpoint_success_ratio(self, value: Optional[float]) -> None:
        """Set the minimum ratio of responses required to return successfully.

        :param value: The minimum ratio of responses required to return successfully.
        :type value: Optional[float]

        return: None
        """
        self._min_endpoint_success_ratio = value
