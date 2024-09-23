# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Optional, Union

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.synthetic_data_generation.synthetic_data_generation_job import SyntheticDataGenerationJob
from azure.ai.ml.entities._workspace.connections.connection_subtypes import ServerlessConnection


@experimental
class SyntheticDataGeneration(SyntheticDataGenerationJob):
    def __init__(
        self,
        *,
        data_generation_type: str,
        data_generation_task_type: str,
        teacher_model_endpoint: Union[ServerlessConnection, str],
        validation_data: Optional[Input],
        enable_chain_of_thought: Optional[bool] = False,
        enable_chain_of_density: Optional[bool] = False,
        inference_parameters: Optional[dict] = None,
        endpoint_request_settings: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        self._data_generation_type = data_generation_type
        self._data_generation_task_type = data_generation_task_type
        self._teacher_model_endpoint = teacher_model_endpoint
        self._validation_data = validation_data
        self._enable_chain_of_thought = enable_chain_of_thought
        self._enable_chain_of_density = enable_chain_of_density
        self._inference_parameters = inference_parameters
        self._endpoint_request_settings = endpoint_request_settings
        super().__init__(**kwargs)

    @property
    def data_generation_type(self) -> str:
        """Get the type of synthetic data generation.

        :return: The type of task to run. Possible values include: "Label_Generation" and "Data_Generation".
        :rtype: str
        """
        return self._data_generation_type

    @data_generation_type.setter
    def data_generation_type(self, data_generation_type: str) -> None:
        """Set the synthetic data generation type.

        :param data_generation_type: The type of task to run. Possible values include: "Label_Generation"
                                     and "Data_Generation".
        :type data_generation_type: str

        :return: None
        """
        self._data_generation_type = data_generation_type

    @property
    def data_generation_task_type(self) -> str:
        """Get synthetic data generation task.

        :return: The type of task to run. Possible values include: "nli", "nlu_qa", "conversational",
                 "math", and "summarization"
        :rtype: str
        """
        return self._data_generation_task_type

    @data_generation_task_type.setter
    def data_generation_task_type(self, data_generation_task_type: str) -> None:
        """Set synthetic data generation task type.

        :param data_generation_task_type: The type of task to run. Possible values include: "nli",
                                          "nlu_qa", "conversational", "math", and "summarization"
        :type data_generation_task_type: str

        :return: None
        """
        self._data_generation_task_type = data_generation_task_type

    @property
    def teacher_model_endpoint(self) -> Union[ServerlessConnection, str]:
        """The endpoint information of the teacher model to use for data or label generation.
        :return: Serverless MaaS connection or endpoint name
        :rtype: Union[ServerlessConnection, str]
        """
        return self._teacher_model_endpoint

    @teacher_model_endpoint.setter
    def teacher_model_endpoint(self, endpoint: Union[ServerlessConnection, str]) -> None:
        """Set the endpoint information of the teacher model.

        :param endpoint: Serverless MaaS connection or endpoint name
        :type endpoint: Union[ServerlessConnection, str]
        """
        self._teacher_model_endpoint = endpoint

    @property
    def validation_data(self) -> Optional[Input]:
        """The Input uri file to use that contains the validation data for label generation.
        :return Optional Input uri file
        :rtype Optional Input
        """
        return self._validation_data

    @validation_data.setter
    def validation_data(self, data: Optional[Input]) -> None:
        """Set the path to the validation data.

        :param data: Input path to the validation data.
        :type data: Optional Input"""
        self._validation_data = data

    @property
    def enable_chain_of_thought(self) -> Optional[bool]:
        """Get whether or not chain of thought is enabled
        :return: Whether or not chain of thought is enabled.
        :rtype: bool
        """
        return self._enable_chain_of_thought

    @enable_chain_of_thought.setter
    def enable_chain_of_thought(self, value: Optional[bool]) -> None:
        """Set chain of thought.

        :param value: Whether or not chain of thought is enabled.
        :type value: bool
        """
        self._enable_chain_of_thought = value

    @property
    def enable_chain_of_density(self) -> Optional[bool]:
        """Get whether or not chain of density is enabled.

        :return: Whether or not chain of thought is enabled
        :rtype: bool
        """
        return self._enable_chain_of_density

    @enable_chain_of_density.setter
    def enable_chain_of_density(self, value: Optional[bool]) -> None:
        """Set whether or not chain of thought is enabled.

        :param value: Whether or not chain of thought is enabled
        :type value: bool
        """
        self._enable_chain_of_density = value

    @property
    def inference_parameters(self) -> Optional[dict]:
        """Get the parameters for endpoint inferencing

        :return: The params for endpoint inferencing
        :rtype: dict
        """
        return self._inference_parameters

    @inference_parameters.setter
    def inference_parameters(self, params: Optional[dict]) -> None:
        """Set the inference parameters.

        :param params: The params for endpoint inferencing
        :type params: Optional[dict]
        """
        self._inference_parameters = params

    @property
    def endpoint_request_settings(self) -> Optional[dict]:
        """Get the endpoint request settings.

        :return: The settings for the requests sent to the endpoint
        :rtype: dict
        """
        return self._endpoint_request_settings

    @endpoint_request_settings.setter
    def endpoint_request_settings(self, settings: Optional[dict]) -> None:
        """Set the endpoint request settings.

        :param settings: The settings for the requests sent to the endpoint
        :type settings: Optional[dict]
        """
        self._endpoint_request_settings = settings
