# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from typing import Any, Dict

from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ModelProvider as RestModelProvider,
    AzureOpenAiFineTuning as RestAzureOpenAIFineTuning,
    FineTuningJob as RestFineTuningJob,
    JobBase as RestJobBase,
)
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs

from azure.ai.ml.entities._job.finetuning.finetuning_vertical import FineTuningVertical
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._utils._experimental import experimental


@experimental
class AzureOpenAIFineTuningJob(FineTuningVertical):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        # Extract any task specific settings
        model = kwargs.pop("model", None)
        task = kwargs.pop("task", None)
        # Convert task to lowercase first letter, this is when we create
        # object from the schema, using dict object from the REST api response.
        # TextCompletion => textCompletion
        if task:
            task = task[0].lower() + task[1:]
        training_data = kwargs.pop("training_data", None)
        validation_data = kwargs.pop("validation_data", None)
        hyperparameters = kwargs.pop("hyperparameters", None)
        if hyperparameters and not isinstance(hyperparameters, AzureOpenAIHyperparameters):
            raise ValidationException(
                category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.JOB,
                message="Hyperparameters if provided should of type AzureOpenAIHyperparameters",
                no_personal_data_message="Hyperparameters if provided should of type AzureOpenAIHyperparameters",
            )

        self._hyperparameters = hyperparameters

        super().__init__(
            task=task,
            model=model,
            model_provider=RestModelProvider.AZURE_OPEN_AI,
            training_data=training_data,
            validation_data=validation_data,
            **kwargs,
        )

    @property
    def hyperparameters(self) -> AzureOpenAIHyperparameters:
        """Get hyperparameters.

        :return: Hyperparameters for finetuning the model.
        :rtype: AzureOpenAIHyperparameters
        """
        return self._hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, hyperparameters: AzureOpenAIHyperparameters) -> None:
        """Set hyperparameters.

        :param hyperparameters: Hyperparameters for finetuning the model.
        :type hyperparameters: AzureOpenAiHyperParameters
        """
        self._hyperparameters = hyperparameters

    def _to_rest_object(self) -> "RestFineTuningJob":
        """Convert CustomFineTuningVertical object to a RestFineTuningJob object.

        :return: REST object representation of this object.
        :rtype: JobBase
        """
        aoai_finetuning_vertical = RestAzureOpenAIFineTuning(
            task_type=self._task,
            model=self._model,
            model_provider=self._model_provider,
            training_data=self._training_data,
            validation_data=self._validation_data,
            hyper_parameters=self.hyperparameters._to_rest_object() if self.hyperparameters else None,
        )

        self._resolve_inputs(aoai_finetuning_vertical)

        finetuning_job = RestFineTuningJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            properties=self.properties,
            fine_tuning_details=aoai_finetuning_vertical,
            outputs=to_rest_data_outputs(self.outputs),
        )

        result = RestJobBase(properties=finetuning_job)
        result.name = self.name

        return result

    def _to_dict(self) -> Dict:  # pylint: disable=arguments-differ
        """Convert the object to a dictionary.

        :return: dictionary representation of the object.
        :rtype: typing.Dict
        """
        from azure.ai.ml._schema._finetuning.azure_openai_finetuning import AzureOpenAIFineTuningSchema

        schema_dict: dict = {}
        # TODO: Combeback to this later for FineTuningJob in Pipelines
        # if inside_pipeline:
        #    schema_dict = AutoMLClassificationNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        # else:
        schema_dict = AzureOpenAIFineTuningSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

        return schema_dict

    def __eq__(self, other: object) -> bool:
        """Returns True if both instances have the same values.

        This method check instances equality and returns True if both of
            the instances have the same attributes with the same values.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        if not isinstance(other, AzureOpenAIFineTuningJob):
            return NotImplemented

        return super().__eq__(other) and self.hyperparameters == other.hyperparameters

    def __ne__(self, other: object) -> bool:
        """Check inequality between two AzureOpenAIFineTuningJob objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)

    @classmethod
    def _from_rest_object(cls, obj: RestJobBase) -> "AzureOpenAIFineTuningJob":
        """Convert a REST object to AzureOpenAIFineTuningJob object.

        :param obj: AzureOpenAIFineTuningJob in Rest format.
        :type obj: JobBase
        :return: AzureOpenAIFineTuningJob objects.
        :rtype: AzureOpenAIFineTuningJob
        """

        properties: RestFineTuningJob = obj.properties
        finetuning_details: RestAzureOpenAIFineTuning = properties.fine_tuning_details

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

        aoai_finetuning_job = cls(
            task=finetuning_details.task_type,
            model=finetuning_details.model,
            training_data=finetuning_details.training_data,
            validation_data=finetuning_details.validation_data,
            hyperparameters=AzureOpenAIHyperparameters._from_rest_object(finetuning_details.hyper_parameters),
            **job_args_dict,
        )

        aoai_finetuning_job._restore_inputs()

        return aoai_finetuning_job

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        **kwargs: Any,
    ) -> "AzureOpenAIFineTuningJob":
        """Load from a dictionary.

        :param data: dictionary representation of the object.
        :type data: typing.Dict
        :param context: dictionary containing the context.
        :type context: typing.Dict
        :param additional_message: additional message to be added to the error message.
        :type additional_message: str
        :return: AzureOpenAIFineTuningJob object.
        :rtype: AzureOpenAIFineTuningJob
        """
        from azure.ai.ml._schema._finetuning.azure_openai_finetuning import AzureOpenAIFineTuningSchema

        # TODO: Combeback to this later - Pipeline part.
        # from azure.ai.ml._schema.pipeline.automl_node import AutoMLClassificationNodeSchema

        # if kwargs.pop("inside_pipeline", False):
        #    loaded_data = load_from_dict(
        #        AutoMLClassificationNodeSchema,
        #        data,
        #        context,
        #        additional_message,
        #        **kwargs,
        #    )
        # else:
        loaded_data = load_from_dict(AzureOpenAIFineTuningSchema, data, context, additional_message, **kwargs)

        job_instance = cls._create_instance_from_schema_dict(loaded_data)
        return job_instance

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "AzureOpenAIFineTuningJob":
        """Create an instance from a schema dictionary.

        :param loaded_data: dictionary containing the data.
        :type loaded_data: typing.Dict
        :return: AzureOpenAIFineTuningJob object.
        :rtype: AzureOpenAIFineTuningJob
        """

        job = AzureOpenAIFineTuningJob(**loaded_data)
        return job
