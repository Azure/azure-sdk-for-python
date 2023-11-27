# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access

from typing import Any

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import (
    BatchJob,
    CustomModelJobInput,
    CustomModelJobOutput,
    DataVersion,
    LiteralJobInput,
    MLFlowModelJobInput,
    MLFlowModelJobOutput,
    MLTableJobInput,
    MLTableJobOutput,
    TritonModelJobInput,
    TritonModelJobOutput,
    UriFileJobInput,
    UriFileJobOutput,
    UriFolderJobInput,
    UriFolderJobOutput,
)
from azure.ai.ml._schema.core.fields import ArmStr, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._common import AzureMLResourceType, InputTypes
from azure.ai.ml.constants._endpoint import EndpointYamlFields
from azure.ai.ml.entities import ComputeConfiguration
from azure.ai.ml.entities._inputs_outputs import Input, Output

from .batch_deployment_settings import BatchRetrySettingsSchema
from .compute_binding import ComputeBindingSchema


class OutputDataSchema(metaclass=PatchedSchemaMeta):
    datastore_id = ArmStr(azureml_type=AzureMLResourceType.DATASTORE)
    path = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        return DataVersion(**data)


class BatchJobSchema(PathAwareSchema):
    compute = NestedField(ComputeBindingSchema)
    dataset = fields.Str()
    error_threshold = fields.Int()
    input_data = fields.Dict()
    mini_batch_size = fields.Int()
    name = fields.Str(data_key="job_name")
    output_data = fields.Dict()
    output_dataset = NestedField(OutputDataSchema)
    output_file_name = fields.Str()
    retry_settings = NestedField(BatchRetrySettingsSchema)
    properties = fields.Dict(data_key="properties")

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=too-many-branches
        if data.get(EndpointYamlFields.BATCH_JOB_INPUT_DATA, None):
            for key, input_data in data[EndpointYamlFields.BATCH_JOB_INPUT_DATA].items():
                if isinstance(input_data, Input):
                    if input_data.type == AssetTypes.URI_FILE:
                        data[EndpointYamlFields.BATCH_JOB_INPUT_DATA][key] = UriFileJobInput(uri=input_data.path)
                    if input_data.type == AssetTypes.URI_FOLDER:
                        data[EndpointYamlFields.BATCH_JOB_INPUT_DATA][key] = UriFolderJobInput(uri=input_data.path)
                    if input_data.type == AssetTypes.TRITON_MODEL:
                        data[EndpointYamlFields.BATCH_JOB_INPUT_DATA][key] = TritonModelJobInput(
                            mode=input_data.mode, uri=input_data.path
                        )  # pylint: disable=line-too-long
                    if input_data.type == AssetTypes.MLFLOW_MODEL:
                        data[EndpointYamlFields.BATCH_JOB_INPUT_DATA][key] = MLFlowModelJobInput(
                            mode=input_data.mode, uri=input_data.path
                        )  # pylint: disable=line-too-long
                    if input_data.type == AssetTypes.MLTABLE:
                        data[EndpointYamlFields.BATCH_JOB_INPUT_DATA][key] = MLTableJobInput(
                            mode=input_data.mode, uri=input_data.path
                        )  # pylint: disable=line-too-long
                    if input_data.type == AssetTypes.CUSTOM_MODEL:
                        data[EndpointYamlFields.BATCH_JOB_INPUT_DATA][key] = CustomModelJobInput(
                            mode=input_data.mode, uri=input_data.path
                        )  # pylint: disable=line-too-long
                    if input_data.type in {
                        InputTypes.INTEGER,
                        InputTypes.NUMBER,
                        InputTypes.STRING,
                        InputTypes.BOOLEAN,
                    }:
                        data[EndpointYamlFields.BATCH_JOB_INPUT_DATA][key] = LiteralJobInput(
                            value=input_data.default
                        )  # pylint: disable=line-too-long
        if data.get(EndpointYamlFields.BATCH_JOB_OUTPUT_DATA, None):
            for key, output_data in data[EndpointYamlFields.BATCH_JOB_OUTPUT_DATA].items():
                if isinstance(output_data, Output):
                    if output_data.type == AssetTypes.URI_FILE:
                        data[EndpointYamlFields.BATCH_JOB_OUTPUT_DATA][key] = UriFileJobOutput(
                            mode=output_data.mode, uri=output_data.path
                        )  # pylint: disable=line-too-long
                    if output_data.type == AssetTypes.URI_FOLDER:
                        data[EndpointYamlFields.BATCH_JOB_OUTPUT_DATA][key] = UriFolderJobOutput(
                            mode=output_data.mode, uri=output_data.path
                        )  # pylint: disable=line-too-long
                    if output_data.type == AssetTypes.TRITON_MODEL:
                        data[EndpointYamlFields.BATCH_JOB_OUTPUT_DATA][key] = TritonModelJobOutput(
                            mode=output_data.mode, uri=output_data.path
                        )  # pylint: disable=line-too-long
                    if output_data.type == AssetTypes.MLFLOW_MODEL:
                        data[EndpointYamlFields.BATCH_JOB_OUTPUT_DATA][key] = MLFlowModelJobOutput(
                            mode=output_data.mode, uri=output_data.path
                        )  # pylint: disable=line-too-long
                    if output_data.type == AssetTypes.MLTABLE:
                        data[EndpointYamlFields.BATCH_JOB_OUTPUT_DATA][key] = MLTableJobOutput(
                            mode=output_data.mode, uri=output_data.path
                        )  # pylint: disable=line-too-long
                    if output_data.type == AssetTypes.CUSTOM_MODEL:
                        data[EndpointYamlFields.BATCH_JOB_OUTPUT_DATA][key] = CustomModelJobOutput(
                            mode=output_data.mode, uri=output_data.path
                        )  # pylint: disable=line-too-long

        if data.get(EndpointYamlFields.COMPUTE, None):
            data[EndpointYamlFields.COMPUTE] = ComputeConfiguration(
                **data[EndpointYamlFields.COMPUTE]
            )._to_rest_object()

        if data.get(EndpointYamlFields.RETRY_SETTINGS, None):
            data[EndpointYamlFields.RETRY_SETTINGS] = data[EndpointYamlFields.RETRY_SETTINGS]._to_rest_object()

        return BatchJob(**data)
