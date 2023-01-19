# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    StringTransformedEnum,
    UnionField,
    LocalPathField,
    NestedField
)

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta, PathAwareSchema
from azure.ai.ml.constants._common import (
    AssetTypes,
    AzureMLResourceType,
    InputOutputModes,
)
from azure.ai.ml.constants._component import ExternalDataType

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
        raise ValidationError("InputSchema needs type Input to dump")


def generate_path_property(azureml_type):
    return UnionField(
        [
            ArmVersionedStr(azureml_type=azureml_type),
            fields.Str(metadata={"pattern": r"^(http(s)?):.*"}),
            fields.Str(metadata={"pattern": r"^(wasb(s)?):.*"}),
            LocalPathField(pattern=r"^file:.*"),
            LocalPathField(pattern=r"^(?!(azureml|http(s)?|wasb(s)?|file):).*",),
        ],
        is_strict=True,
    )


def generate_datastore_property():
    metadata = {
        "description": "Name of the datastore to upload local paths to.",
        "arm_type": AzureMLResourceType.DATASTORE,
    }
    return fields.Str(metadata=metadata, required=False)


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
    path = generate_path_property(azureml_type=AzureMLResourceType.MODEL)
    datastore = generate_datastore_property()


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
    path = generate_path_property(azureml_type=AzureMLResourceType.DATA)
    datastore = generate_datastore_property()



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
    path = generate_path_property(azureml_type=AzureMLResourceType.DATA)
    datastore = generate_datastore_property()



class InputLiteralValueSchema(metaclass=PatchedSchemaMeta):
    value = UnionField([fields.Str(), fields.Bool(), fields.Int(), fields.Float()])

    @post_load
    def make(self, data, **kwargs):
        return data["value"]

    @pre_dump
    def check_dict(self, data, **kwargs):
        if hasattr(data, "value"):
            return data
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
        # Assists with union schema
        raise ValidationError("OutputSchema needs type Output to dump")


class StoredProcedureParamsSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str()
    value = fields.Str()
    type = fields.Str()


class SourceSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[
            ExternalDataType.FILE_SYSTEM,
            ExternalDataType.DATABASE
        ],
        required=True
    )
    path = generate_path_property(azureml_type=AzureMLResourceType.DATA)
    query = fields.Str(
        metadata={
            "description": "The sql query command."
        },
    )
    stored_procedure = fields.Str()
    stored_procedure_params = fields.List(NestedField(StoredProcedureParamsSchema))
    connection = ArmVersionedStr(azureml_type=AzureMLResourceType.WORKSPACE_CONNECTION, required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Source

        return Source(**data)

    @pre_dump
    def check_dict(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Source

        if isinstance(data, Source):
            return data
        raise ValidationError("InputSchema needs type Source to dump")


class SinkSchema(PathAwareSchema):
    type = StringTransformedEnum(
        allowed_values=[
            ExternalDataType.FILE_SYSTEM,
            ExternalDataType.DATABASE
        ],
        required=True
    )
    path = generate_path_property(azureml_type=AzureMLResourceType.DATA)
    table_name = fields.Str()
    connection = ArmVersionedStr(azureml_type=AzureMLResourceType.WORKSPACE_CONNECTION, required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Sink

        return Sink(**data)

    @pre_dump
    def check_dict(self, data, **kwargs):
        from azure.ai.ml.entities._inputs_outputs import Sink

        if isinstance(data, Sink):
            return data
        # Assists with union schema
        raise ValidationError("OutputSchema needs type Sink to dump")