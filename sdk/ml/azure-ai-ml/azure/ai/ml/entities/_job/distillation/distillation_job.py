# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    CustomModelFineTuning as RestCustomModelFineTuningVertical,
)
from azure.ai.ml._restclient.v2024_01_01_preview.models import FineTuningJob as RestFineTuningJob
from azure.ai.ml._restclient.v2024_01_01_preview.models import JobBase as RestJobBase
from azure.ai.ml._restclient.v2024_01_01_preview.models import MLFlowModelJobInput, UriFileJobInput
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import DataGenerationType, JobType
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE, AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.distillation.constants import (
    AzureMLDistillationProperties,
    EndpointSettings,
    PromptSettingKeys,
)
from azure.ai.ml.entities._job.distillation.endpoint_request_settings import EndpointRequestSettings
from azure.ai.ml.entities._job.distillation.prompt_settings import PromptSettings
from azure.ai.ml.entities._job.distillation.teacher_model_settings import TeacherModelSettings
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._workspace.connections.workspace_connection import WorkspaceConnection


# pylint: disable=too-many-instance-attributes
@experimental
class DistillationJob(Job, JobIOMixin):
    def __init__(
        self,
        *,
        data_generation_type: str,
        data_generation_task_type: str,
        teacher_model_endpoint_connection: WorkspaceConnection,
        student_model: Input,
        training_data: Optional[Input] = None,
        validation_data: Optional[Input] = None,
        teacher_model_settings: Optional[TeacherModelSettings] = None,
        prompt_settings: Optional[PromptSettings] = None,
        hyperparameters: Optional[Dict] = None,
        resources: Optional[ResourceConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        self._data_generation_type = data_generation_type
        self._data_generation_task_type = data_generation_task_type
        self._teacher_model_endpoint_connection = teacher_model_endpoint_connection
        self._student_model = student_model
        self._training_data = training_data
        self._validation_data = validation_data
        self._teacher_model_settings = teacher_model_settings
        self._prompt_settings = prompt_settings
        self._hyperparameters = hyperparameters
        self._resources = resources

        if self._training_data is None and self._data_generation_type == DataGenerationType.LABEL_GENERATION:
            raise ValueError(
                f"Training data can not be None when data generation type is set to "
                f"{DataGenerationType.LABEL_GENERATION}."
            )

        if self._validation_data is None and self._data_generation_type == DataGenerationType.LABEL_GENERATION:
            raise ValueError(
                f"Validation data can not be None when data generation type is set to "
                f"{DataGenerationType.LABEL_GENERATION}."
            )

        kwargs[TYPE] = JobType.DISTILLATION
        self._outputs = kwargs.pop("outputs", None)
        super().__init__(**kwargs)

    @property
    def data_generation_type(self) -> str:
        """Get the type of synthetic data generation to perform.

        :return: str representing the type of synthetic data generation to perform.
        :rtype: str
        """
        return self._data_generation_type

    @data_generation_type.setter
    def data_generation_type(self, task: str) -> None:
        """Set the data generation task.

        :param task: The data generation task. Possible values include 'Label_Generation' and 'Data_Generation'.
        :type task: str
        """
        self._data_generation_type = task

    @property
    def data_generation_task_type(self) -> str:
        """Get the type of synthetic data to generate.

        :return: str representing the type of synthetic data to generate.
        :rtype: str
        """
        return self._data_generation_task_type

    @data_generation_task_type.setter
    def data_generation_task_type(self, task: str) -> None:
        """Set the data generation type.

        :param task: The data generation type. Possible values include 'nli', 'nlu_qa', 'conversational',
                     'math', and 'summarization'.
        :type task: str
        """
        self._data_generation_task_type = task

    @property
    def teacher_model_endpoint_connection(self) -> WorkspaceConnection:
        """Get the endpoint connection of the teacher model to use for data generation.

        :return: Endpoint connection
        :rtype: WorkspaceConnection
        """
        return self._teacher_model_endpoint_connection

    @teacher_model_endpoint_connection.setter
    def teacher_model_endpoint_connection(self, connection: WorkspaceConnection) -> None:
        """Set the endpoint information of the teacher model.

        :param connection: Workspace connection
        :type connection: WorkspaceConnection
        """
        self._teacher_model_endpoint_connection = connection

    @property
    def student_model(self) -> Input:
        """Get the student model to be trained with synthetic data

        :return: The student model to be finetuned
        :rtype: Input
        """
        return self._student_model

    @student_model.setter
    def student_model(self, model: Input) -> None:
        """Set the student model to be trained.

        :param model: The model to use for finetuning
        :type model: Input
        """
        self._student_model = model

    @property
    def training_data(self) -> Optional[Input]:
        """Get the training data.

        :return: Training data input
        :rtype: typing.Optional[Input]
        """
        return self._training_data

    @training_data.setter
    def training_data(self, training_data: Optional[Input]) -> None:
        """Set the training data.

        :param training_data: Training data input
        :type training_data: typing.Optional[Input]
        """
        self._training_data = training_data

    @property
    def validation_data(self) -> Optional[Input]:
        """Get the validation data.

        :return: Validation data input
        :rtype: typing.Optional[Input]
        """
        return self._validation_data

    @validation_data.setter
    def validation_data(self, validation_data: Optional[Input]) -> None:
        """Set the validation data.

        :param validation_data: Validation data input
        :type validation_data: typing.Optional[Input]
        """
        self._validation_data = validation_data

    @property
    def teacher_model_settings(self) -> Optional[TeacherModelSettings]:
        """Get the teacher model settings.

        :return: The settings for the teacher model to use.
        :rtype: typing.Optional[TeacherModelSettings]
        """
        return self._teacher_model_settings

    @property
    def prompt_settings(self) -> Optional[PromptSettings]:
        """Get the settings for the prompt.

        :return: The settings for the prompt.
        :rtype: typing.Optional[PromptSettings]
        """
        return self._prompt_settings

    @property
    def hyperparameters(self) -> Optional[Dict]:
        """Get the finetuning hyperparameters.

        :return: The finetuning hyperparameters.
        :rtype: typing.Optional[typing.Dict]
        """
        return self._hyperparameters

    @property
    def resources(self) -> Optional[ResourceConfiguration]:
        """Get the resources for data generation.

        :return: The resources for data generation.
        :rtype: typing.Optional[ResourceConfiguration]
        """
        return self._resources

    @resources.setter
    def resources(self, resource: Optional[ResourceConfiguration]) -> None:
        """Set the resources for data generation.

        :param resource: The resources for data generation.
        :type resource: typing.Optional[ResourceConfiguration]
        """
        self._resources = resource

    def set_teacher_model_settings(
        self,
        inference_parameters: Optional[Dict] = None,
        endpoint_request_settings: Optional[EndpointRequestSettings] = None,
    ):
        """Set settings related to the teacher model.

        :param inference_parameters: Settings the teacher model uses during inferencing.
        :type inference_parameters: typing.Optional[typing.Dict]
        :param endpoint_request_settings: Settings for inference requests to the endpoint
        :type endpoint_request_settings: typing.Optional[EndpointRequestSettings]
        """
        self._teacher_model_settings = TeacherModelSettings(
            inference_parameters=inference_parameters, endpoint_request_settings=endpoint_request_settings
        )

    def set_prompt_settings(self, prompt_settings: Optional[PromptSettings]):
        """Set settings related to the system prompt used for generating data.

        :param prompt_settings: Settings related to the system prompt used for generating data.
        :type prompt_settings: typing.Optional[PromptSettings]
        """
        self._prompt_settings = prompt_settings if prompt_settings is not None else self._prompt_settings

    def set_finetuning_settings(self, hyperparameters: Optional[Dict]):
        """Set the hyperparamters for finetuning.

        :param hyperparameters: The hyperparameters for finetuning.
        :type hyperparameters: typing.Optional[typing.Dict]
        """
        self._hyperparameters = hyperparameters if hyperparameters is not None else self._hyperparameters

    def _to_dict(self) -> Dict:  # pylint: disable=arguments-differ
        """Convert the object to a dictionary.

        :return: dictionary representation of the object.
        :rtype: typing.Dict
        """
        from azure.ai.ml._schema._distillation.distillation_job import DistillationJobSchema

        schema_dict: dict = {}
        schema_dict = DistillationJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

        return schema_dict

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        **kwargs: Any,
    ) -> "DistillationJob":
        """Load from a dictionary.

        :param data: dictionary representation of the object.
        :type data: typing.Dict
        :param context: dictionary containing the context.
        :type context: typing.Dict
        :param additional_message: additional message to be added to the error message.
        :type additional_message: str
        :return: DistillationJob object.
        :rtype: DistillationJob
        """
        from azure.ai.ml._schema._distillation.distillation_job import DistillationJobSchema

        loaded_data = load_from_dict(DistillationJobSchema, data, context, additional_message, **kwargs)

        training_data = loaded_data.get("training_data", None)
        if isinstance(training_data, str):
            loaded_data["training_data"] = Input(type="uri_file", path=training_data)

        validation_data = loaded_data.get("validation_data", None)
        if isinstance(validation_data, str):
            loaded_data["validation_data"] = Input(type="uri_file", path=validation_data)

        student_model = loaded_data.get("student_model", None)
        if isinstance(student_model, str):
            loaded_data["student_model"] = Input(type=AssetTypes.URI_FILE, path=student_model)

        job_instance = DistillationJob(**loaded_data)
        return job_instance

    @classmethod
    def _from_rest_object(cls, obj: RestJobBase) -> "DistillationJob":
        """Convert a REST object to DistillationJob object.

        :param obj: CustomModelFineTuningJob in Rest format.
        :type obj: JobBase
        :return: DistillationJob objects.
        :rtype: DistillationJob
        """
        properties: RestFineTuningJob = obj.properties
        finetuning_details: RestCustomModelFineTuningVertical = properties.fine_tuning_details

        job_kwargs_dict = DistillationJob._filter_properties(properties=properties.properties)

        job_args_dict = {
            "id": obj.id,
            "name": obj.name,
            "description": properties.description,
            "tags": properties.tags,
            "properties": properties.properties,
            "experiment_name": properties.experiment_name,
            "status": properties.status,
            "creation_context": obj.system_data,
            "display_name": properties.display_name,
            "outputs": from_rest_data_outputs(properties.outputs),
        }

        distillation_job = cls(
            student_model=finetuning_details.model,
            training_data=finetuning_details.training_data,
            validation_data=finetuning_details.validation_data,
            hyperparameters=finetuning_details.hyper_parameters,
            **job_kwargs_dict,
            **job_args_dict,
        )

        distillation_job._restore_inputs()

        return distillation_job

    def _to_rest_object(self) -> "RestFineTuningJob":
        """Convert DistillationJob object to a RestFineTuningJob object.

        :return: REST object representation of this object.
        :rtype: JobBase
        """
        distillation = RestCustomModelFineTuningVertical(
            task_type="ChatCompletion",
            model=self.student_model,
            model_provider="Custom",
            training_data=self.training_data,
            validation_data=self.validation_data,
            hyper_parameters=self._hyperparameters,
        )

        if isinstance(distillation.training_data, Input):
            distillation.training_data = UriFileJobInput(uri=distillation.training_data.path)
        if isinstance(distillation.validation_data, Input):
            distillation.validation_data = UriFileJobInput(uri=distillation.validation_data.path)
        if isinstance(distillation.model, Input):
            distillation.model = MLFlowModelJobInput(uri=distillation.model.path)

        self._add_distillation_properties(self.properties)

        finetuning_job = RestFineTuningJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            properties=self.properties,
            fine_tuning_details=distillation,
            outputs=to_rest_data_outputs(self.outputs),
        )

        result = RestJobBase(properties=finetuning_job)
        result.name = self.name

        return result

    @classmethod
    def _load_from_rest(cls, obj: RestJobBase) -> "DistillationJob":
        """Loads the rest object to a dict containing items to init the AutoMLJob objects.

        :param obj: Azure Resource Manager resource envelope.
        :type obj: JobBase
        :raises ValidationException: task type validation error
        :return: A DistillationJob
        :rtype: DistillationJob
        """
        return DistillationJob._from_rest_object(obj)

    # TODO: Remove once Distillation is added to MFE
    def _add_distillation_properties(self, properties: Dict) -> None:
        """Adds DistillationJob attributes to properties to pass into the FT Overloaded API property bag

        :param properties: Current distillation properties
        :type properties: typing.Dict
        """
        properties[AzureMLDistillationProperties.ENABLE_DISTILLATION] = True
        properties[AzureMLDistillationProperties.DATA_GENERATION_TASK_TYPE] = self._data_generation_task_type.upper()
        properties[f"{AzureMLDistillationProperties.TEACHER_MODEL}.endpoint_name"] = (
            self._teacher_model_endpoint_connection.name
        )

        # Not needed for FT Overload API but additional info needed to convert from REST object to Distillation object
        properties[AzureMLDistillationProperties.DATA_GENERATION_TYPE] = self._data_generation_type
        properties[AzureMLDistillationProperties.CONNECTION_INFORMATION] = json.dumps(
            self._teacher_model_endpoint_connection._to_dict()  # pylint: disable=protected-access
        )

        if self._prompt_settings:
            for setting, value in self._prompt_settings.items():
                if value is not None:
                    properties[f"azureml.{setting.strip('_')}"] = value

        if self._teacher_model_settings:
            inference_settings = self._teacher_model_settings.inference_parameters
            endpoint_settings = self._teacher_model_settings.endpoint_request_settings

            if inference_settings:
                for inference_key, value in inference_settings.items():
                    if value is not None:
                        properties[f"{AzureMLDistillationProperties.TEACHER_MODEL}.{inference_key}"] = value

            if endpoint_settings:
                for setting, value in endpoint_settings.items():
                    if value is not None:
                        properties[f"azureml.{setting.strip('_')}"] = value

        if self._resources and self._resources.instance_type:
            properties[f"{AzureMLDistillationProperties.INSTANCE_TYPE}.data_generation"] = self._resources.instance_type

    # TODO: Remove once Distillation is added to MFE
    @classmethod
    def _filter_properties(cls, properties: Dict) -> Dict:
        """Convert properties from REST object back to their original states.

        :param properties: Properties from a REST object
        :type properties: typing.Dict
        :return: A dict that can be used to create a DistillationJob
        :rtype: typing.Dict
        """
        inference_parameters = {}
        endpoint_settings = {}
        prompt_settings = {}
        resources = {}
        teacher_settings = {}
        teacher_model_info = ""
        for key, val in properties.items():
            param = key.split(".")[-1]
            if AzureMLDistillationProperties.TEACHER_MODEL in key and param != "endpoint_name":
                inference_parameters[param] = val
            elif AzureMLDistillationProperties.INSTANCE_TYPE in key:
                resources[key.split(".")[1]] = val
            elif AzureMLDistillationProperties.CONNECTION_INFORMATION in key:
                teacher_model_info = val
            else:
                if param in EndpointSettings.VALID_SETTINGS:
                    endpoint_settings[param] = val
                elif param in PromptSettingKeys.VALID_SETTINGS:
                    prompt_settings[param] = val

        if inference_parameters:
            teacher_settings["inference_parameters"] = inference_parameters
        if endpoint_settings:
            teacher_settings["endpoint_request_settings"] = EndpointRequestSettings(**endpoint_settings)  # type: ignore

        return {
            "data_generation_task_type": properties.get(AzureMLDistillationProperties.DATA_GENERATION_TASK_TYPE),
            "data_generation_type": properties.get(AzureMLDistillationProperties.DATA_GENERATION_TYPE),
            "teacher_model_endpoint_connection": WorkspaceConnection._load(  # pylint: disable=protected-access
                data=json.loads(teacher_model_info)
            ),
            "teacher_model_settings": (
                TeacherModelSettings(**teacher_settings) if teacher_settings else None  # type: ignore
            ),
            "prompt_settings": PromptSettings(**prompt_settings) if prompt_settings else None,
            "resources": ResourceConfiguration(**resources) if resources else None,
        }

    def _restore_inputs(self) -> None:
        """Restore UriFileJobInputs to JobInputs within data_settings."""
        if isinstance(self.training_data, UriFileJobInput):
            self.training_data = Input(
                type=AssetTypes.URI_FILE, path=self.training_data.uri  # pylint: disable=no-member
            )
        if isinstance(self.validation_data, UriFileJobInput):
            self.validation_data = Input(
                type=AssetTypes.URI_FILE, path=self.validation_data.uri  # pylint: disable=no-member
            )
        if isinstance(self.student_model, MLFlowModelJobInput):
            self.student_model = Input(
                type=AssetTypes.MLFLOW_MODEL, path=self.student_model.uri
            )  # pylint: disable=no-member

    def __eq__(self, other: object) -> bool:
        """Returns True if both instances have the same values.

        This method check instances equality and returns True if both of
        the instances have the same attributes with the same values.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        if not isinstance(other, DistillationJob):
            return False
        return (
            super().__eq__(other)
            and self.data_generation_type == other.data_generation_type
            and self.data_generation_task_type == other.data_generation_task_type
            and self.teacher_model_endpoint_connection.name == other.teacher_model_endpoint_connection.name
            and self.student_model == other.student_model
            and self.training_data == other.training_data
            and self.validation_data == other.validation_data
            and self.teacher_model_settings == other.teacher_model_settings
            and self.prompt_settings == other.prompt_settings
            and self.hyperparameters == other.hyperparameters
            and self.resources == other.resources
        )

    def __ne__(self, other: object) -> bool:
        """Check inequality between two DistillationJob objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
