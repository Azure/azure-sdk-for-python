# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta, PathAwareSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, StringTransformedEnum, UnionField
from azure.ai.ml.constants import AssetTypes, AzureMLResourceType, InputOutputModes, LOCAL_PATH

module_logger = logging.getLogger(__name__)


class InputSchema(metaclass=PatchedSchemaMeta):
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

    def generate_path_property(azureml_type):
        return UnionField(
            [
                ArmVersionedStr(azureml_type=azureml_type),
                ArmVersionedStr(azureml_type=LOCAL_PATH, pattern="^file:.*"),
                fields.Str(metadata={"pattern": "^(http(s)?):.*"}),
                fields.Str(metadata={"pattern": "^(wasb(s)?):.*"}),
                ArmVersionedStr(azureml_type=LOCAL_PATH, pattern="^(?!(azureml|http(s)?|wasb(s)?|file):).*"),
            ],
            is_strict=True,
        )


class ModelInputSchema(InputSchema):
    mode = StringTransformedEnum(
        allowed_values=[
            InputOutputModes.DOWNLOAD,
            InputOutputModes.RO_MOUNT,
            InputOutputModes.DIRECT,
        ],
        required=False,
    )
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.CUSTOM_MODEL,
            AssetTypes.MLFLOW_MODEL,
            AssetTypes.TRITON_MODEL,
        ]
    )
    path = InputSchema.generate_path_property(azureml_type=AzureMLResourceType.MODEL)


class DataInputSchema(InputSchema):
    mode = StringTransformedEnum(
        allowed_values=[
            InputOutputModes.DOWNLOAD,
            InputOutputModes.RO_MOUNT,
            InputOutputModes.DIRECT,
        ],
        required=False,
    )
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.URI_FILE,
            AssetTypes.URI_FOLDER,
        ]
    )
    path = InputSchema.generate_path_property(azureml_type=AzureMLResourceType.DATA)


class MLTableInputSchema(InputSchema):
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
    type = StringTransformedEnum(allowed_values=[AssetTypes.MLTABLE])
    path = InputSchema.generate_path_property(azureml_type=AzureMLResourceType.DATA)


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
