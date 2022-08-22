# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

from typing import Any

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import (
    BatchJob,
    DataVersion,
    UriFileJobInput,
    UriFolderJobInput,
)
from azure.ai.ml._schema.core.fields import ArmStr, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants import AssetTypes, AzureMLResourceType, EndpointYamlFields
from azure.ai.ml.entities import ComputeConfiguration
from azure.ai.ml.entities._inputs_outputs import Input

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

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        if data.get(EndpointYamlFields.BATCH_JOB_INPUT_DATA, None):
            input_data = data[EndpointYamlFields.BATCH_JOB_INPUT_DATA]["input_data"]
            if isinstance(input_data, Input):
                if input_data.type == AssetTypes.URI_FILE:
                    data[EndpointYamlFields.BATCH_JOB_INPUT_DATA] = {"uriFile": UriFileJobInput(uri=input_data.path)}
                elif input_data.type == AssetTypes.URI_FOLDER:
                    data[EndpointYamlFields.BATCH_JOB_INPUT_DATA] = {
                        "uriFolder": UriFolderJobInput(uri=input_data.path)
                    }

        if data.get(EndpointYamlFields.COMPUTE, None):
            data[EndpointYamlFields.COMPUTE] = ComputeConfiguration(
                **data[EndpointYamlFields.COMPUTE]
            )._to_rest_object()

        if data.get(EndpointYamlFields.RETRY_SETTINGS, None):
            data[EndpointYamlFields.RETRY_SETTINGS] = data[EndpointYamlFields.RETRY_SETTINGS]._to_rest_object()

        return BatchJob(**data)
