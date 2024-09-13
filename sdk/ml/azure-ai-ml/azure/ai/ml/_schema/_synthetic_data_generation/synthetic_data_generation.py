# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml.constants import JobType
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.job_resource_configuration import JobResourceConfigurationSchema
from azure.ai.ml._schema._synthetic_data_generation.constants import DataGenerationTaskTypes
from azure.ai.ml._schema._synthetic_data_generation.data_generation_fields import (
    EndpointNameSchema,
    EndpointUriSchema,
    EndpointRequestSettingsSchema
)
from azure.ai.ml._schema._synthetic_data_generation.synthetic_data_generation_job import (
    SyntheticDataGenerationJobSchema
)
from azure.ai.ml._utils._experimental import experimental

# from azure.ai.ml._utils.utils import snake_to_camel


@experimental
class SyntheticDataGenerationSchema(SyntheticDataGenerationJobSchema):
    resources = NestedField(JobResourceConfigurationSchema)

    # Verify if data key or casing is needed
    data_generation_task_type = StringTransformedEnum(
        allowed_values=[
            DataGenerationTaskTypes.NLI,
            DataGenerationTaskTypes.NLU_QA,
            DataGenerationTaskTypes.CONVERSATIONAL,
            DataGenerationTaskTypes.MATH,
            DataGenerationTaskTypes.SUMMARIZATION
        ],
        required=True,
    )
    data_generation_type = StringTransformedEnum(
        allowed_values=[
            JobType.LABEL_GENERATION,
            JobType.DATA_GENERATION
        ],
        required=True
    )
    teacher_model_endpoint = UnionField([
            NestedField(EndpointNameSchema),
            NestedField(EndpointUriSchema)
        ],
        required=True
    )
    enable_chain_of_thought = fields.Bool()
    enable_chain_of_density = fields.Bool()
    inference_parameters = fields.Dict(keys=fields.Str(), values=fields.Raw())
    endpoint_request_settings = NestedField(EndpointRequestSettingsSchema)
