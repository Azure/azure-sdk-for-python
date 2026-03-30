import json
import os
from pathlib import Path
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.operations._local_deployment_helper import (
    _write_conda_file,
    _create_build_directory,
    _get_deployment_directory,
    _convert_json_to_deployment,
    _get_stubbed_endpoint_metadata,
    LocalEndpointConstants,
)

@pytest.mark.unittest


class TestLocalDeploymentHelperGaps:
    def test_write_conda_and_readback(self, client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        # Ensure _write_conda_file writes the conda contents to the expected path with correct encoding
        conda_contents = "name: testenv\ndependencies:\n  - python=3.8\n"
        unique = randstr("conda")
        target_dir = tmp_path / unique
        target_dir.mkdir(parents=True, exist_ok=True)
        file_name = "environment.yml"

        # Call the helper (triggering marker lines around conda write)
        _write_conda_file(conda_contents=conda_contents, directory_path=str(target_dir), conda_file_name=file_name)

        written_path = target_dir / file_name
        assert written_path.exists()
        read_text = written_path.read_text(encoding="utf-8")
        assert read_text == conda_contents

    def test_create_and_get_deployment_directory_and_build_dir(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Create a unique endpoint and deployment name to avoid collisions in home directory
        endpoint_name = "ept-" + randstr("ep")
        deployment_name = "dpm-" + randstr("dp")

        # Get the base deployment directory path for a non-None deployment_name
        deployment_dir = _get_deployment_directory(endpoint_name=endpoint_name, deployment_name=deployment_name)
        # The deployment dir should contain the endpoint and deployment name segments
        assert endpoint_name in str(deployment_dir)
        assert deployment_name in str(deployment_dir)

        # Create the build directory and verify it exists
        build_dir = _create_build_directory(endpoint_name=endpoint_name, deployment_name=deployment_name)
        assert build_dir.exists()
        # Cleanup created directory tree if present
        try:
            # Only remove the specific directory created under home to avoid accidental deletions
            if build_dir.exists():
                # Remove only the leaf directory created
                build_dir.rmdir()
        except Exception:
            # If unable to remove due to permissions in recorded environments, ignore
            pass

    def test_convert_json_to_deployment_and_stubbed_metadata(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Prepare a minimal deployment JSON that OnlineDeployment._load can accept
        name = "dep-" + randstr("name")
        endpoint = "ept-" + randstr("ep")
        deployment_json = {"name": name, "endpoint_name": endpoint}

        # Convert JSON to OnlineDeployment using helper
        deployment_entity = _convert_json_to_deployment(
            deployment_json=deployment_json,
            provisioning_state="Succeeded",
            instance_type=LocalEndpointConstants.ENDPOINT_STATE_LOCATION,
        )
        assert isinstance(deployment_entity, OnlineDeployment)
        # The returned entity should carry the name we provided
        assert getattr(deployment_entity, "name") == name

        # Verify stubbed endpoint metadata string contains the endpoint name
        stubbed = _get_stubbed_endpoint_metadata(endpoint_name=endpoint)
        parsed = json.loads(stubbed)
        assert parsed.get("name") == endpoint

# Additional tests merged from generated batch, placed in a separate class to avoid duplicating existing test blocks
import uuid
import random


@pytest.fixture
def randstr():
    """Simple randstr fixture for unit tests that generates random strings without recording infrastructure."""
    def _generate(variable_name: str) -> str:
        return f"test_{random.randint(1, 1000000000000)}"
    return _generate


@pytest.mark.unittest
class TestLocalDeploymentHelperGaps_Additional:
    def test_write_conda_file_and_readback(self, client: MLClient, tmp_path: Path) -> None:
        """Verify _write_conda_file writes contents with correct encoding and filename."""
        conda_contents = "name: test-env\ndependencies:\n  - python=3.8\n"
        filename = "environment.yml"
        target_dir = str(tmp_path)

        # Write file
        _write_conda_file(conda_contents=conda_contents, directory_path=target_dir, conda_file_name=filename)

        # Read back with utf-8 encoding and assert contents match exactly
        written_path = tmp_path / filename
        assert written_path.exists()
        read_back = written_path.read_text(encoding="utf-8")
        assert read_back == conda_contents

    def test_convert_json_to_deployment_and_stubbed_metadata(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Verify _convert_json_to_deployment produces an OnlineDeployment and stubbed metadata is correct."""
        # Prepare minimal deployment json compatible with OnlineDeployment._load
        name = randstr("endpoint")
        deployment_name = "dpm-" + uuid.uuid4().hex[:8]
        deployment_json = {
            "name": deployment_name,
            "endpoint_name": name,
            # Provide minimal required fields for OnlineDeployment entity
            "instance_type": "test",
        }

        # Convert json to deployment and pass extra kwargs to be applied via params_override
        od = _convert_json_to_deployment(deployment_json=deployment_json, provisioning_state=LocalEndpointConstants.ENDPOINT_STATE_LOCATION)
        assert isinstance(od, OnlineDeployment)
        assert od.name == deployment_name
        assert od.endpoint_name == name

        # Stubbed metadata should be valid json containing the endpoint name
        stub = _get_stubbed_endpoint_metadata(endpoint_name=name)
        assert isinstance(stub, str)
        assert '"name": "' + name + '"' in stub

    def test_create_build_directory_and_get_deployment_directory(self, client: MLClient, randstr: Callable[[], str], tmp_path: Path) -> None:
        """Verify _create_build_directory creates the expected path and _get_deployment_directory composes paths."""
        endpoint = randstr("ep")
        deployment = "dep-" + uuid.uuid4().hex[:8]

        # Create build directory using helper which uses Path.home() by design
        build_dir = _create_build_directory(endpoint_name=endpoint, deployment_name=deployment)
        assert build_dir.exists()
        assert build_dir.is_dir()

        # Ensure that returned path matches _get_deployment_directory for the same inputs
        composed = _get_deployment_directory(endpoint_name=endpoint, deployment_name=deployment)
        assert composed == build_dir

        # When deployment_name is None, the path returned will not include a separate empty segment; ensure it contains the endpoint segment
        composed_none = _get_deployment_directory(endpoint_name=endpoint, deployment_name=None)
        assert composed_none.name == endpoint
