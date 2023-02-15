import os
import tempfile
from collections import OrderedDict

import pytest

from azure.ai.ml._utils.utils import (
    _get_mfe_base_url_from_batch_endpoint,
    dict_eq,
    get_all_data_binding_expressions,
    is_data_binding_expression,
    map_single_brackets_and_warn,
    write_to_shared_file,
    get_valid_dot_keys_with_wildcard,
)
from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict


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

    def test_open_with_int_mode(self):
        def get_int_mode(file_path: str) -> str:
            int_mode = os.stat(file_path).st_mode & 0o777
            return oct(int_mode)

        with tempfile.TemporaryDirectory() as temp_dir:
            target_file_path = temp_dir + "/test.txt"
            with open(target_file_path, "w") as f:
                # default mode is 0o666 for windows and 0o755 for linux
                f.write("test")
            write_to_shared_file(target_file_path, "test2")
            # check that the file mode is preserved
            assert get_int_mode(target_file_path) == "0o666"
            with open(target_file_path, "r") as f:
                assert f.read() == "test2"

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
