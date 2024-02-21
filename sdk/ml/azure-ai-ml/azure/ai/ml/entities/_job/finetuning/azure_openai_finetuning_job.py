from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ModelProvider as RestModelProvider,
    AzureOpenAiFineTuning as RestAzureOpenAIFineTuning,
    FineTuningJob as RestFineTuningJob,
    JobBase as RestJobBase,
)
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from typing import Any, Dict, cast
from azure.ai.ml.entities._job.finetuning.finetuning_vertical import FineTuningVertical
from typing import cast
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class AzureOpenAIFineTuningJob(FineTuningVertical):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        # Extract any task specific settings
        model = kwargs.pop("model", None)
        task = kwargs.pop("task", None)
        training_data = kwargs.pop("training_data", None)
        validation_data = kwargs.pop("validation_data", None)
        hyperparameters = kwargs.pop("hyperparameters", None)
        if hyperparameters and cast(hyperparameters, AzureOpenAIHyperparameters) is None:
            raise ValidationException(
                category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.JOB,
                message="Hyperparameters if provided should of type AzureOpenAIHyperparameters",
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

        :return:
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
            task=self._task,
            model=self._model,
            model_provider=self._model_provider,
            training_data=self._training_data,
            validation_data=self._validation_data,
            hyper_parameters=self.hyperparameters.to_rest_object() if self.hyperparameters else None,
        )

        self._resolve_data_inputs(aoai_finetuning_vertical)

        result = RestFineTuningJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            properties=self.properties,
            fine_tuning_details=aoai_finetuning_vertical,
            outputs=to_rest_data_outputs(self.outputs),
        )
        result.name = self.name

        return result

    @classmethod
    def _from_rest_object(cls, obj: RestJobBase) -> "AzureOpenAIFineTuningJob":
        """Convert a REST object to AzureOpenAIFineTuningJob object.

        :param obj: AzureOpenAIFineTuningJob in Rest format.
        :type obj: JobBase
        :return: AzureOpenAIFineTuningJob objects.
        :rtype: AzureOpenAIFineTuningJob
        """

        properties: RestFineTuningJob = obj.properties
        finetuning_details: RestAzureOpenAIFineTuning = properties.task_details

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
            task=finetuning_details.task,
            model=finetuning_details.model,
            model_provider=finetuning_details.model_provider,
            training_data=finetuning_details.training_data,
            validation_data=finetuning_details.validation_data,
            hyperparameters=finetuning_details.hyper_parameters,
            **job_args_dict,
        )

        aoai_finetuning_job._restore_data_inputs()

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
        from azure.ai.ml._schema._finetuning.azure_openai_finetuning import AzureOpenAiFineTuningSchema

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
        loaded_data = load_from_dict(AzureOpenAiFineTuningSchema, data, context, additional_message, **kwargs)

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
        loaded_data.pop("model_provider", None)
        job = AzureOpenAIFineTuningJob(**loaded_data)
        return job

    def _to_dict(self, inside_pipeline: bool = False) -> Dict:  # pylint: disable=arguments-differ
        """Convert the object to a dictionary.

        :param inside_pipeline: whether the job is inside a pipeline or not, defaults to False
        :type inside_pipeline: bool
        :return: dictionary representation of the object.
        :rtype: typing.Dict
        """
        from azure.ai.ml._schema._finetuning.azure_openai_finetuning import AzureOpenAiFineTuningSchema

        # from azure.ai.ml._schema.pipeline.automl_node import AutoMLClassificationNodeSchema

        schema_dict: dict = {}
        # TODO: Combeback to this later
        # if inside_pipeline:
        #    schema_dict = AutoMLClassificationNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        # else:
        schema_dict = AzureOpenAiFineTuningSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

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

        if not super().__eq__(other):
            return False

    def __ne__(self, other: object) -> bool:
        """Check inequality between two AzureOpenAIFineTuningJob objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
