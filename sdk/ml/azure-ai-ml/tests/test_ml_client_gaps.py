import json
from pathlib import Path
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import ValidationException

@pytest.mark.unittest
class TestMLClientGaps:
    def test_create_or_update_with_unsupported_entity_raises_type_error(self, client: MLClient) -> None:
        # Pass an unsupported entity type (a plain dict) to client.create_or_update to trigger singledispatch TypeError
        unsupported_entity = {"not": "a valid entity"}
        with pytest.raises(TypeError):
            client.create_or_update(unsupported_entity)  # should raise before any network call

    def test_from_config_raises_when_config_not_found(self, client: MLClient, tmp_path: Path) -> None:
        # Provide a directory without config.json to from_config and expect a ValidationException
        missing_dir = tmp_path / "no_config_here"
        missing_dir.mkdir()
        with pytest.raises(ValidationException):
            MLClient.from_config(credential=client._credential, path=str(missing_dir))

    def test__get_workspace_info_parses_scope_and_returns_parts(self, client: MLClient, tmp_path: Path) -> None:
        # Create a temporary config file containing a Scope ARM string and verify parsing
        scope_value = (
            "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-example/providers/"
            "Microsoft.MachineLearningServices/workspaces/ws-example"
        )
        cfg = {"Scope": scope_value}
        cfg_file = tmp_path / "cfg_with_scope.json"
        cfg_file.write_text(json.dumps(cfg))

        subscription_id, resource_group, workspace_name = MLClient._get_workspace_info(str(cfg_file))

        assert subscription_id == "11111111-1111-1111-1111-111111111111"
        assert resource_group == "rg-example"
        assert workspace_name == "ws-example"

    def test__ml_client_cli_creates_client_and_repr_contains_subscription(self, client: MLClient) -> None:
        # Use existing client's credential and subscription to create a cli client
        cli_client = MLClient._ml_client_cli(credentials=client._credential, subscription_id=client.subscription_id)
        assert isinstance(cli_client, MLClient)
        # repr should include the subscription id string
        assert str(client.subscription_id) in repr(cli_client)

    def test_create_or_update_with_unsupported_type_raises_type_error(self, client: MLClient) -> None:
        """Trigger the singledispatch default branch for _create_or_update by passing an unsupported type.

        Covered marker lines: 1099, 1109, 1118
        """
        # Pass a plain dict which is not a supported entity type to client.create_or_update
        with pytest.raises(TypeError) as excinfo:
            client.create_or_update({"not": "an entity"})
        assert "Please refer to create_or_update docstring for valid input types." in str(excinfo.value)

    def test_begin_create_or_update_with_unsupported_type_raises_type_error(self, client: MLClient) -> None:
        """Trigger the singledispatch default branch for _begin_create_or_update by passing an unsupported type.

        Covered marker lines: 1164, 1174, 1194
        """
        # Pass a plain dict which is not a supported entity type to client.begin_create_or_update
        with pytest.raises(TypeError) as excinfo:
            client.begin_create_or_update({"not": "an entity"})
        assert "Please refer to begin_create_or_update docstring for valid input types." in str(excinfo.value)

    def test_ml_client_cli_returns_client_and_repr_includes_subscription(self, client: MLClient) -> None:
        """Verify MLClient._ml_client_cli constructs an MLClient and its repr contains the subscription id.

        Covered marker lines: 981, 999, 1232, 1242
        """
        # Use the existing client's credential to create a CLI client simulation
        subscription = "cli-subscription-123"
        cli_client = MLClient._ml_client_cli(client._credential, subscription)
        r = repr(cli_client)
        assert subscription in r
        # Ensure the returned object is an MLClient and has the subscription property set
        assert isinstance(cli_client, MLClient)
        assert cli_client.subscription_id == subscription

@pytest.mark.unittest
class TestMLClientFromConfig:
    def test_from_config_missing_keys_raises_validation(self, client: MLClient, tmp_path: Path) -> None:
        # Create a config file missing required keys (no subscription_id/resource_group/workspace_name and no Scope)
        cfg = {"some_key": "some_value"}
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(cfg))

        # Calling from_config should raise a ValidationException describing missing parameters
        with pytest.raises(ValidationException) as ex:
            MLClient.from_config(credential=client._credential, path=str(cfg_file))

        assert "does not seem to contain the required" in str(ex.value.message)

    def test_from_config_with_scope_parses_scope_and_returns_client(self, client: MLClient, tmp_path: Path) -> None:
        # Create a config file that contains an ARM Scope string
        subscription = "sub-12345"
        resource_group = "rg-test"
        workspace = "ws-test"
        scope = f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace}"
        cfg = {"Scope": scope}
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(cfg))

        # Use existing client's credential to create a new client from the config file
        new_client = MLClient.from_config(credential=client._credential, path=str(cfg_file))

        # The returned MLClient should reflect the parsed subscription id, resource group, and workspace name
        assert new_client.subscription_id == subscription
        assert new_client.resource_group_name == resource_group
        assert new_client.workspace_name == workspace

def test_begin_create_or_update_singledispatch_default_raises_type_error(
    client: MLClient,
) -> None:
    # Passing an unsupported type (dict) to begin_create_or_update should raise TypeError
    with pytest.raises(TypeError) as excinfo:
        client.begin_create_or_update({"not": "an entity"})
    assert "Please refer to begin_create_or_update docstring for valid input types." in str(excinfo.value)
