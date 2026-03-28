import random
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.constants._common import ARM_ID_PREFIX
from azure.ai.ml.operations._environment_operations import _preprocess_environment_name
from azure.core.exceptions import HttpResponseError


@pytest.mark.e2etest
class TestEnvironmentOperationsGaps:
    def test_get_with_both_version_and_label_raises(self, client: MLClient) -> None:
        name = "some-env-name"
        # Pass both version and label to trigger validation branch that forbids both
        with pytest.raises(ValidationException) as ex:
            client.environments.get(name=name, version="1", label="latest")
        assert "Cannot specify both version and label." in str(ex.value)

    def test_get_without_version_or_label_raises(self, client: MLClient) -> None:
        name = "some-env-name"
        # Omit both version and label to trigger missing field validation branch
        with pytest.raises(ValidationException) as ex:
            client.environments.get(name=name)
        assert "Must provide either version or label." in str(ex.value)

    def test_preprocess_environment_name_strips_arm_prefix(self) -> None:
        full = ARM_ID_PREFIX + "my-environment"
        processed = _preprocess_environment_name(full)
        assert processed == "my-environment"


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsGapsAdditional(AzureRecordedTestCase):
    def test_get_preprocess_environment_name_strips_arm_prefix(self, client: MLClient) -> None:
        """Verify that get preprocesses ARM id prefixed names by stripping the ARM prefix.

        This uses a known public curated environment that exists in the workspace and a known
        version so the call proceeds to fetch the environment. The name is passed with the
        ARM_ID_PREFIX to exercise the preprocessing branch.
        """
        # Known environment and version used in existing suite examples
        environment_name = "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu"
        environment_version = "1"
        # Provide the name prefixed with ARM_ID_PREFIX so that preprocessing strips the prefix
        arm_name = ARM_ID_PREFIX + environment_name

        # Call should preprocess the provided name and succeed in fetching the environment
        env = client.environments.get(name=arm_name, version=environment_version)

        assert env.name == environment_name
        assert env.version == environment_version


@pytest.mark.e2etest
class TestEnvironmentOperationsGapsGenerated:
    def test_preprocess_environment_name_returns_same_when_not_arm(self) -> None:
        name = "simple-env-name"
        processed = _preprocess_environment_name(name)
        assert processed == name


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsGapsShare(AzureRecordedTestCase):
    def test_share_restores_registry_client_on_failure(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Choose unique names to avoid collisions
        name = randstr("name")
        version = randstr("ver")
        registry_name = randstr("reg")

        env_ops = client._environments

        # Capture original state
        original_registry_name = env_ops._operation_scope.registry_name
        original_resource_group = env_ops._operation_scope._resource_group_name
        original_subscription = env_ops._operation_scope._subscription_id
        original_service_client = env_ops._service_client
        original_version_operations = env_ops._version_operations

        # Calling share with a likely-nonexistent registry should raise from get_registry_client
        with pytest.raises(HttpResponseError):
            env_ops.share(
                name=name,
                version=version,
                share_with_name=name,
                share_with_version=version,
                registry_name=registry_name,
            )

        # Ensure that even after the exception, the operation scope and service client are restored
        assert env_ops._operation_scope.registry_name == original_registry_name
        assert env_ops._operation_scope._resource_group_name == original_resource_group
        assert env_ops._operation_scope._subscription_id == original_subscription
        assert env_ops._service_client == original_service_client
        assert env_ops._version_operations == original_version_operations
