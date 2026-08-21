import tempfile
from pathlib import Path

import pytest
from marshmallow import ValidationError

from azure.ai.ml import Input, load_component
from azure.ai.ml.entities import CommandComponent, Component, PipelineComponent
from azure.ai.ml.exceptions import UserErrorException, ValidationException

from .._util import _COMPONENT_TIMEOUT_SECOND

components_dir = "./tests/test_configs/components/"


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestAssetBackedInputDefaults:
    @staticmethod
    def _dump_and_reload(component: Component) -> Component:
        with tempfile.TemporaryDirectory() as tmp_dir:
            dump_path = Path(tmp_dir) / "component.yml"
            component.dump(dump_path)
            return load_component(source=dump_path)

    @pytest.mark.parametrize("input_type", ["uri_file", "uri_folder", "mltable"])
    def test_input_with_asset_backed_default(self, input_type: str):
        input_obj = Input(type=input_type, mode="ro_mount", default="azureml:my_asset:1")

        assert input_obj.type == input_type
        assert input_obj.mode == "ro_mount"
        assert input_obj.default == "azureml:my_asset:1"
        assert input_obj._to_dict() == {
            "type": input_type,
            "mode": "ro_mount",
            "default": "azureml:my_asset:1",
        }

    def test_input_with_datastore_uri_default(self):
        default = "azureml://datastores/workspaceblobstore/paths/data/file.csv"
        input_obj = Input(type="uri_file", default=default)

        assert input_obj.default == default
        assert input_obj._to_dict() == {"type": "uri_file", "default": default}

    def test_input_with_optional_asset_backed_default(self):
        input_obj = Input(type="uri_file", mode="ro_mount", default="azureml:my_asset:1", optional=True)

        assert input_obj.optional is True
        assert input_obj._to_dict() == {
            "type": "uri_file",
            "mode": "ro_mount",
            "default": "azureml:my_asset:1",
            "optional": True,
        }

    def test_input_asset_backed_default_rest_round_trip(self):
        input_obj = Input(type="uri_file", mode="ro_mount", default="azureml:my_asset:1")

        rest_obj = input_obj._to_rest_object()
        assert rest_obj["type"] == "uri_file"
        assert rest_obj["default"] == "azureml:my_asset:1"

        from_rest = Input._from_rest_object(dict(rest_obj))
        assert from_rest.type == "uri_file"
        assert from_rest.mode == "ro_mount"
        assert from_rest.default == "azureml:my_asset:1"

    def test_input_non_string_default_raises(self):
        with pytest.raises(ValidationException, match="must be a string asset or path reference"):
            Input(type="uri_file", default=123)

        with pytest.raises(ValidationException, match="must be a string asset or path reference"):
            Input(type="uri_folder", default=True)

    def test_input_unsupported_type_default_raises(self):
        with pytest.raises(UserErrorException, match="Non-primitive type Input has no default value"):
            Input(type="mlflow_model", default="azureml:my_model:1")

    def test_primitive_defaults_not_impacted(self):
        assert Input(type="integer", default=1, min=0, max=10).default == 1
        assert Input(type="number", default="10.99").default == 10.99
        assert Input(type="string", default="value").default == "value"
        assert Input(type="boolean", default=True).default is True
        assert Input(type="uri_file", mode="ro_mount").default is None

        with pytest.raises(UserErrorException):
            Input(type="integer", default=[1])

    def test_load_command_component_with_asset_backed_defaults(self):
        component: CommandComponent = load_component(source=components_dir + "input_asset_defaults_component.yml")

        assert component.inputs["spaceship_data"].type == "uri_file"
        assert component.inputs["spaceship_data"].mode == "ro_mount"
        assert (
            component.inputs["spaceship_data"].default
            == "azureml:dsp_da_test_use_case_spaceships_uri_file:50322a7173b6976c"
        )
        assert component.inputs["folder_data"].default == "azureml:folder_asset:1"
        assert component.inputs["table_data"].default == "azureml:table_asset:1"
        assert component.inputs["year"].default == 2025

        # yaml round trip
        component_dict = component._to_dict()
        assert component_dict["inputs"]["spaceship_data"] == {
            "type": "uri_file",
            "mode": "ro_mount",
            "default": "azureml:dsp_da_test_use_case_spaceships_uri_file:50322a7173b6976c",
        }
        reloaded = self._dump_and_reload(component)
        assert reloaded.inputs["spaceship_data"]._to_dict() == component.inputs["spaceship_data"]._to_dict()
        assert reloaded.inputs["year"]._to_dict() == component.inputs["year"]._to_dict()

        # rest round trip
        rest_object = component._to_rest_object()
        assert rest_object.properties.component_spec["inputs"]["spaceship_data"] == {
            "type": "uri_file",
            "mode": "ro_mount",
            "default": "azureml:dsp_da_test_use_case_spaceships_uri_file:50322a7173b6976c",
        }
        from_rest = Component._from_rest_object(rest_object)
        assert (
            from_rest.inputs["spaceship_data"].default
            == "azureml:dsp_da_test_use_case_spaceships_uri_file:50322a7173b6976c"
        )
        assert from_rest.inputs["spaceship_data"].mode == "ro_mount"

    def test_load_pipeline_component_with_asset_backed_default(self):
        component: PipelineComponent = load_component(
            source=components_dir + "input_asset_defaults_pipeline_component.yml"
        )

        spaceship_data = component.inputs["spaceship_data"]
        assert spaceship_data.type == "uri_file"
        assert spaceship_data.mode == "ro_mount"
        assert spaceship_data.default == "azureml:dsp_da_test_use_case_spaceships_uri_file:50322a7173b6976c"
        assert component._to_dict()["inputs"]["spaceship_data"]["default"] == (
            "azureml:dsp_da_test_use_case_spaceships_uri_file:50322a7173b6976c"
        )

    def test_load_component_with_invalid_default(self):
        with pytest.raises(ValidationError):
            load_component(source=components_dir + "invalid/input_asset_defaults_invalid_component.yml")

    def test_component_call_with_and_without_default(self):
        component: CommandComponent = load_component(source=components_dir + "input_asset_defaults_component.yml")
        expected_default = "azureml:dsp_da_test_use_case_spaceships_uri_file:50322a7173b6976c"

        # input with default is not required, so omitting it is valid
        node = component(year=2025)
        validation_result = node._validate_inputs()
        assert "inputs.spaceship_data" not in validation_result.error_messages
        assert node._component.inputs["spaceship_data"].default == expected_default

        # explicit value overrides the default without mutating the component default
        override = Input(type="uri_file", path="azureml:other_asset:1", mode="ro_mount")
        other_node = component(year=2025, spaceship_data=override)
        assert other_node.inputs["spaceship_data"]._data.path == "azureml:other_asset:1"
        assert component.inputs["spaceship_data"].default == expected_default
        assert node._component.inputs["spaceship_data"].default == expected_default
