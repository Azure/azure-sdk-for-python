# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from azure.ai.ml._schema.automl.automl_vertical import AutoMLVerticalSchema
from azure.ai.ml._schema.automl.image_vertical.image_limit_settings import ImageLimitsSchema
from azure.ai.ml._schema.automl.image_vertical.image_sweep_settings import ImageSweepSettingsSchema
from azure.ai.ml._schema.core.fields import NestedField, UnionField, fields
from azure.ai.ml._schema.job.input_output_entry import MLTableInputSchema


class ImageVerticalSchema(AutoMLVerticalSchema):
    limits = NestedField(ImageLimitsSchema())
    sweep = NestedField(ImageSweepSettingsSchema())
    target_column_name = fields.Str(required=True)
    test_data = UnionField([NestedField(MLTableInputSchema)])
    test_data_size = fields.Float()
    validation_data = UnionField([NestedField(MLTableInputSchema)])
    validation_data_size = fields.Float()
