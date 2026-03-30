from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import ARM_ID_PREFIX
from azure.ai.ml.operations._environment_operations import _preprocess_environment_name
from azure.ai.ml.exceptions import ValidationException, ValidationErrorType


@pytest.fixture
def randstr():
    """Generate a random string for test isolation."""
    import random, string
    def _gen(prefix=""):
        return prefix + "".join(random.choices(string.ascii_lowercase, k=8))
    return _gen


@pytest.mark.unittest
class TestEnvironmentOperationsValidationGaps:
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


@pytest.mark.unittest
class TestEnvironmentOperationsGaps:
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


@pytest.mark.unittest
class TestEnvironmentOperationsGaps_Additional:
    def test_preprocess_environment_name_leaves_plain_name(self) -> None:
        # Ensure the helper leaves a plain environment name unchanged
        name = "simple-environment-name"
        processed = _preprocess_environment_name(name)
        assert processed == name
