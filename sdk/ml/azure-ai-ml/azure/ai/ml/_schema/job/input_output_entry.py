# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._schema import PatchedSchemaMeta, PathAwareSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml.constants import AzureMLResourceType, InputOutputModes, AssetTypes, LegacyAssetTypes
from marshmallow import pre_dump, ValidationError, fields, post_load

from azure.ai.ml._schema.core.fields import ArmVersionedStr, UnionField

module_logger = logging.getLogger(__name__)


class InputSchema(metaclass=PatchedSchemaMeta):
    mode = StringTransformedEnum(
        allowed_values=[
            InputOutputModes.DOWNLOAD,
            InputOutputModes.RO_MOUNT,
            InputOutputModes.EVAL_MOUNT,
            InputOutputModes.EVAL_DOWNLOAD,
            InputOutputModes.DIRECT,
        ],
        required=False,
    )
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.URI_FILE,
            AssetTypes.URI_FOLDER,
            AssetTypes.CUSTOM_MODEL,
            AssetTypes.MLFLOW_MODEL,
            AssetTypes.MLTABLE,
            AssetTypes.TRITON_MODEL,
        ]
    )
    path = UnionField(
        [
            ArmVersionedStr(azureml_type=AzureMLResourceType.DATASET),
            ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL),
            ArmVersionedStr(azureml_type=AzureMLResourceType.DATA),
            fields.URL(),  # For a remote path
            fields.Str(),  # For a local path
        ],
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Input

        return Input(**data)

    @pre_dump
    def check_dict(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Input

        if isinstance(data, Input):
            return data
        else:
            raise ValidationError("InputSchema needs type Input to dump")


class InputLiteralValueSchema(metaclass=PatchedSchemaMeta):
    value = UnionField([fields.Str(), fields.Bool(), fields.Int(), fields.Float()])

    @post_load
    def make(self, data, **kwargs):
        return data["value"]

    @pre_dump
    def check_dict(self, data, **kwargs):
        if hasattr(data, "value"):
            return data
        else:
            raise ValidationError("InputLiteralValue must have a field value")


class OutputSchema(PathAwareSchema):
    mode = StringTransformedEnum(
        allowed_values=[
            InputOutputModes.MOUNT,
            InputOutputModes.UPLOAD,
            InputOutputModes.RW_MOUNT,
            InputOutputModes.DIRECT,
        ],
        required=False,
    )
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.URI_FILE,
            AssetTypes.URI_FOLDER,
            AssetTypes.CUSTOM_MODEL,
            AssetTypes.MLFLOW_MODEL,
            AssetTypes.MLTABLE,
            AssetTypes.TRITON_MODEL,
        ]
    )
    path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Output

        return Output(**data)

    @pre_dump
    def check_dict(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Output

        if isinstance(data, Output):
            return data
        else:
            # Assists with union schema
            raise ValidationError("OutputSchema needs type Output to dump")
