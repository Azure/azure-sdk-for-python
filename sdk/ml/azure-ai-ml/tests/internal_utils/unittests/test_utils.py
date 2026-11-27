import os
import stat
import tempfile
from collections import OrderedDict
from pathlib import Path

import pytest

from azure.ai.ml._internal._schema.component import NodeType as InternalNodeType
from azure.ai.ml._utils.utils import (
    _get_mfe_base_url_from_batch_endpoint,
    dict_eq,
    ensure_private_directory,
    get_all_data_binding_expressions,
    get_base_directory_for_cache,
    get_valid_dot_keys_with_wildcard,
    is_data_binding_expression,
    map_single_brackets_and_warn,
    write_to_private_file,
)
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, get_type_from_spec
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestUtils:
    def test_dict_eq(self) -> None:
        assert dict_eq(dict1={}, dict2=None)
        assert dict_eq(dict1={"blue": 1, "green": 2}, dict2={"blue": 1, "green": 2})

    def test_get_mfe_base_url_from_batch_endpoint(self) -> None:
        endpoint = BatchEndpoint(
            name="bla",
            scoring_uri="https://eastus2euap.api.azureml.ms/mferp/managementfrontend/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/test-rg-eastus2euap-v2-2021W16/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/batchEndpoints/be-20210421/jobs?api-version=2020-09-01-preview",
        )
        assert "https://eastus2euap.api.azureml.ms/mferp/managementfrontend" == _get_mfe_base_url_from_batch_endpoint(
            endpoint
        )

    def test_legacy_command_substitution(self) -> None:
        input_string = "test {inputs.val1} ${{inputs.val2}} {search_space.val3} ${{search_space.val4}} {non-captured}"
        expected_string = (
            "test ${{inputs.val1}} ${{inputs.val2}} ${{search_space.val3}} ${{search_space.val4}} {non-captured}"
        )

        output_string = map_single_brackets_and_warn(input_string)

        assert expected_string == output_string

    def test_is_data_binding_expression(self) -> None:
        target_string = "${{  parent.inputs.input_string  }}"
        assert is_data_binding_expression(target_string)
        assert is_data_binding_expression(target_string, ["parent", "inputs", "input_string"])
        assert not is_data_binding_expression(target_string, ["parent", "outputs"])
        assert not is_data_binding_expression(target_string, ["parent", "inputs", "input_string_2"])

        target_string = "${{  parent.inputs.input_string  }} abc ${{  parent.outputs.output_string  }}"
        assert not is_data_binding_expression(target_string)
        assert is_data_binding_expression(target_string, is_singular=False)
        assert is_data_binding_expression(target_string, ["parent", "inputs", "input_string"], is_singular=False)
        assert not is_data_binding_expression(target_string, ["parent", "name"], is_singular=False)

    def test_get_all_data_binding_expression(self):
        target_string = "cat ${{inputs.input_folder}}/${{inputs.file_name}} && cp ${{inputs.input_folder}}/${{inputs.file_name}} ${{outputs.output_folder}}/${{inputs.file_name}}"
        data_binding_expressions = get_all_data_binding_expressions(target_string, is_singular=False)
        assert data_binding_expressions == [
            "inputs.input_folder",
            "inputs.file_name",
            "inputs.input_folder",
            "inputs.file_name",
            "outputs.output_folder",
            "inputs.file_name",
        ]

    def test_ordered_dict_nested_in_list_conversion(self):
        ordered_dict1, ordered_dict2 = OrderedDict(), OrderedDict()
        ordered_dict1["a"] = 1
        ordered_dict1["b"] = 2
        ordered_dict2["d"] = 3
        ordered_dict2["c"] = 4
        target_list = [ordered_dict1, ordered_dict2]
        assert convert_ordered_dict_to_dict(target_list) == [{"a": 1, "b": 2}, {"d": 3, "c": 4}]

    def test_write_to_private_file(self, tmp_path) -> None:
        target_file_path = tmp_path / "test.txt"
        target_file_path.write_text("test")
        write_to_private_file(target_file_path, "test2")
        assert target_file_path.read_text() == "test2"

    @pytest.mark.skipif(os.name == "nt", reason="POSIX file permissions and symlinks are not used on Windows")
    def test_write_to_private_file_is_owner_only_and_does_not_follow_symlinks(self, tmp_path) -> None:
        target_file_path = tmp_path / "test.txt"
        write_to_private_file(target_file_path, "test")
        assert stat.S_IMODE(target_file_path.stat().st_mode) == 0o600

        existing_file_path = tmp_path / "existing.txt"
        existing_file_path.write_text("old")
        os.chmod(existing_file_path, 0o666)
        write_to_private_file(existing_file_path, "new")
        assert existing_file_path.read_text() == "new"
        assert stat.S_IMODE(existing_file_path.stat().st_mode) == 0o600

        link_path = tmp_path / "link.txt"
        link_path.symlink_to(target_file_path)
        with pytest.raises(OSError):
            write_to_private_file(link_path, "test2")
        assert target_file_path.read_text() == "test"

    def test_get_base_directory_for_cache_is_per_user(self, monkeypatch) -> None:
        monkeypatch.setattr(os, "getuid", lambda: 1234, raising=False)
        assert get_base_directory_for_cache() == Path(tempfile.gettempdir()) / "azure-ai-ml-1234"

    def test_cache_directory_without_user_id_must_be_in_local_app_data(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("azure.ai.ml._utils.utils._get_current_uid", lambda: None)
        local_app_data = tmp_path / "local"
        monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))

        cache_root = get_base_directory_for_cache()
        assert cache_root == local_app_data / "azure-ai-ml" / "cache"
        assert ensure_private_directory(cache_root)

        shared_directory = tmp_path / "shared" / "azure-ai-ml"
        assert not ensure_private_directory(shared_directory)
        assert not shared_directory.exists()

    def test_ensure_private_directory_rejects_directory_owned_by_another_user(self, tmp_path, monkeypatch) -> None:
        directory = tmp_path / "cache"
        directory.mkdir()
        other_uid = os.lstat(directory).st_uid + 1
        monkeypatch.setattr(os, "getuid", lambda: other_uid, raising=False)
        assert not ensure_private_directory(directory)

    @pytest.mark.skipif(os.name == "nt", reason="POSIX file permissions and symlinks are not used on Windows")
    def test_ensure_private_directory_rejects_shared_directories_and_symlinks(self, tmp_path) -> None:
        new_directory = tmp_path / "new"
        old_umask = os.umask(0)
        try:
            assert ensure_private_directory(new_directory)
        finally:
            os.umask(old_umask)
        assert stat.S_IMODE(new_directory.stat().st_mode) == 0o700
        assert ensure_private_directory(new_directory)

        for mode in (0o711, 0o750, 0o755, 0o775, 0o777):
            shared_directory = tmp_path / f"shared_{mode:o}"
            shared_directory.mkdir()
            os.chmod(shared_directory, mode)
            assert not ensure_private_directory(shared_directory)
            assert stat.S_IMODE(shared_directory.stat().st_mode) == mode

        link = tmp_path / "link"
        link.symlink_to(new_directory, target_is_directory=True)
        assert not ensure_private_directory(link)

    def test_get_valid_dot_keys_with_wildcard(self):
        root = {
            "simple": 1,
            "deep": {
                "l1": {
                    "l2": 1,
                    "l2_2": 2,
                },
                "l1_2": {
                    "l2": 3,
                },
            },
        }
        assert get_valid_dot_keys_with_wildcard(root, "simple") == ["simple"]
        assert get_valid_dot_keys_with_wildcard(root, "deep.l1.l2") == ["deep.l1.l2"]
        assert get_valid_dot_keys_with_wildcard(root, "deep.*.l2") == ["deep.l1.l2", "deep.l1_2.l2"]
        assert get_valid_dot_keys_with_wildcard(root, "deep.*.*") == ["deep.l1.l2", "deep.l1.l2_2", "deep.l1_2.l2"]
        assert get_valid_dot_keys_with_wildcard(root, "deep.*.l2_2") == ["deep.l1.l2_2"]
        assert get_valid_dot_keys_with_wildcard(root, "deep.*.l2_3") == []
        assert get_valid_dot_keys_with_wildcard(root, "deep.*.l2.*") == []
        assert get_valid_dot_keys_with_wildcard(root, "deep.*.l2.*.l3") == []

        assert get_valid_dot_keys_with_wildcard(
            root,
            "deep.*.*",
            validate_func=lambda _root, _parts: _parts[1] == "l1_2",
        ) == ["deep.l1_2.l2"]

    def test_get_type_from_spec_case_insensitive(self):
        """Test that get_type_from_spec normalizes type to lowercase for case-insensitive validation."""
        valid_keys = [NodeType.COMMAND, InternalNodeType.COMMAND]

        test_cases = [
            ({"type": "command"}, "command"),  # lowercase
            ({"type": "Command"}, "command"),  # uppercase - should normalize to lowercase
            ({"type": "CommandComponent"}, "CommandComponent"),  # remains unchanged as it's not in NodeType
        ]

        for data, expected in test_cases:
            result = get_type_from_spec(data, valid_keys=valid_keys)
            assert result == expected
