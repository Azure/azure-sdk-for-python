# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from pathlib import Path
from typing import Any, Dict

import pydash
import pytest
import yaml
from azure.ai.ml import Input, load_component, load_job
from azure.ai.ml._internal import (
    Ae365exepool,
    AISuperComputerConfiguration,
    AISuperComputerScalePolicy,
    AISuperComputerStorageReferenceConfiguration,
    Command,
    DataTransfer,
    Distributed,
    HDInsight,
    Hemera,
    ITPConfiguration,
    ITPInteractiveConfiguration,
    ITPPriorityConfiguration,
    ITPResourceConfiguration,
    ITPRetrySettings,
    Parallel,
    Pipeline,
    Scope,
    Starlite,
    TargetSelector,
)
from azure.ai.ml._internal.entities import InternalBaseNode, InternalComponent, Scope
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._job.job import JobComputePropertyFields
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import (
    CommandComponent,
    CommandJobLimits,
    Data,
    JobResourceConfiguration,
    PipelineJob,
    SparkResourceConfiguration,
)
from test_utilities.utils import parse_local_path

from .._utils import (
    DATA_VERSION,
    PARAMETERS_TO_TEST,
    assert_strong_type_intellisense_enabled,
    extract_non_primitive,
    get_expected_runsettings_items,
    set_run_settings,
)


