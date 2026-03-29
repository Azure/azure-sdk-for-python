import random
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.operations._environment_operations import _preprocess_environment_name
from azure.ai.ml.constants._common import ARM_ID_PREFIX


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsGetValidation(AzureRecordedTestCase):
    def test_get_raises_when_version_and_label_provided(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        name = randstr("name")
        # Provide both version and label -> should raise ValidationException (INVALID_VALUE)
        with pytest.raises(ValidationException) as ex:
            client._environments.get(name=name, version="1", label="latest")

        assert "Cannot specify both version and label." in str(ex.value)

    def test_get_raises_when_neither_version_nor_label_provided(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        name = randstr("name")
        # Provide neither version nor label -> should raise ValidationException (MISSING_FIELD)
        with pytest.raises(ValidationException) as ex:
            client._environments.get(name=name)

        assert "Must provide either version or label." in str(ex.value)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsGaps(AzureRecordedTestCase):
    def test_preprocess_environment_name_strips_arm_prefix(self, client: MLClient) -> None:
        # Verify helper strips ARM id prefix when present
        arm_prefixed = "\/subscriptions\/00000000-0000-0000-0000-000000000000\/resourceGroups\/rg\/providers\/Microsoft.MachineLearningServices\/workspaces\/ws\/environments\/env-name"
        # _preprocess_environment_name should remove the ARM_ID_PREFIX if present
        processed = _preprocess_environment_name(arm_prefixed)
        assert processed.endswith("environments\/env-name") is True

    def test_set_registry_client_restores_state_on_failure(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Ensure that even when share fails (likely due to invalid registry), operation scope and clients are restored
        original_registry = client._operation_scope.registry_name
        original_rg = client._operation_scope._resource_group_name
        original_sub = client._operation_scope._subscription_id

        name = randstr("name")
        version = "1"
        share_with_name = name
        share_with_version = version
        # Use a random registry name that will likely cause get_registry_client to fail, triggering finally block
        bad_registry = f"invalid-reg-{random.randint(1,1000000)}"

        with pytest.raises(Exception):
            client._environments.share(name=name, version=version, share_with_name=share_with_name, share_with_version=share_with_version, registry_name=bad_registry)

        # After failure, ensure the client's operation scope and service client were restored
        assert client._operation_scope.registry_name == original_registry
        assert client._operation_scope._resource_group_name == original_rg
        assert client._operation_scope._subscription_id == original_sub


# Additional tests merged from generated batch (non-duplicative names)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsAdditionalGaps(AzureRecordedTestCase):
    def test_preprocess_environment_name_strips_arm_prefix_with_constant(self) -> None:
        # Validate ARM id stripping behavior using the ARM_ID_PREFIX constant
        raw = ARM_ID_PREFIX + "/subscriptions/000/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/environments/myenv/versions/1"
        processed = _preprocess_environment_name(raw)
        assert not processed.startswith(ARM_ID_PREFIX)
        assert "environments/myenv/versions/1" in processed

    def test_set_registry_client_restores_service_client_and_version_ops_on_failure(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Capture pre-call operation scope and service client references
        env_ops = client._environments
        orig_registry = env_ops._operation_scope.registry_name
        orig_rg = env_ops._operation_scope._resource_group_name
        orig_sub = env_ops._operation_scope._subscription_id
        orig_service_client = env_ops._service_client
        orig_version_ops = env_ops._version_operations

        bogus_registry = randstr("reg") + str(random.randint(100000, 999999))

        # Call share with a registry name that is extremely unlikely to exist to force failure
        try:
            with pytest.raises(Exception):
                env_ops.share(name="does-not-matter", version="1", share_with_name="", share_with_version="", registry_name=bogus_registry)
        finally:
            # After failure, ensure the context manager restored original state
            assert env_ops._operation_scope.registry_name == orig_registry
            assert env_ops._operation_scope._resource_group_name == orig_rg
            assert env_ops._operation_scope._subscription_id == orig_sub
            assert env_ops._service_client is orig_service_client
            assert env_ops._version_operations is orig_version_ops
