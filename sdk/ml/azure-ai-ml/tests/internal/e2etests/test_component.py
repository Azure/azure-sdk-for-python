# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pydash
import pytest
from typing import Callable, Dict, List

from azure.ai.ml import MLClient, load_component
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict

from devtools_testutils import AzureRecordedTestCase


def create_component(
    client: MLClient,
    component_name: str,
    path="./tests/test_configs/components/helloworld_component.yml",
    params_override=None,
    is_anonymous=False,
):
    default_param_override = [{"name": component_name}]
    if params_override is None:
        params_override = default_param_override
    else:
        params_override += default_param_override

    command_component = load_component(
        path=path,
        params_override=params_override,
    )
    return client.components.create_or_update(command_component, is_anonymous=is_anonymous)


def load_registered_component(
    client: MLClient,
    component_name: str,
    component_version: str,
    omit_fields: List[str],
) -> Dict:
    """Load registered component from server and omit some fields."""
    component_entity = client.components.get(name=component_name, version=component_version)
    component_rest_object = component_entity._to_rest_object()
    return pydash.omit(component_rest_object.properties.component_spec, *omit_fields)


def _slim_loaded_dict_to_compare(loaded_dict: dict, yaml_dict: dict) -> None:
    """Server returns complete component spec, which may contain more fields than yaml."""
    keys_to_del = []
    for key in loaded_dict:
        if key not in yaml_dict:
            keys_to_del.append(key)
        elif isinstance(loaded_dict[key], dict) and isinstance(yaml_dict[key], dict):
            _slim_loaded_dict_to_compare(loaded_dict[key], yaml_dict[key])

    for key in keys_to_del:
        del loaded_dict[key]

    if "inputs" in loaded_dict:
        for input_name, input_obj in loaded_dict["inputs"].items():
            yaml_input = yaml_dict["inputs"][input_name]
            # remote optional will be dropped if it is False
            if "optional" in yaml_input and "optional" not in input_obj:
                input_obj["optional"] = False
            # remote default will always be a string, so convert & compare separately
            if "default" in yaml_input:
                if isinstance(yaml_input["default"], float):
                    input_obj["default"] = float(input_obj["default"])
                elif isinstance(yaml_input["default"], bool):
                    if input_obj["default"].lower() == "true":
                        input_obj["default"] = True
                    elif input_obj["default"].lower() == "false":
                        input_obj["default"] = False
                elif isinstance(yaml_input["default"], int):
                    input_obj["default"] = int(input_obj["default"])
            if "type" in yaml_input and yaml_input["type"] == "enum":
                input_obj["type"] = input_obj["type"].lower()
                # remote enum will be a list of strings, so convert & compare separately
                yaml_input["enum"] = list(map(str, yaml_input["enum"]))


