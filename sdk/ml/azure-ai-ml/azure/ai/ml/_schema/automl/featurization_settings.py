# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields as flds
from marshmallow import post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import BlockedTransformers
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._job.automl import AutoMLConstants, AutoMLTransformerParameterKeys


class ColumnTransformerSchema(metaclass=PatchedSchemaMeta):
    fields = flds.List(flds.Str())
    parameters = flds.Dict(
        keys=flds.Str(),
        values=UnionField([flds.Float(), flds.Str()], allow_none=True, load_default=None),
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
        allowed_values=[
            AutoMLConstants.AUTO,
            AutoMLConstants.OFF,
            AutoMLConstants.CUSTOM,
        ],
        load_default=AutoMLConstants.AUTO,
    )
    blocked_transformers = flds.List(
        StringTransformedEnum(
            allowed_values=[o.value for o in BlockedTransformers],
            casing_transform=camel_to_snake,
        )
    )
    column_name_and_types = flds.Dict(keys=flds.Str(), values=flds.Str())
    transformer_params = flds.Dict(
        keys=StringTransformedEnum(
            allowed_values=[o.value for o in AutoMLTransformerParameterKeys],
            casing_transform=camel_to_snake,
        ),
        values=flds.List(NestedField(ColumnTransformerSchema())),
    )
    enable_dnn_featurization = flds.Bool()

    @post_load
    def make(self, data, **kwargs) -> "TabularFeaturizationSettings":
        from azure.ai.ml.automl import TabularFeaturizationSettings

        return TabularFeaturizationSettings(**data)
