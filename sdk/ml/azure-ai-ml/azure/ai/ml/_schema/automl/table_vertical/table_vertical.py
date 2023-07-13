# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from azure.ai.ml._restclient.v2023_04_01_preview.models import NCrossValidationsMode
from azure.ai.ml._schema.automl.automl_vertical import AutoMLVerticalSchema
from azure.ai.ml._schema.automl.featurization_settings import TableFeaturizationSettingsSchema
from azure.ai.ml._schema.automl.table_vertical.table_vertical_limit_settings import AutoMLTableLimitsSchema
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField, fields
from azure.ai.ml._schema.job.input_output_entry import MLTableInputSchema
from azure.ai.ml.constants._job.automl import AutoMLConstants


class AutoMLTableVerticalSchema(AutoMLVerticalSchema):
    limits = NestedField(AutoMLTableLimitsSchema(), data_key=AutoMLConstants.LIMITS_YAML)
    featurization = NestedField(TableFeaturizationSettingsSchema(), data_key=AutoMLConstants.FEATURIZATION_YAML)
    target_column_name = fields.Str(required=True)
    validation_data = UnionField([NestedField(MLTableInputSchema)])
    validation_data_size = fields.Float()
    cv_split_column_names = fields.List(fields.Str())
    n_cross_validations = UnionField(
        [
            StringTransformedEnum(allowed_values=[NCrossValidationsMode.AUTO]),
            fields.Int(),
        ],
    )
    weight_column_name = fields.Str()
    test_data = UnionField([NestedField(MLTableInputSchema)])
    test_data_size = fields.Float()
