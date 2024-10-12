# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

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
    PromptSettings,
)
from azure.ai.ml.entities._job.distillation.distillation_types import (
    DistillationPromptSettings,
    EndpointRequestSettings,
)
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._util import load_from_dict


# pylint: disable=too-many-instance-attributes
@experimental
class DistillationJob(Job, JobIOMixin):
    def __init__(
        self,
        data_generation_type: str,
        data_generation_task_type: str,
        teacher_model_endpoint: str,
        student_model: Input,
        training_data: Optional[Input] = None,
        validation_data: Optional[Input] = None,
        inference_parameters: Optional[Dict] = None,
        endpoint_request_settings: Optional[EndpointRequestSettings] = None,
        prompt_settings: Optional[DistillationPromptSettings] = None,
        hyperparameters: Optional[Dict] = None,
        resources: Optional[ResourceConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        self._data_generation_type = data_generation_type
        self._data_generation_task_type = data_generation_task_type
        self._teacher_model_endpoint = teacher_model_endpoint
        self._student_model = student_model
        self._training_data = training_data
        self._validation_data = validation_data
        self._inference_parameters = inference_parameters
        self._endpoint_request_settings = endpoint_request_settings
        self._prompt_settings = prompt_settings
        self._hyperparameters = hyperparameters
        self._resources = resources

        if self._training_data is None and self._data_generation_type == DataGenerationType.LabelGeneration:
            raise ValueError(
                f"Training data can only be None when data generation type is set to "
                f"{DataGenerationType.DataGeneration}."
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
    def teacher_model_endpoint(self) -> str:
        """Get the endpoint information of the teacher model to use for data generation.
        :return: Endpoint name
        :rtype: str
        """
        return self._teacher_model_endpoint

    @teacher_model_endpoint.setter
    def teacher_model_endpoint(self, endpoint: str) -> None:
        """Set the endpoint information of the teacher model.

        :param endpoint: Serverless MaaS connection
        :type endpoint: str
        """
        self._teacher_model_endpoint = endpoint

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
        :rtype: Input
        """
        return self._training_data

    @training_data.setter
    def training_data(self, training_data: Optional[Input]) -> None:
        """Set the training data.

        :param training_data: Training data input
        :type training_data: Input
        """
        self._training_data = training_data

    @property
    def validation_data(self) -> Optional[Input]:
        """Get the validation data.

        :return: Validation data input
        :rtype: Input
        """
        return self._validation_data

    @validation_data.setter
    def validation_data(self, validation_data: Optional[Input]) -> None:
        """Set the validation data.

        :param validation_data: Validation data input
        :type validation_data: Input
        """
        self._validation_data = validation_data

    @property
    def inference_parameters(self) -> Optional[Dict]:
        """Get the parameters for endpoint inferencing.

        :return: The params for endpoint inferencing.
        :rtype: Dict
        """
        return self._inference_parameters

    @property
    def endpoint_request_settings(self) -> Optional[EndpointRequestSettings]:
        """Get the endpoint request settings.

        :return: The settings for the requests sent to the endpoint
        :rtype: Optional[EndpointRequestSettings]
        """
        return self._endpoint_request_settings

    @property
    def prompt_settings(self) -> Optional[DistillationPromptSettings]:
        """Get the settings for the prompt.

        :return: The settings for the prompt.
        :rtype: Optional[DistillationPromptSettings]
        """
        return self._prompt_settings

    @property
    def hyperparameters(self) -> Dict:
        """Get the finetuning hyperparameters.

        :return: The finetuning hyperparameters.
        :rtype: Dict
        """
        return self._hyperparameters

    @property
    def resources(self) -> Optional[ResourceConfiguration]:
        """Get the resources for data generation.
        :return: The resources for data generation.
        :rtype: Optional[ResourceConfiguration]
        """
        return self._resources

    @resources.setter
    def resources(self, resource: Optional[ResourceConfiguration]) -> None:
        """Set the resources for data generation.

        :param resource: The resources for data generation.
        :type resource: Optional[ResourceConfiguration]
        """
        self._resources = resource

    def set_teacher_model_settings(
        self,
        inference_parameters: Optional[Dict] = None,
        endpoint_request_settings: Optional[EndpointRequestSettings] = None,
    ):
        self._inference_parameters = (
            inference_parameters if inference_parameters is not None else self._inference_parameters
        )
        self._endpoint_request_settings = (
            endpoint_request_settings if endpoint_request_settings is not None else self._endpoint_request_settings
        )

    def set_prompt_settings(self, prompt_settings: Optional[DistillationPromptSettings]):
        self._prompt_settings = prompt_settings if prompt_settings is not None else self._prompt_settings

    def set_finetuning_settings(self, hyperparameters: Optional[Dict]):
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
        if isinstance(distillation.model, str):
            distillation.model = MLFlowModelJobInput(uri=distillation.model)

        print(f"properties are {self.properties}")
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

    # TODO: Remove once Distillation is added to MFE
    def _add_distillation_properties(self, properties: Dict) -> None:
        properties[AzureMLDistillationProperties.EnableDistillation] = True
        properties[AzureMLDistillationProperties.DataGenerationTaskType] = self._data_generation_task_type.upper()

        # Not needed for FT Overloaded API but needed to store data gen type
        properties[AzureMLDistillationProperties.DataGenerationType] = self._data_generation_type
        properties[f"{AzureMLDistillationProperties.TeacherModel}.endpoint_name"] = self._teacher_model_endpoint

        if self._prompt_settings:
            for setting, val in self._prompt_settings.items():
                properties[f"azureml.{setting.strip('_')}"] = val

        if self._inference_parameters:
            for inference_key, value in self._inference_parameters.items():
                properties[f"{AzureMLDistillationProperties.TeacherModel}.{inference_key}"] = value

        if self._endpoint_request_settings:
            for setting, value in self._endpoint_request_settings.items():
                properties[f"azureml.{setting.strip('_')}"] = value

        if self._resources:
            properties[f"{AzureMLDistillationProperties.InstanceType}.data_generation"] = self._resources.instance_type

    # TODO: Remove once Distillation is added to MFE
    @classmethod
    def _filter_properties(cls, properties: Dict) -> Dict:
        inference_parameters = {}
        endpoint_settings = {}
        prompt_settings = {}
        resources = {}
        teacher_model = ""
        for key, val in properties.items():
            if AzureMLDistillationProperties.TeacherModel in key:
                param = key.split(".")[-1]
                if param == "endpoint_name":
                    teacher_model = val
                else:
                    inference_parameters[param] = val
            elif AzureMLDistillationProperties.InstanceType in key:
                resources[key.split(".")[-1]] = val
            else:
                param = key.split(".")[-1]
                if param in EndpointSettings.valid_settings:
                    endpoint_settings[param] = val
                elif param in PromptSettings.valid_settings:
                    prompt_settings[param] = val

        return {
            "data_generation_task_type": properties.get(AzureMLDistillationProperties.DataGenerationTaskType),
            "data_generation_type": properties.get(AzureMLDistillationProperties.DataGenerationType),
            "teacher_model_endpoint": teacher_model,
            "inference_parameters": inference_parameters if inference_parameters else None,
            "endpoint_request_settings": EndpointRequestSettings(**endpoint_settings) if endpoint_settings else None,
            "prompt_settings": DistillationPromptSettings(**prompt_settings) if prompt_settings else None,
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
        a = super().__eq__(other)
        b = self.data_generation_type == other.data_generation_type
        c = self.data_generation_task_type == other.data_generation_task_type
        d = self.teacher_model_endpoint == other.teacher_model_endpoint
        e = self.student_model == other.student_model
        f = self.training_data == other.training_data
        g = self._inference_parameters == other._inference_parameters
        print(f"self inference params are {self._inference_parameters}")
        print(f"other inference params are {other._inference_parameters}")
        h = self._endpoint_request_settings == other._endpoint_request_settings
        i = self._prompt_settings == other._prompt_settings
        j = self._hyperparameters == other._hyperparameters
        l = self.resources == other.resources
        if not a:
            print("a is not equal")
        if not b:
            print("b is not equal")
        if not c:
            print("c is not equal")
        if not d:
            print("d is not equal")
        if not e:
            print("e is not equal")
        if not f:
            print("f is not equal")
        if not g:
            print("g is not equal")
        if not h:
            print("h is not equal")
        if not i:
            print("i is not equal")
        if not j:
            print("j is not equal")
        if not l:
            print("l is not equal")

        return (
            super().__eq__(other)
            and self.data_generation_type == other.data_generation_type
            and self.data_generation_task_type == other.data_generation_task_type
            and self.teacher_model_endpoint == other.teacher_model_endpoint
            and self.student_model == other.student_model
            and self.training_data == other.training_data
            and self._inference_parameters == other._inference_parameters
            and self._endpoint_request_settings == other._endpoint_request_settings
            and self._prompt_settings == other._prompt_settings
            and self._hyperparameters == other._hyperparameters
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
