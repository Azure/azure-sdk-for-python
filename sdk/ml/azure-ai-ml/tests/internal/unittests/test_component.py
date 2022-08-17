# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import os
from pathlib import Path
from typing import Dict

import pytest
import yaml

from azure.ai.ml import load_component
from azure.ai.ml._internal._schema.component import NodeType
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml._ml_exceptions import ValidationException
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import AZUREML_INTERNAL_COMPONENTS_ENV_VAR
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._assets import Code


@pytest.mark.usefixtures("enable_internal_components")
@pytest.mark.unittest
class TestComponent:
    def test_load_v2_component(self):
        yaml_path = "./tests/test_configs/components/helloworld_component.yml"
        load_component(yaml_path)

    def test_specific_error_message_on_load_from_dict(self):
        os.environ[AZUREML_INTERNAL_COMPONENTS_ENV_VAR] = "false"
        yaml_path = "./tests/test_configs/internal/helloworld_component_command.yml"
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
            environment={"name": "AzureML-Minimal", "version": "45", "os": "linux"},
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
            "inputs": {"train_data": {"type": "path", "optional": False}},
            "outputs": {"output_dir": {"type": "path", "datastore_mode": "Upload"}},
            "command": "sh ls.sh {inputs.input_dir} {inputs.file_name} {outputs.output_dir}",
            "environment": {"name": "AzureML-Minimal", "version": "45", "os": "linux"},
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
            "outputs": {"output_dir": {"type": "path"}},  # TODO: 1871902 "datastore_mode": "Upload"}},
            "command": "sh ls.sh {inputs.input_dir} {inputs.file_name} {outputs.output_dir}",
            "environment": {"name": "AzureML-Minimal", "version": "45", "os": "linux"},
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
                    "type": "AnyFile",  # TODO: support list of type
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
                    "optional": False,
                    "description": "relative path on ADLS storage",
                },
                "ExtractionClause": {
                    "type": "string",
                    "optional": False,
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
        [
            # use this file to avoid empty inputs & outputs
            "./tests/test_configs/internal/helloworld_component_command.yml",  # Command
            "./tests/test_configs/internal/hemera-component/component.yaml",  # Hemera
            "./tests/test_configs/internal/hdi-component/component_spec.yaml",  # HDInsight
            "./tests/test_configs/internal/batch_inference/batch_score.yaml",  # Parallel
            "./tests/test_configs/internal/scope-component/component_spec.yaml",  # Scope
            "./tests/test_configs/internal/data-transfer-component/component_spec.yaml",  # Data Transfer
            "./tests/test_configs/internal/starlite-component/component_spec.yaml",  # Starlite
        ],
    )
    def test_component_serialization(self, yaml_path: str):
        with open(yaml_path, encoding="utf-8") as yaml_file:
            yaml_dict = yaml.safe_load(yaml_file)

        entity = load_component(yaml_path)

        expected_dict = copy.deepcopy(yaml_dict)
        for input_port_name in expected_dict["inputs"]:
            input_port = expected_dict["inputs"][input_port_name]
            # enum will be transformed to string
            if input_port["type"].lower() == "enum":
                if "enum" in input_port:
                    input_port["enum"] = list(map(lambda x: str(x), input_port["enum"]))
                if "default" in input_port:
                    input_port["default"] = str(input_port["default"])

        assert entity._to_dict() == expected_dict
        rest_obj = entity._to_rest_object()
        assert rest_obj.properties.component_spec == expected_dict
        assert InternalComponent._load_from_rest(rest_obj)._to_dict() == expected_dict
        result = entity._validate()
        assert result._to_dict() == {"result": "Succeeded"}

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
        ],
    )
    def test_environment_dependencies_resolve(self, yaml_path: str, expected_dict: Dict) -> None:
        component: InternalComponent = load_component(path=yaml_path)
        component._resolve_local_dependencies()
        assert component.environment == expected_dict
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
        component = load_component(path=yaml_path)
        validation_result = component._customized_validate()
        assert not validation_result.passed
        assert validation_result.invalid_fields[0] == f"environment.conda.{invalid_field}"

    def test_environment_duplicate_dependencies_warning(self) -> None:
        yaml_path = "./tests/test_configs/internal/env-duplicate-dependencies/component_spec.yaml"
        component = load_component(path=yaml_path)
        validation_result = component._customized_validate()
        # pass validate with warning message
        assert validation_result.passed
        expected_warning_message = (
            "environment.conda: Duplicated declaration of dependencies, "
            "will honor in the order conda_dependencies, conda_dependencies_file, pip_requirements_file."
        )
        assert str(validation_result._warnings[0]) == expected_warning_message

    def test_additional_includes(self) -> None:
        yaml_path = (
            "./tests/test_configs/internal/component_with_additional_includes/helloworld_additional_includes.yml"
        )
        component: InternalComponent = load_component(path=yaml_path)
        assert component._customized_validate().passed, component._customized_validate()._to_dict()
        # resolve
        component._resolve_local_dependencies()
        code_path = Path(Code(base_path=component._base_path, path=component.code).path)
        assert code_path.is_dir()
        assert (code_path / "LICENSE").exists(), component.code
        assert (code_path / "library" / "hello.py").exists(), component.code
        assert (code_path / "library" / "world.py").exists(), component.code
        # cleanup
        component._cleanup_tmp_local_dependencies()
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
        component: InternalComponent = load_component(path=yaml_path)
        assert component._customized_validate().passed, component._customized_validate()._to_dict()
        # resolve
        component._resolve_local_dependencies()
        code_path = Path(Code(base_path=component._base_path, path=component.code).path)
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
        component._cleanup_tmp_local_dependencies()

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
        ],
    )
    def test_invalid_additional_includes(self, yaml_path: str, expected_error_msg_prefix: str) -> None:
        component = load_component(
            path=os.path.join("./tests/test_configs/internal/component_with_additional_includes", yaml_path)
        )
        validation_result = component._customized_validate()
        assert validation_result.passed is False
        assert validation_result.messages["*"].startswith(expected_error_msg_prefix), validation_result.messages["*"]
