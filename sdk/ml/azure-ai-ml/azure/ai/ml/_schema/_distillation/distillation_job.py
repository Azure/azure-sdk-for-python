# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema._distillation.prompt_settings import PromptSettingsSchema
from azure.ai.ml._schema._distillation.teacher_model_settings import TeacherModelSettingsSchema
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    LocalPathField,
    NestedField,
    RegistryStr,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_entry import DataInputSchema, ModelInputSchema
from azure.ai.ml._schema.job.input_output_fields_provider import OutputsField
from azure.ai.ml._schema.job_resource_configuration import ResourceConfigurationSchema
from azure.ai.ml._schema.workspace.connections import ServerlessConnectionSchema, WorkspaceConnectionSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import DataGenerationTaskType, DataGenerationType, JobType
from azure.ai.ml.constants._common import AzureMLResourceType


@experimental
class DistillationJobSchema(BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.DISTILLATION)
    data_generation_type = StringTransformedEnum(
        allowed_values=[DataGenerationType.LABEL_GENERATION, DataGenerationType.DATA_GENERATION],
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
    teacher_model_endpoint_connection = UnionField(
        [NestedField(WorkspaceConnectionSchema), NestedField(ServerlessConnectionSchema)], required=True
    )
    student_model = UnionField(
        [
            NestedField(ModelInputSchema),
            RegistryStr(azureml_type=AzureMLResourceType.MODEL),
            ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL, allow_default_version=True),
        ],
        required=True,
    )
    training_data = UnionField(
        [
            NestedField(DataInputSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.DATA),
            fields.Str(metadata={"pattern": r"^(http(s)?):.*"}),
            fields.Str(metadata={"pattern": r"^(wasb(s)?):.*"}),
            LocalPathField(pattern=r"^file:.*"),
            LocalPathField(
                pattern=r"^(?!(azureml|http(s)?|wasb(s)?|file):).*",
            ),
        ]
    )
    validation_data = UnionField(
        [
            NestedField(DataInputSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.DATA),
            fields.Str(metadata={"pattern": r"^(http(s)?):.*"}),
            fields.Str(metadata={"pattern": r"^(wasb(s)?):.*"}),
            LocalPathField(pattern=r"^file:.*"),
            LocalPathField(
                pattern=r"^(?!(azureml|http(s)?|wasb(s)?|file):).*",
            ),
        ]
    )
    teacher_model_settings = NestedField(TeacherModelSettingsSchema)
    prompt_settings = NestedField(PromptSettingsSchema)
    hyperparameters = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))
    resources = NestedField(ResourceConfigurationSchema)
    outputs = OutputsField()
