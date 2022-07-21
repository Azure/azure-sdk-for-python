# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields, validate, pre_load

from azure.ai.ml._schema import PatchedSchemaMeta, UnionField
from azure.ai.ml.constants import AssetTypes, LegacyAssetTypes


class InputPortSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(
        validate=validate.OneOf(
            [
                LegacyAssetTypes.PATH,
                AssetTypes.URI_FILE,
                AssetTypes.URI_FOLDER,
                AssetTypes.CUSTOM_MODEL,
                AssetTypes.MLFLOW_MODEL,
                AssetTypes.MLTABLE,
                AssetTypes.TRITON_MODEL,
            ]
        ),
        required=True,
        data_key="type",
    )
    description = fields.Str()
    optional = fields.Bool()
    default = fields.Str()

    @pre_load
    def trim_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "mode" in data:
                data.pop("mode")
        return data


class OutputPortSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(
        validate=validate.OneOf(
            [
                LegacyAssetTypes.PATH,
                AssetTypes.URI_FILE,
                AssetTypes.URI_FOLDER,
                AssetTypes.CUSTOM_MODEL,
                AssetTypes.MLFLOW_MODEL,
                AssetTypes.MLTABLE,
                AssetTypes.TRITON_MODEL,
            ]
        ),
        required=True,
        data_key="type",
    )
    description = fields.Str()

    @pre_load
    def trim_output(self, data, **kwargs):
        if isinstance(data, dict):
            if "mode" in data:
                data.pop("mode")
        return data


class ParameterSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(
        validate=validate.OneOf(["number", "integer", "boolean", "string", "object"]),
        required=True,
        data_key="type",
    )
    optional = fields.Bool()
    default = UnionField([fields.Str(), fields.Number(), fields.Bool()])
    description = fields.Str()
    max = UnionField([fields.Str(), fields.Number()])
    min = UnionField([fields.Str(), fields.Number()])
    enum = fields.List(fields.Str())
