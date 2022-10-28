# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import os
from pathlib import Path
from typing import Dict
from zipfile import ZipFile

import pydash
import pytest
import yaml

from azure.ai.ml import load_component
from azure.ai.ml._internal._schema.component import NodeType
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import AZUREML_INTERNAL_COMPONENTS_ENV_VAR
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders.control_flow_node import LoopNode
from azure.ai.ml.exceptions import ValidationException

from .._utils import PARAMETERS_TO_TEST


@pytest.mark.usefixtures("enable_internal_components")
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestComponent:
    def test_load_v2_component(self):
        yaml_path = "./tests/test_configs/components/helloworld_component.yml"
        load_component(yaml_path)

    def test_validate_internal_component(self):
        yaml_path = r"./tests/test_configs/internal/component_with_code/component_spec.yaml"
        from azure.ai.ml.entities._validate_funcs import validate_component
        validation_result = validate_component(yaml_path)
        assert validation_result.passed, repr(validation_result)

    def test_specific_error_message_on_load_from_dict(self):
        os.environ[AZUREML_INTERNAL_COMPONENTS_ENV_VAR] = "false"
        yaml_path = "./tests/test_configs/internal/helloworld/helloworld_component_command.yml"
        with pytest.raises(
            ValidationException,
            match="Internal components is a private feature in v2, " "please set environment variable",
        ):
            load_component(yaml_path, params_override=[{"type": "UnsupportedComponent"}])
        os.environ[AZUREML_INTERNAL_COMPONENTS_ENV_VAR] = "true"

    def test_load_from_registered_internal_command_component_rest_obj(self):
        base_component_internal = InternalComponent(
            _schema="https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            name="ls_command",
            version="0.0.1",
            display_name="0.0.1",
            type=NodeType.COMMAND,
            tags={"category": "Component Tutorial", "contact": "amldesigner@microsoft.com"},
            is_deterministic=True,
            successful_return_code="Zero",
            inputs={"train_data": {"type": "path", "optional": False}},
            outputs={"output_dir": {"type": "path", "datastore_mode": "Upload"}},
            environment={"name": "AzureML-Minimal", "version": "45", "os": "Linux"},
            command="sh ls.sh {inputs.input_dir} {inputs.file_name} {outputs.output_dir}",
        )
        rest_obj = base_component_internal._to_rest_object()
        assert rest_obj.properties.component_spec == {
            "name": "ls_command",
            "tags": {"category": "Component Tutorial", "contact": "amldesigner@microsoft.com"},
            "type": "CommandComponent",
            "$schema": "https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            "version": "0.0.1",
            "display_name": "0.0.1",
            "is_deterministic": True,
            "successful_return_code": "Zero",
            "inputs": {"train_data": {"type": "path"}},
            "outputs": {"output_dir": {"type": "path", "datastore_mode": "Upload"}},
            "command": "sh ls.sh {inputs.input_dir} {inputs.file_name} {outputs.output_dir}",
            "environment": {"name": "AzureML-Minimal", "version": "45", "os": "Linux"},
        }
        component = Component._from_rest_object(rest_obj)
        assert component._to_dict() == {
            "name": "ls_command",
            "tags": {"category": "Component Tutorial", "contact": "amldesigner@microsoft.com"},
            "type": "CommandComponent",
            "$schema": "https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            "version": "0.0.1",
            "display_name": "0.0.1",
            "is_deterministic": True,
            "successful_return_code": "Zero",
            "inputs": {"train_data": {"type": "path"}},  # optional will be drop if False
            "outputs": {"output_dir": {"type": "path", "datastore_mode": "Upload"}},
            "command": "sh ls.sh {inputs.input_dir} {inputs.file_name} {outputs.output_dir}",
            "environment": {"name": "AzureML-Minimal", "version": "45", "os": "Linux"},
        }

    def test_load_from_registered_internal_scope_component_rest_obj(self):
        base_component_internal = InternalComponent(
            _schema="https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            name="levance.convert2ss_31201029556679",
            version="85b54741.0bf9.4734.a5bb.0e469c7bf792",
            display_name="Convert Text to StructureStream",
            type=NodeType.SCOPE,
            tags={"org": "bing", "project": "relevance"},
            is_deterministic=True,
            inputs={
                "TextData": {
                    "type": "AnyFile",
                    "optional": False,
                    "description": "relative path on ADLS storage",
                },
                "ExtractionClause": {
                    "type": "string",
                    "optional": False,
                    "description": 'the extraction clause,something like "column1:string, column2:int"',
                },
            },
            outputs={"SSPath": {"type": "CosmosStructuredStream", "description": "output path  of ss"}},
            scope={
                "args": "RawData {inputs.TextData} SS_Data {outputs.SSPath} ExtractClause {inputs.ExtractionClause}",
                "script": "convert2ss.script",
            },
        )
        rest_obj = base_component_internal._to_rest_object()
        assert rest_obj.properties.component_spec == {
            "name": "levance.convert2ss_31201029556679",
            "tags": {"org": "bing", "project": "relevance"},
            "type": "ScopeComponent",
            "$schema": "https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            "version": "85b54741.0bf9.4734.a5bb.0e469c7bf792",
            "display_name": "Convert Text to StructureStream",
            "is_deterministic": True,
            "inputs": {
                "TextData": {
                    "type": "AnyFile",
                    "description": "relative path on ADLS storage",
                },
                "ExtractionClause": {
                    "type": "string",
                    "description": 'the extraction clause,something like "column1:string, column2:int"',
                },
            },
            "outputs": {"SSPath": {"type": "CosmosStructuredStream", "description": "output path  of ss"}},
            "scope": {
                "args": "RawData {inputs.TextData} SS_Data {outputs.SSPath} ExtractClause {inputs.ExtractionClause}",
                "script": "convert2ss.script",
            },
        }
        component = Component._from_rest_object(rest_obj)
        assert component._to_dict() == {
            "name": "levance.convert2ss_31201029556679",
            "tags": {"org": "bing", "project": "relevance"},
            "type": "ScopeComponent",
            "$schema": "https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            "version": "85b54741.0bf9.4734.a5bb.0e469c7bf792",
            "display_name": "Convert Text to StructureStream",
            "is_deterministic": True,
            "inputs": {
                "TextData": {
                    "type": "AnyFile",
                    # "optional": False,  # expected. optional will be dropped if it's False
                    "description": "relative path on ADLS storage",
                },
                "ExtractionClause": {
                    "type": "string",
                    # "optional": False,  # expected. optional will be dropped if it's False
                    "description": 'the extraction clause,something like "column1:string, column2:int"',
                },
            },
            "outputs": {"SSPath": {"type": "CosmosStructuredStream", "description": "output path  of ss"}},
            "scope": {
                "args": "RawData {inputs.TextData} SS_Data {outputs.SSPath} ExtractClause {inputs.ExtractionClause}",
                "script": "convert2ss.script",
            },
        }

    @pytest.mark.parametrize(
        "yaml_path",
        list(map(lambda x: x[0], PARAMETERS_TO_TEST)),
    )
    def test_component_serialization(self, yaml_path):
        with open(yaml_path, encoding="utf-8") as yaml_file:
            yaml_dict = yaml.safe_load(yaml_file)

        entity = load_component(yaml_path)

        expected_dict = copy.deepcopy(yaml_dict)
        for key, value in {
            "type": expected_dict["type"].rsplit("@", 1)[0]
            if expected_dict["type"].endswith("@1-legacy")
            else expected_dict["type"],
            "tags": expected_dict.get("tags", {}),
            "inputs": expected_dict.get("inputs", {}),
            "outputs": expected_dict.get("outputs", {}),
        }.items():
            pydash.set_(expected_dict, key, value)
        if "environment" in expected_dict:
            expected_dict["environment"]["os"] = "Linux"
        for input_port_name in expected_dict["inputs"]:
            input_port = expected_dict["inputs"][input_port_name]
            # enum will be transformed to string
            if isinstance(input_port["type"], str) and input_port["type"].lower() in ["string", "enum"]:
                if "enum" in input_port:
                    input_port["enum"] = list(map(lambda x: str(x), input_port["enum"]))
                if "default" in input_port:
                    input_port["default"] = str(input_port["default"])
            # optional will be dropped if it's False
            if "optional" in input_port and input_port["optional"] is False:
                del input_port["optional"]

        assert entity._to_dict() == expected_dict
        rest_obj = entity._to_rest_object()
        assert rest_obj.properties.component_spec == expected_dict

        # inherit input type map from Component._from_rest_object
        for input_port in expected_dict["inputs"].values():
            if input_port["type"] == "String":
                input_port["type"] = input_port["type"].lower()
        assert InternalComponent._from_rest_object(rest_obj)._to_dict() == expected_dict
        result = entity._validate()
        assert result._to_dict() == {"result": "Succeeded"}

    def test_ipp_component_serialization(self):
        yaml_path = "./tests/test_configs/internal/ipp-component/spec.yaml"
        load_component(yaml_path)

    @pytest.mark.parametrize(
        "yaml_path,expected_dict",
        [
            (
                "./tests/test_configs/internal/env-conda-dependencies/component_spec.yaml",
                {
                    "conda": {
                        "conda_dependencies": {
                            "name": "project_environment",
                            "channels": ["defaults"],
                            "dependencies": [
                                "python=3.7.9",
                                "pip=20.0",
                                {"pip": ["azureml-defaults", "azureml-dataprep>=1.6"]},
                            ],
                        }
                    },
                    "os": "Linux",
                },
            ),
            (
                "./tests/test_configs/internal/env-pip-dependencies/component_spec.yaml",
                {
                    "conda": {
                        "conda_dependencies": {
                            "name": "project_environment",
                            "dependencies": [
                                "python=3.8.5",
                                {
                                    "pip": ["azureml-defaults", "rsa==4.7"],
                                },
                            ],
                        },
                    },
                    "os": "Linux",
                },
            ),
            (
                "./tests/test_configs/internal/env-dockerfile-build/component_spec.yaml",
                {
                    "docker": {
                        "build": {
                            "dockerfile": "FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:20220815.v1\n",
                        },
                    },
                    "python": {
                        "user_managed_dependencies": True,
                    },
                    "os": "Linux",
                },
            ),
        ],
    )
    def test_environment_dependencies_resolve(self, yaml_path: str, expected_dict: Dict) -> None:
        component: InternalComponent = load_component(source=yaml_path)
        component.environment.resolve(component._base_path)
        rest_obj = component._to_rest_object()
        assert rest_obj.properties.component_spec["environment"] == expected_dict

    @pytest.mark.parametrize(
        "yaml_path,invalid_field",
        [
            ("./tests/test_configs/internal/env-invalid/conda_file_not_exist.yaml", "conda_dependencies_file"),
            ("./tests/test_configs/internal/env-invalid/pip_file_not_exist.yaml", "pip_requirements_file"),
        ],
    )
    def test_invalid_environment(self, yaml_path: str, invalid_field: str) -> None:
        component = load_component(source=yaml_path)
        validation_result = component._validate()
        assert not validation_result.passed
        assert f"environment.conda.{invalid_field}" in validation_result.error_messages

    def test_environment_duplicate_dependencies_warning(self) -> None:
        yaml_path = "./tests/test_configs/internal/env-duplicate-dependencies/component_spec.yaml"
        component = load_component(source=yaml_path)
        validation_result = component._validate()
        # pass validate with warning message
        assert validation_result.passed
        expected_warning_message = (
            "environment.conda: Duplicated declaration of dependencies, "
            "will honor in the order conda_dependencies, conda_dependencies_file and pip_requirements_file."
        )
        assert str(validation_result._warnings[0]) == expected_warning_message

    def test_resolve_local_code(self) -> None:
        # internal component code (snapshot) default includes items in base directory when code is None,
        # rather than COMPONENT_PLACEHOLDER in v2, this test targets to this case.
        from azure.ai.ml.entities._component.component import COMPONENT_PLACEHOLDER
        from azure.ai.ml.operations._component_operations import _try_resolve_code_for_component

        # create a mock function for param `get_arm_id_and_fill_back`
        def mock_get_arm_id_and_fill_back(asset, *args, **kwargs):
            return asset

        yaml_path = (
            "./tests/test_configs/internal/component_with_additional_includes/helloworld_additional_includes.yml"
        )
        component: InternalComponent = load_component(source=yaml_path)
        _try_resolve_code_for_component(
            component=component,
            get_arm_id_and_fill_back=mock_get_arm_id_and_fill_back,
        )
        assert component.code.path.name != COMPONENT_PLACEHOLDER

    def test_additional_includes(self) -> None:
        yaml_path = (
            "./tests/test_configs/internal/component_with_additional_includes/helloworld_additional_includes.yml"
        )
        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        # resolve
        with component._resolve_local_code() as code:
            code_path = code.path
            assert code_path.is_dir()
            assert (code_path / "LICENSE").exists()
            assert (code_path / "library.zip").exists()
            assert ZipFile(code_path / "library.zip").namelist() == ["hello.py", "world.py"]
            assert (code_path / "library1" / "hello.py").exists()
            assert (code_path / "library1" / "world.py").exists()

        assert not code_path.is_dir()

    @pytest.mark.parametrize(
        "yaml_path,has_additional_includes",
        [
            ("helloworld_without_code_and_additional_includes.yml", False),
            ("helloworld_with_code.yml", False),
            ("helloworld_with_code_and_additional_includes.yml", True),
        ],
    )
    def test_additional_includes_with_code_specified(self, yaml_path: str, has_additional_includes: bool) -> None:
        yaml_path = os.path.join("./tests/test_configs/internal/component_with_additional_includes/", yaml_path)
        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        # resolve
        with component._resolve_local_code() as code:
            code_path = code.path
            assert code_path.is_dir()
            if has_additional_includes:
                # additional includes is specified, code will be tmp folder and need to check each item
                for path in os.listdir("./tests/test_configs/internal/"):
                    assert (code_path / path).exists(), component.code
                assert (code_path / "LICENSE").exists(), component.code
            else:
                # additional includes not specified, code should be specified path (default yaml folder)
                yaml_dict = load_yaml(yaml_path)
                specified_code_path = Path(yaml_path).parent / yaml_dict.get("code", "./")
                assert code_path.resolve() == specified_code_path.resolve()

    def test_docker_file_in_additional_includes(self):
        yaml_path = "./tests/test_configs/internal/component_with_dependency_" \
                    "in_additional_includes/with_docker_file.yml"

        docker_file_path = "./tests/test_configs/internal/additional_includes/docker/DockerFile"
        with open(docker_file_path, "r") as docker_file:
            docker_file_content = docker_file.read()

        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        with component._resolve_local_code():
            environment_rest_obj = component._to_rest_object().properties.component_spec["environment"]
            assert environment_rest_obj == {
                "docker": {
                    "build": {
                        "dockerfile": docker_file_content,
                    }
                },
                "os": "Linux",
            }

    def test_conda_pip_in_additional_includes(self):
        yaml_path = "./tests/test_configs/internal/component_with_dependency_" \
                    "in_additional_includes/with_conda_pip.yml"

        conda_file_path = "./tests/test_configs/internal/env-conda-dependencies/conda.yaml"
        with open(conda_file_path, "r") as conda_file:
            conda_file_content = yaml.safe_load(conda_file)

        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        with component._resolve_local_code():
            environment_rest_obj = component._to_rest_object().properties.component_spec["environment"]
            assert environment_rest_obj == {
                "conda": {
                    "conda_dependencies": conda_file_content,
                },
                "os": "Linux",
            }

    @pytest.mark.parametrize(
        "yaml_path,expected_error_msg_prefix",
        [
            (
                "helloworld_invalid_additional_includes_root_directory.yml",
                "Root directory is not supported for additional includes",
            ),
            (
                "helloworld_invalid_additional_includes_existing_file.yml",
                "A file already exists for additional include",
            ),
            (
                "helloworld_invalid_additional_includes_zip_file_not_found.yml",
                "Unable to find additional include ../additional_includes/assets/LICENSE.zip",
            ),
        ],
    )
    def test_invalid_additional_includes(self, yaml_path: str, expected_error_msg_prefix: str) -> None:
        component = load_component(
            os.path.join("./tests/test_configs/internal/component_with_additional_includes", yaml_path)
        )
        validation_result = component._validate()
        assert validation_result.passed is False
        assert validation_result.error_messages["*"].startswith(expected_error_msg_prefix)

    def test_component_input_types(self) -> None:
        yaml_path = "./tests/test_configs/internal/component_with_input_outputs/component_spec.yaml"
        component: InternalComponent = load_component(yaml_path)
        component.code = "scope:1"

        with open(yaml_path, "r") as f:
            yaml_dict = yaml.safe_load(f)
            for key, value in {
                "inputs.param_enum_cap.type": "enum",
            }.items():
                pydash.set_(yaml_dict, key, value)
        assert component._to_rest_object().properties.component_spec["inputs"] == yaml_dict["inputs"]
        assert component._to_rest_object().properties.component_spec["outputs"] == yaml_dict["outputs"]
        assert component._validate().passed is True, repr(component._validate())

        for key, value in {
            "inputs.param_bool_cap.type": "boolean",
            "inputs.param_int_cap.type": "integer",
            "inputs.param_string_cap.type": "string",
        }.items():
            pydash.set_(yaml_dict, key, value)
        regen_component = Component._from_rest_object(component._to_rest_object())
        assert regen_component._to_rest_object().properties.component_spec["inputs"] == yaml_dict["inputs"]
        assert regen_component._to_rest_object().properties.component_spec["outputs"] == yaml_dict["outputs"]
        assert component._validate().passed is True, repr(component._validate())

    def test_component_input_with_attrs(self) -> None:
        yaml_path = "./tests/test_configs/internal/component_with_input_outputs/component_spec_with_attrs.yaml"
        component: InternalComponent = load_component(source=yaml_path)

        expected_inputs = {
            "inputs": {
                "param_data_path": {
                    "description": "Path to the data",
                    "is_resource": True,
                    "datastore_mode": "mount",
                    "type": "path",
                },
                "param_bool": {"type": "boolean"},
                "param_enum_cap": {"enum": ["minimal", "reuse", "expiry", "policies"], "type": "enum"},
                "param_enum_with_int_values": {"default": "3", "enum": ["1", "2.0", "3", "4"], "type": "enum"},
                "param_float": {"type": "float"},
                "param_int": {"type": "integer"},
                "param_string_with_default_value": {"default": ",", "type": "string"},
                "param_string_with_default_value_2": {"default": "utf8", "type": "string"},
                # yes will be converted to true in YAML 1.2, users may use "yes" as a workaround
                "param_string_with_yes_value": {"default": "True", "type": "string"},
                "param_string_with_quote_yes_value": {"default": "yes", "type": "string"},
            }
        }
        assert component._to_rest_object().properties.component_spec["inputs"] == expected_inputs["inputs"]
        assert component._validate().passed is True, repr(component._validate())

        regenerated_component = Component._from_rest_object(component._to_rest_object())
        assert regenerated_component._to_rest_object().properties.component_spec["inputs"] == expected_inputs["inputs"]
        assert component._validate().passed is True, repr(component._validate())

    def test_component_output_with_attrs(self) -> None:
        yaml_path = "./tests/test_configs/internal/component_with_input_outputs/component_spec_with_outputs.yaml"
        component: InternalComponent = load_component(source=yaml_path)
        assert component

        expected_outputs = {
            "path_with_optional": {
                # unknown field optional will be ignored
                "type": 'AnyDirectory',
            },
            "primitive_is_control": {
                "is_control": True,
                "type": "boolean",
            }
        }
        assert component._to_rest_object().properties.component_spec["outputs"] == expected_outputs
        assert component._validate().passed is True, repr(component._validate())

        regenerated_component = Component._from_rest_object(component._to_rest_object())
        assert regenerated_component._to_rest_object().properties.component_spec["outputs"] == expected_outputs
        assert component._validate().passed is True, repr(component._validate())

    def test_component_input_list_type(self) -> None:
        yaml_path = "./tests/test_configs/internal/scope-component/component_spec.yaml"
        component: InternalComponent = load_component(yaml_path)
        assert component._validate().passed is True
        input_text_data_type = component._to_rest_object().properties.component_spec["inputs"]["TextData"]["type"]
        # for list type component input, REST object should remain type list for service contract
        assert isinstance(input_text_data_type, list)
        assert input_text_data_type == ["AnyFile", "AnyDirectory"]

    def test_loop_node_is_internal_components(self):
        from azure.ai.ml.constants._common import AZUREML_INTERNAL_COMPONENTS_ENV_VAR
        from azure.ai.ml.dsl._utils import environment_variable_overwrite

        yaml_path = "./tests/test_configs/internal/helloworld/helloworld_component_command.yml"
        component_func = load_component(source=yaml_path)
        loop_node = LoopNode(body=component_func())
        loop_node.body._referenced_control_flow_node_instance_id = loop_node._instance_id
        with environment_variable_overwrite(AZUREML_INTERNAL_COMPONENTS_ENV_VAR, "True"):
            validate_result = loop_node._validate_body(raise_error=False)
            assert validate_result.passed

    def test_anonymous_component_reuse(self):
        yaml_path = Path("./tests/test_configs/internal/command-component-reuse/powershell_copy.yaml")
        expected_snapshot_id = "75c43313-4777-b2e9-fe3a-3b98cabfaa77"

        component: InternalComponent = load_component(source=yaml_path)
        with component._resolve_local_code() as code:
            assert code.name == expected_snapshot_id

            code.name = expected_snapshot_id
            with pytest.raises(
                AttributeError,
                match="InternalCode name are calculated based on its content and cannot be changed.*"
            ):
                code.name = expected_snapshot_id + "1"
