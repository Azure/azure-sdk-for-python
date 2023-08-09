from pathlib import Path
from typing import Callable

import pytest
import yaml
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient, load_data
from azure.ai.ml._restclient.v2022_10_01.models import ListViewType
from azure.ai.ml._utils._arm_id_utils import generate_data_arm_id
from azure.core.paging import ItemPaged

# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
@pytest.mark.data_experiences_test
class TestData(AzureRecordedTestCase):
    def test_data_upload_file(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        f = tmp_path / "data_local.yaml"
        data_path = tmp_path / "sample1.csv"
        data_path.write_text("hello world")
        name = randstr("name")
        version = 4
        f.write_text(
            f"""
        name: {name}
        version: {version}
        path: {data_path}
        type: uri_file
    """
        )

        data_asset = load_data(source=f)
        client.data.create_or_update(data_asset)
        internal_data = client.data.get(name=name, version=str(version))

        assert internal_data.name == name
        assert internal_data.version == str(version)
        assert internal_data.path.endswith("sample1.csv")
        assert internal_data.id == generate_data_arm_id(client._operation_scope, name, version)

    def test_create_uri_folder(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        data_path = tmp_path / "data_directory.yaml"
        tmp_folder = tmp_path / "tmp_folder"
        tmp_folder.mkdir()
        tmp_file = tmp_folder / "tmp_file.csv"
        tmp_file.write_text("hello world")
        name = randstr("name")
        data_path.write_text(
            f"""
            name: {name}
            version: 1
            description: "this is a test dataset"
            path: {tmp_folder}
            type: uri_folder
        """
        )

        with open(data_path, "r") as f:
            config = yaml.safe_load(f)
        name = config["name"]
        version = config["version"]

        data_asset = load_data(source=data_path)
        obj = client.data.create_or_update(data_asset)
        assert obj is not None
        assert config["name"] == obj.name
        assert obj.id == generate_data_arm_id(client._operation_scope, name, version)

        data_version = client.data.get(name, version)

        assert data_version.name == obj.name
        assert data_version.id == generate_data_arm_id(client._operation_scope, name, version)
        assert data_version.path.endswith("/tmp_folder/")

    def test_create_uri_file(
        self, client: MLClient, resource_group_name: str, tmp_path: Path, randstr: Callable[[], str]
    ) -> None:
        data_yaml = tmp_path / "data_directory.yaml"
        tmp_folder = tmp_path / "tmp_folder"
        tmp_folder.mkdir()
        tmp_file = tmp_folder / "tmp_file.csv"
        tmp_file.write_text("hello world")
        name = randstr("name")
        data_yaml.write_text(
            f"""
            name: {name}
            version: 2
            description: "this is a test dataset"
            path: {tmp_file}
            type: uri_file
        """
        )

        with open(data_yaml, "r") as f:
            config = yaml.safe_load(f)
        name = config["name"]
        version = config["version"]

        data_asset = load_data(source=data_yaml)
        obj = client.data.create_or_update(data_asset)
        assert obj is not None
        assert config["name"] == obj.name
        assert obj.id == generate_data_arm_id(client._operation_scope, name, version)

        data_version = client.data.get(name, version)

        assert data_version.name == obj.name
        assert data_version.version == obj.version
        assert data_version.id == generate_data_arm_id(client._operation_scope, name, version)
        assert data_version.path.endswith("/tmp_file.csv")

    def test_create_mltable(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        data_path = tmp_path / "mltable_directory.yaml"
        tmp_folder = tmp_path / "tmp_folder"
        tmp_folder.mkdir()
        tmp_metadata_file = tmp_folder / "MLTable"
        tmp_metadata_file.write_text(
            """
paths:
  - file: ./tmp_file.csv
transformations:
  - read_delimited:
      delimiter: ","
      encoding: ascii
      header: all_files_same_headers
"""
        )
        tmp_file = tmp_folder / "tmp_file.csv"
        tmp_file.write_text(
            """
sepal_length,sepal_width,petal_length,petal_width,species
101,152,123,187,Iris-setosa
4.9,3,1.4,0.2,Iris-setosa
4.7,3.2,1.3,0.2,Iris-setosa
4.6,3.1,1.5,0.2,Iris-setosa
5,3.6,1.4,0.2,Iris-setosa
5.4,3.9,1.7,0.4,Iris-setosa
4.6,3.4,1.4,0.3,Iris-setosa
5,3.4,1.5,0.2,Iris-setosa
4.4,2.9,1.4,0.2,Iris-setosa
4.9,3.1,1.5,0.1,Iris-setosa
5.4,3.7,1.5,0.2,Iris-setosa
4.8,3.4,1.6,0.2,Iris-setosa
"""
        )
        name = randstr("name")
        data_path.write_text(
            f"""
            name: {name}
            version: 1
            description: "this is an mltable dataset"
            path: {tmp_folder}
            type: mltable
        """
        )

        with open(data_path, "r") as f:
            config = yaml.safe_load(f)
        name = config["name"]
        version = config["version"]

        data_asset = load_data(source=data_path)
        obj = client.data.create_or_update(data_asset)
        assert obj is not None
        assert config["name"] == obj.name
        assert obj.id == generate_data_arm_id(client._operation_scope, name, version)

        data_version = client.data.get(name, version)

        assert data_version.name == obj.name
        assert data_version.id == generate_data_arm_id(client._operation_scope, name, version)
        assert data_version.path.endswith("/tmp_folder/")

    @pytest.mark.skipif(condition=not is_live(), reason="Auth issue in Registry")
    def test_create_data_asset_in_registry(
        self, data_asset_registry_client: MLClient, randstr: Callable[[], str]
    ) -> None:
        name = randstr("name")
        version = "1"
        data_asset = load_data(
            source="./tests/test_configs/dataset/data_file.yaml",
            params_override=[{"name": name}, {"version": version}],
        )
        sleep_if_live(3)
        obj = data_asset_registry_client.data.create_or_update(data_asset)
        assert obj is not None
        assert name == obj.name
        data_version = data_asset_registry_client.data.get(name, version)

        assert data_version.name == obj.name

    def test_list(self, client: MLClient, data_with_2_versions: str) -> None:
        data_iterator = client.data.list(name=data_with_2_versions)
        assert isinstance(data_iterator, ItemPaged)

        # iterating the whole iterable object
        data_list = list(data_iterator)

        assert len(data_list) == 2
        assert all(data.name == data_with_2_versions for data in data_list)
        # use a set since ordering of elements returned from list isn't guaranteed
        assert {"1", "2"} == {data.version for data in data_list}

    @pytest.mark.skipif(condition=not is_live(), reason="Auth issue in Registry")
    def test_list_data_in_registry(self, data_asset_registry_client: MLClient) -> None:
        data_iterator = data_asset_registry_client.data.list()
        assert data_iterator
        assert isinstance(data_iterator, ItemPaged)

    def test_data_get_latest_label(self, client: MLClient, randstr: Callable[[], str]) -> None:
        name = randstr("name")
        versions = ["foo", "bar", "baz", "foobar"]

        for version in versions:
            client.data.create_or_update(
                load_data(
                    source="./tests/test_configs/dataset/data_file.yaml",
                    params_override=[{"name": name}, {"version": version}],
                )
            )
            sleep_if_live(3)
            assert client.data.get(name, label="latest").version == version

    @pytest.mark.skipif(condition=not is_live(), reason="Auth issue in Registry")
    def test_data_get_latest_label_in_registry(
        self, data_asset_registry_client: MLClient, randstr: Callable[[], str]
    ) -> None:
        name = randstr("name")
        versions = ["foo", "bar", "baz", "foobar"]
        for version in versions:
            data_asset_registry_client.data.create_or_update(
                load_data(
                    source="./tests/test_configs/dataset/data_file.yaml",
                    params_override=[{"name": name}, {"version": version}],
                )
            )
            sleep_if_live(3)
            assert data_asset_registry_client.data.get(name, label="latest").version == version

    @pytest.mark.e2etest
    def test_data_archive_restore_version(self, client: MLClient, randstr: Callable[[], str]) -> None:
        name = randstr("name")
        versions = ["1", "2"]
        version_archived = versions[0]
        for version in versions:
            client.data.create_or_update(
                load_data(
                    source="./tests/test_configs/dataset/data_file.yaml",
                    params_override=[{"name": name}, {"version": version}],
                )
            )

        def get_data_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            data_list = client.data.list(name=name, list_view_type=ListViewType.ACTIVE_ONLY)
            return [d.version for d in data_list if d is not None]

        assert version_archived in get_data_list()
        client.data.archive(name=name, version=version_archived)
        assert version_archived not in get_data_list()
        client.data.restore(name=name, version=version_archived)
        assert version_archived in get_data_list()

    @pytest.mark.e2etest
    @pytest.mark.skip(reason="Task 1791832: Inefficient, possibly causing testing pipeline to time out.")
    def test_data_archive_restore_container(self, client: MLClient, randstr: Callable[[], str]) -> None:
        name = randstr("name")
        version = "1"
        client.data.create_or_update(
            load_data(
                source="./tests/test_configs/dataset/data_file.yaml",
                params_override=[{"name": name}, {"version": version}],
            )
        )

        def get_data_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            data_list = client.data.list(list_view_type=ListViewType.ACTIVE_ONLY)
            return [d.name for d in data_list if d is not None]

        assert name in get_data_list()
        client.data.archive(name=name)
        assert name not in get_data_list()
        client.data.restore(name=name)
        assert name in get_data_list()

    @pytest.mark.skip(reason="investigate later")
    def test_data_unsupported_datastore(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        f = tmp_path / "data_local.yaml"
        data_path = tmp_path / "sample1.csv"
        data_path.write_text("hello world")
        name = randstr("name")
        version = 4
        f.write_text(
            f"""
        name: {name}
        version: {version}
        path: {data_path}
        type: uri_file
        datastore: workspacefilestore
    """
        )

        data_asset = load_data(f)
        assert data_asset.datastore == "workspacefilestore"

        with pytest.raises(Exception) as e:
            client.data.create_or_update(data_asset)

        assert (
            str(e.value.args[1])
            == "Datastore type AzureFile is not supported for uploads. Supported types are AzureBlob and AzureDataLakeGen2."
        )

    def test_data_auto_delete_setting(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        data_path = tmp_path / "data_with_auto_delete_setting.yaml"
        tmp_folder = tmp_path / "tmp_folder_with_auto_dete_setting"
        tmp_folder.mkdir()
        tmp_file = tmp_folder / "tmp_file_with_auto_delete_setting.csv"
        tmp_file.write_text("hello world")
        name = randstr("name")
        data_path.write_text(
            f"""
            name: {name}
            version: 1
            description: "this is a test dataset with auto delete setting"
            path: {tmp_folder}
            type: uri_folder
            auto_delete_setting:
                condition: created_greater_than
                value: "30d"
        """
        )

        data_asset = load_data(source=data_path)
        client.data.create_or_update(data_asset)
        internal_data = client.data.get(name=name, version="1")

        assert internal_data.auto_delete_setting is not None
        assert internal_data.auto_delete_setting.condition == "createdGreaterThan"
        assert internal_data.auto_delete_setting.value == "30d"
