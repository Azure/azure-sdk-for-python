import pytest
from collections import OrderedDict

from azure.ai.ml._utils.utils import (
    dict_eq,
    _get_mfe_base_url_from_batch_endpoint,
    map_single_brackets_and_warn,
    is_data_binding_expression,
    get_all_data_binding_expressions,
)
from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict


@pytest.mark.unittest
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
