# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema._distillation.constants import DistillationSchemaKeys
from azure.ai.ml._schema._distillation.distillation_types import DistillationPromptSettingsSchema
from azure.ai.ml._schema._finetuning.finetuning_vertical import FineTuningVerticalSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, RegistryStr, StringTransformedEnum, UnionField
from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_entry import DataInputSchema, ModelInputSchema
from azure.ai.ml._schema.job.input_output_fields_provider import OutputsField
from azure.ai.ml._schema.job_resource_configuration import JobResourceConfigurationSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import AssetTypes, DataGenerationTaskType, DataGenerationType, JobType
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.distillation.distillation_types import (
    DistillationPromptSettings,
    EndpointRequestSettings,
)


@experimental
class DistillationJobSchema(FineTuningVerticalSchema, BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.DISTILLATION)
    data_generation_type = StringTransformedEnum(
        allowed_values=[DataGenerationType.LabelGeneration, DataGenerationType.DataGeneration],
        required=True,
    )
    data_generation_task_type = StringTransformedEnum(
        allowed_values=[
            DataGenerationTaskType.NLI,
            DataGenerationTaskType.NLU_QA,
            DataGenerationTaskType.CONVERSATION,
            DataGenerationTaskType.MATH,
            DataGenerationTaskType.SUMMARIZATION,
        ],
        casing_transform=str.upper,
        required=True,
    )
    teacher_model_endpoint = fields.Str()
    student_model = UnionField(
        [
            NestedField(ModelInputSchema),
            RegistryStr(azureml_type=AzureMLResourceType.MODEL),
            ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL, allow_default_version=True),
        ],
        required=True,
    )
    training_data = NestedField(DataInputSchema)
    validation_data = NestedField(DataInputSchema)
    inference_parameters = fields.Dict(keys=fields.Str(), values=fields.Raw())
    prompt_settings = NestedField(DistillationPromptSettingsSchema)
    endpoint_request_settings = fields.Dict(keys=fields.Str(), values=fields.Raw())
    hyperparameters = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))
    resources = NestedField(JobResourceConfigurationSchema)
    outputs = OutputsField()

    class Meta:  # type: ignore
        exclude = ("model", "task")

    @post_load
    def post_load_processing(self, data: Dict, **kwargs) -> Dict:  # pylint: disable=unused-argument
        """Post load processing for the schema.

        :param data: Dictionary of parsed values from the yaml.
        :type data: typing.Dict

        :return Dictionary of parsed values from the yaml.
        :rtype Dict[str, Any]
        """
        student_model = data.pop(DistillationSchemaKeys.StudentModel, None)
        prompt_settings = data.pop(DistillationSchemaKeys.PromptSettings, {})
        endpoint_request_settings = data.pop(DistillationSchemaKeys.EndpointRequestSettings, {})

        if student_model and isinstance(student_model, str):
            data[DistillationSchemaKeys.StudentModel] = Input(type=AssetTypes.MLFLOW_MODEL, path=student_model)

        if prompt_settings and not isinstance(prompt_settings, DistillationPromptSettings):
            data[DistillationSchemaKeys.PromptSettings] = DistillationPromptSettings(**prompt_settings)

        if endpoint_request_settings and not isinstance(endpoint_request_settings, EndpointRequestSettings):
            data[DistillationSchemaKeys.EndpointRequestSettings] = EndpointRequestSettings(**endpoint_request_settings)

        return data
