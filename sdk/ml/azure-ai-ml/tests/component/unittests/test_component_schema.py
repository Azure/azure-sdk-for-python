import copy
import json
import os
from pathlib import Path
from unittest import mock

import pydash
import pytest
import yaml
from azure.ai.ml import MLClient, load_component
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData
from azure.ai.ml._utils._arm_id_utils import PROVIDER_RESOURCE_ID_WITH_VERSION
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, AssetTypes, LegacyAssetTypes
from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.entities import CommandComponent, Component, PipelineComponent
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._component.component import COMPONENT_PLACEHOLDER
from azure.ai.ml.entities._component.component_factory import component_factory

from .._util import _COMPONENT_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


def load_component_entity_from_yaml(
    path: str,
    mock_machinelearning_client: MLClient,
    context={},
    is_anonymous=False,
    fields_to_override=None,
    _type="command",
) -> CommandComponent:
    """Component yaml -> component entity -> rest component object -> component entity"""
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    context.update({BASE_PATH_CONTEXT_KEY: Path(path).parent})
    create_instance_func, create_schema_func = component_factory.get_create_funcs(data)
    data = dict(create_schema_func(context).load(data))
    if fields_to_override is None:
        fields_to_override = {}
    data.update(fields_to_override)
    if is_anonymous is True:
        data["name"] = None
        data["version"] = None

    internal_representation = create_instance_func()
    internal_representation.__init__(
        **data,
    )
    internal_representation._base_path = context[BASE_PATH_CONTEXT_KEY]

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
                elif os.path.isfile(arg.path):
                    return f"{str(arg.path)}:1"
                else:
                    return f"{Path(arg.path).name}:1"
        return "xxx"

    # change internal assets into arm id
    with mock.patch(
        "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
        side_effect=mock_get_asset_arm_id,
    ):
        mock_machinelearning_client.components._resolve_arm_id_or_upload_dependencies(internal_representation)
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


