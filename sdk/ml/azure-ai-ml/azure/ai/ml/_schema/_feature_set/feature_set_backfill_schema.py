# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema._feature_set.feature_window_schema import FeatureWindowSchema
from azure.ai.ml._schema._feature_set.materialization_settings_schema import MaterializationComputeResourceSchema
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema


class FeatureSetBackfillSchema(YamlFileSchema):
    name = fields.Str(required=True)
    version = fields.Str(required=True)
    feature_window = NestedField(FeatureWindowSchema)
    description = fields.Str()
    tags = fields.Dict()
    resource = NestedField(MaterializationComputeResourceSchema)
    spark_configuration = fields.Dict()
    data_status = fields.List(fields.Str())
    job_id = fields.Str()
