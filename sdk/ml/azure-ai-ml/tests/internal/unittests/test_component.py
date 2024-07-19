# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import enum
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict
from zipfile import ZipFile

import pydash
import pytest
import yaml
from pytest_mock import MockFixture
from test_utilities.utils import build_temp_folder, mock_artifact_download_to_temp_directory, parse_local_path

from azure.ai.ml import load_component
from azure.ai.ml._internal._schema.component import NodeType
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml._internal.entities.spark import InternalSparkComponent
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import AZUREML_INTERNAL_COMPONENTS_ENV_VAR
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders.control_flow_node import LoopNode
from azure.ai.ml.exceptions import ValidationException

from .._utils import ANONYMOUS_COMPONENT_TEST_PARAMS, PARAMETERS_TO_TEST


class AdditionalIncludesCheckFunc(enum.Enum):
    """Enum for additional includes check function"""

    SKIP = 0
    SELF_IS_FILE = 1
    PARENT_EXISTS = 2
    NOT_EXISTS = 3
    NO_PARENT = 4


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

    def test_component_inputs_with_bool_and_date_value(self):
        yaml_path = (
            r"tests/test_configs/internal/command-component/command-linux/"
            r"component_with_bool_and_data_input/component.yaml"
        )
        component = load_component(yaml_path)
        assert component.inputs["bool_input"].default == "true"
        assert component.inputs["enum_input"].default == "true"
        assert component.inputs["enum_input"].enum == ["true", "false"]
        assert component.inputs["date_input"].default == "2023-01-01"

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
            "_source": "CLASS",
            "version": "0.0.1",
            "display_name": "0.0.1",
            "is_deterministic": True,
            "successful_return_code": "Zero",
            "inputs": {"train_data": {"type": "path", "optional": False}},
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
            "inputs": {"train_data": {"type": "path", "optional": False}},  # optional will be drop if False
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
            "_source": "CLASS",
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

    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict,pipeline_runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_component_serialization(
        self,
        yaml_path: str,
        inputs: Dict,
        runsettings_dict: Dict,
        pipeline_runsettings_dict: Dict,
    ) -> None:
        with open(yaml_path, encoding="utf-8") as yaml_file:
            yaml_dict = yaml.safe_load(yaml_file)

        entity = load_component(yaml_path)

        expected_dict = copy.deepcopy(yaml_dict)

        # Linux is the default value of os in InternalEnvironment
        if "environment" in expected_dict:
            expected_dict["environment"]["os"] = "Linux"

        for input_port_name in expected_dict.get("inputs", {}):
            input_port = expected_dict["inputs"][input_port_name]
            # enum will be transformed to string
            if isinstance(input_port["type"], str) and input_port["type"].lower() in [
                "string",
                "enum",
                "float",
                "integer",
            ]:
                if "enum" in input_port:
                    input_port["enum"] = list(
                        map(lambda x: str(x).lower() if isinstance(x, bool) else str(x), input_port["enum"])
                    )
                if "default" in input_port:
                    input_port["default"] = (
                        str(input_port["default"]).lower()
                        if isinstance(input_port["default"], bool)
                        else str(input_port["default"])
                    )

        # code will be dumped as absolute path
        if "code" in expected_dict:
            expected_dict["code"] = parse_local_path(expected_dict["code"], entity.base_path)

        expected_dict["version"] = str(expected_dict["version"])

        if entity.type == "spark":
            expected_dict["jars"] = [expected_dict["jars"]]
            expected_dict["pyFiles"] = [expected_dict["pyFiles"]]
            expected_dict["environment"] = {
                "conda_file": {
                    "dependencies": ["python=3.8", {"pip": ["azureml-core==1.44.0", "shrike==1.31.2"]}],
                    "name": "component_env",
                },
                "image": "conda/miniconda3",
                "name": "CliV2AnonymousEnvironment",
                "version": entity.environment.version,
            }
        assert entity._to_dict() == expected_dict

        expected_rest_object = copy.deepcopy(expected_dict)
        expected_rest_object["_source"] = "YAML.COMPONENT"
        if entity.type == "spark":
            expected_rest_object["py_files"] = expected_rest_object.pop("pyFiles")
        rest_obj = entity._to_rest_object()
        assert rest_obj.properties.component_spec == expected_rest_object

        # inherit input type map from Component._from_rest_object
        for input_port in expected_dict.get("inputs", {}).values():
            if input_port["type"] == "String":
                input_port["type"] = input_port["type"].lower()

        try:
            from_rest_entity = InternalComponent._from_rest_object(rest_obj)
        except Exception as e:
            raise RuntimeError(
                "Failed to load component from rest object:\n{}\n"
                "Full error message:\n{}".format(json.dumps(rest_obj.as_dict(), indent=4), e)
            )
        assert from_rest_entity._to_dict() == expected_dict
        result = entity._validate()
        assert result._to_dict() == {"result": "Succeeded"}

    @pytest.mark.parametrize(
        "yaml_path,label",
        [
            ("preview_command_component.yaml", "1-preview"),
            ("legacy_distributed_component.yaml", "1-legacy"),
        ],
    )
    def test_command_mode_command_component(self, yaml_path: str, label: str):
        component = load_component("./tests/test_configs/internal/command-mode/{}".format(yaml_path))
        assert component._to_rest_object().properties.component_spec["type"] == f"{component.type}@{label}"

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
        assert component.environment._validate_docker_section(
            base_path=component.base_path, skip_path_validation=False
        ).passed

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

    def test_load_environment_with_version(self):
        yaml_path = (
            r"tests/test_configs/internal/command-component/command-linux/"
            r"component_with_bool_and_data_input/component.yaml"
        )
        yaml_dict = load_yaml(yaml_path)
        component = load_component(source=yaml_path)
        assert component.environment.name == yaml_dict["environment"]["name"]
        assert component.environment.version == str(yaml_dict["environment"]["version"])
        assert component.environment.os == yaml_dict["environment"]["os"]

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
            resolver=mock_get_arm_id_and_fill_back,
        )
        assert component.code.path.name != COMPONENT_PLACEHOLDER

    def test_additional_includes(self) -> None:
        yaml_path = (
            "./tests/test_configs/internal/component_with_additional_includes/helloworld_additional_includes.yml"
        )
        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        # resolve
        with component._build_code() as code:
            code_path: Path = code.path
            assert code_path.is_dir()
            assert (code_path / "LICENSE").is_file()
            assert (code_path / "library.zip").is_file()
            assert ZipFile(code_path / "library.zip").namelist() == ["library/", "library/hello.py", "library/world.py"]
            assert (code_path / "library1" / "hello.py").is_file()
            assert (code_path / "library1" / "world.py").is_file()
            assert code._ignore_file.is_file_excluded(code_path / "helloworld_additional_includes.additional_includes")

        assert not code_path.is_dir()

    @pytest.mark.parametrize(
        "test_files",
        [
            pytest.param(
                [
                    (
                        "component_with_additional_includes/.amlignore",
                        "test_ignore/*\nlibrary1/ignore.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    (
                        "component_with_additional_includes/test_ignore/a.py",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                    # will be saved to library1/ignore.py, should be ignored
                    ("additional_includes/library1/ignore.py", None, AdditionalIncludesCheckFunc.NOT_EXISTS),
                    # will be saved to library1/ignore.py/a.py, should be ignored
                    # TODO: can't create with the same name?
                    # ("additional_includes/library1/ignore.py/a.py", None, AdditionalIncludesCheckFunc.NO_PARENT),
                    # will be saved to library1/test_ignore, should be kept
                    ("additional_includes/library1/test_ignore/a.py", None, AdditionalIncludesCheckFunc.SELF_IS_FILE),
                ],
                id="amlignore",
            ),
            pytest.param(
                [
                    # additional_includes for other spec, should be kept
                    (
                        "component_with_additional_includes/x.additional_includes",
                        None,
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    (
                        "additional_includes/library1/x.additional_includes",
                        None,
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    (
                        "additional_includes/library1/test/x.additional_includes",
                        None,
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    # additional_includes in a different level, should be kept
                    (
                        "component_with_additional_includes/library2/helloworld_additional_includes.additional_includes",
                        None,
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    (
                        "component_with_additional_includes/library2/library/helloworld_additional_includes.additional_includes",
                        None,
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    # additional_includes in a different level in additional includes, should be kept
                    (
                        "additional_includes/library1/helloworld_additional_includes.additional_includes",
                        None,
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                ],
                id="additional_includes",
            ),
            pytest.param(
                [
                    ("component_with_additional_includes/hello.py", None, AdditionalIncludesCheckFunc.SELF_IS_FILE),
                    (
                        "component_with_additional_includes/test_code/.amlignore",
                        "hello.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    (
                        "component_with_additional_includes/test_code/hello.py",
                        None,
                        AdditionalIncludesCheckFunc.NOT_EXISTS,
                    ),
                    # shall we keep the empty folder?
                    (
                        "component_with_additional_includes/test_code/a/hello.py",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                ],
                id="amlignore_subfolder",
            ),
            pytest.param(
                [
                    (
                        "additional_includes/library1/.amlignore",
                        "test_ignore\nignore.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    # will be saved to library1/ignore.py, should be ignored
                    ("additional_includes/library1/ignore.py", None, AdditionalIncludesCheckFunc.NOT_EXISTS),
                    # will be saved to library1/ignore.py/a.py, should be ignored
                    # TODO: can't create with the same name?
                    # ("additional_includes/library1/ignore.py/a.py", None, AdditionalIncludesCheckFunc.NO_PARENT),
                    # will be saved to library1/test_ignore, should be kept
                    ("additional_includes/library1/test_ignore/a.py", None, AdditionalIncludesCheckFunc.NOT_EXISTS),
                ],
                id="amlignore_in_additional_includes_folder",
            ),
            pytest.param(
                [
                    (
                        "additional_includes/library1/test_ignore/.amlignore",
                        "ignore.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    # will be saved to library1/ignore.py, should be ignored
                    (
                        "additional_includes/library1/test_ignore/ignore.py",
                        None,
                        AdditionalIncludesCheckFunc.NOT_EXISTS,
                    ),
                    (
                        "additional_includes/library1/test_ignore/ignore.py",
                        None,
                        AdditionalIncludesCheckFunc.NOT_EXISTS,
                    ),
                ],
                id="amlignore_in_additional_includes_subfolder",
            ),
            pytest.param(
                [
                    (
                        "component_with_additional_includes/__pycache__/a.pyc",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                    (
                        "component_with_additional_includes/test/__pycache__/a.pyc",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                    ("additional_includes/library1/__pycache__/a.pyc", None, AdditionalIncludesCheckFunc.NO_PARENT),
                    (
                        "additional_includes/library1/test/__pycache__/a.pyc",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                ],
                id="pycache",
            ),
        ],
    )
    def test_additional_includes_advanced(self, test_files) -> None:
        with build_temp_folder(
            source_base_dir="./tests/test_configs/internal/",
            relative_dirs_to_copy=["component_with_additional_includes", "additional_includes"],
            extra_files_to_create={file: content for file, content, _ in test_files},
        ) as test_configs_dir:
            yaml_path = (
                Path(test_configs_dir) / "component_with_additional_includes" / "helloworld_additional_includes.yml"
            )

            component: InternalComponent = load_component(source=yaml_path)

            # resolve and check snapshot directory
            with component._build_code() as code:
                for file, content, check_func in test_files:
                    # original file is based on test_configs_dir, need to remove the leading
                    # "component_with_additional_includes" or "additional_includes" to get the relative path
                    resolved_file_path = Path(os.path.join(code.path, *Path(file).parts[1:]))
                    if check_func == AdditionalIncludesCheckFunc.NO_PARENT:
                        assert not resolved_file_path.parent.exists(), f"{file} should not have parent"
                    elif check_func == AdditionalIncludesCheckFunc.SELF_IS_FILE:
                        assert resolved_file_path.is_file(), f"{file} is not a file"
                        if content is not None:
                            assert resolved_file_path.read_text() == content, f"{file} content is not expected"
                    elif check_func == AdditionalIncludesCheckFunc.PARENT_EXISTS:
                        assert resolved_file_path.parent.is_dir(), f"{file} should have parent"
                    elif check_func == AdditionalIncludesCheckFunc.NOT_EXISTS:
                        assert not resolved_file_path.exists(), f"{file} should not exist"
                    elif check_func == AdditionalIncludesCheckFunc.SKIP:
                        pass
                    else:
                        raise ValueError(f"Unknown check func: {check_func}")

    def test_additional_includes_merge_folder(self) -> None:
        yaml_path = (
            "./tests/test_configs/internal/component_with_additional_includes/additional_includes_merge_folder.yml"
        )
        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        with component._build_code() as code:
            code_path = code.path
            # first folder
            assert (code_path / "library1" / "__init__.py").is_file()
            assert (code_path / "library1" / "hello.py").is_file()
            # second folder content
            assert (code_path / "library1" / "utils").is_dir()
            assert (code_path / "library1" / "utils" / "__init__.py").is_file()
            assert (code_path / "library1" / "utils" / "salute.py").is_file()

    @pytest.mark.parametrize(
        "yaml_path,has_additional_includes",
        [
            ("no_code_and_additional_includes/component_spec.yml", False),
            ("code_only/component_spec.yml", False),
            ("code_and_additional_includes/component_spec.yml", True),
        ],
    )
    def test_additional_includes_with_code_specified(self, yaml_path: str, has_additional_includes: bool) -> None:
        yaml_path = os.path.join("./tests/test_configs/internal/component_with_additional_includes/", yaml_path)
        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        # resolve
        with component._build_code() as code:
            code_path = code.path
            assert code_path.is_dir()
            if has_additional_includes:
                # additional includes is specified, code will be tmp folder and need to check each item
                # manually list here to avoid temp folder like __pycache__ breaking test.
                for path in [
                    "additional_includes_merge_folder.yml",
                    "code_and_additional_includes",
                    "code_only",
                    "helloworld_additional_includes.yml",
                    "helloworld_invalid_additional_includes_existing_file.yml",
                    "helloworld_invalid_additional_includes_root_directory.yml",
                    "helloworld_invalid_additional_includes_zip_file_not_found.yml",
                    "no_code_and_additional_includes",
                ]:
                    assert (code_path / path).is_file() if ".yml" in path else (code_path / path).is_dir()
                assert (code_path / "LICENSE").is_file()
            else:
                # additional includes not specified, code should be specified path (default yaml folder)
                yaml_dict = load_yaml(yaml_path)
                specified_code_path = Path(yaml_path).parent / yaml_dict.get("code", "./")
                assert code_path.resolve() == specified_code_path.resolve()

    def test_docker_file_in_additional_includes(self):
        yaml_path = (
            "./tests/test_configs/internal/component_with_dependency_" "in_additional_includes/with_docker_file.yml"
        )

        docker_file_path = "./tests/test_configs/internal/additional_includes/docker/DockerFile"
        with open(docker_file_path, "r") as docker_file:
            docker_file_content = docker_file.read()

        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        with component._build_code():
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
        yaml_path = (
            "./tests/test_configs/internal/component_with_dependency_" "in_additional_includes/with_conda_pip.yml"
        )

        conda_file_path = "./tests/test_configs/internal/env-conda-dependencies/conda.yaml"
        with open(conda_file_path, "r") as conda_file:
            conda_file_content = yaml.safe_load(conda_file)

        component: InternalComponent = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        with component._build_code():
            environment_rest_obj = component._to_rest_object().properties.component_spec["environment"]
            assert environment_rest_obj == {
                "conda": {
                    "conda_dependencies": conda_file_content,
                },
                "os": "Linux",
            }

    def test_artifacts_in_additional_includes(self):
        with mock_artifact_download_to_temp_directory():
            yaml_path = "./tests/test_configs/internal/component_with_additional_includes/with_artifacts.yml"
            component: InternalComponent = load_component(source=yaml_path)
            assert component._validate().passed, repr(component._validate())
            with component._build_code() as code:
                code_path = code.path
                assert code_path.is_dir()
                for path in [
                    "version_1/",
                    "version_1/file",
                    "version_2/",
                    "version_2/file",
                    "file_version_1",
                    "file_version_2",
                    "DockerFile",
                ]:
                    assert (code_path / path).exists()

            yaml_path = (
                "./tests/test_configs/internal/component_with_additional_includes/"
                "artifacts_additional_includes_with_conflict.yml"
            )
            component: InternalComponent = load_component(source=yaml_path)
            with pytest.raises(
                RuntimeError,
                match="There are conflict files in additional include"
                ".*test_additional_include:version_1 in component-sdk-test-feed"
                ".*test_additional_include:version_3 in component-sdk-test-feed",
            ):
                with component._build_code():
                    pass

    @pytest.mark.parametrize(
        "yaml_path,expected_error_msg_prefix",
        [
            pytest.param(
                "helloworld_invalid_additional_includes_root_directory.yml",
                "Root directory is not supported for additional includes",
                id="root_as_additional_includes",
            ),
            pytest.param(
                "helloworld_invalid_additional_includes_existing_file.yml",
                "A file already exists for additional include",
                id="file_already_exists",
            ),
            pytest.param(
                "helloworld_invalid_additional_includes_zip_file_not_found.yml",
                "Unable to find additional include ../additional_includes/assets/LICENSE.zip",
                id="zip_file_not_found",
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
                "param_float": {"type": "float", "default": "0.15", "max": "1.0", "min": "-1.0"},
                "param_int": {"type": "integer"},
                "param_string_with_default_value": {"default": ",", "type": "string"},
                "param_string_with_default_value_2": {"default": "utf8", "type": "string"},
                # yes will be converted to true in YAML 1.2, but we will load it as "yes" for backward compatibility
                "param_string_with_yes_value": {"default": "yes", "type": "string"},
                "param_string_with_quote_yes_value": {"default": "yes", "type": "string"},
            },
            "outputs": {
                "output_data_path": {
                    "datastore_mode": "mount",
                    "description": "Path to the data",
                    "is_link_mode": True,
                    "type": "path",
                }
            },
        }
        assert component._to_rest_object().properties.component_spec["inputs"] == expected_inputs["inputs"]
        assert component._to_rest_object().properties.component_spec["outputs"] == expected_inputs["outputs"]
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
                "type": "AnyDirectory",
            },
            "primitive_is_control": {"type": "boolean"},
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
            validate_result = loop_node._validate_body()
            assert validate_result.passed

    @pytest.mark.parametrize(
        "relative_yaml_path,expected_snapshot_id",
        ANONYMOUS_COMPONENT_TEST_PARAMS,
    )
    def test_anonymous_component_reuse(self, relative_yaml_path: str, expected_snapshot_id: str):
        component: InternalComponent = load_component(
            source=Path("./tests/test_configs/internal/component-reuse/") / relative_yaml_path
        )
        with component._build_code() as code:
            assert code.name == expected_snapshot_id

            code.name = expected_snapshot_id
            with pytest.raises(
                AttributeError, match="InternalCode name are calculated based on its content and cannot be changed.*"
            ):
                code.name = expected_snapshot_id + "1"

    def test_snapshot_id_calculation(self):
        origin_test_configs_dir = Path("./tests/test_configs/internal/")
        with tempfile.TemporaryDirectory() as test_configs_dir:
            shutil.copytree(
                origin_test_configs_dir / "component-reuse/simple-command", Path(test_configs_dir) / "simple-command"
            )

            yaml_path = Path(test_configs_dir) / "simple-command" / "powershell_copy.yaml"

            component: InternalComponent = load_component(source=yaml_path)
            # create some files/folders expected to ignore
            code_pycache = yaml_path.parent / "__pycache__"
            code_pycache.mkdir()
            (code_pycache / "a.pyc").touch()

            # resolve and check snapshot directory
            with component._build_code() as code:
                # ANONYMOUS_COMPONENT_TEST_PARAMS[0] is the test params for simple-command
                assert code.name == ANONYMOUS_COMPONENT_TEST_PARAMS[0][1]

    def test_component_serialization_corner_case(self):
        yaml_path = "./tests/test_configs/internal/command-component-serialization-core-case/component_spec.yaml"
        component: InternalComponent = load_component(source=yaml_path)
        assert component
        rest_object = component._to_rest_object()
        assert rest_object.properties.component_spec == {
            "$schema": "https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            "_source": "YAML.COMPONENT",
            "command": "echo {inputs.input_float} && echo {inputs.delimiter}",
            "display_name": "Hello Command",
            "environment": {"name": "AzureML-Designer", "os": "Linux"},
            "inputs": {
                "input_float": {"default": "1", "optional": False, "type": "Float"},  # previously this is 1.0
                "input_boolean": {"default": "False", "optional": False, "type": "Boolean"},
                "delimiter": {"default": "\t", "optional": True, "type": "String"},
            },
            "is_deterministic": True,
            "name": "hello_command",
            "type": "CommandComponent",
            "version": "0.10",  # previously this is 0.1
            "datatransfer": {"cloud_type": "aether"},
        }

    def test_load_from_internal_spark_component(self):
        yaml_path = PARAMETERS_TO_TEST[9].values[0]
        origin_component: InternalSparkComponent = load_component(source=yaml_path)
        base_rest_object = origin_component._to_rest_object()
        base_component: InternalSparkComponent = Component._from_rest_object(base_rest_object)
        expected_dict = base_component._to_dict()

        treat_rest_object = origin_component._to_rest_object()
        treat_rest_object.properties.component_spec["environment"] = {
            "os": "Linux",
            "conda": {
                "conda_dependencies": [
                    "python=3.8",
                    {
                        "pip": [
                            "azureml-core==1.44.0",
                            "shrike==1.31.2",
                        ],
                    },
                ],
            },
        }
        treat_component: InternalSparkComponent = Component._from_rest_object(treat_rest_object)

        for component in (base_component, treat_component, origin_component):
            assert isinstance(component, InternalSparkComponent)

        expected_dict["environment"]["version"] = treat_component.environment.version
        del expected_dict["environment"]["conda_file"]["name"]
        assert treat_component._to_dict() == expected_dict

    def test_load_from_internal_aether_bridge_component(self):
        yaml_path = "./tests/test_configs/internal/aether_bridge_component/component_spec.yaml"
        component: InternalComponent = load_component(source=yaml_path)
        assert component
        rest_object = component._to_rest_object()
        assert rest_object.properties.component_spec == {
            "name": "aether_bridge_component",
            "version": "0.0.1",
            "$schema": "https://componentsdk.azureedge.net/jsonschema/AetherBridgeComponent.json",
            "display_name": "Aether Bridge Component",
            "inputs": {
                "mock_param1": {"type": "AnyFile", "optional": False},
                "mock_param2": {"type": "AnyFile", "optional": False},
            },
            "aether": {"module_type": "ScrapingCloud", "ref_id": "mock_ref_id"},
            "outputs": {"job_info": {"type": "AnyFile"}},
            "type": "AetherBridgeComponent",
            "command": "mock.exe {inputs.mock_param1} {inputs.mock_param2} {outputs.job_info}",
            "_source": "YAML.COMPONENT",
        }

    def test_spark_component_special_type(self):
        yaml_path = "./tests/test_configs/internal/spark-component-special-type/spec.yaml"
        component: InternalSparkComponent = load_component(source=yaml_path)
        assert component
        rest_object = component._to_rest_object()
        assert rest_object.properties.component_spec["inputs"] == {
            "file_input1": {"datastore_mode": "hdfs", "description": "The data to be read.", "type": "path"},
            "file_input2": {"datastore_mode": "hdfs", "description": "The data to be read.", "type": "path"},
            "number_input": {
                "description": "The number to be used in the computation.",
                "max": "3.0",
                "min": "0.0",
                "type": "number",
            },
            "string_input": {"description": "The string to be used in the computation.", "type": "string"},
        }
