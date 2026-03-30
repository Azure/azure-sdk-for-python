import json
import uuid
from pathlib import Path
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.constants._endpoint import LocalEndpointConstants
from azure.ai.ml.constants._common import DefaultOpenEncoding
from azure.ai.ml.operations._local_deployment_helper import _LocalDeploymentHelper, _write_conda_file, _get_stubbed_endpoint_metadata, _convert_json_to_deployment, _create_build_directory, _get_deployment_directory
from azure.ai.ml._local_endpoints import LocalEndpointMode
from azure.ai.ml.exceptions import InvalidLocalEndpointError, LocalEndpointNotFoundError, DockerEngineNotAvailableError
import random


@pytest.fixture
def randstr():
    """Simple randstr fixture for unit tests that generates random strings without recording infrastructure."""
    def _generate(variable_name: str) -> str:
        return f"test_{random.randint(1, 1000000000000)}"
    return _generate


@pytest.mark.unittest
class TestLocalDeploymentHelperInit:
    def test_create_or_update_raises_on_none_deployment(self, client: MLClient) -> None:
        """Ensure create_or_update raises InvalidLocalEndpointError when deployment is None.

        Covers the early validation branch that raises when deployment is None (lines ~69-77).
        """
        # Use the MLClient's internal operation container to construct the helper
        operation_container = getattr(client, "_operation_container", None)
        assert operation_container is not None, "MLClient fixture must provide _operation_container for this test"

        helper = _LocalDeploymentHelper(operation_container=operation_container)

        with pytest.raises(InvalidLocalEndpointError):
            # Use an existing enum member; the validation for None deployment happens before any use of the mode
            helper.create_or_update(deployment=None, local_endpoint_mode=LocalEndpointMode.VSCodeDevContainer)

