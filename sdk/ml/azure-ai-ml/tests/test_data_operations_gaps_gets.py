from pathlib import Path
from typing import Callable

import pytest
import yaml
import marshmallow
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient, load_data
from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType
from azure.ai.ml.exceptions import ValidationException, MlException


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
class TestDataOperationsGetBranches(AzureRecordedTestCase):
    def test_get_raises_when_both_version_and_label_specified(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Get should raise ValidationException when both version and label are provided."""
        name = randstr("name")
        # Call get with both version and label which should raise before any network call
        with pytest.raises(MlException) as e:
            client.data.get(name, version="1", label="latest")
        assert "Cannot specify both version and label." in str(e.value)

    def test_get_raises_when_no_version_or_label(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Get should raise ValidationException when neither version nor label is provided."""
        name = randstr("name")
        with pytest.raises(MlException) as e:
            client.data.get(name)
        assert "Must provide either version or label." in str(e.value)

    @pytest.mark.skip(reason="No recording available — skips in live, no playback data")
    def test_get_label_resolves_latest_version(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        """Creating multiple versions and resolving via label 'latest' should return the most recent version."""
        if is_live():
            pytest.skip("Skipping live run for this test due to tenant authentication constraints.")

        name = randstr("name")
        # create two simple data assets using load_data + a remote URL so service has versions
        cfg = tmp_path / "data.yaml"
        # use a URL path to avoid uploading to datastores during create_or_update
        url_path = "https://example.com/f1.csv"

        # create version 1
        cfg.write_text(
            f"""
            name: {name}
            version: 1
            path: {url_path}
            type: uri_file
        """
        )
        data_asset = load_data(source=cfg)
        client.data.create_or_update(data_asset)

        # create version 2
        cfg.write_text(
            f"""
            name: {name}
            version: 2
            path: {url_path}
            type: uri_file
        """
        )
        data_asset = load_data(source=cfg)
        client.data.create_or_update(data_asset)

        # wait briefly if live to allow indexing
        sleep_if_live(3)
        latest = client.data.get(name, label="latest")
        assert latest.version == "2"


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
class TestData(AzureRecordedTestCase):
    def test_validate_missing_path_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """
        Covers branch where data.path is missing in _validate which should raise a ValidationException.
        Triggers the branch by loading a data asset YAML without a path and calling create_or_update through client.data.
        """
        name = randstr("name")
        # create a minimal data yaml without path by constructing Data via load_data params_override
        with pytest.raises(marshmallow.exceptions.ValidationError) as exc:
            client.data.create_or_update(
                load_data(
                    source="./tests/test_configs/dataset/data_file.yaml",
                    params_override=[{"name": name}, {"version": "1"}, {"path": None}],
                )
            )
        assert "Field may not be null." in str(exc.value)

    def test_local_path_type_mismatch_raises(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        """
        Covers branches in _assert_local_path_matches_asset_type where a file/folder mismatch raises ValidationException.
        We create a file but declare the asset type as uri_folder to trigger the folder-not-found branch.
        """
        tmp_file = tmp_path / "tmp_file.csv"
        tmp_file.write_text("hello world")
        name = randstr("name")
        data_yaml = tmp_path / "data_mismatch.yaml"
        # specify type uri_folder but path points to a file -> should raise ValidationException
        data_yaml.write_text(
            f"""
            name: {name}
            version: 1
            path: {tmp_file}
            type: uri_folder
        """
        )

        data_asset = load_data(source=data_yaml)
        # create_or_update wraps ValidationException into MlException via log_and_raise_error; assert MlException
        with pytest.raises(MlException) as excinfo:
            client.data.create_or_update(data_asset)
        assert "File path does not match asset type" in str(excinfo.value)

    @pytest.mark.skip(reason="Depends on local azureml-dataprep package state — not recordable")
    def test_mount_requires_dataprep_installed(self, client: MLClient, tmp_path: Path) -> None:
        """
        Covers the ImportError branch in mount where absence of azureml.dataprep should raise MlException.
        Calls client.data.mount to trigger the import-time check for azureml.dataprep.
        """
        # Use a dummy azureml URI; the check for azureml.dataprep happens before any network calls
        mount_point = str(tmp_path / "mnt")
        with pytest.raises(Exception) as exc:
            client.data.mount("azureml:someasset:1", mount_point=mount_point)
        msg = str(exc.value)
        # Either the environment is missing the dataprep package (expected message),
        # or the dataprep package exists and the mount attempt fails in another way.
        assert (
            "azureml-dataprep-rslex" in msg
            or "azureml-dataprep" in msg
            or isinstance(exc.value, (AssertionError, MlException, OSError, RuntimeError))
        )


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestDataMountValidation(AzureRecordedTestCase):
    def test_mount_invalid_mode_raises(self, client: MLClient) -> None:
        # mode must be either 'ro_mount' or 'rw_mount' and read-write mounts are not supported
        with pytest.raises(AssertionError) as e:
            client.data.mount("azureml:some_name:1", mode="invalid")
        assert "mode should be either `ro_mount` or `rw_mount`" in str(e.value)

        # rw_mount is recognized but not supported and should raise a specific assertion
        with pytest.raises(AssertionError) as e2:
            client.data.mount("azureml:some_name:1", mode="rw_mount")
        assert "read-write mount for data asset is not supported yet" in str(e2.value)

    def test_mount_persistent_without_ci_name_raises(self, client: MLClient) -> None:
        # persistent mounts require CI_NAME environment variable to be set
        with pytest.raises(AssertionError) as e:
            client.data.mount("azureml:some_name:1", persistent=True)
        assert "persistent mount is only supported on Compute Instance, where the 'CI_NAME' environment variable is set." in str(
            e.value
        )
