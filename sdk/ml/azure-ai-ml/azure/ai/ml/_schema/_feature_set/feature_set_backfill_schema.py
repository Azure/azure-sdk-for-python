# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema
from azure.ai.ml._restclient.v2023_04_01_preview.models import FeatureWindow
from azure.ai.ml._schema._feature_set.materialization_settings_schema import MaterializationComputeResourceSchema
from azure.ai.ml._schema._feature_set.feature_window_schema import FeatureWindowSchema

class FeatureSetBackfillSchema(YamlFileSchema):
    name = fields.Str()
    version = fields.Str()
    feature_window = NestedField(FeatureWindowSchema)
    description = fields.Str()
    tags =  fields.Dict()
    resource = NestedField(MaterializationComputeResourceSchema)
    spark_conf = fields.Dict()
