from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineDeployment, ManagedOnlineEndpoint, Model, CodeConfiguration, Environment
from azure.ai.ml.exceptions import InvalidVSCodeRequestError, LocalDeploymentGPUNotAvailable, ValidationException
from azure.ai.ml.constants._deployment import EndpointDeploymentLogContainerType


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestOnlineDeploymentGaps(AzureRecordedTestCase):
    def test_vscode_debug_raises_when_not_local(
        self, client: MLClient, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]
    ) -> None:
        """Covers branch where vscode_debug is True but local is False -> InvalidVSCodeRequestError"""
        online_endpoint_name = rand_online_name("online_endpoint_name")
        online_deployment_name = rand_online_deployment_name("online_deployment_name")

        # create an online endpoint minimal
        endpoint = ManagedOnlineEndpoint(
            name=online_endpoint_name,
            description="endpoint for vscode debug test",
            auth_mode="key",
            tags={"foo": "bar"},
        )

        client.begin_create_or_update(endpoint).result()

        try:
            # prepare a minimal deployment
            model = Model(name="test-model", path="tests/test_configs/deployments/model-1/model")
            code_config = CodeConfiguration(code="tests/test_configs/deployments/model-1/onlinescoring/", scoring_script="score.py")
            environment = Environment(conda_file="tests/test_configs/deployments/model-1/environment/conda.yml")

            blue_deployment = ManagedOnlineDeployment(
                name=online_deployment_name,
                endpoint_name=online_endpoint_name,
                code_configuration=code_config,
                environment=environment,
                model=model,
                instance_type="Standard_DS3_v2",
                instance_count=1,
            )

            with pytest.raises(InvalidVSCodeRequestError):
                # This should raise before any remote call because vscode_debug requires local=True
                client.online_deployments.begin_create_or_update(blue_deployment, vscode_debug=True).result()
        finally:
            client.online_endpoints.begin_delete(name=online_endpoint_name)

    def test_local_enable_gpu_raises_when_nvidia_missing(self, client: MLClient, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]) -> None:
        """Covers branch where local is True and local_enable_gpu True but nvidia-smi is unavailable -> LocalDeploymentGPUNotAvailable"""
        online_endpoint_name = rand_online_name("online_endpoint_name")
        online_deployment_name = rand_online_deployment_name("online_deployment_name")

        # create an online endpoint for local deployment testing
        endpoint = ManagedOnlineEndpoint(
            name=online_endpoint_name,
            description="endpoint for local gpu test",
            auth_mode="key",
        )

        client.begin_create_or_update(endpoint).result()

        try:
            model = Model(name="test-model", path="tests/test_configs/deployments/model-1/model")
            code_config = CodeConfiguration(code="tests/test_configs/deployments/model-1/onlinescoring/", scoring_script="score.py")
            environment = Environment(conda_file="tests/test_configs/deployments/model-1/environment/conda.yml")

            blue_deployment = ManagedOnlineDeployment(
                name=online_deployment_name,
                endpoint_name=online_endpoint_name,
                code_configuration=code_config,
                environment=environment,
                model=model,
                instance_type="Standard_DS3_v2",
                instance_count=1,
            )

            # Request local deployment with GPU enabled. In CI environment without GPUs, this should raise.
            with pytest.raises(LocalDeploymentGPUNotAvailable):
                client.online_deployments.begin_create_or_update(blue_deployment, local=True, local_enable_gpu=True).result()
        finally:
            client.online_endpoints.begin_delete(name=online_endpoint_name)

    def test_get_logs_invalid_container_type_raises_validation(self, client: MLClient, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]) -> None:
        """Covers branches in _validate_deployment_log_container_type that raise ValidationException for invalid types"""
        online_endpoint_name = rand_online_name("online_endpoint_name")
        online_deployment_name = rand_online_deployment_name("online_deployment_name")

        # create an online endpoint
        endpoint = ManagedOnlineEndpoint(
            name=online_endpoint_name,
            description="endpoint for logs test",
            auth_mode="key",
        )

        client.begin_create_or_update(endpoint).result()

        try:
            # Do not create a deployment or environment here because the validation of container_type
            # happens before any remote call in get_logs. Calling get_logs with an invalid container_type
            # should raise ValidationException without needing a deployed deployment.
            with pytest.raises(ValidationException):
                client.online_deployments.get_logs(name=online_deployment_name, endpoint_name=online_endpoint_name, lines=10, container_type="invalid_container")
        finally:
            client.online_endpoints.begin_delete(name=online_endpoint_name)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestOnlineDeploymentOperationsGaps(AzureRecordedTestCase):
    def test_get_logs_invalid_container_type_raises_validation_without_endpoint(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Calling get_logs with an invalid container_type should raise a ValidationException before any service call."""
        endpoint_name = randstr("endpoint-name")
        deployment_name = randstr("deployment-name")

        # Use a container_type string that is not supported to trigger the validation branch
        with pytest.raises(ValidationException):
            client.online_deployments.get_logs(name=deployment_name, endpoint_name=endpoint_name, lines=10, container_type="INVALID_CONTAINER_TYPE")

    def test_get_logs_accepts_known_container_enum(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Passing a supported EndpointDeploymentLogContainerType should be accepted by validator (may still fail on service call)."""
        endpoint_name = randstr("endpoint-name")
        deployment_name = randstr("deployment-name")

        # This triggers the branch that maps the enum to the REST representation. The call may raise if the endpoint/deployment doesn't exist;
        # we assert that, if an exception is raised, it is not a ValidationException coming from the client-side validator.
        try:
            client.online_deployments.get_logs(
                name=deployment_name,
                endpoint_name=endpoint_name,
                lines=5,
                container_type=EndpointDeploymentLogContainerType.INFERENCE_SERVER,
            )
        except Exception as ex:
            # Ensure validation did not raise; other service errors are acceptable for this integration-level check
            assert not isinstance(ex, ValidationException)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestOnlineDeploymentLogsValidation(AzureRecordedTestCase):
    def test_get_logs_with_invalid_container_type_raises_validation(self, client: MLClient) -> None:
        """Ensure passing an unsupported container_type raises a ValidationException.

        Covers: branch where _validate_deployment_log_container_type raises ValidationException for invalid value.
        """
        # Use an obviously invalid container type string to trigger client-side validation
        with pytest.raises(ValidationException):
            client.online_deployments.get_logs(name="nonexistent", endpoint_name="nonexistent", lines=10, container_type="INVALID")

    def test_get_logs_with_known_container_enum_does_not_raise_validation(self, client: MLClient) -> None:
        """Ensure passing a known EndpointDeploymentLogContainerType enum value does not raise client-side ValidationException.

        Covers: mapping branches for EndpointDeploymentLogContainerType.INFERENCE_SERVER (and by symmetry STORAGE_INITIALIZER).
        The call may raise service-side errors, but it must not raise ValidationException from client-side validation.
        """
        try:
            result = client.online_deployments.get_logs(
                name="nonexistent",
                endpoint_name="nonexistent",
                lines=5,
                container_type=EndpointDeploymentLogContainerType.INFERENCE_SERVER,
            )
            # If the service returned content, ensure it is returned as a string
            assert isinstance(result, str)
        except Exception as ex:
            assert not isinstance(ex, ValidationException), "ValidationException was raised for a known EndpointDeploymentLogContainerType enum value"