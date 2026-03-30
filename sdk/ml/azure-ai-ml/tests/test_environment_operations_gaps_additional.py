import random
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsShareRestore(AzureRecordedTestCase):
    def test_share_restores_operation_scope_on_failure(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Call share with a (likely) non-existent registry to force get_registry_client to fail.
        # Ensure that even on failure the _set_registry_client contextmanager restores the original scope and service client.
        env_name = randstr("name")
        version = "1"
        registry_name = f"nonexistent-reg-{random.randint(1,1000000)}"

        env_ops = client._environments
        # capture current scope values
        original_registry = env_ops._operation_scope.registry_name
        original_rg = env_ops._operation_scope._resource_group_name
        original_sub = env_ops._operation_scope._subscription_id
        original_service_client = env_ops._service_client
        original_version_ops = env_ops._version_operations

        with pytest.raises(Exception):
            env_ops.share(name=env_name, version=version, share_with_name="", share_with_version="", registry_name=registry_name)

        # After exception, contextmanager finally should have restored original values
        assert env_ops._operation_scope.registry_name == original_registry
        assert env_ops._operation_scope._resource_group_name == original_rg
        assert env_ops._operation_scope._subscription_id == original_sub
        assert env_ops._service_client == original_service_client
        assert env_ops._version_operations == original_version_ops


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsGaps_Additional(AzureRecordedTestCase):
    def test_set_registry_client_restores_state_on_failure(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Capture original state
        env_ops = client._environments
        original_registry = env_ops._operation_scope.registry_name
        original_rg = env_ops._operation_scope._resource_group_name
        original_sub = env_ops._operation_scope._subscription_id
        original_service_client = env_ops._service_client
        original_version_ops = env_ops._version_operations

        # Use unlikely registry name to trigger failure in get_registry_client or subsequent registry client setup.
        # The call is expected to raise an exception but the context manager should restore internal state in finally.
        bad_registry_name = randstr("reg") + str(random.randint(100000, 999999))

        with pytest.raises(Exception):
            # call share which uses the _set_registry_client context manager internally
            env_ops.share(
                name=randstr("name"),
                version="1",
                share_with_name=randstr("name2"),
                share_with_version="1",
                registry_name=bad_registry_name,
            )

        # After exception, internal state should be restored to originals
        assert env_ops._operation_scope.registry_name == original_registry
        assert env_ops._operation_scope._resource_group_name == original_rg
        assert env_ops._operation_scope._subscription_id == original_sub
        assert env_ops._service_client == original_service_client
        assert env_ops._version_operations == original_version_ops
