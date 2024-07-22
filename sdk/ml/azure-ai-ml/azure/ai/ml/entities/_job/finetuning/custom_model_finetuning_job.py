# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from typing import Any, Dict

from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ModelProvider as RestModelProvider,
    CustomModelFineTuning as RestCustomModelFineTuningVertical,
    FineTuningJob as RestFineTuningJob,
    JobBase as RestJobBase,
)
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._job.finetuning.finetuning_vertical import FineTuningVertical
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils._experimental import experimental


@experimental
class CustomModelFineTuningJob(FineTuningVertical):
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
        self._hyperparameters = kwargs.pop("hyperparameters", None)
        super().__init__(
            task=task,
            model=model,
            model_provider=RestModelProvider.CUSTOM,
            training_data=training_data,
            validation_data=validation_data,
            **kwargs,
        )

    @property
    def hyperparameters(self) -> Dict[str, str]:
        """Get hyperparameters.

        :return:
        :rtype: hyperparameters: Dict[str,str]
        """
        return self._hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, hyperparameters: Dict[str, str]) -> None:
        """Set hyperparameters.

        :param hyperparameters: Hyperparameters for finetuning the model
        :type hyperparameters: Dict[str,str]
        """
        self._hyperparameters = hyperparameters

    def _to_rest_object(self) -> "RestFineTuningJob":
        """Convert CustomFineTuningVertical object to a RestFineTuningJob object.

        :return: REST object representation of this object.
        :rtype: JobBase
        """
        custom_finetuning_vertical = RestCustomModelFineTuningVertical(
            task_type=self._task,
            model=self._model,
            model_provider=self._model_provider,
            training_data=self._training_data,
            validation_data=self._validation_data,
            hyper_parameters=self._hyperparameters,
        )
        self._resolve_inputs(custom_finetuning_vertical)

        finetuning_job = RestFineTuningJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            properties=self.properties,
            fine_tuning_details=custom_finetuning_vertical,
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
        from azure.ai.ml._schema._finetuning.custom_model_finetuning import CustomModelFineTuningSchema

        schema_dict: dict = {}
        # TODO: Combeback to this later for FineTuningJob in pipeline
        # if inside_pipeline:
        #    schema_dict = AutoMLClassificationNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        # else:
        schema_dict = CustomModelFineTuningSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

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
        if not isinstance(other, CustomModelFineTuningJob):
            return NotImplemented

        return super().__eq__(other) and self.hyperparameters == other.hyperparameters

    def __ne__(self, other: object) -> bool:
        """Check inequality between two CustomModelFineTuningJob objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)

    @classmethod
    def _from_rest_object(cls, obj: RestJobBase) -> "CustomModelFineTuningJob":
        """Convert a REST object to CustomModelFineTuningJob object.

        :param obj: CustomModelFineTuningJob in Rest format.
        :type obj: JobBase
        :return: CustomModelFineTuningJob objects.
        :rtype: CustomModelFineTuningJob
        """

        properties: RestFineTuningJob = obj.properties
        finetuning_details: RestCustomModelFineTuningVertical = properties.fine_tuning_details

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

        custom_model_finetuning_job = cls(
            task=finetuning_details.task_type,
            model=finetuning_details.model,
            training_data=finetuning_details.training_data,
            validation_data=finetuning_details.validation_data,
            hyperparameters=finetuning_details.hyper_parameters,
            **job_args_dict,
        )

        custom_model_finetuning_job._restore_inputs()

        return custom_model_finetuning_job

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        **kwargs: Any,
    ) -> "CustomModelFineTuningJob":
        """Load from a dictionary.

        :param data: dictionary representation of the object.
        :type data: typing.Dict
        :param context: dictionary containing the context.
        :type context: typing.Dict
        :param additional_message: additional message to be added to the error message.
        :type additional_message: str
        :return: CustomModelFineTuningJob object.
        :rtype: CustomModelFineTuningJob
        """
        from azure.ai.ml._schema._finetuning.custom_model_finetuning import CustomModelFineTuningSchema

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
        loaded_data = load_from_dict(CustomModelFineTuningSchema, data, context, additional_message, **kwargs)

        training_data = loaded_data.get("training_data", None)
        if isinstance(training_data, str):
            loaded_data["training_data"] = Input(type="uri_file", path=training_data)

        validation_data = loaded_data.get("validation_data", None)
        if isinstance(validation_data, str):
            loaded_data["validation_data"] = Input(type="uri_file", path=validation_data)

        job_instance = cls._create_instance_from_schema_dict(loaded_data)
        return job_instance

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "CustomModelFineTuningJob":
        """Create an instance from a schema dictionary.

        :param loaded_data: dictionary containing the data.
        :type loaded_data: typing.Dict
        :return: CustomModelFineTuningJob object.
        :rtype: CustomModelFineTuningJob
        """
        job = CustomModelFineTuningJob(**loaded_data)
        return job