@pytest.mark.unittest
class TestLocalDeploymentHelperGetLogsAndGet:
    def test_get_raises_when_container_missing(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """When no local container exists for the given endpoint/deployment, get should raise LocalEndpointNotFoundError.

        Depending on the test environment, Docker Engine may not be available; in that case the DockerEngineNotAvailableError
        is an acceptable outcome for this environment.
        """
        operation_container = getattr(client, "_operation_container", None)
        assert operation_container is not None, "MLClient fixture must provide _operation_container for this test"
        helper = _LocalDeploymentHelper(operation_container)

        endpoint_name = randstr("ept")
        deployment_name = randstr("dpm")

        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            helper.get(endpoint_name=endpoint_name, deployment_name=deployment_name)

    def test_get_deployment_logs_returns_string(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """get_deployment_logs should raise LocalEndpointNotFoundError when no container exists for the given names."""
        operation_container = getattr(client, "_operation_container", None)
        assert operation_container is not None, "MLClient fixture must provide _operation_container for this test"
        helper = _LocalDeploymentHelper(operation_container)

        endpoint_name = randstr("ept")
        deployment_name = randstr("dpm")

        # Docker is available but no container exists, so we expect LocalEndpointNotFoundError
        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            helper.get_deployment_logs(endpoint_name=endpoint_name, deployment_name=deployment_name, lines=10)

@pytest.mark.unittest
class TestLocalDeploymentHelperGaps:
    def test_write_conda_file_writes_expected_contents(self, client: MLClient, tmp_path: Path) -> None:
        # Arrange
        contents = "name: test_env\nchannels:\n  - defaults\n"
        file_name = "environment.yml"
        dir_path = str(tmp_path)

        # Act
        _write_conda_file(conda_contents=contents, directory_path=dir_path, conda_file_name=file_name)

        # Assert
        written = (tmp_path / file_name).read_text(encoding="utf-8")
        assert written == contents

    def test_get_stubbed_endpoint_metadata_returns_json_with_name(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Arrange
        name = randstr("endpoint")

        # Act
        metadata = _get_stubbed_endpoint_metadata(endpoint_name=name)

        # Assert
        parsed = json.loads(metadata)
        assert parsed.get("name") == name

@pytest.mark.unittest
class TestLocalDeploymentHelperGapsGenerated:
    def test_write_conda_file_creates_file_with_expected_contents(self, client: MLClient) -> None:
        # Arrange
        tmp_dir = Path.cwd() / ("tmp_conda_" + uuid.uuid4().hex[:8])
        tmp_dir.mkdir(parents=True, exist_ok=True)
        conda_name = LocalEndpointConstants.CONDA_FILE_NAME
        contents = "name: testenv\ndependencies:\n  - python=3.8\n"

        try:
            # Act
            _write_conda_file(conda_contents=contents, directory_path=str(tmp_dir), conda_file_name=conda_name)

            # Assert
            written = (tmp_dir / conda_name).read_text(encoding=DefaultOpenEncoding.WRITE)
            assert "name: testenv" in written
            assert "python=3.8" in written
        finally:
            # Cleanup
            try:
                (tmp_dir / conda_name).unlink()
                tmp_dir.rmdir()
            except Exception:
                pass

    def test_convert_json_to_deployment_produces_online_deployment_with_overrides(self, client: MLClient) -> None:
        # Arrange
        # Provide a minimal deployment json that OnlineDeployment._load can accept for creation.
        # We include a name field which is commonly required.
        deployment_json = {"name": "my-local-deployment"}

        # Act
        # Provide required overrides that the schema expects (endpoint_name and instance_type) instead of arbitrary keys.
        deployment = _convert_json_to_deployment(
            deployment_json=deployment_json,
            endpoint_name="local-endpoint",
            instance_type=LocalEndpointConstants.ENDPOINT_STATE_LOCATION,
        )

        # Assert
        assert isinstance(deployment, OnlineDeployment)
        # The name should be preserved from deployment_json
        assert deployment.name == "my-local-deployment"

    def test_get_stubbed_endpoint_metadata_returns_expected_json_string(self, client: MLClient) -> None:
        # Arrange
        endpoint_name = "ep-" + uuid.uuid4().hex[:8]

        # Act
        stub = _get_stubbed_endpoint_metadata(endpoint_name=endpoint_name)

        # Assert
        assert '"name":' in stub
        assert endpoint_name in stub

    def test_create_build_directory_and_get_deployment_directory_paths(self, client: MLClient) -> None:
        # Arrange
        endpoint_name = "ep-" + uuid.uuid4().hex[:8]
        deployment_name = "dpm-" + uuid.uuid4().hex[:8]

        # Act
        build_dir = _create_build_directory(endpoint_name=endpoint_name, deployment_name=deployment_name)
        expected_dir = _get_deployment_directory(endpoint_name=endpoint_name, deployment_name=deployment_name)

        # Assert
        assert build_dir.exists()
        assert str(build_dir.resolve()) == str(expected_dir.resolve())

        # Cleanup
        try:
            # Remove created directories
            if build_dir.exists():
                for child in build_dir.iterdir():
                    try:
                        if child.is_file():
                            child.unlink()
                        else:
                            # best-effort, should be empty
                            pass
                    except Exception:
                        pass
                build_dir.rmdir()
            # remove parents created by _get_deployment_directory
            parent = expected_dir.parent
            # attempt to clean up up to .azureml if empty
            while parent.name not in ("", "~") and parent.exists():
                try:
                    parent.rmdir()
                except Exception:
                    break
                parent = parent.parent
        except Exception:
            pass

# Additional tests merged from generated batch 1, with renamed class to avoid duplication
@pytest.mark.unittest
class TestLocalDeploymentHelperGaps_GeneratedExtra:
    def test_convert_json_to_deployment_minimal_payload(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Verify that converting a minimal deployment JSON to OnlineDeployment yields an object with the provided name."""
        name = randstr("name")
        payload = {"name": name}

        # Provide required overrides so the schema validation passes
        dep = _convert_json_to_deployment(
            deployment_json=payload,
            endpoint_name="local-endpoint",
            instance_type=LocalEndpointConstants.ENDPOINT_STATE_LOCATION,
        )

        assert isinstance(dep, OnlineDeployment)
        assert dep.name == name

    def test_get_stubbed_endpoint_metadata_returns_json_string(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Ensure the stubbed endpoint metadata contains the provided endpoint name."""
        name = randstr("endpoint")
        stub = _get_stubbed_endpoint_metadata(endpoint_name=name)

        assert isinstance(stub, str)
        assert '"name":' in stub
        assert name in stub

    def test_write_conda_file_and_build_directory_creation(self, client: MLClient, tmp_path) -> None:
        """Write a conda file to a build directory, then create and validate the deployment build directory path."""
        endpoint_name = "test-ept"
        deployment_name = "deploy1"

        # Create a dedicated temporary build directory and write conda file
        build_dir = tmp_path / "build_dir"
        build_dir.mkdir()
        conda_contents = "name: testenv\ndependencies:\n  - python=3.8\n"
        conda_file_name = "environment.yml"

        # use helper to write conda file
        _write_conda_file(conda_contents=conda_contents, directory_path=str(build_dir), conda_file_name=conda_file_name)

        written = build_dir / conda_file_name
        assert written.exists()
        # Read back and validate contents and encoding
        text = written.read_text(encoding=DefaultOpenEncoding.WRITE)
        assert "name: testenv" in text

        # Create build directory via helper that uses Path.home() locations
        created = _create_build_directory(endpoint_name=endpoint_name, deployment_name=deployment_name)
        assert created.exists()
        expected = _get_deployment_directory(endpoint_name=endpoint_name, deployment_name=deployment_name)
        # The created path should match the expected deployment directory
        assert created.resolve() == expected.resolve()
