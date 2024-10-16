# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azure.ai.ml._utils._experimental import experimental


@experimental
class DistillationPromptSettings:
    def __init__(
        self,
        enable_chain_of_thought: bool = False,
        enable_chain_of_density: bool = False,
        max_len_summary: Optional[int] = None,
        # custom_prompt: Optional[str] = None
    ):
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
        :rtype: int
        """
        return self._max_len_summary

    @max_len_summary.setter
    def max_len_summary(self, length: Optional[int]) -> None:
        """Set the number of tokens to use for summarization.

        :param length: The number of tokens to use for summarization.
        :type length: int
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
        if not isinstance(other, DistillationPromptSettings):
            return False
        return (
            self.enable_chain_of_thought == other.enable_chain_of_thought
            and self.enable_chain_of_density == other.enable_chain_of_density
            and self.max_len_summary == other.max_len_summary
            # self.custom_prompt == other.custom_prompt
        )

    def __ne__(self, other: object) -> bool:
        """Check inequality between two TeacherModelEndpoint objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)


@experimental
class EndpointRequestSettings:
    def __init__(self, request_batch_size: Optional[int] = None, min_endpoint_success_ratio: Optional[float] = None):
        self._request_batch_size = request_batch_size
        self._min_endpoint_success_ratio = min_endpoint_success_ratio

    @property
    def request_batch_size(self) -> Optional[int]:
        """Get the number of inference requests to send to the teacher model as a batch.

        :return: The number of inference requests to send to the teacher model as a batch.
        :rtype: int
        """
        return self._request_batch_size

    @request_batch_size.setter
    def request_batch_size(self, value: Optional[int]) -> None:
        """Set the number of inference requests to send to the teacher model as a batch.

        :param value: The number of inference requests to send to the teacher model as a batch.
        :type value: int
        """
        self._request_batch_size = value

    @property
    def min_endpoint_success_ratio(self) -> Optional[float]:
        """Get the minimum ratio of successful inferencing requests.
        :return: The minimum ratio of successful inferencing requests.
        :rtype: float
        """
        return self._min_endpoint_success_ratio

    @min_endpoint_success_ratio.setter
    def min_endpoint_success_ratio(self, ratio: Optional[float]) -> None:
        """Set the minimum ratio of successful inferencing requests.

        :param ratio: The minimum ratio of successful inferencing requests.
        :type ratio: float
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
