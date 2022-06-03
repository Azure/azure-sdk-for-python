from unittest import mock

import json
import pydash
import yaml
from pathlib import Path
import pytest
from marshmallow import ValidationError

from azure.ai.ml import MLClient
from azure.ai.ml._operations.component_operations import (
    COMPONENT_PLACEHOLDER,
    COMPONENT_CODE_PLACEHOLDER,
    get_anonymous_component_name,
)
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData
from azure.ai.ml._schema.component.command_component import CommandComponentSchema
from azure.ai.ml._utils._arm_id_utils import PROVIDER_RESOURCE_ID_WITH_VERSION
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    AssetTypes,
    InputOutputModes,
    LegacyAssetTypes,
)
from azure.ai.ml.entities import CommandComponent
from azure.ai.ml.entities._assets import Code
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

components_dir = Path("./tests/test_configs/components/")


def load_component_entity_from_yaml(
    path: str,
    mock_machinelearning_client: MLClient,
    context={},
    is_anonymous=False,
    fields_to_override=None,
) -> CommandComponent:
    """Component yaml -> component entity -> rest component object -> component entity"""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    context.update({BASE_PATH_CONTEXT_KEY: Path(path).parent})
    schema = CommandComponentSchema(context=context)
    data = dict(schema.load(cfg))
    if fields_to_override is None:
        fields_to_override = {}
    data.update(fields_to_override)
    if is_anonymous is True:
        data["name"] = None
        data["version"] = None
    internal_representation: CommandComponent = CommandComponent(**data)

    def mock_get_asset_arm_id(*args, **kwargs):
        if len(args) > 0:
            arg = args[0]
            if isinstance(arg, str):
                return arg
            elif isinstance(arg, Code):
                if COMPONENT_PLACEHOLDER in str(arg.path):
                    # for generated code, return content in it
                    with open(arg.path) as f:
                        return f.read()
                return f"{str(arg.path)}:1"
        return "xxx"

    # change internal assets into arm id
    with mock.patch(
        "azure.ai.ml._operations.OperationOrchestrator.get_asset_arm_id",
        side_effect=mock_get_asset_arm_id,
    ):
        mock_machinelearning_client.components._upload_dependencies(internal_representation)
    rest_component = internal_representation._to_rest_object()
    # set arm id before deserialize
    mock_workspace_scope = mock_machinelearning_client._operation_scope
    rest_component.id = PROVIDER_RESOURCE_ID_WITH_VERSION.format(
        mock_workspace_scope.subscription_id,
        mock_workspace_scope.resource_group_name,
        mock_workspace_scope.workspace_name,
        "components",
        internal_representation.name,
        "1",
    )
    internal_component = CommandComponent._from_rest_object(rest_component)
    return internal_component


def load_component_entity_from_rest_json(path) -> CommandComponent:
    """Rest component json -> rest component object -> component entity"""
    with open(path, "r") as f:
        target = yaml.safe_load(f)
    rest_obj = ComponentVersionData.from_dict(json.loads(json.dumps(target)))
    internal_component = CommandComponent._from_rest_object(rest_obj)
    return internal_component


