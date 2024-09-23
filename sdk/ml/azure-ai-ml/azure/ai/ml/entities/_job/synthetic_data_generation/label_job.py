# # ---------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # ---------------------------------------------------------

# # pylint: disable=protected-access,no-member

from typing import Any, Dict, Optional, Union

# from ..job import Job
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.synthetic_data_generation.synthetic_data_generation import SyntheticDataGeneration
from azure.ai.ml.entities._workspace.connections.connection_subtypes import ServerlessConnection


@experimental
class SyntheticDataGenerationLabelTaskJob(SyntheticDataGeneration):
    def __init__(
        self,
        data_generation_task: str,
        data_generation_task_type: str,
        teacher_model_endpoint: Union[ServerlessConnection, str],
        training_data: Input,
        validation_data: Optional[Input] = None,
        inference_parameters: Optional[dict] = None,
        **kwargs
    ):
        self._training_data = training_data
        enable_chain_of_thought = kwargs.pop("enable_chain_of_thought", False)
        enable_chain_of_density = kwargs.pop("enable_chain_of_density", False)
        endpoint_request_settings = kwargs.pop("endpoint_request_settings", None)
        super().__init__(
            data_generation_type=data_generation_task,
            data_generation_task_type=data_generation_task_type,
            teacher_model_endpoint=teacher_model_endpoint,
            validation_data=validation_data,
            enable_chain_of_thought=enable_chain_of_thought,
            enable_chain_of_density=enable_chain_of_density,
            inference_parameters=inference_parameters,
            endpoint_request_settings=endpoint_request_settings,
        )

    @property
    def training_data(self) -> Input:
        """Get the training data info.
        :return: The training data
        :rtype: Input
        """
        return self._training_data

    @training_data.setter
    def training_data(self, data: Input) -> None:
        """Set the training data path.
        :param data: Path to training data
        :type data: Input
        :return: None
        """
        self._training_data = data

    def _to_dict(self) -> dict:
        """Transform to a dict.
        :return: A dict
        :rtype: dict
        """
        return {}

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any
    ) -> "SyntheticDataGenerationLabelTaskJob":
        """Load from a dictionary.
        :param data: dictionary representation of the object.
        :type data: typing.Dict
        :param context: dictionary containing the context.
        :type context: typing.Dict
        :param additional_message: additional message to be added to the error message.
        :type additional_message: str
        :return: SyntheticDataGenerationLabelTaskJob object.
        :rtype: SyntheticDataGenerationLabelTaskJob
        """
        return SyntheticDataGenerationLabelTaskJob(
            data_generation_task="",
            data_generation_task_type="",
            teacher_model_endpoint=additional_message,
            training_data=data["training_data"],
            validation_data=None,
            inference_parameters=context,
            **kwargs
        )
