from pathlib import Path
import pytest
from azure.ai.resources._utils._ai_client_utils import find_config_file_path, get_config_info
from azure.ai.ml.exceptions import ValidationException

class TestFindConfigFilePath:
    def test_passes_with_file_as_path(self):
        config_file_path = find_config_file_path("samples/sample_config/config.json")
        assert(Path(config_file_path).as_posix() == Path("samples/sample_config/config.json").as_posix())

    def test_passes_without_file(self):
        config_file_path = find_config_file_path("samples/sample_config")
        assert(Path(config_file_path).as_posix() == Path("samples/sample_config/config.json").as_posix())

    def test_passes_with_file(self):
        config_file_path = find_config_file_path("samples/sample_config", "config_with_scope.json")
        assert(Path(config_file_path).as_posix() == Path("samples/sample_config/config_with_scope.json").as_posix())

    def test_fails_with_wrong_path(self):
        with pytest.raises(ValidationException):
            find_config_file_path("samples/sample_config2")

class TestGetConfigInfo:
    def test_passes_with_proj_name(self):
        config_info = get_config_info("samples/sample_config/config.json")
        assert(config_info["subscription_id"] == "my_subscription_id")
        assert(config_info["resource_group_name"] == "my_resource_group")
        assert(config_info["project_name"] == "my_project_name")

    def test_passes_with_ws_name(self):
        config_info = get_config_info("samples/sample_config/config_with_ws_name.json")
        assert(config_info["subscription_id"] == "my_subscription_id")
        assert(config_info["resource_group_name"] == "my_resource_group")
        assert(config_info["project_name"] == "my_workspace_name")

    def test_passes_with_ws_and_proj_name(self):
        config_info = get_config_info("samples/sample_config/config_with_ws_and_proj_name.json")
        assert(config_info["subscription_id"] == "my_subscription_id")
        assert(config_info["resource_group_name"] == "my_resource_group")
        assert(config_info["project_name"] == "my_project_name")

    def test_passes_with_scope(self):
        config_info = get_config_info("samples/sample_config/config_with_scope.json")
        assert(config_info["subscription_id"] == "my_subscription_id")
        assert(config_info["resource_group_name"] == "my_resource_group")
        assert(config_info["project_name"] == "my_project_name")

    def test_fails_with_invalid_fields(self):
        with pytest.raises(Exception):
            get_config_info("samples/sample_config/config_with_invalid_fields.json")

    def test_fails_with_file_not_found(self):
        with pytest.raises(Exception):
            get_config_info("samples/sample_config2")
