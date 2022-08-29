# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_02_01_preview.models import LogVerbosity
from azure.ai.ml._schema.automl.automl_job import AutoMLJobSchema
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.job.input_output_entry import MLTableInputSchema
from azure.ai.ml._utils.utils import camel_to_snake


class AutoMLVerticalSchema(AutoMLJobSchema):
    log_verbosity = StringTransformedEnum(
        allowed_values=[o.value for o in LogVerbosity],
        casing_transform=camel_to_snake,
        load_default=LogVerbosity.INFO,
    )
    training_data = UnionField([NestedField(MLTableInputSchema)])
