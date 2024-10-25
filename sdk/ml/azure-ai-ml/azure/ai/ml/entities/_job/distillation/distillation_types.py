# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional

from azure.ai.ml._utils._experimental import experimental


@experimental
class PromptSettings:
    def __init__(
        self,
        *,
        enable_chain_of_thought: bool = False,
        enable_chain_of_density: bool = False,
        max_len_summary: Optional[int] = None,
        # custom_prompt: Optional[str] = None
    ):
        """Initialize PromptSettings.

        :param enable_chain_of_thought: Whether or not to enable chain of thought which modifies the system prompt
            used. Can be used for all `data_generation_task_type` values except `SUMMARIZATION`, defaults to False
        :type enable_chain_of_thought: bool, optional
        :param enable_chain_of_density: Whether or not to enable chain of density which modifies the system prompt
            used. Can only be used for `data_generation_task_type` of `SUMMARIZATION`, defaults to False
        :type enable_chain_of_density: bool, optional
        :param max_len_summary: The maximum length of the summary generated for data_generation_task_type` of
            `SUMMARIZATION`, defaults to None
        :type max_len_summary: typing.Optional[int]
        """
        self._enable_chain_of_thought = enable_chain_of_thought
        self._enable_chain_of_density = enable_chain_of_density
        self._max_len_summary = max_len_summary
        # self._custom_prompt = custom_prompt

    @property
    def enable_chain_of_thought(self) -> bool:
        """Get whether or not chain of thought is enabled.

        :return: Whether or not chain of thought is enabled.
        :rtype: bool
        """
        return self._enable_chain_of_thought

    @enable_chain_of_thought.setter
    def enable_chain_of_thought(self, value: bool) -> None:
        """Set chain of thought.

        :param value: Whether or not chain of thought is enabled.
        :type value: bool
        """
        self._enable_chain_of_thought = value

    @property
    def enable_chain_of_density(self) -> bool:
        """Get whether or not chain of density is enabled.

        :return: Whether or not chain of thought is enabled
        :rtype: bool
        """
        return self._enable_chain_of_density

    @enable_chain_of_density.setter
    def enable_chain_of_density(self, value: bool) -> None:
        """Set whether or not chain of thought is enabled.

        :param value: Whether or not chain of thought is enabled
        :type value: bool
        """
        self._enable_chain_of_density = value

    @property
    def max_len_summary(self) -> Optional[int]:
        """The number of tokens to use for summarization.

        :return: The number of tokens to use for summarization
        :rtype: typing.Optional[int]
        """
        return self._max_len_summary

    @max_len_summary.setter
    def max_len_summary(self, length: Optional[int]) -> None:
        """Set the number of tokens to use for summarization.

        :param length: The number of tokens to use for summarization.
        :type length: typing.Optional[int]
        """
        self._max_len_summary = length

    # @property
    # def custom_prompt(self) -> Optional[str]:
    #     """Get the custom system prompt to use for inferencing.
    #     :return: The custom prompt to use for inferencing.
    #     :rtype: Optional[str]
    #     """
    #     return self._custom_prompt

    # @custom_prompt.setter
    # def custom_prompt(self, prompt: Optional[str]) -> None:
    #     """Set the custom prompt to use for inferencing.

    #     :param prompt: The custom prompt to use for inferencing.
    #     :type prompt: Optional[str]
    #     """
    #     self._custom_prompt = prompt

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
        if not isinstance(other, PromptSettings):
            return False
        return (
            self.enable_chain_of_thought == other.enable_chain_of_thought
            and self.enable_chain_of_density == other.enable_chain_of_density
            and self.max_len_summary == other.max_len_summary
            # self.custom_prompt == other.custom_prompt
        )

    def __ne__(self, other: object) -> bool:
        """Check inequality between two PromptSettings objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)


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
