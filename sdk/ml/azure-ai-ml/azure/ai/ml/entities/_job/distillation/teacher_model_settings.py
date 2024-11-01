# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._job.distillation.endpoint_request_settings import EndpointRequestSettings


@experimental
class TeacherModelSettings:
    def __init__(
        self,
        *,
        inference_parameters: Optional[Dict] = None,
        endpoint_request_settings: Optional[EndpointRequestSettings] = None,
    ):
        """Initialize TeacherModelSettings

        :param inference_parameters: The inference parameters inferencing requests will use, defaults to None
        :type inference_parameters: typing.Optional[typing.Dict], optional
        :param endpoint_request_settings: The settings to use for the endpoint, defaults to None
        :type endpoint_request_settings: typing.Optional[EndpointRequestSettings], optional
        """
        self._inference_parameters = inference_parameters
        self._endpoint_request_settings = endpoint_request_settings

    @property
    def inference_parameters(self) -> Optional[Dict]:
        """Get the inference parameters.

        :return: The inference parameters.
        :rtype: typing.Optional[typing.Dict]
        """
        return self._inference_parameters

    @inference_parameters.setter
    def inference_parameters(self, params: Optional[Dict]) -> None:
        """Set the inference parameters.

        :param params: Inference parameters.
        :type params: typing.Optional[typing.Dict]
        """
        self._inference_parameters = params

    @property
    def endpoint_request_settings(self) -> Optional[EndpointRequestSettings]:
        """Get the endpoint request settings.

        :return: The endpoint request settings.
        :rtype: typing.Optional[EndpointRequestSettings]
        """
        return self._endpoint_request_settings

    @endpoint_request_settings.setter
    def endpoint_request_settings(self, endpoint_settings: Optional[EndpointRequestSettings]) -> None:
        """Set the endpoint request settings.

        :param endpoint_settings: Endpoint request settings
        :type endpoint_settings: typing.Optional[EndpointRequestSettings]
        """
        self._endpoint_request_settings = endpoint_settings

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
        if not isinstance(other, TeacherModelSettings):
            return False
        return (
            self.inference_parameters == other.inference_parameters
            and self.endpoint_request_settings == other.endpoint_request_settings
        )

    def __ne__(self, other: object) -> bool:
        """Check inequality between two TeacherModelSettings objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
