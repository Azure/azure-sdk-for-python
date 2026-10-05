# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access

from typing import Any, Dict

from marshmallow import fields
from marshmallow.decorators import post_load

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
        # ``DataVersion`` is not modeled on arm_ml_service; carry the fields as a plain dict for the operation.
        return dict(data)


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

    # ``jobInputType`` / ``jobOutputType`` wire discriminators for the v2020_09 batch-scoring job models.
    _JOB_DATA_TYPE_MAP = {
        AssetTypes.URI_FILE: "UriFile",
        AssetTypes.URI_FOLDER: "UriFolder",
        AssetTypes.TRITON_MODEL: "TritonModel",
        AssetTypes.MLFLOW_MODEL: "MLFlowModel",
        AssetTypes.MLTABLE: "MLTable",
        AssetTypes.CUSTOM_MODEL: "CustomModel",
    }

    @staticmethod
    def _input_to_wire(input_data: Input) -> Dict[str, Any]:
        # JSON-direct wire, byte-identical to the legacy v2020_09 job-input models.
        if input_data.type in {InputTypes.INTEGER, InputTypes.NUMBER, InputTypes.STRING, InputTypes.BOOLEAN}:
            wire: Dict[str, Any] = {"jobInputType": "Literal"}
            if input_data.default is not None:
                wire["value"] = input_data.default
            return wire
        wire = {"jobInputType": BatchJobSchema._JOB_DATA_TYPE_MAP[input_data.type]}
        # ``UriFile``/``UriFolder`` inputs carry only ``uri``; the model inputs additionally carry ``mode``.
        if input_data.type not in {AssetTypes.URI_FILE, AssetTypes.URI_FOLDER} and input_data.mode is not None:
            wire["mode"] = input_data.mode
        if input_data.path is not None:
            wire["uri"] = input_data.path
        return wire

    @staticmethod
    def _output_to_wire(output_data: Output) -> Dict[str, Any]:
        wire: Dict[str, Any] = {"jobOutputType": BatchJobSchema._JOB_DATA_TYPE_MAP[output_data.type]}
        if output_data.mode is not None:
            wire["mode"] = output_data.mode
        if output_data.path is not None:
            wire["uri"] = output_data.path
        return wire

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        # ``BatchJob`` and its input/output models are not on arm_ml_service; build the camelCase wire body as a
        # plain dict (JSON-direct), byte-identical to the legacy ``BatchJob(...).serialize()`` output.
        # ``output_dataset`` is carried under ``_output_dataset`` because the operation must run the datastore-id
        # ARM check on it before it becomes wire.
        wire: Dict[str, Any] = {}

        input_data = data.get(EndpointYamlFields.BATCH_JOB_INPUT_DATA, None)
        if input_data:
            wire["inputData"] = {
                key: (self._input_to_wire(item) if isinstance(item, Input) else item)
                for key, item in input_data.items()
            }

        output_data = data.get(EndpointYamlFields.BATCH_JOB_OUTPUT_DATA, None)
        if output_data:
            wire["outputData"] = {
                key: (self._output_to_wire(item) if isinstance(item, Output) else item)
                for key, item in output_data.items()
            }

        if data.get(EndpointYamlFields.COMPUTE, None):
            wire["compute"] = ComputeConfiguration(**data[EndpointYamlFields.COMPUTE])._to_rest_object()
        if data.get(EndpointYamlFields.RETRY_SETTINGS, None):
            wire["retrySettings"] = data[EndpointYamlFields.RETRY_SETTINGS]._to_rest_object().as_dict()
        if data.get("error_threshold", None) is not None:
            wire["errorThreshold"] = data["error_threshold"]
        if data.get("mini_batch_size", None) is not None:
            wire["miniBatchSize"] = data["mini_batch_size"]
        if data.get("output_file_name", None) is not None:
            wire["outputFileName"] = data["output_file_name"]
        if data.get("name", None) is not None:
            wire["name"] = data["name"]
        if data.get("properties", None) is not None:
            wire["properties"] = data["properties"]
        if data.get("dataset", None) is not None:
            wire["dataset"] = data["dataset"]
        if data.get("output_dataset", None) is not None:
            wire["_output_dataset"] = data["output_dataset"]
        return wire
