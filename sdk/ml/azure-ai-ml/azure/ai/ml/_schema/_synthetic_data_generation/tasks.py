# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.job.input_output_entry import DataInputSchema
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._schema._synthetic_data_generation.synthetic_data_generation import SyntheticDataGenerationSchema


@experimental
class SyntheticDataGenerationLabelTaskPropertiesSchema(SyntheticDataGenerationSchema):
    training_data = NestedField(DataInputSchema, required=True)
    validation_data = NestedField(DataInputSchema)


@experimental
class SyntheticDataGenerationDataTaskPropertiesSchema(SyntheticDataGenerationSchema):
    training_data = NestedField(DataInputSchema)
