from collections import OrderedDict
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml._utils._data_utils import read_local_mltable_metadata_contents, read_remote_mltable_metadata_contents
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.core.exceptions import ServiceRequestError


@pytest.fixture
def mock_datastore_operations(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_01_01_preview: Mock,
    mock_aml_services_2024_07_01_preview: Mock,
) -> CodeOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2024_01_01_preview=mock_aml_services_2024_01_01_preview,
        serviceclient_2024_07_01_preview=mock_aml_services_2024_07_01_preview,
    )


@pytest.fixture
def mock_requests_pipeline(mock_machinelearning_client) -> HttpPipeline:
    yield mock_machinelearning_client._requests_pipeline


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestDataUtils:
    @patch("azure.ai.ml._utils._data_utils.get_datastore_info")
    @patch("azure.ai.ml._utils._data_utils.get_storage_client")
    def test_read_mltable_metadata_contents(
        self,
        _mock_get_storage_click,
        _mock_get_datastore_info,
        tmp_path: Path,
        mock_datastore_operations,
        mock_requests_pipeline,
    ):
        mltable_folder = tmp_path / "mltable_folder"
        mltable_folder.mkdir()
        tmp_metadata_file = mltable_folder / "MLTable"
        file_contents = """
            paths:
                - file: ./tmp_file.csv
            transformations:
                - read_delimited:
                    delimiter: ","
                    encoding: ascii
                    header: all_files_same_headers
        """
        tmp_metadata_file.write_text(file_contents)

        # remote https accessible
        with patch.object(
            mock_requests_pipeline, "get", return_value=Mock(content=file_contents.encode(encoding="UTF-8"))
        ):
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations,
                base_uri="https://fake.localhost/file.yaml",
                requests_pipeline=mock_requests_pipeline,
            )
            assert contents["paths"] == [OrderedDict([("file", "./tmp_file.csv")])]

        # remote https inaccessible
        with pytest.raises(ServiceRequestError) as ex:
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations,
                base_uri="https://fake.localhost/file.yaml",
                requests_pipeline=mock_requests_pipeline,
            )

        # remote azureml accessible
        with patch("azure.ai.ml._utils._data_utils.TemporaryDirectory", return_value=mltable_folder):
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations,
                base_uri="azureml://datastores/mydatastore/paths/images/dogs",
                requests_pipeline=mock_requests_pipeline,
            )
            assert contents["paths"] == [OrderedDict([("file", "./tmp_file.csv")])]

        # remote azureml inaccessible
        with pytest.raises(Exception) as ex:
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations,
                base_uri="azureml://datastores/mydatastore/paths/images/dogs",
                requests_pipeline=mock_requests_pipeline,
            )
        assert "No such file or directory" in str(ex)

        # local accessible
        contents = read_local_mltable_metadata_contents(path=mltable_folder)
        assert contents["paths"] == [OrderedDict([("file", "./tmp_file.csv")])]

        # local inaccessible: should raise an error when an MLTable metadata file cannot be read from local path (path is not "is_url")
        with pytest.raises(Exception) as ex:
            read_local_mltable_metadata_contents(path=mltable_folder / "should-fail")
        assert "No such file or directory" in str(ex)
