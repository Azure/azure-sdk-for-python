import pytest
import requests
from pathlib import Path
from azure.ai.ml._utils._data_utils import read_local_mltable_metadata_contents, read_remote_mltable_metadata_contents
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml.operations._code_operations import CodeOperations
from unittest.mock import Mock, patch
from collections import OrderedDict


@pytest.fixture
def mock_datastore_operations(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> CodeOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
    )


@pytest.mark.unittest
class TestDataUtils:
    @patch("azure.ai.ml._utils._data_utils.get_datastore_info")
    @patch("azure.ai.ml._utils._data_utils.get_storage_client")
    def test_read_mltable_metadata_contents(
        self, _mock_get_storage_click, _mock_get_datastore_info, tmp_path: Path, mock_datastore_operations
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
        with patch.object(requests, "get", return_value=Mock(content=file_contents.encode(encoding="UTF-8"))):
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations, path="https://fake.localhost/file.yaml"
            )
            assert contents["paths"] == [OrderedDict([("file", "./tmp_file.csv")])]

        # remote https inaccessible
        with pytest.raises(Exception) as ex:
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations,
                path="https://fake.localhost/file.yaml",
            )
        assert "Invalid URL" in str(ex)

        # remote azureml accessible
        with patch("azure.ai.ml._utils._data_utils.TemporaryDirectory", return_value=mltable_folder):
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations,
                path="azureml://datastores/mydatastore/paths/images/dogs",
            )
            assert contents["paths"] == [OrderedDict([("file", "./tmp_file.csv")])]

        # remote azureml inaccessible
        with pytest.raises(Exception) as ex:
            contents = read_remote_mltable_metadata_contents(
                datastore_operations=mock_datastore_operations,
                path="azureml://datastores/mydatastore/paths/images/dogs",
            )
        assert "No such file or directory" in str(ex)

        # local accessible
        contents = read_local_mltable_metadata_contents(path=mltable_folder)
        assert contents["paths"] == [OrderedDict([("file", "./tmp_file.csv")])]

        # local inaccessible: should raise an error when an MLTable metadata file cannot be read from local path (path is not "is_url")
        with pytest.raises(Exception) as ex:
            read_local_mltable_metadata_contents(path=mltable_folder / "should-fail")
        assert "No such file or directory" in str(ex)
