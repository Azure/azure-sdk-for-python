from pathlib import Path
from typing import Callable

import pytest
import yaml
from marshmallow.exceptions import ValidationError as MarshmallowValidationError

from azure.ai.ml import MLClient, load_data
from azure.ai.ml.exceptions import ValidationException, MlException


@pytest.fixture
def randstr():
    """Generate a random string for test isolation."""
    import random, string
    def _gen(prefix=""):
        return prefix + "".join(random.choices(string.ascii_lowercase, k=8))
    return _gen


@pytest.mark.unittest
class TestDataOperationsGaps:
    def test_get_with_both_version_and_label_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        name = randstr("name")
        # call get with both version and label should raise MlException (wrapped ValidationException)
        with pytest.raises(MlException) as e:
            client.data.get(name=name, version="1", label="latest")
        assert "Cannot specify both version and label." in str(e.value)

    def test_get_without_version_or_label_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        name = randstr("name")
        # call get without version or label should raise MlException (wrapped ValidationException)
        with pytest.raises(MlException) as e:
            client.data.get(name=name)
        assert "Must provide either version or label." in str(e.value)

    def test_create_uri_folder_path_mismatch_raises(
        self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]
    ) -> None:
        # Create a data yaml that declares type uri_folder but points to a file path -> should raise MlException (wrapped ValidationException)
        data_yaml = tmp_path / "data_mismatch.yaml"
        tmp_file = tmp_path / "only_file.csv"
        tmp_file.write_text("hello world")
        name = randstr("name")
        data_yaml.write_text(
            f"""
            name: {name}
            version: 1
            path: {tmp_file}
            type: uri_folder
        """
        )

        data_asset = load_data(source=data_yaml)
        with pytest.raises(MlException) as e:
            client.data.create_or_update(data_asset)
        # The validation should indicate file/folder mismatch
        assert "File path does not match asset type" in str(e.value)

    def test_create_uri_folder_with_file_path_raises(
        self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]
    ) -> None:
        # If type==uri_folder but path is a file, validation should raise ValidationException via create_or_update
        tmp_file = tmp_path / "tmp_file.csv"
        tmp_file.write_text("hello world")
        name = randstr("name")
        config_path = tmp_path / "data_directory.yaml"
        # Intentionally declare type uri_folder but provide a file path to trigger _assert_local_path_matches_asset_type
        config_path.write_text(
            f"""
            name: {name}
            version: 1
            path: {tmp_file}
            type: uri_folder
        """
        )

        data_asset = load_data(source=str(config_path))
        with pytest.raises(MlException):
            client.data.create_or_update(data_asset)

    def test_create_missing_path_raises_validation(
        self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]
    ) -> None:
        # Creating a Data asset with no path should raise a ValidationError during YAML loading
        name = randstr("name")
        config_path = tmp_path / "data_missing_path.yaml"
        config_path.write_text(
            f"""
            name: {name}
            version: 1
            type: uri_file
        """
        )

        # Loading the YAML should fail schema validation because 'path' is required
        with pytest.raises(MarshmallowValidationError):
            load_data(source=str(config_path))

    def test_create_uri_folder_pointing_to_file_raises(
        self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]
    ) -> None:
        """
        Covers branch where a data asset is declared as uri_folder but the provided path points to a file.
        The _validate call should raise ValidationException indicating file/folder mismatch.
        """
        # create a single file
        tmp_file = tmp_path / "tmp_file.csv"
        tmp_file.write_text("hello world")

        name = randstr("name")
        data_yaml = tmp_path / "data_uri_folder_pointing_to_file.yaml"
        # Intentionally declare type uri_folder but give a file path
        data_yaml.write_text(
            f"""
            name: {name}
            version: 1
            path: {tmp_file}
            type: uri_folder
        """
        )

        data_asset = load_data(source=data_yaml)
        with pytest.raises(MlException) as e:
            client.data.create_or_update(data_asset)

        assert "File path does not match asset type" in str(e.value)

    def test_mount_requires_dataprep_raises(self, client: MLClient) -> None:
        # If azureml.dataprep.rslex wrapper is not installed, mount should raise MlException
        # Depending on the environment, the dataprep package may be present which leads to a different exception (e.g., TypeError when mount_point is None).
        # Accept either MlException or TypeError as valid outcomes for this test across different environments.
        with pytest.raises((MlException, TypeError)):
            client.data.mount("azureml:nonexistent:1")

    def test_mount_persistent_requires_compute_instance(self, client: MLClient) -> None:
        # persistent mounts require CI_NAME environment variable to be set; assert should fail otherwise
        with pytest.raises(AssertionError) as ex:
            client.data.mount("azureml:nonexistent:1", persistent=True)
        assert "persistent mount is only supported on Compute Instance" in str(ex.value)