@pytest.mark.usefixtures(
    "recorded_test",
    "enable_internal_components",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash"
)
@pytest.mark.e2etest
class TestComponent(AzureRecordedTestCase):
    @pytest.mark.parametrize(
        "yaml_path,with_code",
        [
            ("./tests/test_configs/internal/ls_command_component.yaml", True),  # Command
            ("./tests/test_configs/internal/hemera-component/component.yaml", True),  # Hemera
            ("./tests/test_configs/internal/hdi-component/component_spec.yaml", True),  # HDInsight
            (
                "./tests/test_configs/internal/batch_inference/batch_score.yaml",  # Parallel
                True,  # Parallel component doesn't have code?
            ),
            ("./tests/test_configs/internal/scope-component/component_spec.yaml", True),  # Scope
            ("./tests/test_configs/internal/data-transfer-component/component_spec.yaml", True),  # Data Transfer
            ("./tests/test_configs/internal/starlite-component/component_spec.yaml", True),  # Starlite
        ],
    )
    def test_component_create(
        self, client: MLClient, randstr: Callable[[str], str], yaml_path: str, with_code: bool
    ) -> None:
        component_name = randstr("component_name")
        component_resource = create_component(client, component_name, path=yaml_path)
        assert component_resource.name == component_name
        if with_code:
            assert component_resource.code
        else:
            assert not component_resource.code
        assert component_resource.creation_context

        component = client.components.get(component_name, component_resource.version)
        assert component_resource._to_dict() == component._to_dict()
        assert component_resource.creation_context

    @pytest.mark.parametrize(
        "yaml_path,omit_fields",
        [
            (
                # Command Component
                "./tests/test_configs/internal/ls_command_component.yaml",
                ["id", "creation_context", "code"],
            ),
            (
                "./tests/test_configs/internal/hemera-component/component.yaml",  # Hemera
                [
                    "id",
                    "creation_context",
                    # TODO: 1871902 is_resource will be lost after load_from_rest, but is correct in creation
                    "inputs.InitialModelDir.is_resource",
                    "inputs.ValidationDataDir.is_resource",
                    "inputs.TrainingDataDir.is_resource",
                ],
            ),
            (
                "./tests/test_configs/internal/hdi-component/component_spec.yaml",  # HDInsight
                ["id", "creation_context"],
            ),
            (
                "./tests/test_configs/internal/batch_inference/batch_score.yaml",  # Parallel
                ["id", "creation_context"],
            ),
            (
                "./tests/test_configs/internal/scope-component/component_spec.yaml",  # Scope
                ["id", "creation_context", "code"],
            ),
            (
                # Data Transfer Component
                "./tests/test_configs/internal/data-transfer-component/component_spec.yaml",
                ["id", "creation_context", "code"],
            ),
            (
                "./tests/test_configs/internal/starlite-component/component_spec.yaml",  # Starlite
                ["id", "creation_context", "code"],
            ),
        ],
    )
    def test_component_load(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        yaml_path: str,
        omit_fields: List[str],
    ) -> None:
        yaml_dict = dict(**load_yaml(yaml_path))
        component_name = randstr("component_name")
        component_resource = create_component(client, component_name, path=yaml_path)
        loaded_dict = load_registered_component(client, component_name, component_resource.version, omit_fields)
        yaml_dict["type"] = yaml_dict["type"].rsplit("@", 1)[0]
        _slim_loaded_dict_to_compare(loaded_dict, yaml_dict)
        yaml_dict["name"] = component_name
        # TODO: check if loaded environment is expected to be an ordered dict
        assert loaded_dict == pydash.omit(convert_ordered_dict_to_dict(yaml_dict), *omit_fields)

    @pytest.mark.skip(reason="Target component is not in target workspace")
    def test_load_registered_internal_scope_component(self, client: MLClient):
        # curated env with name & version
        component_entity = client.components.get(
            "levance.convert2ss_31201029556679", "85b54741.0bf9.4734.a5bb.0e469c7bf792"
        )
        component_rest_object = component_entity._to_rest_object()
        component_spec = pydash.omit(component_rest_object.properties.component_spec, "code")
        assert component_spec == {
            "name": "levance.convert2ss_31201029556679",
            "description": "Convert ADLS test data to SS format",
            "tags": {"org": "bing", "project": "relevance"},
            "type": "scopecomponent",
            "$schema": "https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            "version": "85b54741.0bf9.4734.a5bb.0e469c7bf792",
            "display_name": "Convert Text to StructureStream",
            "is_deterministic": True,
            "inputs": {
                "TextData": {
                    "type": "['AnyFile', 'AnyDirectory']",
                    "optional": False,
                    "description": "relative path on ADLS storage",
                    "is_resource": False,
                },
                "ExtractionClause": {
                    "type": "string",
                    "optional": False,
                    "description": 'the extraction clause, something like "column1:string, column2:int"',
                },
            },
            "outputs": {"SSPath": {"type": "CosmosStructuredStream", "description": "output path of ss"}},
        }

    @pytest.mark.skip(reason="Target component is not in target workspace")
    def test_load_registered_internal_command_component(self, client: MLClient):
        # curated env with name & version
        component_entity = client.components.get("ls_command", "0.0.1")
        component_rest_object = component_entity._to_rest_object()
        omit_fields = ["id", "creation_context", "code", "environment"]
        component_spec = pydash.omit(component_rest_object.properties.component_spec, *omit_fields)
        assert component_spec == {
            "$schema": "https://componentsdk.azureedge.net/jsonschema/CommandComponent.json",
            "name": "ls_command",
            "version": "0.0.1",
            "display_name": "Ls Command",
            "tags": {},
            "is_deterministic": True,
            "inputs": {
                "input_dir": {"type": "path", "optional": False},
                "file_name": {"type": "string", "optional": False, "default": "files.txt"},
            },
            "outputs": {"output_dir": {"type": "path"}},
            "type": "command",
            "command": "sh ls.sh {inputs.input_dir} {inputs.file_name} {outputs.output_dir}",
        }

    @pytest.mark.skip(reason="Target component is not in target workspace")
    def test_load_registered_internal_hemera_component(self, client: MLClient):
        component_entity = client.components.get("microsoft.com.azureml.samples.hemera.adslrdnnrawkeys_dummy", "0.0.1")
        component_rest_object = component_entity._to_rest_object()
        omit_fileds = ["code", "creation_context", "id"]
        component_spec = pydash.omit(component_rest_object.properties.component_spec, *omit_fileds)
        assert component_spec == {
            "$schema": "https://componentsdk.azureedge.net/jsonschema/HemeraComponent.json",
            "name": "microsoft.com.azureml.samples.hemera.adslrdnnrawkeys_dummy",
            "version": "0.0.1",
            "display_name": "Ads LR DNN Raw Keys",
            "description": "Ads LR DNN Raw Keys Dummy sample.",
            "tags": {},
            "is_deterministic": True,
            "hemera": {"ref_id": "1bd1525c-082e-4652-a9b2-9c60783ec551"},
            "inputs": {
                "TrainingDataDir": {"type": "path", "optional": True, "is_resource": "True"},
                "ValidationDataDir": {"type": "path", "optional": True, "is_resource": "True"},
                "InitialModelDir": {"type": "path", "optional": True, "is_resource": "True"},
                "YarnCluster": {"type": "string", "optional": False, "default": "mtprime-bn2-0"},
                "JobQueue": {"type": "string", "optional": False, "default": "default"},
                "WorkerCount": {"type": "string", "optional": False, "default": 2.0},
                "Cpu": {"type": "string", "optional": False, "default": 2.0},
                "Memory": {"type": "string", "optional": False, "default": "10g"},
                "HdfsRootDir": {"type": "string", "optional": False, "default": "/projects/default/"},
                "CosmosRootDir": {
                    "type": "string",
                    "optional": False,
                    "default": "https://cosmos09.osdinfra.net/cosmos/dummy/local/root/",
                },
            },
            "outputs": {"output1": {"type": "AnyFile"}, "output2": {"type": "AnyFile"}},
            "type": "hemeracomponent",
            "command": "run.bat [-_TrainingDataDir {inputs.TrainingDataDir}] "
            "[-_ValidationDataDir {inputs.ValidationDataDir}] "
            "[-_InitialModelDir {inputs.InitialModelDir}] -_CosmosRootDir "
            "{inputs.CosmosRootDir} -_PsCount 0 %CLUSTER%={inputs.YarnCluster} "
            "-JobQueue {inputs.JobQueue} -_WorkerCount {inputs.WorkerCount} "
            "-_Cpu {inputs.Cpu} -_Memory {inputs.Memory} -_HdfsRootDir "
            '{inputs.HdfsRootDir} -_ExposedPort "3200-3210,3300-3321" '
            "-_NodeLostBlocker -_UsePhysicalIP -_SyncWorker -_EntranceFileName "
            'run.py -_StartupArguments "" -_PythonZipPath '
            '"https://dummy/foo/bar.zip" -_ModelOutputDir {outputs.output1} '
            "-_ValidationOutputDir {outputs.output2}",
        }

    @pytest.mark.skip(reason="Target component is not in target workspace")
    def test_load_registered_internal_hdi_component(self, client: MLClient):
        component_entity = client.components.get("microsoft.com.azureml.samples.train-in-spark", "0.0.1")
        component_rest_object = component_entity._to_rest_object()
        omit_fileds = ["code", "creation_context", "id"]
        component_spec = pydash.omit(component_rest_object.properties.component_spec, *omit_fileds)
        assert component_spec == {
            "$schema": "https://componentsdk.azureedge.net/jsonschema/HDInsightComponent.json",
            "name": "microsoft.com.azureml.samples.train-in-spark",
            "version": "0.0.1",
            "display_name": "Train in Spark",
            "hdinsight": {
                "args": "--input_path {inputs.input_path} "
                "[--regularization_rate {inputs.regularization_rate}] "
                "--output_path {outputs.output_path}",
                "file": "train-spark.py",
            },
            "description": "Train a Spark ML model using an HDInsight Spark cluster",
            "tags": {
                "HDInsight": "",
                "Sample": "",
                "contact": "Microsoft Coporation <xxx@microsoft.com>",
                "helpDocument": "https://aka.ms/hdinsight-modules",
            },
            "is_deterministic": True,
            "inputs": {
                "input_path": {"type": "AnyDirectory", "optional": False, "description": "Iris csv file"},
                "regularization_rate": {
                    "type": "Float",
                    "optional": True,
                    "default": 0.01,
                    "description": "Regularization rate when training with logistic regression",
                },
            },
            "outputs": {
                "output_path": {"type": "AnyDirectory", "description": "The output path to save the trained model to"}
            },
            "type": "hdinsightcomponent",
        }

    @pytest.mark.skip(reason="Target component is not in target workspace")
    def test_load_registered_internal_parallel_component(self, client: MLClient):
        # curated env with name & version
        component_entity = client.components.get("microsoft.com.azureml.samples.parallel_copy_files_v1", "0.0.2")
        component_rest_object = component_entity._to_rest_object()
        omit_fileds = ["code", "creation_context", "id"]
        component_spec = pydash.omit(component_rest_object.properties.component_spec, *omit_fileds)
        assert component_spec == {
            "$schema": "https://componentsdk.azureedge.net/jsonschema/ParallelComponent.json",
            "name": "microsoft.com.azureml.samples.parallel_copy_files_v1",
            "version": "0.0.2",
            "display_name": "Parallel Copy Files v1",
            "description": "A sample Parallel module to copy files.",
            "tags": {
                "Sample": "",
                "Parallel": "",
                "helpDocument": "https://aka.ms/parallel-modules",
                "contact": "Microsoft Coporation <xxx@microsoft.com>",
            },
            "is_deterministic": True,
            "inputs": {"input_folder": {"type": "AnyDirectory", "optional": False, "datastore_mode": "Mount"}},
            "outputs": {
                "output_folder": {"type": "AnyDirectory", "description": "Output images", "datastore_mode": "Upload"}
            },
            "type": "parallelcomponent",
            "environment": {
                "conda": {
                    "conda_dependencies": {
                        "name": "project_environment",
                        "channels": ["conda-forge"],
                        "dependencies": ["pip=20.2", "python=3.8", {"pip": ["azureml-defaults==1.35.0"]}],
                    }
                },
                "docker": {"image": "mcr.microsoft.com/azureml/base:intelmpi2018.3-ubuntu16.04"},
                "os": "Linux",
            },
            "parallel": {
                "args": "--output-dir {outputs.output_folder}",
                "input_data": "inputs.input_folder",
                "output_data": "outputs.output_folder",
                "entry": "copy_files.py",
            },
        }
