# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any
from .compute_binding import ComputeBindingSchema
from azure.ai.ml._schema.core.fields import ArmStr, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants import AzureMLResourceType, EndpointYamlFields
from azure.ai.ml.entities import ComputeConfiguration
from marshmallow import fields
from marshmallow.decorators import post_load
from .batch_deployment_settings import (
    BatchRetrySettingsSchema,
)
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJob, InferenceDatasetIdInput, DataVersion


class OutputDataSchema(metaclass=PatchedSchemaMeta):
    datastore_id = ArmStr(azureml_type=AzureMLResourceType.DATASTORE)
    path = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        return DataVersion(**data)


class BatchJobSchema(PathAwareSchema):
    compute = NestedField(ComputeBindingSchema)
    error_threshold = fields.Int()
    retry_settings = NestedField(BatchRetrySettingsSchema)
    mini_batch_size = fields.Int()
    dataset = fields.Str()
    output_dataset = NestedField(OutputDataSchema)
    output_file_name = fields.Str()
    name = fields.Str(data_key="job_name")

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        # "dataset" is required field
        data[EndpointYamlFields.BATCH_JOB_DATASET] = InferenceDatasetIdInput(
            dataset_id=data[EndpointYamlFields.BATCH_JOB_DATASET]
        )
        if data.get(EndpointYamlFields.COMPUTE, None):
            data[EndpointYamlFields.COMPUTE] = ComputeConfiguration(
                **data[EndpointYamlFields.COMPUTE]
            )._to_rest_object()

        if data.get(EndpointYamlFields.RETRY_SETTINGS, None):
            data[EndpointYamlFields.RETRY_SETTINGS] = data[EndpointYamlFields.RETRY_SETTINGS]._to_rest_object()

        return BatchJob(**data)