@pytest.mark.unittest
class TestCommandComponent:
    def test_serialize_deserialize_basic(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        rest_path = "./tests/test_configs/components/helloworld_component_rest.json"
        target_entity = load_component_entity_from_rest_json(rest_path)

        # backend add optional=False and port name to inputs/outputs so we add it here manually
        for name, input in component_entity.inputs.items():
            input["optional"] = str(input.get("optional", False))
            input["name"] = name
        for name, output in component_entity.outputs.items():
            output["name"] = name
        # skip check code and environment
        component_dict = component_entity._to_dict()
        assert component_dict["id"]
        component_dict = pydash.omit(dict(component_dict), "command", "environment", "code", "id")
        expected_dict = pydash.omit(
            dict(target_entity._to_dict()),
            "command",
            "environment",
            "code",
            "creation_context",
            "id",
        )
        assert component_dict == expected_dict
        assert component_entity.code
        assert component_entity.environment == "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1"

    def test_serialize_deserialize_environment_no_version(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/helloworld_component_alt1.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)

        assert component_entity.environment == "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu"

    def test_serialize_deserialize_input_types(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/input_types_component.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        rest_path = "./tests/test_configs/components/input_types_component_rest.json"
        target_entity = load_component_entity_from_rest_json(rest_path)

        # backend add optional=False and port name to inputs/outputs so we add it here manually
        for name, input in component_entity.inputs.items():
            input["optional"] = "False"
            input["name"] = name
        for name, output in component_entity.outputs.items():
            output["name"] = name
        # skip check code and environment
        component_dict = pydash.omit(dict(component_entity._to_dict()), "command", "environment", "code", "id")
        expected_dict = pydash.omit(
            dict(target_entity._to_dict()),
            "command",
            "environment",
            "creation_context",
            "code",
            "id",
        )
        assert component_dict == expected_dict

    def test_override_params(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        context = {
            PARAMS_OVERRIDE_KEY: [
                {
                    "inputs.component_in_path": {
                        "description": "override component_in_path",
                        "type": "uri_folder",
                    }
                }
            ]
        }
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client, context)
        assert component_entity.inputs == {
            "component_in_number": {
                "type": "number",
                "default": "10.99",
                "description": "A number",
                "optional": True,
            },
            "component_in_path": {
                "type": "uri_folder",
                "description": "override component_in_path",
            },
        }

        override_inputs = {
            "component_in_path": {"type": "uri_folder"},
            "component_in_number": {"max": "1.0", "min": "0.0", "type": "number"},
            "override_param3": {"optional": True, "type": "integer"},
            "override_param4": {"default": False, "type": "boolean"},
            "override_param5": {"default": "str", "type": "string"},
            "override_param6": {"enum": ["enum1", "enum2", "enum3"], "type": "string"},
        }
        context = {PARAMS_OVERRIDE_KEY: [{"inputs": override_inputs}]}
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client, context)

        assert component_entity.inputs == override_inputs

    def test_serialize_deserialize_with_code_path(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/basic_component_code_local_path.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        # make sure code has "created"
        assert component_entity.code
        expected_path = Path("./tests/test_configs/components/helloworld_components_with_env").resolve()
        assert component_entity.code == f"{str(expected_path)}:1"

    def test_serialize_deserialize_default_code(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        # make sure default code has generated with name and version as content
        assert component_entity.code
        assert COMPONENT_CODE_PLACEHOLDER == component_entity.code

    def test_serialize_deserialize_input_output_path(self, mock_machinelearning_client: MLClient):
        expected_value_dict = {
            "path": {
                "inputs.component_in_path.type": LegacyAssetTypes.PATH,
                "inputs.component_in_file.type": AssetTypes.URI_FILE,
                "inputs.component_in_folder.type": AssetTypes.URI_FOLDER,
                "outputs.component_out_file.type": AssetTypes.URI_FILE,
                "outputs.component_out_folder.type": AssetTypes.URI_FOLDER,
            },
            "mltable": {
                "inputs.component_in_mltable_mount.type": AssetTypes.MLTABLE,
                "outputs.component_out_mltable_rw_mount.type": AssetTypes.MLTABLE,
            },
            "mlflow_model": {
                "inputs.component_in_mlflow_model_azure.type": AssetTypes.MLFLOW_MODEL,
                "outputs.component_out_mlflow_model.type": AssetTypes.MLFLOW_MODEL,
            },
            "custom_model": {
                "inputs.component_in_custom_model.type": AssetTypes.CUSTOM_MODEL,
                "outputs.component_out_custom_model.type": AssetTypes.CUSTOM_MODEL,
                "inputs.component_in_trition_model.type": AssetTypes.TRITON_MODEL,
                "outputs.component_out_trition_model.type": AssetTypes.TRITON_MODEL,
            },
        }
        for contract_type, expected_values in expected_value_dict.items():
            test_path = "./tests/test_configs/components/type_contract/{}.yml".format(contract_type)
            component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
            component_entity_dict = component_entity._to_dict()
            for dot_key, expected_value in expected_values.items():
                assert pydash.get(component_entity_dict, dot_key) == expected_value

    def test_command_component_str(self):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        component_entity = CommandComponent.load(path=test_path)
        component_str = str(component_entity)
        assert component_entity.name in component_str
        assert component_entity.version in component_str

    def test_anonymous_component_same_name(self, mock_machinelearning_client: MLClient):
        # scenario 1: same component interface, same code
        test_path1 = "./tests/test_configs/components/basic_component_code_local_path.yml"
        component_entity1 = load_component_entity_from_yaml(test_path1, mock_machinelearning_client, is_anonymous=True)
        component_name1 = get_anonymous_component_name(component_entity1)
        component_entity2 = load_component_entity_from_yaml(test_path1, mock_machinelearning_client, is_anonymous=True)
        component_name2 = get_anonymous_component_name(component_entity2)
        assert component_name1 == component_name2

        # scenario 2: same component, no code
        test_path2 = "./tests/test_configs/components/helloworld_component.yml"
        component_entity1 = load_component_entity_from_yaml(test_path2, mock_machinelearning_client, is_anonymous=True)
        component_name1 = get_anonymous_component_name(component_entity1)
        component_entity2 = load_component_entity_from_yaml(test_path2, mock_machinelearning_client, is_anonymous=True)
        component_name2 = get_anonymous_component_name(component_entity2)
        assert component_name1 == component_name2

        # scenario 3: same component interface, different code
        code_path1 = "./tests/test_configs/components/basic_component_code_local_path.yml"
        data1 = {"code": code_path1}
        code_path2 = "./tests/test_configs/components/helloworld_component.yml"
        data2 = {"code": code_path2}
        # only code is different in data1 and data2
        component_entity1 = load_component_entity_from_yaml(
            test_path1,
            mock_machinelearning_client,
            is_anonymous=True,
            fields_to_override=data1,
        )
        component_name1 = get_anonymous_component_name(component_entity1)
        component_entity2 = load_component_entity_from_yaml(
            test_path1,
            mock_machinelearning_client,
            is_anonymous=True,
            fields_to_override=data2,
        )
        component_name2 = get_anonymous_component_name(component_entity2)
        assert component_name1 != component_name2

        # scenario 4: different component interface, same code
        data1 = {"display_name": "CommandComponentBasic1"}
        data2 = {"display_name": "CommandComponentBasic2"}
        # only display name is different in data1 and data2
        component_entity1 = load_component_entity_from_yaml(
            test_path1,
            mock_machinelearning_client,
            is_anonymous=True,
            fields_to_override=data1,
        )
        component_name1 = get_anonymous_component_name(component_entity1)
        component_entity2 = load_component_entity_from_yaml(
            test_path1,
            mock_machinelearning_client,
            is_anonymous=True,
            fields_to_override=data2,
        )
        component_name2 = get_anonymous_component_name(component_entity2)
        assert component_name1 != component_name2

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
                CommandComponent.load(path=test_path, params_override=params_override)
            err_msg = "Component name should only contain lower letter, number, underscore"
            assert err_msg in str(e.value)

        valid_component_names = ["n", "name", "n_a_m_e", "name_1"]
        for valid_name in valid_component_names:
            params_override = [{"name": valid_name}]
            CommandComponent.load(path=test_path, params_override=params_override)

    def test_component_input_name_validate(self):
        yaml_files = [
            str(components_dir / "invalid/helloworld_component_with_blank_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_dash_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_special_character_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_dash_input_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_number_input_names.yml"),
        ]
        for yaml_file in yaml_files:
            with pytest.raises(ValidationException, match="is not a valid parameter name"):
                CommandComponent.load(path=yaml_file)

    def test_component_output_name_validate(self):
        yaml_files = [
            str(components_dir / "invalid/helloworld_component_with_blank_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_dash_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_special_character_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_dash_output_names.yml"),
            str(components_dir / "invalid/helloworld_component_with_start_number_output_names.yml"),
        ]
        for yaml_file in yaml_files:
            with pytest.raises(ValidationException, match="is not a valid parameter name"):
                CommandComponent.load(path=yaml_file)
