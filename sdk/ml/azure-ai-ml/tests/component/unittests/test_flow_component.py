import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from azure.ai.ml import Input, load_component
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities._component.flow import FlowComponent

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestFlowComponent:
    def test_component_load_from_dag(self):
        target_path = "./tests/test_configs/flows/basic/flow.dag.yaml"

        component = load_component(target_path)
        component._fill_back_code_value("/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/codes/xxx/versions/1")

        component.version = "2"
        component.description = "test load component from flow"

        expected_rest_dict = {
            "name": "basic",
            "properties": {
                "component_spec": {
                    "_source": "YAML.COMPONENT",
                    "description": "test load component from flow",
                    # name of the component will be the flow directory name by default
                    "name": "basic",
                    "type": "promptflow_parallel",
                    "version": "2",
                    "is_deterministic": True,
                    "code": "/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/codes/xxx/versions/1",
                    "flow_file_name": "flow.dag.yaml",
                    "environment_variables": {
                        "AZURE_OPENAI_API_BASE": "${my_connection.api_base}",
                        "AZURE_OPENAI_API_KEY": "${my_connection.api_key}",
                        "AZURE_OPENAI_API_TYPE": "azure",
                        "AZURE_OPENAI_API_VERSION": "2023-03-15-preview",
                    },
                },
                "description": "test load component from flow",
                "is_anonymous": False,
                "is_archived": False,
                "properties": {
                    "client_component_hash": "19278001-3d52-0e43-dc43-4082128d8243",
                },
                "tags": {},
            },
        }

        assert component._to_rest_object().as_dict() == expected_rest_dict

        named_component = load_component(
            target_path,
            params_override=[
                {
                    "version": "2",
                    "description": "test load component from flow",
                }
            ],
        )
        named_component._fill_back_code_value(
            "/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/codes/xxx/versions/1"
        )

        assert named_component._to_rest_object().as_dict() == expected_rest_dict

    def test_component_normalize_folder_name(self):
        target_path = "./tests/test_configs/flows/basic/"
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copytree(
                target_path,
                f"{temp_dir}/basic-with-slash",
            )
            target_flow_dag_path = f"{temp_dir}/basic-with-slash/flow.dag.yaml"
            component = load_component(target_flow_dag_path)
            assert component.name == "basic_with_slash"

    def test_component_load_from_run(self):
        target_path = "./tests/test_configs/flows/runs/basic_run.yml"

        component = load_component(target_path)

        expected_rest_dict = {
            "name": "basic",
            "properties": {
                "component_spec": {
                    "_source": "YAML.COMPONENT",
                    "connections": {
                        "llm": {"connection": "azure_open_ai_connection", "deployment_name": "text-davinci-003"}
                    },
                    "description": "A run of the basic flow",
                    "display_name": "Basic Run",
                    "environment_variables": {
                        "AZURE_OPENAI_API_BASE": "${azure_open_ai_connection.api_base}",
                        "AZURE_OPENAI_API_KEY": "${azure_open_ai_connection.api_key}",
                        "AZURE_OPENAI_API_TYPE": "azure",
                        "AZURE_OPENAI_API_VERSION": "2023-03-15-preview",
                    },
                    "is_deterministic": True,
                    # TODO: should we use default run name (the dir name of the run yaml) as component name?
                    "name": "basic",
                    "type": "promptflow_parallel",
                    "version": "1",
                    "code": "/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/codes/xxx/versions/1",
                    "flow_file_name": "flow.dag.yaml",
                },
                "description": "A run of the basic flow",
                "is_anonymous": False,
                "is_archived": False,
                "properties": {"client_component_hash": "bc6d5b98-1aef-0d5a-96ff-5803f1a906c8"},
                "tags": {},
            },
        }

        component._fill_back_code_value("/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/codes/xxx/versions/1")

        assert component._to_rest_object().as_dict() == expected_rest_dict

    def test_component_load_fail(self):
        flow_dir_path = "./tests/test_configs/flows/basic"

        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copytree(
                flow_dir_path,
                f"{temp_dir}/basic",
                ignore=shutil.ignore_patterns(".promptflow"),
            )

            component = load_component(f"{temp_dir}/basic/flow.dag.yaml")
            with pytest.raises(Exception, match="Flow component must be created with a ./promptflow/flow.tools.json"):
                with component._build_code():
                    pass

    def test_flow_component_load_with_additional_includes(self):
        flow_dir_path = "./tests/test_configs/flows/web_classification_with_additional_includes"
        component = load_component(f"{flow_dir_path}/flow.dag.yaml")
        with component._build_code() as code:
            assert Path(code.path, "convert_to_dict.py").is_file()
            flow_dag = yaml.safe_load(Path(code.path, "flow.dag.yaml").read_text(encoding="utf-8"))
            # we won't update the flow.dag.yaml for now. user may use `mldesigner compile` if they want to update it
            assert "additional_includes" in flow_dag

    def test_flow_component_load_from_run_with_additional_includes(self):
        flow_base_dir = "./tests/test_configs/flows"
        component = load_component(f"{flow_base_dir}/runs/additional_includes_run.yml")
        with component._build_code() as code:
            assert Path(code.path, "convert_to_dict.py").is_file()

    def test_flow_component_entity(self):
        component: FlowComponent = load_component("./tests/test_configs/flows/basic/flow.dag.yaml")

        assert component.type == NodeType.FLOW_PARALLEL

        input_port_dict = component.inputs
        with pytest.raises(RuntimeError, match="Ports of flow component are not editable."):
            input_port_dict["text"] = None

        with pytest.raises(RuntimeError, match="Ports of flow component are not editable."):
            del input_port_dict["text"]

        with pytest.raises(AttributeError):
            component.flow = None

        component.column_mapping = None
        component.variant = None
        component.connections = None
        component.additional_includes = None
        assert component.additional_includes == []
        component.environment_variables = {
            "AZURE_OPENAI_API_BASE": "${azure_open_ai_connection.api_base}",
        }
        assert component.environment_variables == {
            "AZURE_OPENAI_API_BASE": "${azure_open_ai_connection.api_base}",
        }

        component._fill_back_code_value("/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/codes/xxx/versions/1")

        assert component._to_rest_object().as_dict() == {
            "name": "basic",
            "properties": {
                "component_spec": {
                    "_source": "YAML.COMPONENT",
                    "code": "/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/codes/xxx/versions/1",
                    "environment_variables": {"AZURE_OPENAI_API_BASE": "${azure_open_ai_connection.api_base}"},
                    "flow_file_name": "flow.dag.yaml",
                    "is_deterministic": True,
                    "name": "basic",
                    "type": "promptflow_parallel",
                    "version": "1",
                },
                "is_anonymous": False,
                "is_archived": False,
                # note that this won't take effect actually
                "properties": {"client_component_hash": "0eec0297-5f6d-e333-780d-c76871ad9c57"},
                "tags": {},
            },
        }

        flow_node = component(
            data=Input(path="./tests/test_configs/flows/data/basic.jsonl", type=AssetTypes.URI_FILE),
            text="${data.text}",
        )

        assert flow_node.type == "parallel"
        flow_node._component = "/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/components/xxx/versions/1"
        assert flow_node._to_rest_object() == {
            "_source": "YAML.COMPONENT",
            "componentId": "/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/components/xxx/versions/1",
            "inputs": {
                "data": {"job_input_type": "uri_file", "uri": "./tests/test_configs/flows/data/basic.jsonl"},
                "text": {"job_input_type": "literal", "value": "${data.text}"},
            },
            "type": "parallel",
        }

    @pytest.mark.parametrize(
        "input_values, expected_rest_objects",
        [
            pytest.param(
                {"connections": {"llm": {"connection": "azure_open_ai_connection"}}},
                {
                    "connections.llm.connection": {"job_input_type": "literal", "value": "azure_open_ai_connection"},
                },
                id="dict-1",
            ),
            pytest.param(
                {
                    "connections": {
                        "llm": {
                            "connection": "azure_open_ai_connection",
                            "deployment_name": "text-davinci-003",
                            "custom_connection": "azure_open_ai_connection",
                        }
                    }
                },
                {
                    "connections.llm.connection": {"job_input_type": "literal", "value": "azure_open_ai_connection"},
                    "connections.llm.deployment_name": {"job_input_type": "literal", "value": "text-davinci-003"},
                    "connections.llm.custom_connection": {
                        "job_input_type": "literal",
                        "value": "azure_open_ai_connection",
                    },
                },
                id="dict-2",
            ),
            pytest.param(
                {"connections.llm.connection": "azure_open_ai_connection"},
                {
                    "connections.llm.connection": {"job_input_type": "literal", "value": "azure_open_ai_connection"},
                },
                id="dot-key-1",
            ),
            pytest.param(
                {
                    "connections.llm.connection": "azure_open_ai_connection",
                    "connections.llm.custom_connection": "azure_open_ai_connection",
                    "connections": {"llm": {"deployment_name": "text-davinci-003"}},
                },
                {
                    "connections.llm.connection": {"job_input_type": "literal", "value": "azure_open_ai_connection"},
                    "connections.llm.custom_connection": {
                        "job_input_type": "literal",
                        "value": "azure_open_ai_connection",
                    },
                    "connections.llm.deployment_name": {"job_input_type": "literal", "value": "text-davinci-003"},
                },
                id="dot-key-plus-dict",
            ),
        ],
    )
    def test_component_connection_inputs(self, input_values: dict, expected_rest_objects: dict):
        component = load_component("./tests/test_configs/flows/basic/flow.dag.yaml")
        data_input = Input(path="./tests/test_configs/flows/data/basic.jsonl", type=AssetTypes.URI_FILE)

        # validation_result = component()._validate()
        # assert validation_result.passed is False
        node = component(data=data_input, **input_values)
        node._component = "/subscriptions/xxx/resourceGroups/xxx/workspaces/xxx/components/xxx/versions/1"
        assert node._to_rest_object()["inputs"] == {
            "data": {"job_input_type": "uri_file", "uri": "./tests/test_configs/flows/data/basic.jsonl"},
            **expected_rest_objects,
        }
