import pydash
import pytest

from azure.ai.ml import MLClient, load_component
from azure.ai.ml.constants._component import DataCopyMode, DataTransferTaskType
from azure.ai.ml.entities._component.datatransfer_component import (
    DataTransferCopyComponent,
    DataTransferExportComponent,
    DataTransferImportComponent,
)

from .._util import _COMPONENT_TIMEOUT_SECOND
from .test_component_schema import load_component_entity_from_rest_json, load_component_entity_from_yaml


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestDataTransferComponentEntity:
    def test_serialize_deserialize_copy_task_component(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/data_transfer/copy_files.yaml"
        component_entity = load_component_entity_from_yaml(
            test_path, mock_machinelearning_client, _type="data_transfer"
        )
        assert isinstance(component_entity, DataTransferCopyComponent)

        rest_path = "./tests/test_configs/components/data_transfer/copy_files.json"
        rest_entity = load_component_entity_from_rest_json(rest_path)
        data_transfer_copy_component = DataTransferCopyComponent(
            name="datatransfer_copy_files",
            display_name="Data Transfer Component copy-files",
            inputs={"folder1": {"type": "uri_folder"}},
            outputs={"output_folder": {"type": "uri_folder"}},
            data_copy_mode=DataCopyMode.MERGE_WITH_OVERWRITE,
            base_path="./tests/test_configs/components/data_transfer",
        )

        # data_copy_mode is a run time config, cannot be decided in registering progress. So won't be returned from
        # backend.
        omit_fields = [
            "name",
            "id",
            "$schema",
            "data_copy_mode",
            "inputs.folder1.optional",
            "version",
        ]
        yaml_dict = pydash.omit(dict(component_entity._to_dict()), *omit_fields)
        rest_dict = pydash.omit(dict(rest_entity._to_dict()), *omit_fields)
        sdk_dict = pydash.omit(dict(data_transfer_copy_component._to_dict()), *omit_fields)
        assert yaml_dict == rest_dict
        assert sdk_dict == yaml_dict

    def test_serialize_deserialize_merge_task_component(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/data_transfer/merge_files.yaml"
        component_entity = load_component_entity_from_yaml(
            test_path, mock_machinelearning_client, _type="data_transfer"
        )
        assert isinstance(component_entity, DataTransferCopyComponent)
        rest_path = "./tests/test_configs/components/data_transfer/merge_files.json"
        rest_entity = load_component_entity_from_rest_json(rest_path)
        data_transfer_copy_component = DataTransferCopyComponent(
            name="datatransfer_merge_files",
            display_name="Data Transfer Component merge-files",
            inputs={
                "folder1": {"type": "uri_folder"},
                "folder2": {"type": "uri_folder"},
            },
            outputs={"output_folder": {"type": "uri_folder"}},
            data_copy_mode=DataCopyMode.MERGE_WITH_OVERWRITE,
            base_path="./tests/test_configs/components/data_transfer",
        )

        # data_copy_mode is a run time config, cannot be decided in registering progress. So won't be returned from
        # backend.
        omit_fields = [
            "name",
            "id",
            "$schema",
            "data_copy_mode",
            "inputs.folder1.optional",
            "version",
            "inputs.folder2.optional",
            "inputs.folder3.optional",
        ]
        yaml_dict = pydash.omit(dict(component_entity._to_dict()), *omit_fields)
        rest_dict = pydash.omit(dict(rest_entity._to_dict()), *omit_fields)
        sdk_dict = pydash.omit(dict(data_transfer_copy_component._to_dict()), *omit_fields)
        assert yaml_dict == rest_dict
        assert sdk_dict == yaml_dict

    def test_serialize_deserialize_import_task_component(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/data_transfer/import_file_to_blob.yaml"
        component_entity = load_component_entity_from_yaml(
            test_path, mock_machinelearning_client, _type="data_transfer"
        )
        assert isinstance(component_entity, DataTransferImportComponent)

        data_transfer_copy_component = DataTransferImportComponent(
            name="datatransfer_s3_blob",
            display_name="Data Transfer s3-blob",
            source={"type": "file_system"},
            outputs={"sink": {"type": "uri_folder"}},
            base_path="./tests/test_configs/components/data_transfer",
        )

        omit_fields = ["name", "id", "$schema"]
        yaml_dict = pydash.omit(dict(component_entity._to_dict()), *omit_fields)
        sdk_dict = pydash.omit(dict(data_transfer_copy_component._to_dict()), *omit_fields)
        assert sdk_dict == yaml_dict

    def test_serialize_deserialize_export_task_component(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/data_transfer/export_blob_to_database.yaml"
        component_entity = load_component_entity_from_yaml(
            test_path, mock_machinelearning_client, _type="data_transfer"
        )
        assert isinstance(component_entity, DataTransferExportComponent)

        data_transfer_copy_component = DataTransferExportComponent(
            name="datatransfer_blob_azuresql",
            display_name="Data Transfer blob-azuresql",
            inputs={"source": {"type": "uri_folder"}},
            sink={"type": "database"},
            base_path="./tests/test_configs/components/data_transfer",
        )

        omit_fields = ["name", "id", "$schema"]
        yaml_dict = pydash.omit(dict(component_entity._to_dict()), *omit_fields)
        sdk_dict = pydash.omit(dict(data_transfer_copy_component._to_dict()), *omit_fields)
        assert sdk_dict == yaml_dict

    def test_copy_task_component_entity(self):
        component = DataTransferCopyComponent(
            name="datatransfer_copy_files",
            display_name="Data Transfer Component copy-files",
            inputs={
                "folder1": {"type": "uri_folder"},
            },
            outputs={
                "output_folder": {"type": "uri_folder"},
            },
            data_copy_mode=DataCopyMode.MERGE_WITH_OVERWRITE,
            base_path="./tests/test_configs/components/data_transfer",
        )
        omit_fields = [
            "properties.component_spec.$schema",
            "properties.component_spec._source",
            "properties.properties.client_component_hash",
        ]
        component._validate()
        component_dict = component._to_rest_object().as_dict()
        component_dict = pydash.omit(component_dict, *omit_fields)

        yaml_path = "./tests/test_configs/components/data_transfer/copy_files.yaml"
        yaml_component = load_component(yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()
        yaml_component_dict = pydash.omit(yaml_component_dict, *omit_fields)

        assert component_dict == yaml_component_dict
