# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields as flds, post_load
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema import PatchedSchemaMeta, NestedField, StringTransformedEnum, UnionField


class ColumnTransformerSchema(metaclass=PatchedSchemaMeta):
    fields = flds.List(flds.Str())
    parameters = flds.Dict(
        keys=flds.Str(), values=UnionField([flds.Float(), flds.Str()], allow_none=True, missing=None)
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ColumnTransformer

        return ColumnTransformer(**data)


class FeaturizationSettingsSchema(metaclass=PatchedSchemaMeta):
    dataset_language = flds.Str()


class NlpFeaturizationSettingsSchema(FeaturizationSettingsSchema):
    dataset_language = flds.Str()

    @post_load
    def make(self, data, **kwargs) -> "NlpFeaturizationSettings":
        from azure.ai.ml.automl import NlpFeaturizationSettings

        return NlpFeaturizationSettings(**data)


class TableFeaturizationSettingsSchema(FeaturizationSettingsSchema):
    mode = StringTransformedEnum(
        allowed_values=[AutoMLConstants.AUTO, AutoMLConstants.OFF, AutoMLConstants.CUSTOM],
        load_default=AutoMLConstants.AUTO,
    )
    blocked_transformers = flds.List(flds.Str())
    column_name_and_types = flds.Dict(keys=flds.Str(), values=flds.Str())
    transformer_params = flds.Dict(keys=flds.Str(), values=flds.List(NestedField(ColumnTransformerSchema())))
    enable_dnn_featurization = flds.Bool()

    @post_load
    def make(self, data, **kwargs) -> "TabularFeaturizationSettings":
        from azure.ai.ml.automl import TabularFeaturizationSettings

        return TabularFeaturizationSettings(**data)
