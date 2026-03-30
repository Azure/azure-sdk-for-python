import json
from pathlib import Path
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import ValidationException, MlException
from azure.ai.ml._ml_client import _add_user_agent, USER_AGENT


@pytest.fixture
def randstr():
    """Generate a random string for test isolation."""
    import random, string
    def _gen(prefix=""):
        return prefix + "".join(random.choices(string.ascii_lowercase, k=8))
    return _gen


@pytest.mark.unittest
class TestMLClientInitBranches:
    def test_init_without_cloud_uses_default_and_sets_cloud_attribute(self, client: MLClient) -> None:
        # When no 'cloud' kwarg is provided, MLClient should use the default cloud name
        ml = MLClient(credential=client._credential)
        # The _cloud attribute should be set (to some default string); ensure it's present and non-empty
        assert hasattr(ml, "_cloud")
        assert isinstance(ml._cloud, str)
        assert ml._cloud

    def test_init_with_none_credential_raises_value_error(self) -> None:
        # Passing None as credential should raise ValueError per constructor validation
        with pytest.raises(ValueError) as exc:
            MLClient(credential=None)
        assert "credential can not be None" in str(exc.value)

    def test_init_with_both_registry_and_workspace_raises_validation_exception(self, client: MLClient) -> None:
        # Supplying both registry_name and workspace_name should raise ValidationException
        with pytest.raises(ValidationException):
            MLClient(credential=client._credential, workspace_name="w", registry_name="r")


@pytest.mark.unittest
class TestMLClientFromConfig:
    def test_from_config_with_file_reads_file(self, client: MLClient, tmp_path: Path) -> None:
        # Arrange: create a config file with subscription_id, resource_group, workspace_name
        config = {
            "subscription_id": "sub-123",
            "resource_group": "rg-abc",
            "workspace_name": "ws-name",
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        # Act: call from_config with the file path
        new_client = MLClient.from_config(credential=client._credential, path=str(config_path))

        # Assert: returned MLClient has workspace_name taken from config
        assert new_client.workspace_name == "ws-name"
        assert new_client.resource_group_name == "rg-abc"
        assert new_client.subscription_id == "sub-123"

    def test_from_config_missing_raises_validation_exception(self, client: MLClient, tmp_path: Path) -> None:
        # Arrange: use an empty directory with no config files present
        search_path = tmp_path / "subdir"
        search_path.mkdir()

        # Act / Assert: calling from_config should raise ValidationException when no config found
        with pytest.raises(ValidationException):
            MLClient.from_config(credential=client._credential, path=str(search_path))

    def test_from_config_with_scope_parses_arm_scope(self, client: MLClient, tmp_path: Path) -> None:
        # Create a config file that contains an ARM Scope string
        # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{ws}
        scope_value = "/subscriptions/sub-scope/resourceGroups/rg-scope/providers/Microsoft.MachineLearningServices/workspaces/ws-scope"
        config = {"Scope": scope_value}
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        new_client = MLClient.from_config(credential=client._credential, path=str(config_path))

        # Values should be parsed from the Scope string
        assert new_client.subscription_id == "sub-scope"
        assert new_client.resource_group_name == "rg-scope"
        assert new_client.workspace_name == "ws-scope"

    def test_from_config_with_scope_parses_scope_and_returns_client(self, client: MLClient, randstr: Callable[[str], str], tmp_path: Path) -> None:
        # Create a config file that contains a Scope value and ensure MLClient.from_config parses it
        scope = "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.MachineLearningServices/workspaces/{ws}".format(
            sub=randstr("sub"), rg=randstr("rg"), ws=randstr("ws")
        )
        config = {"Scope": scope}
        config_path = tmp_path / "config_with_scope.json"
        config_path.write_text(json.dumps(config))

        new_client = MLClient.from_config(credential=client._credential, path=str(config_path))
        # The workspace name should be parsed out of the Scope
        assert new_client.workspace_name == scope.split("/")[8]

    def test_from_config_missing_required_keys_raises_validation(self, client: MLClient, tmp_path: Path) -> None:
        # Create a config file without Scope and missing required keys to trigger ValidationException
        # Provide only subscription_id to make it invalid
        config = {"subscription_id": "only-sub"}
        config_path = tmp_path / "invalid_config.json"
        config_path.write_text(json.dumps(config))

        with pytest.raises(ValidationException) as excinfo:
            MLClient.from_config(credential=client._credential, path=str(config_path))

        assert "does not seem to contain the required parameters" in str(excinfo.value)


@pytest.mark.unittest
class TestMLClientGaps:
    def test_create_or_update_with_unsupported_type_raises_typeerror(self, client: MLClient) -> None:
        """Verify calling create_or_update with an unsupported type raises the exact TypeError.

        Covered marker lines: 875, 878
        Trigger strategy: Call public client.create_or_update with an integer to hit the singledispatch fallback.
        """
        expected_message = "Please refer to create_or_update docstring for valid input types."
        with pytest.raises(TypeError) as excinfo:
            client.create_or_update(123)  # unsupported type triggers singledispatch fallback
        assert str(excinfo.value) == expected_message

    def test_begin_create_or_update_with_unsupported_type_raises_typeerror(self, client: MLClient) -> None:
        """Verify calling begin_create_or_update with an unsupported type raises the exact TypeError.

        Covered marker lines: 885
        Trigger strategy: Call public client.begin_create_or_update with an integer to hit the singledispatch fallback.
        """
        expected_message = "Please refer to begin_create_or_update docstring for valid input types."
        with pytest.raises(TypeError) as excinfo:
            client.begin_create_or_update(123)  # unsupported type triggers singledispatch fallback
        assert str(excinfo.value) == expected_message

    def test_add_user_agent_appends_sdk_user_agent(self) -> None:
        """Verify the internal _add_user_agent helper sets/ appends the SDK USER_AGENT correctly.

        Covered marker lines: 766, 767
        Trigger strategy: Call the module-level helper directly and inspect the kwargs mutation.
        """
        # case 1: no existing user_agent
        kwargs = {}
        _add_user_agent(kwargs)
        assert "USER_AGENT" in globals() or True  # sanity placeholder to align with style; real check follows
        assert kwargs.get("user_agent") == USER_AGENT

        # case 2: existing user_agent value should be appended with a space separator
        kwargs = {"user_agent": "my-app/1.0"}
        _add_user_agent(kwargs)
        assert kwargs.get("user_agent") == f"my-app/1.0 {USER_AGENT}"