@pytest.mark.usefixtures("enable_internal_components", "enable_pipeline_private_preview_features")
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPipelineJob:
    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict,pipeline_runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_anonymous_internal_component_in_pipeline(
        self, yaml_path, inputs, runsettings_dict, pipeline_runsettings_dict
    ):
        node_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func():
            node = node_func(**inputs)
            set_run_settings(node, runsettings_dict)
            assert_strong_type_intellisense_enabled(node, runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        set_run_settings(dsl_pipeline.settings, pipeline_runsettings_dict)
        result = dsl_pipeline._validate()
        assert result._to_dict() == {"result": "Succeeded"}

        # check if node type is correct
        node_in_pipeline = dsl_pipeline.jobs["node"]
        if node_func.type == "CommandComponent":
            assert isinstance(node_in_pipeline, Command)
        elif node_func.type == "ScopeComponent":
            assert isinstance(node_in_pipeline, Scope)
        elif node_func.type == "HDInsightComponent":
            assert isinstance(node_in_pipeline, HDInsight)
        elif node_func.type == "ParallelComponent":
            assert isinstance(node_in_pipeline, Parallel)
        elif node_func.type == "DistributedComponent":
            assert isinstance(node_in_pipeline, Distributed)
        elif node_func.type == "DataTransferComponent":
            assert isinstance(node_in_pipeline, DataTransfer)
        elif node_func.type == "StarliteComponent":
            assert isinstance(node_in_pipeline, Starlite)
        elif node_func.type == "PipelineComponent":
            assert isinstance(node_in_pipeline, Pipeline)
        elif node_func.type == "HemeraComponent":
            assert isinstance(node_in_pipeline, Hemera)
        elif node_func.type == "Ae365exepoolComponent":
            assert isinstance(node_in_pipeline, Ae365exepool)

        # check if node's runsettings are set correctly
        node_rest_dict = dsl_pipeline._to_rest_object().properties.jobs["node"]
        del node_rest_dict["componentId"]  # delete component spec to make it a pure dict
        mismatched_runsettings = {}
        for dot_key, expected_value in get_expected_runsettings_items(runsettings_dict):
            value = pydash.get(node_rest_dict, dot_key)
            if value != expected_value:
                mismatched_runsettings[dot_key] = (value, expected_value)
        assert not mismatched_runsettings, "Current value:\n{}\nMismatched fields:\n{}".format(
            json.dumps(node_rest_dict, indent=2), json.dumps(mismatched_runsettings, indent=2)
        )

        pipeline_dict = dsl_pipeline._to_dict()
        pipeline_dict = extract_non_primitive(pipeline_dict)
        assert not pipeline_dict, pipeline_dict

    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict,pipeline_runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_data_as_node_inputs(self, yaml_path, inputs, runsettings_dict, pipeline_runsettings_dict):
        node_func: InternalComponent = load_component(yaml_path)

        input_data_names = {}
        for input_name, input_obj in inputs.items():
            if isinstance(input_obj, Input):
                data_name = input_obj.path.split("@")[0]
                if "spark" in yaml_path:
                    input_data_names[input_name] = input_obj
                else:
                    inputs[input_name] = Data(name=data_name, version=DATA_VERSION, type=AssetTypes.MLTABLE)
                    input_data_names[input_name] = data_name
        if len(input_data_names) == 0:
            return

        @pipeline()
        def pipeline_func():
            node = node_func(**inputs)
            set_run_settings(node, runsettings_dict)
            assert_strong_type_intellisense_enabled(node, runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        set_run_settings(dsl_pipeline.settings, pipeline_runsettings_dict)
        assert dsl_pipeline._validate().passed, repr(dsl_pipeline._validate())

        node_rest_dict = dsl_pipeline._to_rest_object().properties.jobs["node"]
        for input_name, dataset_name in input_data_names.items():
            if "spark" in yaml_path:
                expected_rest_obj = {"job_input_type": AssetTypes.MLTABLE, "uri": dataset_name.path, "mode": "Direct"}
            else:
                expected_rest_obj = {
                    "job_input_type": AssetTypes.MLTABLE,
                    "uri": dataset_name + ":" + DATA_VERSION,
                }
            assert node_rest_dict["inputs"][input_name] == expected_rest_obj

    @pytest.mark.parametrize(
        "input_path",
        [
            "test:" + DATA_VERSION,
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/"
            "Microsoft.MachineLearningServices/workspaces/ws/datasets/test/versions/" + DATA_VERSION,
        ],
    )
    def test_data_as_pipeline_inputs(self, input_path):
        yaml_path = "./tests/test_configs/internal/distribution-component/component_spec.yaml"
        node_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func(pipeline_input):
            node = node_func(input_path=pipeline_input)
            node.compute = "cpu-cluster"

        dsl_pipeline: PipelineJob = pipeline_func(pipeline_input=Input(path=input_path, type=AssetTypes.MLTABLE))
        if input_path.startswith("test:"):
            dsl_pipeline_with_data_input: PipelineJob = pipeline_func(
                pipeline_input=Data(name="test", version=DATA_VERSION, type=AssetTypes.MLTABLE)
            )
        else:
            dsl_pipeline_with_data_input: PipelineJob = pipeline_func(
                pipeline_input=Data(name="test", id=input_path, type=AssetTypes.MLTABLE)
            )
        result = dsl_pipeline_with_data_input._validate()
        assert result._to_dict() == {"result": "Succeeded"}

        assert (
            dsl_pipeline_with_data_input._to_rest_object().properties.as_dict()
            == dsl_pipeline._to_rest_object().properties.as_dict()
        )

        pipeline_rest_dict = dsl_pipeline_with_data_input._to_rest_object().properties

        expected_rest_obj = {
            "job_input_type": AssetTypes.MLTABLE,
            "uri": input_path,
        }
        assert pipeline_rest_dict.inputs["pipeline_input"].as_dict() == expected_rest_obj

        expected_rest_obj = {
            "job_input_type": "literal",
            "value": "${{parent.inputs.pipeline_input}}",
        }
        assert pipeline_rest_dict.jobs["node"]["inputs"]["input_path"] == expected_rest_obj

    def test_internal_component_node_output_type(self):
        from azure.ai.ml._utils.utils import try_enable_internal_components

        # force register internal components after partially reload schema files
        try_enable_internal_components(force=True)
        yaml_path = "./tests/test_configs/internal/component_with_input_outputs/component_spec.yaml"
        component_func = load_component(yaml_path)

        @pipeline
        def pipeline_func():
            node = component_func()
            # node level should have correct output type when type not configured
            node.outputs.data_any_file.mode = "mount"

        pipeline_job = pipeline_func()
        rest_pipeline_job_dict = pipeline_job._to_rest_object().as_dict()
        assert rest_pipeline_job_dict["properties"]["jobs"]["node"]["outputs"] == {
            "data_any_file": {"mode": "ReadWriteMount", "job_output_type": "uri_file"}
        }

    def test_internal_component_output_as_pipeline_component_output(self):
        from azure.ai.ml._utils.utils import try_enable_internal_components

        # force register internal components after partially reload schema files
        try_enable_internal_components(force=True)

        yaml_path = "./tests/test_configs/internal/component_with_input_outputs/component_spec.yaml"
        component_func = load_component(yaml_path, params_override=[{"inputs": {}}])

        @pipeline()
        def sub_pipeline_func():
            node = component_func()
            node.adla_account_name = "adla_account_name"
            return node.outputs

        sub_pipeline_1 = sub_pipeline_func()
        assert sub_pipeline_1._validate().passed
        assert sub_pipeline_1.outputs["data_any_file"].type == "uri_file"

        # confirm that the output won't change in further call
        sub_pipeline_2 = sub_pipeline_func()
        assert sub_pipeline_2.outputs["data_any_file"].type == "uri_file"

        @pipeline()
        def pipeline_func():
            sub_pipeline_func()

        dsl_pipeline: PipelineJob = pipeline_func()
        assert dsl_pipeline._validate().passed
        dsl_pipeline._to_rest_object()
        pipeline_component = dsl_pipeline.jobs["sub_pipeline_func"].component
        assert pipeline_component._to_rest_object().properties.component_spec["outputs"] == {
            "data_any_directory": {"type": "uri_folder"},
            "data_any_file": {"type": "uri_file"},  # AnyFile => uri_file
            "data_azureml_dataset": {"type": "uri_folder"},
            "data_cosmos_structured_stream": {"type": "uri_folder"},
            "data_csv_file": {"type": "uri_folder"},
            "data_data_frame_directory": {"type": "uri_folder"},
            "data_image_directory": {"type": "uri_folder"},
            "data_model_directory": {"type": "uri_folder"},
            "data_path": {"type": "uri_folder"},
            "data_transformation_directory": {"type": "uri_folder"},
            "data_untrained_model_directory": {"type": "uri_folder"},
            "data_zip_file": {"type": "uri_folder"},
        }

    def test_ipp_internal_component_in_pipeline(self):
        yaml_path = "./tests/test_configs/internal/ipp-component/spec.yaml"
        # TODO: support anonymous ipp component creation
        # curated env with name & version
        # command_func: InternalComponent = client.components.get("ls_command", "0.0.1")
        node_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func():
            node_func()

        dsl_pipeline: PipelineJob = pipeline_func()
        result = dsl_pipeline._validate()
        assert result._to_dict() == {"result": "Succeeded"}

    def test_gjd_internal_component_in_pipeline(self):
        yaml_path = "./tests/test_configs/internal/command-component-ls/ls_command_component.yaml"  # GJD is based on CommandComponent
        node_func: CommandComponent = load_component(yaml_path)
        node = node_func()

        ts = TargetSelector(
            compute_type="AMLK8s",  # runsettings.target_selector.compute_type
            instance_types=["STANDARD_D2_V2"],  # runsettings.target_selector.instance_types
            regions=["eastus2euap"],  # runsettings.target_selector.regions
            my_resource_only=True,  # runsettings.target_selector.my_resource_only
            allow_spot_vm=True,  # runsettings.target_selector.allow_spot_vm
        )
        node.resources.properties["target_selector"] = ts

        properties_rest_dict = node._to_rest_object()["resources"]["properties"]
        assert properties_rest_dict == {
            "target_selector": {
                "compute_type": "AMLK8s",
                "instance_types": ["STANDARD_D2_V2"],
                "regions": ["eastus2euap"],
                "my_resource_only": True,
                "allow_spot_vm": True,
            }
        }

    def test_elastic_component_in_pipeline(self):
        yaml_path = "./tests/test_configs/internal/command-component-ls/ls_command_component.yaml"  # itp & elastic are based on CommandComponent
        node_func: CommandComponent = load_component(yaml_path)
        node = node_func()
        configuration = ITPConfiguration(
            resource_configuration=ITPResourceConfiguration(
                gpu_count=2,
                cpu_count=2,
                memory_request_in_gb=2,
            ),
            priority_configuration=ITPPriorityConfiguration(
                job_priority=1,
                is_preemptible=True,
                node_count_set=[1, 2, 3],
                scale_interval=60,
            ),
            interactive_configuration=ITPInteractiveConfiguration(
                is_ssh_enabled=True,
                ssh_public_key="ssh_key",
                is_i_python_enabled=True,
                is_tensor_board_enabled=True,
                interactive_port=40000,
            ),
            retry=ITPRetrySettings(
                max_retry_count=1,
            ),
        )
        node.resources.properties["itp"] = configuration
        properties_rest_dict = node._to_rest_object()["resources"]["properties"]
        assert properties_rest_dict == {
            "itp": {
                "resource_configuration": {
                    "gpu_count": 2,
                    "cpu_count": 2,
                    "memory_request_in_gb": 2,
                },
                "priority_configuration": {
                    "job_priority": 1,
                    "is_preemptible": True,
                    "node_count_set": [1, 2, 3],
                    "scale_interval": 60,
                },
                "interactive_configuration": {
                    "interactive_port": 40000,
                    "is_i_python_enabled": True,
                    "is_ssh_enabled": True,
                    "is_tensor_board_enabled": True,
                    "ssh_public_key": "ssh_key",
                },
                "retry": {
                    "max_retry_count": 1,
                },
            }
        }

    def test_singularity_component_in_pipeline(self):
        yaml_path = "./tests/test_configs/internal/command-component-ls/ls_command_component.yaml"  # singularity is based on CommandComponent
        node_func: CommandComponent = load_component(yaml_path)
        node = node_func()
        configuration = AISuperComputerConfiguration(
            instance_type="STANDARD_D2_V2",
            image_version="1.0",
            locations=["eastus2euap"],
            ai_super_computer_storage_data={
                "data": AISuperComputerStorageReferenceConfiguration(
                    container_name="container_name",
                    relative_path="relative_path",
                )
            },
            interactive=True,
            scale_policy=AISuperComputerScalePolicy(
                auto_scale_instance_type_count_set=[1, 2, 3],
                auto_scale_interval_in_sec=60,
                max_instance_type_count=3,
                min_instance_type_count=1,
            ),
            virtual_cluster_arm_id="virtual_cluster_arm_id",
            tensorboard_log_directory="tensorboard_log_directory",
            ssh_public_key="ssh_public_key",
            enable_azml_int=True,
            priority="Medium",
            sla_tier="Standard",
            suspend_on_idle_time_hours=1,
            user_alias="user_alias",
        )
        # what if key is not in lower case?
        node.resources.properties[JobComputePropertyFields.SINGULARITY.lower()] = configuration
        properties_rest_dict = node._to_rest_object()["resources"]["properties"]
        assert properties_rest_dict == {
            JobComputePropertyFields.AISUPERCOMPUTER: {
                "InstanceType": "STANDARD_D2_V2",
                "ImageVersion": "1.0",
                "Locations": ["eastus2euap"],
                "AISuperComputerStorageData": {
                    "data": {
                        "ContainerName": "container_name",
                        "RelativePath": "relative_path",
                    }
                },
                "Interactive": True,
                "ScalePolicy": {
                    "AutoScaleInstanceTypeCountSet": [1, 2, 3],
                    "AutoScaleIntervalInSec": 60,
                    "MaxInstanceTypeCount": 3,
                    "MinInstanceTypeCount": 1,
                },
                "VirtualClusterArmId": "virtual_cluster_arm_id",
                "TensorboardLogDirectory": "tensorboard_log_directory",
                "SSHPublicKey": "ssh_public_key",
                "EnableAzmlInt": True,
                "Priority": "Medium",
                "SLATier": "Standard",
                "SuspendOnIdleTimeHours": 1,
                "UserAlias": "user_alias",
            }
        }

    def test_load_pipeline_job_with_internal_components_as_node(self):
        yaml_path = Path("./tests/test_configs/internal/helloworld/helloworld_component_scope.yml")
        scope_internal_func = load_component(source=yaml_path)
        with open(yaml_path, encoding="utf-8") as yaml_file:
            yaml_dict = yaml.safe_load(yaml_file)

        yaml_dict["code"] = parse_local_path(yaml_dict["code"], scope_internal_func.base_path)

        command_func = load_component("./tests/test_configs/components/helloworld_component.yml")

        @pipeline()
        def pipeline_func():
            node = command_func(component_in_path=Input(path="./tests/test_configs/data"))
            node.compute = "cpu-cluster"

            node_internal: Scope = scope_internal_func(
                TextData=Input(type=AssetTypes.MLTABLE, path="azureml:scope_tsv:1"),
                ExtractionClause="column1:string, column2:int",
            )

            node_internal.priority = 800
            node_internal.adla_account_name = "adla_account_name"
            node_internal.scope_param = "-tokens 50"
            node_internal.custom_job_name_suffix = "component_sdk_test"
            node_internal.properties["AZURE_ML_PathOnCompute_mock_output"] = "mock_path"

        dsl_pipeline: PipelineJob = pipeline_func()
        internal_node_name = "node_internal"
        assert dsl_pipeline.jobs[internal_node_name]._component._to_dict() == yaml_dict

        scope_node: InternalBaseNode = dsl_pipeline.jobs[internal_node_name]
        # TODO: check why need to set base path manually
        scope_node._set_base_path(yaml_path.parent)
        scope_node_dict = scope_node._to_dict()
        assert scope_node_dict == {
            "priority": 800,
            "adla_account_name": "adla_account_name",
            "custom_job_name_suffix": "component_sdk_test",
            "scope_param": "-tokens 50",
            "component": yaml_dict,
            "type": "ScopeComponent",
            "inputs": {
                "ExtractionClause": "column1:string, column2:int",
                "TextData": {"path": "azureml:scope_tsv:1", "type": "mltable"},
            },
            "properties": {"AZURE_ML_PathOnCompute_mock_output": "mock_path"},
        }
        assert pydash.omit(scope_node._to_rest_object(), "componentId") == {
            "_source": "YAML.COMPONENT",
            "priority": 800,
            "adla_account_name": "adla_account_name",
            "custom_job_name_suffix": "component_sdk_test",
            "scope_param": "-tokens 50",
            "inputs": {
                "ExtractionClause": {"job_input_type": "literal", "value": "column1:string, column2:int"},
                "TextData": {"job_input_type": "mltable", "uri": "azureml:scope_tsv:1"},
            },
            "type": "ScopeComponent",
            "properties": {"AZURE_ML_PathOnCompute_mock_output": "mock_path"},
        }
        scope_node._validate(raise_error=True)

        omit_fields = ["jobs.node.component", "jobs.node_internal.component"]
        assert pydash.omit(dsl_pipeline._to_dict(), *omit_fields) == pydash.omit(
            {
                "display_name": "pipeline_func",
                "jobs": {"node": dsl_pipeline.jobs["node"]._to_dict(), "node_internal": scope_node._to_dict()},
                "type": "pipeline",
            },
            *omit_fields,
        )

        dsl_pipeline._validate(raise_error=True)

        rest_object = dsl_pipeline._to_rest_object()
        assert rest_object.properties.jobs == {
            "node": dsl_pipeline.jobs["node"]._to_rest_object(),
            "node_internal": scope_node._to_rest_object(),
        }

    def test_components_in_registry(self):
        command_func = load_component("./tests/test_configs/components/helloworld_component.yml")
        registry_code_id = "azureml://feeds/testFeed/codes/hello_component/versions/0.0.1"

        @pipeline()
        def pipeline_func():
            node = command_func(component_in_path=Input(path="./tests/test_configs/data"))

            # can't create a component from azureml-components in ci workspace
            # so just use a local test
            node._component.code = registry_code_id
            node.compute = "cpu-cluster"

        dsl_pipeline: PipelineJob = pipeline_func()
        assert dsl_pipeline._validate().passed
        regenerated_pipeline_job = PipelineJob._from_rest_object(dsl_pipeline._to_rest_object())
        assert dsl_pipeline._to_dict() == regenerated_pipeline_job._to_dict()

    def test_components_input_output(self):
        yaml_path = "./tests/test_configs/internal/component_with_input_outputs/component_spec.yaml"
        component: InternalComponent = load_component(yaml_path)

        fake_input = Input(type=AssetTypes.MLTABLE, path="azureml:scope_tsv:1")
        inputs = {
            "data_path": fake_input,
            "data_azureml_dataset": fake_input,
            "data_any_directory": fake_input,
            "data_any_file": fake_input,
            "data_zip_file": fake_input,
            "data_csv_file": fake_input,
            "data_transformation_directory": fake_input,
            "data_untrained_model_directory": fake_input,
            "data_image_directory": fake_input,
            "data_model_directory": fake_input,
            "data_data_frame_directory": fake_input,
            "data_cosmos_structured_stream": fake_input,
            "param_string": "xxx",
            "param_string_cap": "xxx",
            "param_int": 1,
            "param_int_cap": 1,
            "param_float": 1.0,
            "param_float_cap": 1.0,
            "param_bool": True,
            "param_bool_cap": False,
            "param_enum": "minimal",
            "param_enum_cap": "reuse",
        }

        @pipeline()
        def pipeline_func():
            node = component(
                **inputs,
            )
            node.adla_account_name = "adla_account_name"

        pipeline_job = pipeline_func()
        assert pipeline_job._validate().passed, pipeline_job._validate()
        rest_obj = pipeline_job._to_rest_object()
        expected_inputs = {
            "param_bool": {"job_input_type": "literal", "value": "True"},
            "param_bool_cap": {"job_input_type": "literal", "value": "False"},
            "param_enum": {"job_input_type": "literal", "value": "minimal"},
            "param_enum_cap": {"job_input_type": "literal", "value": "reuse"},
            "param_float": {"job_input_type": "literal", "value": "1.0"},
            "param_float_cap": {"job_input_type": "literal", "value": "1.0"},
            "param_int": {"job_input_type": "literal", "value": "1"},
            "param_int_cap": {"job_input_type": "literal", "value": "1"},
            "param_string": {"job_input_type": "literal", "value": "xxx"},
            "param_string_cap": {"job_input_type": "literal", "value": "xxx"},
        }
        for key in inputs:
            if key.startswith("data_"):
                expected_inputs[key] = {"job_input_type": "mltable", "uri": "azureml:scope_tsv:1"}
        assert rest_obj.properties.jobs["node"]["inputs"] == expected_inputs

    def test_data_binding_on_node_runsettings(self):
        test_path = "./tests/test_configs/internal/helloworld/helloworld_component_command.yml"
        component: InternalComponent = load_component(test_path)

        @pipeline()
        def pipeline_func(
            compute_name: str = "cpu-cluster", environment_name: str = "AzureML-ACPT-pytorch-1.12-py39-cuda11.6-gpu:8"
        ):
            node = component(
                training_data=Input(path="./tests/test_configs/data"),
                max_epochs=1,
            )
            node.compute = compute_name
            node.environment = environment_name

        pipeline_job = pipeline_func()
        assert pipeline_job._validate().passed, repr(pipeline_job._validate())
        rest_object = pipeline_job._to_rest_object().properties.jobs["node"]
        assert str(rest_object["computeId"]) == "${{parent.inputs.compute_name}}"
        assert str(rest_object["environment"]) == "${{parent.inputs.environment_name}}"

    def test_pipeline_with_setting_node_output_directly(self) -> None:
        component_dir = Path(__file__).parent.parent.parent / "test_configs" / "internal" / "command-component"
        copy_func = load_component(component_dir / "command-linux/copy/component.yaml")

        copy_file = copy_func(
            input_dir=None,
            file_names=None,
        )

        copy_file.outputs.output_dir.path = "path_on_datastore"
        assert copy_file.outputs.output_dir.path == "path_on_datastore"
        assert copy_file.outputs.output_dir.type == "path"

    def test_job_properties(self):
        pipeline_job: PipelineJob = load_job(
            source="./tests/test_configs/internal/pipeline_jobs/pipeline_job_with_properties.yml"
        )
        pipeline_dict = pipeline_job._to_dict()
        rest_pipeline_dict = pipeline_job._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["properties"] == {"AZURE_ML_PathOnCompute_input_data": "/tmp/test"}
        assert rest_pipeline_dict["properties"] == pipeline_dict["properties"]
        for name, node_dict in pipeline_dict["jobs"].items():
            rest_node_dict = rest_pipeline_dict["jobs"][name]
            assert len(node_dict["properties"]) == 1
            assert "AZURE_ML_PathOnCompute_" in list(node_dict["properties"].keys())[0]
            assert node_dict["properties"] == rest_node_dict["properties"]

    @pytest.mark.parametrize(
        "component_path, fields_to_test, fake_inputs",
        [
            pytest.param(
                "./tests/test_configs/internal/command-component-ls/ls_command_component.yaml",
                {
                    "resources.instance_count": JobResourceConfiguration(instance_count=1),
                    "limits.timeout": CommandJobLimits(timeout=100),
                },
                {},
                id="command",
            ),
            pytest.param(
                "./tests/test_configs/internal/batch_inference/batch_score.yaml",
                {
                    "resources.instance_count": JobResourceConfiguration(instance_count=1),
                    "limits.timeout": CommandJobLimits(timeout=100),
                },
                {
                    "model_path": Input(type=AssetTypes.MLTABLE, path="mltable_mnist_model@latest"),
                    "images_to_score": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest"),
                },
                id="parallel.resources",
            ),
            pytest.param(
                "tests/test_configs/internal/spark-component/spec.yaml",
                {
                    "resources.runtime_version": SparkResourceConfiguration(runtime_version="2.4"),
                },
                {
                    "file_input1": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest", mode="direct"),
                    "file_input2": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest", mode="direct"),
                },
                id="spark",
            ),
        ],
    )
    def test_data_binding_expression_on_node_runsettings(
        self, component_path: str, fields_to_test: Dict[str, Any], fake_inputs: Dict[str, Input]
    ):
        component = load_component(component_path)

        @pipeline()
        def pipeline_func(param: str = "2"):
            node = component(**fake_inputs)
            for field, value in fields_to_test.items():
                attr, sub_attr = field.split(".")
                setattr(node, attr, value)
                setattr(getattr(node, attr), sub_attr, str(param))

        pipeline_job: PipelineJob = pipeline_func()
        rest_object = pipeline_job._to_rest_object()
        regenerated_job = PipelineJob._from_rest_object(rest_object)
        expected_dict, actual_dict = pipeline_job._to_dict(), regenerated_job._to_dict()

        assert actual_dict == expected_dict

        # directly update component to arm id
        for _node in pipeline_job.jobs.values():
            _node._component = (
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/"
                "Microsoft.MachineLearningServices/workspaces/ws/components/component_name/"
                "versions/1.0.0"
            )
        # check if all the fields are correctly serialized
        pipeline_job.component._get_anonymous_hash()

    def test_node_output_type_promotion(self):
        test_path = "./tests/test_configs/internal/helloworld/helloworld_component_command.yml"
        component: InternalComponent = load_component(test_path)

        @pipeline()
        def pipeline_func():
            node = component(
                training_data=Input(path="./tests/test_configs/data"),
                max_epochs=1,
            )
            node.outputs.model_output.mode = "mount"
            return node.outputs

        pipeline_job = pipeline_func()
        pipeline_dict = pipeline_job._to_rest_object().as_dict()
        # type will be preserved & mode will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["model_output"] == {
            "job_output_type": "uri_folder",
            "mode": "ReadWriteMount",
        }