def load_component_entity_from_rest_json(path) -> Component:
    """Rest component json -> rest component object -> component entity"""
    with open(path, "r") as f:
        target = yaml.safe_load(f)
    rest_obj = ComponentVersionData.from_dict(json.loads(json.dumps(target)))
    internal_component = Component._from_rest_object(rest_obj)
    return internal_component


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestCommandComponent:
    def test_serialize_deserialize_basic(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        rest_path = "./tests/test_configs/components/helloworld_component_rest.json"
        target_entity = load_component_entity_from_rest_json(rest_path)

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
        assert component_entity.code is None
        assert component_entity.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"

    def test_serialize_deserialize_environment_no_version(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/helloworld_component_alt1.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)

        assert component_entity.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"

    def test_serialize_deserialize_input_types(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/input_types_component.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        rest_path = "./tests/test_configs/components/input_types_component_rest.json"
        target_entity = load_component_entity_from_rest_json(rest_path)

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

        rest_component_resource = component_entity._to_rest_object()
        assert rest_component_resource.properties.component_spec["inputs"] == expected_dict["inputs"]

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
        inputs_dict = {k: v._to_dict() for k, v in component_entity.inputs.items()}
        assert inputs_dict == {
            "component_in_number": {
                "type": "number",
                "default": 10.99,
                "description": "A number",
                "optional": True,
            },
            "component_in_path": {
                "type": "uri_folder",
                "description": "override component_in_path",
            },
        }

        override_inputs = {
            # according to InputPortSchema, mode in component input will not take effect
            "component_in_path": {"type": "uri_folder"},
            "component_in_number": {"max": 1.0, "min": 0.0, "type": "number"},
            "override_param3": {"optional": True, "type": "integer"},
            "override_param4": {"default": False, "type": "boolean"},
            "override_param5": {"default": "str", "type": "string"},
            "override_param6": {"enum": ["enum1", "enum2", "enum3"], "type": "string"},
        }
        context = {PARAMS_OVERRIDE_KEY: [{"inputs": copy.deepcopy(override_inputs)}]}
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client, context)
        inputs_dict = {k: v._to_dict() for k, v in component_entity.inputs.items()}
        assert inputs_dict == override_inputs

    def test_serialize_deserialize_with_code_path(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/basic_component_code_local_path.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        # make sure code has "created"
        assert component_entity.code

    def test_serialize_deserialize_default_code(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        component_entity = load_component_entity_from_yaml(test_path, mock_machinelearning_client)
        assert component_entity.code is None

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
        component_entity = load_component(source=test_path)
        component_str = str(component_entity)
        assert component_entity.name in component_str
        assert component_entity.version in component_str

    def test_anonymous_component_same_name(self, mock_machinelearning_client: MLClient):
        # scenario 1: same component interface, same code
        test_path1 = "./tests/test_configs/components/basic_component_code_local_path.yml"
        component_entity1 = load_component_entity_from_yaml(test_path1, mock_machinelearning_client, is_anonymous=True)
        component_hash1 = component_entity1._get_anonymous_hash()
        component_entity2 = load_component_entity_from_yaml(test_path1, mock_machinelearning_client, is_anonymous=True)
        component_hash2 = component_entity2._get_anonymous_hash()
        assert component_hash1 == component_hash2

        # scenario 2: same component, no code
        test_path2 = "./tests/test_configs/components/helloworld_component.yml"
        component_entity1 = load_component_entity_from_yaml(test_path2, mock_machinelearning_client, is_anonymous=True)
        component_hash1 = component_entity1._get_anonymous_hash()
        component_entity2 = load_component_entity_from_yaml(test_path2, mock_machinelearning_client, is_anonymous=True)
        component_hash2 = component_entity2._get_anonymous_hash()
        assert component_hash1 == component_hash2

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
        component_hash1 = component_entity1._get_anonymous_hash()
        component_entity2 = load_component_entity_from_yaml(
            test_path1,
            mock_machinelearning_client,
            is_anonymous=True,
            fields_to_override=data2,
        )
        component_hash2 = component_entity2._get_anonymous_hash()
        assert component_hash1 != component_hash2

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
        component_hash1 = component_entity1._get_anonymous_hash()
        component_entity2 = load_component_entity_from_yaml(
            test_path1,
            mock_machinelearning_client,
            is_anonymous=True,
            fields_to_override=data2,
        )
        component_hash2 = component_entity2._get_anonymous_hash()
        assert component_hash1 != component_hash2

    def test_command_component_with_properties(self):
        test_path = "./tests/test_configs/components/helloworld_component_with_properties.yml"
        component_entity = load_component(source=test_path)
        assert component_entity.properties == {"azureml.pipelines.dynamic": "true"}

        validation_result = component_entity._validate()
        assert validation_result.passed is True

    def test_component_factory(self):
        test_path = "./tests/test_configs/components/helloworld_component_with_properties.yml"
        component_entity = load_component(source=test_path)
        recreated_component = component_factory.load_from_dict(
            data=component_entity._to_dict(),
            context={
                "source_path": test_path,
            },
            _source=ComponentSource.YAML_COMPONENT,
        )
        assert recreated_component._to_dict() == component_entity._to_dict()

        recreated_component = component_factory.load_from_rest(obj=component_entity._to_rest_object())
        assert recreated_component._to_dict() == component_entity._to_dict()

    def test_dump_with_non_existent_base_path(self):
        test_path = "./tests/test_configs/components/helloworld_component.yml"
        component_entity = load_component(source=test_path)
        component_entity._base_path = "/non/existent/path"
        component_entity._to_dict()

    def test_arm_code_from_rest_object(self):
        arm_code = (
            "azureml:/subscriptions/xxx/resourceGroups/xxx/providers/Microsoft.MachineLearningServices/"
            "workspaces/zzz/codes/90b33c11-365d-4ee4-aaa1-224a042deb41/versions/1"
        )
        yaml_path = "./tests/test_configs/components/helloworld_component.yml"
        yaml_component = load_component(yaml_path)

        from azure.ai.ml.entities import Component

        rest_object = yaml_component._to_rest_object()
        rest_object.properties.component_spec["code"] = arm_code
        component = Component._from_rest_object(rest_object)
        assert component.code == arm_code[8:]


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestPipelineComponent:
    def test_inline_helloworld_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_inline_pipeline_component.yml"
        component: PipelineComponent = load_component(source=component_path)

        validation_result = component._validate()
        assert validation_result.passed is True

    def test_helloworld_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_pipeline_component.yml"
        component: PipelineComponent = load_component(source=component_path)

        validation_result = component._validate()
        assert validation_result.passed is True

    def test_helloworld_nested_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_nested_pipeline_component.yml"
        component: PipelineComponent = load_component(source=component_path)

        validation_result = component._validate()
        assert validation_result.passed is True


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestSparkComponent:
    def test_component_load(self):
        # code is specified in yaml, value is respected
        component_yaml = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        spark_component = load_component(
            component_yaml,
        )
        validation_result = spark_component._validate()
        assert validation_result.passed is True
