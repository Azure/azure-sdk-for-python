# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema._synthetic_data_generation.synthetic_data_generation import SyntheticDataGenerationSchema
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.job.input_output_entry import DataInputSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import JobType


@experimental
class SyntheticDataGenerationLabelTaskSchema(SyntheticDataGenerationSchema):
    data_generation_type = StringTransformedEnum(allowed_values=[JobType.LABEL_GENERATION], required=True)
    training_data = NestedField(DataInputSchema, required=True)
    validation_data = NestedField(DataInputSchema)
