# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import re
import pytest
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import DatasetVersion, DatasetType
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording
from azure.core.exceptions import HttpResponseError


# Construct the paths to the data folder and data file used in this test
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "../test_data/datasets"))
data_file1 = os.path.join(data_folder, "data_file1.txt")
data_file2 = os.path.join(data_folder, "data_file2.txt")


class TestDatasets(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_datasets.py::TestDatasets::test_datasets_upload_file -s
    @servicePreparer()
    @pytest.mark.skipif(
        not is_live_and_not_recording(),
        reason="Skipped because this test involves network calls from another client (azure.storage.blob) that is not recorded.",
    )
    @recorded_by_proxy
    def test_datasets_upload_file(self, **kwargs):

        connection_name = self.test_datasets_params["connection_name"]
        dataset_name = self.test_datasets_params["dataset_name_1"]
        dataset_version = self.test_datasets_params["dataset_version"]

        with self.create_client(**kwargs) as project_client:

            print(
                f"[test_datasets_upload_file] Upload a single file and create a new Dataset `{dataset_name}`, version `{dataset_version}`, to reference the file."
            )
            dataset: DatasetVersion = project_client.datasets.upload_file(
                name=dataset_name,
                version=str(dataset_version),
                file_path=data_file1,
                connection_name=connection_name,
            )
            print(dataset)
            TestBase.validate_dataset(
                dataset,
                expected_dataset_type=DatasetType.URI_FILE,
                expected_dataset_name=dataset_name,
                expected_dataset_version=str(dataset_version),
            )

            print(f"[test_datasets_upload_file] Get an existing Dataset version `{dataset_version}`:")
            dataset = project_client.datasets.get(name=dataset_name, version=dataset_version)
            print(dataset)
            TestBase.validate_dataset(
                dataset,
                expected_dataset_type=DatasetType.URI_FILE,
                expected_dataset_name=dataset_name,
                expected_dataset_version=str(dataset_version),
            )

            print(
                f"[test_datasets_upload_file] Upload a single file and create a new version in existing Dataset `{dataset_name}`, to reference the file."
            )
            dataset: DatasetVersion = project_client.datasets.upload_file(
                name=dataset_name,
                version=str(dataset_version + 1),
                file_path=data_file2,
                connection_name=connection_name,
            )
            print(dataset)
            TestBase.validate_dataset(
                dataset,
                expected_dataset_type=DatasetType.URI_FILE,
                expected_dataset_name=dataset_name,
                expected_dataset_version=str(dataset_version + 1),
            )

            print(f"[test_datasets_upload_file] Get credentials of an existing Dataset version `{dataset_version}`:")
            dataset_credential = project_client.datasets.get_credentials(
                name=dataset_name, version=str(dataset_version)
            )
            print(dataset_credential)
            TestBase.validate_dataset_credential(dataset_credential)

            """
            print("[test_datasets_upload_file] List latest versions of all Datasets:")
            empty = True
            for dataset in project_client.datasets.list():
                empty = False
                print(dataset)
                TestBase.validate_dataset(dataset)
            assert not empty

            print(f"[test_datasets_upload_file] Listing all versions of the Dataset named `{dataset_name}`:")
            empty = True
            for dataset in project_client.datasets.list_versions(name=dataset_name):
                empty = False
                print(dataset)
                TestBase.validate_dataset(dataset, expected_dataset_name=dataset_name)
            assert not empty
            """

            print(
                f"[test_datasets_upload_file] Delete Dataset `{dataset_name}`, version `{dataset_version}` that was created above."
            )
            project_client.datasets.delete(name=dataset_name, version=str(dataset_version))
            project_client.datasets.delete(name=dataset_name, version=str(dataset_version + 1))

            print(
                "[test_datasets_upload_file] Delete the same (now non-existing) Dataset. REST API call should return 204 (No content). This call should NOT throw an exception."
            )
            project_client.datasets.delete(name=dataset_name, version=str(dataset_version))

            print(
                f"[test_datasets_upload_file] Try to get a non-existing Dataset `{dataset_name}`, version `{dataset_version}`. This should throw an exception."
            )
            try:
                exception_thrown = False
                dataset = project_client.datasets.get(name=dataset_name, version=str(dataset_version))
            except HttpResponseError as e:
                exception_thrown = True
                print(f"Expected exception occurred: {e}")
                assert "Could not find asset with ID" in e.message
            assert exception_thrown

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_datasets.py::TestDatasets::test_datasets_upload_folder -s
    @servicePreparer()
    @pytest.mark.skipif(
        not is_live_and_not_recording(),
        reason="Skipped because this test involves network calls from another client (azure.storage.blob) that is not recorded.",
    )
    @recorded_by_proxy
    def test_datasets_upload_folder(self, **kwargs):

        endpoint = kwargs.pop("AZURE_AI_PROJECT_ENDPOINT")
        print("\n=====> Endpoint:", endpoint)

        connection_name = self.test_datasets_params["connection_name"]
        dataset_name = self.test_datasets_params["dataset_name_2"]
        dataset_version = self.test_datasets_params["dataset_version"]

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            print(
                f"[test_datasets_upload_folder] Upload files in a folder (including sub-folders) and create a new version `{dataset_version}` in the same Dataset, to reference the files."
            )
            dataset = project_client.datasets.upload_folder(
                name=dataset_name,
                version=str(dataset_version),
                folder=data_folder,
                connection_name=connection_name,
                file_pattern=re.compile(r"\.(txt|csv|md)$", re.IGNORECASE),
            )
            print(dataset)
            TestBase.validate_dataset(
                dataset,
                expected_dataset_type=DatasetType.URI_FOLDER,
                expected_dataset_name=dataset_name,
                expected_dataset_version=str(dataset_version),
            )

            print(f"[test_datasets_upload_file] Get an existing Dataset version `{dataset_version}`:")
            dataset = project_client.datasets.get(name=dataset_name, version=str(dataset_version))
            print(dataset)
            TestBase.validate_dataset(
                dataset,
                expected_dataset_type=DatasetType.URI_FOLDER,
                expected_dataset_name=dataset_name,
                expected_dataset_version=str(dataset_version),
            )

            print(f"[test_datasets_upload_file] Get credentials of an existing Dataset version `{dataset_version}`:")
            dataset_credential = project_client.datasets.get_credentials(
                name=dataset_name, version=str(dataset_version)
            )
            print(dataset_credential)
            TestBase.validate_dataset_credential(dataset_credential)

            print(
                f"[test_datasets_upload_file] Delete Dataset `{dataset_name}`, version `{dataset_version}` that was created above."
            )
            project_client.datasets.delete(name=dataset_name, version=str(dataset_version))
