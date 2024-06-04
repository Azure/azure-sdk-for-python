import json
from pathlib import Path
from typing import Union

import pytest
from marshmallow import ValidationError

from azure.ai.ml import MLClient, load_component
from azure.ai.ml.entities import CommandComponent, Environment
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.exceptions import ValidationException

from .._util import _COMPONENT_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestComponentValidate:
    def test_component_name_validate(self):
        invalid_component_names = [
            "1",
            "Abc",
            "aBc",
            "a-c",
            "_abc",
            "1abc",
            ":::",
            "hello.world",
        ]
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        for invalid_name in invalid_component_names:
            params_override = [{"name": invalid_name}]
            with pytest.raises(ValidationError) as e:
                load_component(test_path, params_override=params_override)
            err_msg = "Component name should only contain lower letter, number, underscore"
            assert err_msg in str(e.value)

        valid_component_names = ["n", "name", "n_a_m_e", "name_1"]
        for valid_name in valid_component_names:
            params_override = [{"name": valid_name}]
            load_component(test_path, params_override=params_override)

    def test_component_input_name_validate(self):
        yaml_files = [
            str(components_dir / "invalid/helloworld_component_with_blank_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_dash_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_special_character_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_dash_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_number_input_names.yml"),
        ]
        for yaml_file in yaml_files:
            component = load_component(yaml_file)
            with pytest.raises(ValidationException, match="is not a valid parameter name"):
                component()

    def test_component_output_name_validate(self):
        yaml_files = [
            str(components_dir / "invalid/helloworld_component_with_blank_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_dash_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_special_character_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_dash_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_number_output_names.yml"),
        ]
        for yaml_file in yaml_files:
            component = load_component(yaml_file)
            with pytest.raises(ValidationException, match="is not a valid parameter name"):
                component()

    @pytest.mark.usefixtures("enable_private_preview_schema_features")
    def test_component_early_available_output_not_set_is_control(self):
        yaml_file = str(components_dir / "invalid/helloworld_component_early_available_output_not_set_is_control.yml")
        component = load_component(yaml_file)
        validation_result = component._validate()
        assert validation_result.passed

    @pytest.mark.parametrize(
        "expected_location,asset_object",
        [
            pytest.param(
                "code",
                Code(name="AzureML-Code", version="1"),
                id="code",
            ),
            pytest.param(
                "environment",
                Environment(name="AzureML-Minimal", version="1"),
                id="environment",
            ),
        ],
    )
    def test_component_validate_versioned_asset_dependencies(
        self,
        expected_location: str,
        asset_object: Union[Code, Environment],
    ) -> None:
        component_path = "./tests/test_configs/components/helloworld_component.yml"
        component = load_component(component_path)
        assert component._validate().passed is True, json.dumps(component._to_dict(), indent=2)

        def _check_validation_result(new_asset, should_fail=False) -> None:
            setattr(component, expected_location, new_asset)
            validation_result = component._validate()
            if should_fail:
                assert validation_result.passed is False and expected_location in validation_result.error_messages, (
                    f"field {expected_location} with value {str(new_asset)} should be invalid, "
                    f"but validation message is {repr(validation_result)}"
                )
            else:
                assert validation_result.passed, (
                    f"field {expected_location} with value {str(new_asset)} should be valid, "
                    f"but met unexpected error: {repr(validation_result)}"
                )

        # object
        # _check_validation_result(asset_object)
        # versioned
        _check_validation_result("azureml:{}:1".format(asset_object.name))
        # labelled
        _check_validation_result("{}@latest".format(asset_object.name))

        # invalid. default version is allowed for environment
        if expected_location not in ["environment"]:
            _check_validation_result("{}".format(asset_object.name), True)

        if expected_location in ["code"]:
            # non-existent path
            _check_validation_result("/tmp/non-existent-path", True)
            # existent path
            _check_validation_result("../python")

    def test_component_validate_multiple_invalid_fields(self, mock_machinelearning_client: MLClient) -> None:
        component_path = "./tests/test_configs/components/helloworld_component.yml"
        location_str = str(Path(component_path).resolve().absolute())
        component: CommandComponent = load_component(component_path)
        component.name = None
        component.command += " & echo ${{inputs.non_existent}} & echo ${{outputs.non_existent}}"
        validation_result = mock_machinelearning_client.components.validate(
            component,
            # skip remote validation for unit test as it requires a valid workspace to fetch the location
            skip_remote_validation=True,
        )
        assert validation_result.passed is False
        assert validation_result._to_dict() == {
            "errors": [
                {
                    "location": f"{location_str}#line 3",
                    "message": "Missing data for required field.",
                    "path": "name",
                    "value": None,
                },
                {
                    "location": f"{location_str}#line 28",
                    "message": "Invalid data binding expression: inputs.non_existent, outputs.non_existent",
                    "path": "command",
                    "value": "echo Hello World & echo "
                    "$[[${{inputs.component_in_number}}]] & echo "
                    "${{inputs.component_in_path}} & echo "
                    "${{outputs.component_out_path}} > "
                    "${{outputs.component_out_path}}/component_in_number & "
                    "echo ${{inputs.non_existent}} & echo "
                    "${{outputs.non_existent}}",
                },
            ],
            "result": "Failed",
        }
