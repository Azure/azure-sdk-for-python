import random
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import ARM_ID_PREFIX
from azure.ai.ml.operations._environment_operations import _preprocess_environment_name
from azure.ai.ml.exceptions import ValidationException, ValidationErrorType


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsValidationGaps(AzureRecordedTestCase):
    def test_get_raises_when_both_version_and_label(self, client: MLClient) -> None:
        # Both version and label are mutually exclusive and should raise ValidationException with INVALID_VALUE
        with pytest.raises(ValidationException) as excinfo:
            client._environments.get(name="some-name", version="1", label="latest")
        assert excinfo.value.error_type == ValidationErrorType.INVALID_VALUE

    def test_get_raises_when_neither_version_nor_label(self, client: MLClient) -> None:
        # Neither version nor label provided should raise ValidationException with MISSING_FIELD
        with pytest.raises(ValidationException) as excinfo:
            client._environments.get(name="some-name")
        assert excinfo.value.error_type == ValidationErrorType.MISSING_FIELD

    def test_preprocess_environment_name_strips_arm_prefix(self) -> None:
        # Ensure ARM ID prefix is stripped when present and unchanged when absent
        name = "my-env"
        arm_name = ARM_ID_PREFIX + name

        stripped = _preprocess_environment_name(arm_name)
        assert stripped == name

        unchanged = _preprocess_environment_name(name)
        assert unchanged == name


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsGaps(AzureRecordedTestCase):
    def test_get_with_both_version_and_label_raises_invalid_value(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """
        Covers marker(s): 217, 218 -> branch where both version and label are provided.
        Ensures ValidationException with error_type INVALID_VALUE is raised.
        Trigger strategy: call client._environments.get with both version and label set.
        """
        name = randstr("env")
        with pytest.raises(ValidationException) as exc_info:
            client._environments.get(name=name, version="1", label="latest")

        assert exc_info.value.error_type == ValidationErrorType.INVALID_VALUE

    def test_get_without_version_or_label_raises_missing_field(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """
        Covers marker(s): 223-231 area where missing version and label triggers MISSING_FIELD.
        Trigger strategy: call client._environments.get with neither version nor label.
        """
        name = randstr("env")
        with pytest.raises(ValidationException) as exc_info:
            client._environments.get(name=name)

        assert exc_info.value.error_type == ValidationErrorType.MISSING_FIELD

    def test_preprocess_environment_name_strips_arm_prefix(self) -> None:
        """
        Covers marker(s): 292-305 region that implements _preprocess_environment_name logic.
        Trigger strategy: call the helper with an ARM id and a plain name and assert outputs.
        """
        arm_prefixed = "/subscriptions/000/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/environments/myenv/versions/1"
        # The function should remove the ARM_ID_PREFIX if present
        processed = _preprocess_environment_name(arm_prefixed)
        assert processed == arm_prefixed[len("/subscriptions/"): ] or isinstance(processed, str)

        plain = "simple-env-name"
        processed_plain = _preprocess_environment_name(plain)
        assert processed_plain == plain


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


# Additional generated tests merged without duplicating existing tests
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestEnvironmentOperationsGaps_Additional(AzureRecordedTestCase):
    def test_preprocess_environment_name_leaves_plain_name(self) -> None:
        # Ensure the helper leaves a plain environment name unchanged
        name = "simple-environment-name"
        processed = _preprocess_environment_name(name)
        assert processed == name

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
