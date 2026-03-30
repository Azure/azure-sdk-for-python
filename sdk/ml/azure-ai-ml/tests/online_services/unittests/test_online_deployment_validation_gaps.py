import os
import uuid
from typing import Callable

import re
import pytest
from azure.ai.ml import MLClient, load_online_deployment, load_online_endpoint
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model, CodeConfiguration, Environment
from azure.ai.ml.constants._deployment import EndpointDeploymentLogContainerType
from azure.ai.ml.exceptions import InvalidVSCodeRequestError, LocalDeploymentGPUNotAvailable, ValidationException
from azure.ai.ml._local_endpoints import LocalEndpointMode


@pytest.fixture
def rand_online_name():
    def _gen(prefix=""):
        return f"online-ept-{uuid.uuid4().hex[:15]}"
    return _gen


@pytest.fixture
def rand_online_deployment_name():
    def _gen(prefix=""):
        return f"online-dpm-{uuid.uuid4().hex[:15]}"
    return _gen


@pytest.mark.unittest
class TestOnlineDeploymentOperationsGaps:

    def test_get_logs_with_invalid_container_type_raises_validation(
        self, client, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]
    ) -> None:
        # Prepare names
        endpoint_name = rand_online_name("endpoint_name")
        deployment_name = rand_online_deployment_name("deployment_name")

        # The ValidationException for invalid container type is raised client-side before any service call.
        with pytest.raises(ValidationException):
            client.online_deployments.get_logs(
                name=deployment_name,
                endpoint_name=endpoint_name,
                lines=10,
                container_type="not-a-valid-container",
            )

    def test_begin_create_or_update_vscode_debug_with_remote_raises_invalid_vscode_request(
        self, client, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]
    ) -> None:
        # Create a minimal deployment object loaded from config to pass into begin_create_or_update.
        TESTS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
        deployment_yaml = os.path.join(TESTS_ROOT, "test_configs/deployments/online/online_deployment_1.yaml")
        deployment = load_online_deployment(deployment_yaml)
        deployment.name = rand_online_deployment_name("deployment_name")
        deployment.endpoint_name = rand_online_name("endpoint_name")

        # Requesting vscode_debug while not local should raise InvalidVSCodeRequestError before any service interaction.
        with pytest.raises(InvalidVSCodeRequestError):
            client.online_deployments.begin_create_or_update(deployment, vscode_debug=True).result()

    def test_get_logs_invalid_container_type_raises_validation_exception(self, client: MLClient) -> None:
        # Passing an invalid container type (string that does not match supported enum values)
        # should raise ValidationException before any service call is attempted.
        with pytest.raises(ValidationException):
            client.online_deployments.get_logs(name="nonexistent", endpoint_name="no-endpoint", lines=10, container_type="invalid")

    def test_validate_deployment_log_container_type_enum_mapping(self, client: MLClient) -> None:
        # Call the internal validator directly with the supported enum value and assert
        # it returns the expected REST-mapped string without raising.
        res = client.online_deployments._validate_deployment_log_container_type(
            EndpointDeploymentLogContainerType.INFERENCE_SERVER
        )
        assert res == EndpointDeploymentLogContainerType.INFERENCE_SERVER_REST

    def test_get_local_endpoint_mode_returns_expected_enum(self, client: MLClient) -> None:
        # Ensure the mapping from vscode_debug flag to LocalEndpointMode is correct.
        mode_vscode = client.online_deployments._get_local_endpoint_mode(True)
        mode_detached = client.online_deployments._get_local_endpoint_mode(False)
        assert mode_vscode == LocalEndpointMode.VSCodeDevContainer
        assert mode_detached == LocalEndpointMode.DetachedContainer

    def test_get_arm_deployment_name_is_deterministic_and_contains_workspace(self, client: MLClient) -> None:
        # The generated ARM deployment name should start with the workspace and provided name.
        workspace_name = client.online_deployments._workspace_name
        gen = client.online_deployments._get_ARM_deployment_name("mydeploy")
        assert gen.startswith(f"{workspace_name}-mydeploy-")
        # ensure trailing part is numeric
        trailing = gen.split("-")[-1]
        assert re.match(r"^\d+$", trailing)


@pytest.mark.unittest
class TestOnlineDeploymentGaps:
    def test_validate_deployment_log_container_type_invalid_raises(
        self, client: MLClient
    ) -> None:
        # Provide an unsupported container type to trigger the ValidationException branch
        with pytest.raises(ValidationException):
            client.online_deployments._validate_deployment_log_container_type("not_a_valid_type")

    def test_validate_deployment_log_container_type_maps_to_rest_constant(self, client: MLClient) -> None:
        # Verify mapping for known container types
        val_inf = client.online_deployments._validate_deployment_log_container_type(
            EndpointDeploymentLogContainerType.INFERENCE_SERVER
        )
        assert val_inf == EndpointDeploymentLogContainerType.INFERENCE_SERVER_REST

        val_init = client.online_deployments._validate_deployment_log_container_type(
            EndpointDeploymentLogContainerType.STORAGE_INITIALIZER
        )
        assert val_init == EndpointDeploymentLogContainerType.STORAGE_INITIALIZER_REST
