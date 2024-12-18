import logging
import os
from io import StringIO
from pathlib import Path
from typing import Any, Dict
from unittest import mock
from unittest.mock import patch

import pydash
import pytest
from test_configs.dsl_pipeline import data_binding_expression
from test_utilities.utils import assert_job_cancel, omit_with_wildcard, prepare_dsl_curated

from azure.ai.ml import (
    AmlTokenConfiguration,
    Input,
    ManagedIdentityConfiguration,
    MLClient,
    MpiDistribution,
    Output,
    UserIdentityConfiguration,
    command,
    dsl,
    load_component,
    load_job,
)
from azure.ai.ml._restclient.v2022_05_01.models import ComponentContainerData, ComponentContainerDetails, SystemData
from azure.ai.ml.constants._common import (
    AZUREML_PRIVATE_FEATURES_ENV_VAR,
    AZUREML_RESOURCE_PROVIDER,
    NAMED_RESOURCE_ID_FORMAT,
    VERSIONED_RESOURCE_ID_FORMAT,
    AssetTypes,
    AzureMLResourceType,
    InputOutputModes,
)
from azure.ai.ml.constants._job import PipelineConstants
from azure.ai.ml.entities import (
    Component,
    Data,
    JobResourceConfiguration,
    PipelineJob,
    QueueSettings,
    SparkResourceConfiguration,
)
from azure.ai.ml.entities._builders import Command, DataTransferCopy, Spark
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function
from azure.ai.ml.exceptions import (
    MultipleValueError,
    ParamValueNotExistsError,
    UnsupportedParameterKindError,
    UserErrorException,
    ValidationException,
)

from .._util import _DSL_TIMEOUT_SECOND, get_predecessors

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.usefixtures("enable_pipeline_private_preview_features", "enable_private_preview_schema_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestDSLPipeline:
    def test_dsl_pipeline(self) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline_no_arg():
            component_func = load_component(source=path)
            component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline1 = pipeline_no_arg()
        assert len(pipeline1.component.jobs) == 1, pipeline1.component.jobs

    def test_dsl_pipeline_name_and_display_name(self):
        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @dsl.pipeline()
        def sample_pipeline_with_no_annotation():
            hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline = sample_pipeline_with_no_annotation()
        assert pipeline.component.name == "sample_pipeline_with_no_annotation"
        assert pipeline.component.display_name == pipeline.component.name
        assert pipeline.name is None
        assert pipeline.display_name == pipeline.component.display_name

        @dsl.pipeline(name="hello_world_component")
        def sample_pipeline_with_name():
            hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline = sample_pipeline_with_name()
        assert pipeline.component.name == "hello_world_component"
        assert pipeline.component.display_name == pipeline.component.name
        assert pipeline.name is None
        assert pipeline.display_name == pipeline.component.display_name

        @dsl.pipeline(display_name="my_component")
        def sample_pipeline_with_display_name():
            hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline = sample_pipeline_with_display_name()
        assert pipeline.component.name == "sample_pipeline_with_display_name"
        assert pipeline.component.display_name == "my_component"
        assert pipeline.name is None
        assert pipeline.display_name == pipeline.component.display_name

        @dsl.pipeline(name="hello_world_component", display_name="my_component")
        def sample_pipeline_with_name_and_display_name():
            hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline = sample_pipeline_with_name_and_display_name()
        assert pipeline.component.name == "hello_world_component"
        assert pipeline.component.display_name == "my_component"
        assert pipeline.name is None
        assert pipeline.display_name == pipeline.component.display_name

    def test_dsl_pipeline_description(self):
        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @dsl.pipeline()
        def sample_pipeline():
            hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline = sample_pipeline()
        assert pipeline.component.description is None
        assert pipeline.description == pipeline.component.description

        @dsl.pipeline()
        def sample_pipeline_with_docstring():
            """Docstring for sample pipeline"""
            hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline = sample_pipeline_with_docstring()
        assert pipeline.component.description == "Docstring for sample pipeline"
        assert pipeline.description == pipeline.component.description

        @dsl.pipeline(description="Top description for sample pipeline")
        def sample_pipeline_with_description_and_docstring():
            """Docstring for sample pipeline"""
            hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline = sample_pipeline_with_description_and_docstring()
        assert pipeline.component.description == "Top description for sample pipeline"
        assert pipeline.description == pipeline.component.description

        @dsl.pipeline()
        def sample_pipeline_with_detailed_docstring(job_in_path, job_in_number):
            """A pipeline with detailed docstring, including descriptions for inputs and outputs.

            In this pipeline docstring, there are descriptions for inputs and outputs, via pipeline decorator,
            Input/Output descriptions can infer from these descriptions.

            Args:
                job_in_path: a path parameter
                              with multi-line description
                job_in_number (float): a number parameter
                job_out_path: a path output

            Other docstring xxxxxx
                random_key: random_value
            """
            node = hello_world_component_func(component_in_path=job_in_path, component_in_number=job_in_number)
            return {"job_out_path": node.outputs.component_out_path}

        pipeline = sample_pipeline_with_detailed_docstring(Input(path="/a/path/on/ds"), 1)
        assert pipeline.component.description.startswith("A pipeline with detailed docstring")
        assert pipeline.component.inputs["job_in_path"]["description"] == "a path parameter with multi-line description"
        assert pipeline.component.inputs["job_in_number"]["description"] == "a number parameter"
        assert pipeline.component.outputs["job_out_path"].description == "a path output"
        assert pipeline.description == pipeline.component.description

    def test_dsl_pipeline_comment(self) -> None:
        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @dsl.pipeline
        def sample_pipeline_with_comment():
            node = hello_world_component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)
            node.comment = "arbitrary string"

        pipeline = sample_pipeline_with_comment()
        assert pipeline.jobs["node"].comment == "arbitrary string"

    def test_dsl_pipeline_input_output(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(number, path):
            component_func = load_component(source=yaml_file)
            node1 = component_func(component_in_number=number, component_in_path=path)
            return {"pipeline_output": node1.outputs.component_out_path}

        pipeline1 = pipeline(10, Input(path="/a/path/on/ds"))

        assert pipeline1._build_inputs().keys() == {"number", "path"}

        # un-configured output will have type of bounded node output
        assert pipeline1._build_outputs() == {"pipeline_output": Output(type="uri_folder")}

        # after setting mode, default output with type Input is built
        pipeline1.outputs.pipeline_output.mode = "download"
        assert pipeline1._build_outputs()["pipeline_output"].mode == "download"

        component_nodes = list(pipeline1.jobs.values())
        assert len(component_nodes) == 1
        component_node = component_nodes[0]

        assert component_node._build_inputs() == {
            "component_in_number": Input(path="${{parent.inputs.number}}", type="uri_folder", mode=None),
            "component_in_path": Input(path="${{parent.inputs.path}}", type="uri_folder", mode=None),
        }
        assert component_node._build_outputs() == {
            "component_out_path": Output(path="${{parent.outputs.pipeline_output}}", type="uri_folder", mode=None)
        }

        # Test Input as pipeline input
        pipeline2 = pipeline(8, Input(path="/a/path/on/ds"))
        assert pipeline2._build_inputs().keys() == {"number", "path"}

        component_nodes = list(pipeline2.jobs.values())
        assert len(component_nodes) == 1
        component_node = component_nodes[0]

        assert component_node._build_inputs() == {
            "component_in_number": Input(path="${{parent.inputs.number}}", type="uri_folder", mode=None),
            "component_in_path": Input(path="${{parent.inputs.path}}", type="uri_folder", mode=None),
        }

    @pytest.mark.parametrize("output_type", ["uri_file", "mltable", "mlflow_model", "triton_model", "custom_model"])
    def test_dsl_pipeline_output_type(self, output_type):
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(number, path):
            component_func = load_component(
                source=yaml_file, params_override=[{"outputs.component_out_path.type": output_type}]
            )
            node1 = component_func(component_in_number=number, component_in_path=path)
            return {"pipeline_output": node1.outputs.component_out_path}

        pipeline1 = pipeline(10, Input(path="/a/path/on/ds"))
        # un-configured output will have type of bound output
        assert pipeline1._build_outputs() == {"pipeline_output": Output(type=output_type)}

    def test_dsl_pipeline_complex_input_output(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component_multiple_data.yml"

        @dsl.pipeline()
        def pipeline(
            job_in_data_name_version_def_mode,
            job_in_data_name_version_mode_mount,
            job_in_data_name_version_mode_download,
            job_in_data_by_name,
            job_in_data_by_armid,
            job_in_data_by_store_path,
            job_in_data_by_path_default_store,
            job_in_data_by_store_path_and_mount,
            job_in_data_by_store_path_and_download,
            job_in_data_by_blob_dir,
            job_in_data_by_blob_file,
            job_in_data_local_dir,
            job_in_data_local_file,
            job_in_data_local_yaml_definition,
            job_in_data_uri,
        ):
            component_func = load_component(source=yaml_file)
            multiple_data_component = component_func(
                component_in_1=job_in_data_name_version_def_mode,
                component_in_2=job_in_data_name_version_mode_mount,
                component_in_3=job_in_data_name_version_mode_download,
                component_in_4=job_in_data_by_name,
                component_in_5=job_in_data_by_armid,
                component_in_6=job_in_data_by_store_path,
                component_in_7=job_in_data_by_path_default_store,
                component_in_8=job_in_data_by_store_path_and_mount,
                component_in_9=job_in_data_by_store_path_and_download,
                component_in_10=job_in_data_by_blob_dir,
                component_in_11=job_in_data_by_blob_file,
                component_in_12=job_in_data_local_dir,
                component_in_13=job_in_data_local_file,
                component_in_14=job_in_data_local_yaml_definition,
                component_in_15=job_in_data_uri,
            )
            multiple_data_component.outputs.component_out_9.mode = "upload"
            return {
                "job_in_data_name": multiple_data_component.outputs.component_out_1,
                "job_in_data_name_upload": multiple_data_component.outputs.component_out_2,
                "job_in_data_name_mount": multiple_data_component.outputs.component_out_3,
                "job_out_data_name_apart": multiple_data_component.outputs.component_out_4,
                "job_out_data_path": multiple_data_component.outputs.component_out_5,
                "job_out_data_store_path_upload": multiple_data_component.outputs.component_out_6,
                "job_out_data_store_path_mount": multiple_data_component.outputs.component_out_7,
                "job_out_data_store_url": multiple_data_component.outputs.component_out_8,
            }

        job_yaml = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_data_options.yml"
        pipeline_job: PipelineJob = load_job(source=job_yaml)

        pipeline = pipeline(**{key: val for key, val in pipeline_job._build_inputs().items()})
        pipeline.inputs.job_in_data_by_store_path_and_mount.mode = "ro_mount"
        pipeline.inputs.job_in_data_by_store_path_and_download.mode = "download"
        pipeline.inputs.job_in_data_name_version_mode_download.mode = "download"
        assert pipeline_job._build_inputs() == pipeline._build_inputs()

        pipeline.outputs.job_in_data_name.mode = "upload"
        pipeline.outputs.job_in_data_name_upload.mode = "upload"
        pipeline.outputs.job_out_data_name_apart.mode = "upload"
        pipeline.outputs.job_out_data_path.mode = "upload"
        pipeline.outputs.job_out_data_store_path_upload.mode = "upload"
        pipeline.outputs.job_out_data_store_url.mode = "upload"
        pipeline.outputs.job_in_data_name_mount.mode = "mount"
        pipeline.outputs.job_out_data_store_path_mount.mode = "mount"

        actual_outputs = pipeline._build_outputs()
        for k, v in actual_outputs.items():
            v.mode = v.mode.lower()
            # outputs defined in yaml are all uri_folder, while its default value in dsl is None
            v.type = "uri_folder"
        assert pipeline_job._build_outputs() == actual_outputs

        component_job = next(iter(pipeline_job.jobs.values()))._to_rest_object()
        component = next(iter(pipeline.jobs.values()))._to_rest_object()

        omit_fields = ["componentId", "_source"]
        actual_component = pydash.omit(component_job, *omit_fields)
        expected_component = pydash.omit(component, *omit_fields)
        assert actual_component == expected_component

    def test_dsl_pipeline_to_job(self) -> None:
        component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(source=component_yaml)

        @dsl.pipeline(
            name="simplepipelinejob",
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name="my_first_experiment",
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            hello_world_component = component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            hello_world_component.compute = "cpu-cluster"
            hello_world_component._component._id = "microsoftsamplesCommandComponentBasic_second:1"

            hello_world_component_2 = component_func(
                component_in_number=job_in_other_number, component_in_path=job_in_path
            )
            hello_world_component_2._component._id = "microsoftsamplesCommandComponentBasic_second:1"
            hello_world_component_2.compute = "cpu-cluster"

        pipeline = pipeline(10, 15, Input(path="./tests/test_configs/data"))
        pipeline.inputs.job_in_path.mode = "mount"

        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()

        job_yaml = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml"
        pipeline_job_dict = load_job(source=job_yaml)._to_rest_object().as_dict()

        omit_fields = [
            "name",
            "properties.display_name",
            "properties.inputs.job_in_path.uri",
            "properties.settings",
            "properties.jobs.*._source",
        ]
        dsl_pipeline_job_dict = omit_with_wildcard(dsl_pipeline_job_dict, *omit_fields)
        pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert dsl_pipeline_job_dict == pipeline_job_dict

    def test_dsl_pipeline_with_settings_and_overrides(self):
        component_yaml = "./tests/test_configs/components/helloworld_component_no_paths.yml"
        component_func = load_component(source=component_yaml)

        @dsl.pipeline(
            name="simplepipelinejobnopath",
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name="my_first_experiment",
            continue_on_step_failure=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_string):
            hello_world_component = component_func(component_in_number=job_in_number)
            hello_world_component.compute = "cpu-cluster"
            hello_world_component._component._id = "microsoftsamplescommandcomponentbasic_nopaths_test:1"

            hello_world_component_2 = component_func(component_in_number=job_in_other_number)
            hello_world_component_2._component._id = "microsoftsamplescommandcomponentbasic_nopaths_test:1"
            hello_world_component_2.compute = "cpu-cluster"
            # set overrides for component job
            hello_world_component_2.resources = JobResourceConfiguration()
            hello_world_component_2.resources.instance_count = 2
            hello_world_component_2.resources.properties = {"prop1": "a_prop", "prop2": "another_prop"}
            hello_world_component_2.distribution = MpiDistribution()
            hello_world_component_2.distribution.process_count_per_instance = 2
            hello_world_component_2.additional_override.nested_override = 5
            hello_world_component_2.environment_variables["FOO"] = "bar"

        pipeline = pipeline(10, 15, "a_random_string")
        # set experiment name and settings when submit
        pipeline_job = pipeline

        dsl_pipeline_job_dict = pipeline_job._to_rest_object().as_dict()

        job_yaml = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_no_paths.yml"
        pipeline_job_dict = load_job(source=job_yaml)._to_rest_object().as_dict()

        omit_fields = ["name", "properties.display_name", "properties.jobs.*._source", "properties.settings._source"]
        dsl_pipeline_job = omit_with_wildcard(dsl_pipeline_job_dict, *omit_fields)
        yaml_pipeline_job = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert dsl_pipeline_job == yaml_pipeline_job

    def test_pipeline_variable_name(self):
        component_yaml = "./tests/test_configs/components/helloworld_component_no_paths.yml"
        component_func1 = load_component(source=component_yaml)
        component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        component_func2 = load_component(source=component_yaml)

        @dsl.pipeline(name="pipeline_with_default_node_name")
        def pipeline_with_default_node_name():
            component_func1(component_in_number=1)
            component_func1(component_in_number=1)
            component_func2(component_in_number=1, component_in_path=Input(path="./tests/test_configs/data"))
            component_func2(component_in_number=1, component_in_path=Input(path="./tests/test_configs/data"))

        pipeline = pipeline_with_default_node_name()
        variable_names = list(pipeline.component.jobs.keys())
        pipeline_job_names = list(pipeline.jobs.keys())
        assert len(variable_names) == 4
        assert variable_names == pipeline_job_names
        assert variable_names == [
            "microsoftsamplescommandcomponentbasic_nopaths_test",
            "microsoftsamplescommandcomponentbasic_nopaths_test_1",
            "microsoftsamples_command_component_basic",
            "microsoftsamples_command_component_basic_1",
        ]

        @dsl.pipeline(name="pipeline_with_for_loop_nodes")
        def pipeline_with_for_loop_nodes():
            for i in range(3):
                for_loop_node = component_func1()
                for_loop_node.compute = "cpu-cluster"
            component_func1()

        pipeline = pipeline_with_for_loop_nodes()
        variable_names = list(pipeline.component.jobs.keys())
        pipeline_job_names = list(pipeline.jobs.keys())
        assert len(variable_names) == 4
        assert variable_names == pipeline_job_names
        # Last node in loop has exact variable name, others have suffix
        assert variable_names == [
            "for_loop_node_1",
            "for_loop_node_2",
            "for_loop_node",
            "for_loop_node_3",
        ]

        @dsl.pipeline(name="pipeline_with_user_defined_nodes_1")
        def pipeline_with_user_defined_nodes_1():
            for i in range(2):
                for_loop_node = component_func1()
                for_loop_node.name = f"dummy_{i}"
            node = component_func1()
            node.name = "another"
            node_1 = component_func1()
            node_1.name = "my_node_1"
            node_2 = component_func1()
            node_2.name = "_my_node"

        pipeline = pipeline_with_user_defined_nodes_1()
        variable_names = list(pipeline.component.jobs.keys())
        pipeline_job_names = list(pipeline.jobs.keys())
        assert len(variable_names) == 5
        assert variable_names == pipeline_job_names
        assert variable_names == [
            "dummy_0",
            "dummy_1",
            "another",
            "my_node_1",
            "_my_node",
        ]

        @dsl.pipeline(name="pipeline_with_user_defined_nodes_2")
        def pipeline_with_user_defined_nodes_2():
            component_func1()
            for i in range(2):
                for_loop_node = component_func1()
                for_loop_node.name = f"dummy_{i}"
            component_func1()
            node_1 = component_func1()
            node_1.name = "my_node"
            component_func1()

        pipeline = pipeline_with_user_defined_nodes_2()
        variable_names = list(pipeline.component.jobs.keys())
        pipeline_job_names = list(pipeline.jobs.keys())
        assert len(variable_names) == 6
        assert variable_names == pipeline_job_names
        assert variable_names == [
            "microsoftsamplescommandcomponentbasic_nopaths_test",
            "dummy_0",
            "dummy_1",
            "microsoftsamplescommandcomponentbasic_nopaths_test_1",
            "my_node",
            "microsoftsamplescommandcomponentbasic_nopaths_test_2",
        ]

        @dsl.pipeline(name="pipeline_with_user_defined_nodes_3")
        def pipeline_with_user_defined_nodes_3():
            node1 = component_func1()
            node1.name = "my_node"
            node2 = node1

        pipeline = pipeline_with_user_defined_nodes_3()
        variable_names = list(pipeline.component.jobs.keys())
        pipeline_job_names = list(pipeline.jobs.keys())
        assert variable_names == pipeline_job_names
        assert variable_names == ["my_node"]

        @dsl.pipeline(name="pipeline_with_duplicate_user_defined_nodes_1")
        def pipeline_with_duplicate_user_defined_nodes_1():
            node1 = component_func1()
            node1.compute = "cpu-cluster"
            node2 = component_func1()
            node2.name = "node1"

        with pytest.raises(UserErrorException, match="Duplicate node name found"):
            pipeline_with_duplicate_user_defined_nodes_1()

        # Duplicate check is case-insensitive

        @dsl.pipeline(name="pipeline_with_duplicate_user_defined_nodes_2")
        def pipeline_with_duplicate_user_defined_nodes_2():
            node1 = component_func1()
            node1.compute = "cpu-cluster"
            node2 = component_func1()
            node2.name = "Node1"

        with pytest.raises(UserErrorException, match="Duplicate node name found"):
            pipeline_with_duplicate_user_defined_nodes_2()

        # Node name must be 1-255 characters, start with a letter or underscore,
        # and can only contain letters, numbers, underscores
        @dsl.pipeline(name="pipeline_with_invalid_user_defined_nodes_1")
        def pipeline_with_invalid_user_defined_nodes_1():
            node = component_func1()
            node.name = "my_node 1"

        with pytest.raises(UserErrorException, match="Invalid node name found"):
            pipeline_with_invalid_user_defined_nodes_1()

        @dsl.pipeline(name="pipeline_with_invalid_user_defined_nodes_2")
        def pipeline_with_invalid_user_defined_nodes_2():
            node = component_func1()
            node.name = "1_my_node"

        with pytest.raises(UserErrorException, match="Invalid node name found"):
            pipeline_with_invalid_user_defined_nodes_2()

        @dsl.pipeline(name="pipeline_with_invalid_user_defined_nodes_3")
        def pipeline_with_invalid_user_defined_nodes_3():
            node = component_func1()
            node.name = "β"

        with pytest.raises(UserErrorException, match="Invalid node name found"):
            pipeline_with_invalid_user_defined_nodes_3()

    def test_pipeline_variable_name_uppercase(self):
        component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(
            source=component_yaml,
        )

        @dsl.pipeline(name="pipeline_with_uppercase_node_names")
        def pipeline_with_user_defined_nodes_1():
            for i in range(2):
                node1 = component_func(component_in_path=Input(path="fake_input"))
                # change node name to lower when setting it to avoid upper case in nxt_input's binding
                node1.name = f"Dummy_{i}"
                nxt_input = Input(
                    path=node1.outputs.component_out_path,
                    mode=InputOutputModes.DIRECT,
                )
                node2 = component_func(component_in_path=nxt_input)
                node2.name = f"Another_{i}"

        pipeline_job = pipeline_with_user_defined_nodes_1()
        rest_pipeline_job = pipeline_job._to_rest_object().as_dict()
        assert rest_pipeline_job["properties"]["jobs"]["another_0"]["inputs"]["component_in_path"] == {
            "job_input_type": "literal",
            "mode": "Direct",
            "value": "${{parent.jobs.dummy_0.outputs.component_out_path}}",
        }
        assert rest_pipeline_job["properties"]["jobs"]["another_1"]["inputs"]["component_in_path"] == {
            "job_input_type": "literal",
            "mode": "Direct",
            "value": "${{parent.jobs.dummy_1.outputs.component_out_path}}",
        }

    def test_connect_components_in_pipeline(self):
        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component_with_input_and_output.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        merge_outputs_component_yaml = "./tests/test_configs/components/merge_outputs_component.yml"
        merge_outputs_component_func = load_component(source=merge_outputs_component_yaml)

        @dsl.pipeline(
            name="simplePipelineJobWithComponentOutput",
            description="The hello world pipeline job with component output",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            default_datastore="workspaceblobstore",
        )
        def pipeline(job_in_number, job_in_path):
            hello_world_component_1 = hello_world_component_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )
            hello_world_component_2 = hello_world_component_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )

            # configure component outputs
            hello_world_component_1.outputs.component_out_path_1.mode = "Mount"
            hello_world_component_2.outputs.component_out_path_1.mode = "Mount"

            merge_component_outputs = merge_outputs_component_func(
                component_in_number=job_in_number,
                component_in_path_1=hello_world_component_1.outputs.component_out_path_1,
                component_in_path_2=hello_world_component_2.outputs.component_out_path_1,
            )

            # configure component compute(not necessary)
            hello_world_component_1.compute = "cpu-cluster"
            hello_world_component_2.compute = "cpu-cluster"
            merge_component_outputs.compute = "cpu-cluster"

            return {
                "job_out_path_1": merge_component_outputs.outputs.component_out_path_1,
                "job_out_path_2": merge_component_outputs.outputs.component_out_path_2,
            }

        pipeline = pipeline(10, Input(path="./tests/test_configs/data", mode="ro_mount"))
        pipeline.outputs.job_out_path_1.mode = "mount"
        pipeline.outputs.job_out_path_2.mode = "Upload"
        dsl_pipeline_job = pipeline._to_rest_object().as_dict()

        yaml_job_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_component_output.yml"
        yaml_pipeline_job = (
            load_job(
                yaml_job_path,
                params_override=[
                    {"jobs.hello_world_component_1.inputs.component_in_path": "${{parent.inputs.job_in_path}}"},
                    {"jobs.hello_world_component_2.inputs.component_in_path": "${{parent.inputs.job_in_path}}"},
                ],
            )
            ._to_rest_object()
            .as_dict()
        )

        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_world_component_1.componentId",
            "properties.jobs.hello_world_component_2.componentId",
            "properties.jobs.merge_component_outputs.componentId",
            "properties.jobs.*._source",
            "properties.inputs.job_in_path.uri",
            "properties.settings",
        ]
        dsl_pipeline_job = omit_with_wildcard(dsl_pipeline_job, *omit_fields)
        yaml_pipeline_job = omit_with_wildcard(yaml_pipeline_job, *omit_fields)
        assert dsl_pipeline_job == yaml_pipeline_job

    def test_same_pipeline_via_dsl_or_curated_sdk(self):
        hello_world_component_yaml_path = "./tests/test_configs/components/helloworld_component.yml"
        merge_outputs_component_yaml_path = "./tests/test_configs/components/merge_outputs_component.yml"

        # Define pipeline job via curated SDK YAML
        pipeline_job_from_yaml = load_job(source="./tests/test_configs/pipeline_jobs/sample_pipeline_job.yml")

        # Define pipeline job via curated SDK code
        pipeline_job = PipelineJob(
            name="SimplePipelineJob",
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            inputs={
                "job_in_number": 10,
                "job_in_other_number": 15,
                "job_in_path": Input(path="./tests/test_configs/data"),
            },
            outputs={
                "job_out_data_1": Output(mode="mount"),
                "job_out_data_2": Output(mode="upload"),
            },
            jobs={
                "hello_world_component_1": Command(
                    component=load_component(source=hello_world_component_yaml_path),
                    name="hello_world_component_1",
                    compute="cpu-cluster",
                    inputs={
                        "component_in_number": "${{parent.inputs.job_in_number}}",
                        "component_in_path": "${{parent.inputs.job_in_path}}",
                    },
                    outputs={"component_out_path": Output(mode="upload")},
                ),
                "hello_world_component_2": Command(
                    component=load_component(source=hello_world_component_yaml_path),
                    name="hello_world_component_2",
                    compute="cpu-cluster",
                    inputs={
                        "component_in_number": "${{parent.inputs.job_in_number}}",
                        "component_in_path": "${{parent.inputs.job_in_path}}",
                    },
                    outputs={"component_out_path": Output(mode="upload")},
                    resources=JobResourceConfiguration(instance_count=2),
                ),
                "merge_component_outputs": Command(
                    component=load_component(source=merge_outputs_component_yaml_path),
                    name="merge_component_outputs",
                    compute="cpu-cluster",
                    inputs={
                        "component_in_number": "${{parent.inputs.job_in_other_number}}",
                        "component_in_path_1": "${{parent.jobs.hello_world_component_1.outputs.component_out_path}}",
                        "component_in_path_2": "${{parent.jobs.hello_world_component_2.outputs.component_out_path}}",
                    },
                    outputs={
                        "component_out_path_1": "${{parent.outputs.job_out_data_1}}",
                        "component_out_path_2": "${{parent.outputs.job_out_data_2}}",
                    },
                ),
            },
        )

        # Define pipeline job via DSL
        hello_world_component_func = load_component(source=hello_world_component_yaml_path)

        merge_outputs_component_func = load_component(source=merge_outputs_component_yaml_path)

        @dsl.pipeline(
            name="SimplePipelineJob",
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            hello_world_component_1 = hello_world_component_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )
            hello_world_component_1.compute = "cpu-cluster"
            hello_world_component_2 = hello_world_component_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )
            hello_world_component_2.compute = "cpu-cluster"

            # configure component overrides
            hello_world_component_2.resources = JobResourceConfiguration()
            hello_world_component_2.resources.instance_count = 2

            # configure component outputs
            # Note: this configures output type too
            hello_world_component_1.outputs.component_out_path = Output(mode="Upload")
            hello_world_component_2.outputs.component_out_path = Output(mode="Upload")

            merge_component_outputs = merge_outputs_component_func(
                component_in_number=job_in_other_number,
                component_in_path_1=hello_world_component_1.outputs.component_out_path,
                component_in_path_2=hello_world_component_2.outputs.component_out_path,
            )
            merge_component_outputs.compute = "cpu-cluster"
            return {
                "job_out_data_1": merge_component_outputs.outputs.component_out_path_1,
                "job_out_data_2": merge_component_outputs.outputs.component_out_path_2,
            }

        dsl_pipeline = pipeline(10, 15, Input(path="./tests/test_configs/data"))
        dsl_pipeline.outputs.job_out_data_1.mode = "mount"
        dsl_pipeline.outputs.job_out_data_2.mode = "Upload"
        pipeline_job_from_yaml = pipeline_job_from_yaml._to_rest_object().as_dict()
        pipeline_job = pipeline_job._to_rest_object().as_dict()
        dsl_pipeline = dsl_pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_world_component_1.componentId",
            "properties.jobs.hello_world_component_2.componentId",
            "properties.jobs.*._source",
            "properties.jobs.merge_component_outputs.componentId",
            "properties.inputs.job_in_path.uri",
            "properties.settings",
        ]
        pipeline_job_from_yaml = omit_with_wildcard(pipeline_job_from_yaml, *omit_fields)
        pipeline_job = omit_with_wildcard(pipeline_job, *omit_fields)
        dsl_pipeline = omit_with_wildcard(dsl_pipeline, *omit_fields)

        assert pipeline_job_from_yaml == pipeline_job
        assert pipeline_job == dsl_pipeline

    def test_pipeline_with_comma_after_pipeline_input_brackets(self):
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            component_func = load_component(source=path)
            component_func(component_in_number=component_in_number, component_in_path=component_in_path)

        test_job_input = (Input(path="azureml:fake_data:1"),)
        with pytest.raises(UserErrorException) as ex:
            pipeline(10, test_job_input)
        assert (
            "Pipeline input expected an azure.ai.ml.Input or primitive types (str, bool, int or float), but got type <class 'tuple'>."
            in ex.__str__()
        )

    def test_dsl_pipeline_multi_times(self):
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(source=yaml_file)

        @dsl.pipeline()
        def pipeline(number, path):
            node1 = component_func(component_in_number=number, component_in_path=path)
            node2 = component_func(component_in_number=number, component_in_path=node1.outputs.component_out_path)
            return {"pipeline_output": node2.outputs.component_out_path}

        data = Input(type=AssetTypes.URI_FOLDER, path="/a/path/on/ds")
        omit_fields = ["name"]
        pipeline1 = pipeline(10, data)
        pipeline_job1 = pipeline1._to_rest_object().as_dict()
        pipeline_job1 = pydash.omit(pipeline_job1, omit_fields)
        pipeline2 = pipeline(10, data)
        pipeline_job2 = pipeline2._to_rest_object().as_dict()
        pipeline_job2 = pydash.omit(pipeline_job2, omit_fields)
        pipeline3 = pipeline(10, data)
        pipeline_job3 = pipeline3._to_rest_object().as_dict()
        pipeline_job3 = pydash.omit(pipeline_job3, omit_fields)

        assert pipeline_job1 == pipeline_job2
        assert pipeline_job2 == pipeline_job3

    def test_component_source(self):
        from azure.ai.ml.dsl._pipeline_component_builder import _add_component_to_current_definition_builder

        def mock_add_to_builder(component):
            _add_component_to_current_definition_builder(component)

        with mock.patch(
            "azure.ai.ml.dsl._pipeline_component_builder._add_component_to_current_definition_builder",
            side_effect=mock_add_to_builder,
        ) as mocker:
            # DSL
            yaml_file = "./tests/test_configs/components/helloworld_component.yml"

            component_entity = load_component(source=yaml_file, params_override=[{"name": "hello_world_component_1"}])
            component_func = _generate_component_function(component_entity)

            job_in_number = PipelineInput(name="job_in_number", owner="pipeline", meta=None)
            job_in_path = PipelineInput(name="job_in_path", owner="pipeline", meta=None)
            component_from_dsl = component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            component_from_dsl.compute = "cpu-cluster"
            component_from_dsl.outputs.component_out_path.mode = "upload"
            component_from_dsl.name = "hello_world_component_1"

            # YAML
            pipeline = load_job(source="./tests/test_configs/pipeline_jobs/sample_pipeline_job.yml")
            component_from_yaml = pipeline.jobs["hello_world_component_1"]

            # REST
            # manually change component field
            rest_component = component_from_dsl._to_rest_object()
            rest_component["componentId"] = "fake_arm_id"
            component_from_rest = Command._from_rest_object(rest_component)

            # SDK
            component_from_sdk = Command(
                name="hello_world_component_1",
                component=component_entity,
                inputs={
                    "component_in_number": "${{parent.inputs.job_in_number}}",
                    "component_in_path": "${{parent.inputs.job_in_path}}",
                },
                outputs={"component_out_path": Output(mode="upload")},
                compute="cpu-cluster",
            )

        # component load from different sources are same type
        assert isinstance(component_from_dsl, Command)
        assert isinstance(component_from_sdk, Command)
        assert isinstance(component_from_rest, Command)
        assert isinstance(component_from_yaml, Command)

        # only Mldesigner component will be added to the stack
        assert mocker.call_count == 1

        # Node with component entity(DSL, SDK, YAML) inputs will have meta
        assert component_from_dsl.inputs.component_in_number._meta is not None
        assert component_from_sdk.inputs.component_in_number._meta is not None
        assert component_from_yaml.inputs.component_in_number._meta is not None

        # Node without component entity(REST) component inputs won't
        assert component_from_rest.inputs.component_in_number._meta is None

        # all components will have same format when passing to backend
        expected_component = {
            "_source": "YAML.COMPONENT",
            "computeId": "cpu-cluster",
            "inputs": {
                "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
            },
            "name": "hello_world_component_1",
            "outputs": {"component_out_path": {"job_output_type": "uri_folder", "mode": "Upload"}},
            "type": "command",
        }
        omit_fields = ["componentId", "properties"]
        assert pydash.omit(component_from_dsl._to_rest_object(), *omit_fields) == expected_component
        assert pydash.omit(component_from_sdk._to_rest_object(), *omit_fields) == expected_component
        assert pydash.omit(component_from_rest._to_rest_object(), *omit_fields) == expected_component
        expected_component.update({"_source": "YAML.JOB"})
        assert pydash.omit(component_from_yaml._to_rest_object(), *omit_fields) == expected_component

    def assert_component_reuse(self, pipeline, expected_component_num, mock_machinelearning_client: MLClient):
        def mock_arm_id(asset, azureml_type: str, *args, **kwargs):
            if azureml_type in AzureMLResourceType.NAMED_TYPES:
                return NAMED_RESOURCE_ID_FORMAT.format(
                    "subscription_id",
                    "resource_group",
                    AZUREML_RESOURCE_PROVIDER,
                    "workspace",
                    azureml_type,
                    "name",
                )
            elif azureml_type in AzureMLResourceType.VERSIONED_TYPES:
                return VERSIONED_RESOURCE_ID_FORMAT.format(
                    "subscription_id",
                    "resource_group",
                    AZUREML_RESOURCE_PROVIDER,
                    "workspace",
                    azureml_type,
                    "name",
                    "1",
                )

        def mock_create(*args, **kwargs):
            return f"{kwargs['name']}:{kwargs['version']}"

        def mock_from_rest(*args, **kwargs):
            return args[0]

        component_names = set()
        with mock.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            side_effect=mock_arm_id,
        ):
            with mock.patch(
                "azure.ai.ml._restclient.v2024_01_01_preview.operations.ComponentVersionsOperations.create_or_update",
                side_effect=mock_create,
            ):
                with mock.patch.object(Component, "_from_rest_object", side_effect=mock_from_rest):
                    for _, job in pipeline.jobs.items():
                        component_name = mock_machinelearning_client.components.create_or_update(
                            job.component, is_anonymous=True
                        )
                        component_names.add(component_name)
        err_msg = f"Got unexpected component id: {component_names}, expecting {expected_component_num} of them."
        assert len(component_names) == expected_component_num, err_msg

    def test_load_component_reuse(self, mock_machinelearning_client: MLClient):
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            component_func1 = load_component(source=path)
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)

            component_func2 = load_component(source=path)
            node3 = component_func2(component_in_number=component_in_number, component_in_path=component_in_path)

            node1.compute = "cpu-cluster"
            node2.compute = "cpu-cluster"
            node3.compute = "cpu-cluster"

        test_job_input = Input(path="azureml:fake_data:1")
        pipeline1 = pipeline(10, test_job_input)
        self.assert_component_reuse(pipeline1, 1, mock_machinelearning_client)

    @pytest.mark.skip(
        "Could not rerecord the test , errors: (InvalidSubscriptionId) The provided subscription identifier 'test_subscription'"
    )
    def test_command_function_reuse(self, mock_machinelearning_client: MLClient):
        path = "./tests/test_configs/components/helloworld_component.yml"
        environment = "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        expected_resources = {"instance_count": 2}
        expected_environment_variables = {"key": "val"}
        inputs = {
            "component_in_path": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
            "component_in_number": 0.01,
        }
        outputs = {"component_out_path": Output(type="mlflow_model", mode="rw_mount")}

        component_func = load_component(source=path)
        command_func1 = command(
            display_name="my-evaluate-job",
            environment=environment,
            command='echo "hello world"',
            distribution={"type": "Pytorch", "process_count_per_instance": 2},
            resources=expected_resources,
            environment_variables=expected_environment_variables,
            inputs=inputs,
            outputs=outputs,
        )

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            node1 = component_func(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func(component_in_number=1, component_in_path=component_in_path)

            node3 = command_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node4 = command_func1(component_in_number=1, component_in_path=component_in_path)

            # same command func as command 1
            command_func2 = command(
                name="new_command",  # different name does not change hash of component.
                display_name="my-evaluate-job",
                environment=environment,
                command='echo "hello world"',
                distribution={"type": "Pytorch", "process_count_per_instance": 2},
                resources=expected_resources,
                environment_variables=expected_environment_variables,
                inputs=inputs,
                outputs=outputs,
            )
            node5 = command_func2(component_in_number=component_in_number, component_in_path=component_in_path)
            node6 = command_func2(component_in_number=1, component_in_path=component_in_path)

            return {
                **node1.outputs,
                **node2.outputs,
                **node3.outputs,
                **node4.outputs,
                **node5.outputs,
                **node6.outputs,
            }

        test_job_input = Input(path="azureml:fake_data:1")
        pipeline1 = pipeline(10, test_job_input)
        self.assert_component_reuse(pipeline1, 2, mock_machinelearning_client)

    @patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"})
    def test_nested_dsl_pipeline_creation(self):
        one2one = load_component(source="./tests/test_configs/components/1in1out.yaml")
        one2two = load_component(source="./tests/test_configs/components/1in2out.yaml")

        @dsl.pipeline(name="2x Splits", description="A sample")
        def cell_division(data):
            layer = 5
            nodes = [one2two(input1=data)]
            last_layer = []
            for i in range(0, layer - 1):
                print("i=", i, " nodes len=", len(nodes))
                current_layer_nodes = []
                for j in range(0, pow(2, i)):
                    print("j=", j)
                    n = nodes[-j - 1]
                    current_layer_nodes.append(one2two(input1=n.outputs.output1))
                    current_layer_nodes.append(one2two(input1=n.outputs.output2))
                nodes = nodes + current_layer_nodes
                last_layer = current_layer_nodes

            x = {}
            seq = 0
            for n in last_layer:
                seq += 1
                x["output{}".format(seq)] = n.outputs.output1
                seq += 1
                x["output{}".format(seq)] = n.outputs.output2
            return x

        @dsl.pipeline(name="Chain", description="A sample")
        def chain(input):
            length = 10
            last = None
            for i in range(0, length):
                if last is None:
                    j = input
                else:
                    j = last.outputs.output1
                node = one2one(input1=j)
                last = node

            return {**last.outputs}

        @dsl.pipeline(
            name="A pipeline composed with split and chain",
            description="A sample",
            default_compute="cpu-cluster",
        )
        def waterfall(data):
            part1 = cell_division(data)
            x = {}
            for o in part1.outputs.values():
                part2 = chain(o)
                x = {**x, **part2.outputs}

            return x

        test_data = Input(type=AssetTypes.URI_FOLDER, path="./")
        cell_division(test_data)
        chain(test_data)

        job = waterfall(test_data)
        assert len(job.jobs) == 33

    def test_pipeline_job_help_function(self):
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(number, path):
            component_func = load_component(source=yaml_file)
            node1 = component_func(component_in_number=number, component_in_path=path)
            return {"pipeline_output": node1.outputs.component_out_path}

        pipeline1 = pipeline(10, Input(path="/a/path/on/ds"))
        with patch("sys.stdout", new=StringIO()) as std_out:
            print(pipeline1)
            assert (
                "display_name: pipeline\ntype: pipeline\ninputs:\n  number: 10\n  path:\n    type: uri_folder"
                in std_out.getvalue()
            )

    @pytest.mark.parametrize(
        "target_yml, target_dsl_pipeline",
        [
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/input_basic.yml",
                data_binding_expression.input_basic(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/input_literal_cross_type.yml",
                data_binding_expression.input_literal_cross_type(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/input_literal_meta.yml",
                data_binding_expression.input_literal_meta(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/input_path_concatenate.yml",
                data_binding_expression.input_path_concatenate(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/input_reason_expression.yml",
                data_binding_expression.input_reason_expression(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/input_string_concatenate.yml",
                data_binding_expression.input_string_concatenate(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_compute.yml",
                data_binding_expression.run_settings_compute(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/input_path.yml",
                data_binding_expression.input_path(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_sweep_choice.yml",
                data_binding_expression.run_settings_sweep_choice(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_sweep_limits.yml",
                data_binding_expression.run_settings_sweep_limits(),
            ),
            (
                "./tests/test_configs/dsl_pipeline/data_binding_expression/run_settings_sweep_literal.yml",
                data_binding_expression.run_settings_sweep_literal(),
            ),
        ],
    )
    def test_dsl_pipeline_with_data_binding_expression(self, target_yml: str, target_dsl_pipeline: PipelineJob) -> None:
        dsl_pipeline_job_rest_dict, pipeline_job_rest_dict = prepare_dsl_curated(
            target_dsl_pipeline, target_yml, in_rest=True
        )
        assert dsl_pipeline_job_rest_dict == pipeline_job_rest_dict
        dsl_pipeline_job_dict, pipeline_job_dict = prepare_dsl_curated(
            target_dsl_pipeline,
            target_yml,
        )
        assert dsl_pipeline_job_dict == pipeline_job_dict

    def test_dsl_pipeline_support_data_binding_for_fields(self) -> None:
        from azure.ai.ml._schema._utils.data_binding_expression import support_data_binding_expression_for_fields
        from azure.ai.ml._schema.job.distribution import MPIDistributionSchema

        schema = MPIDistributionSchema()
        support_data_binding_expression_for_fields(schema, ["type"])
        distribution = schema.load({"type": "mpi", "process_count_per_instance": "${{parent.inputs.test}}"})
        test_input = PipelineInput("test", None)
        assert distribution.type == "mpi"
        assert distribution.process_count_per_instance == str(test_input)
        distribution.process_count_per_instance = test_input
        dumped = schema.dump(distribution)
        assert dumped == {"type": "mpi", "process_count_per_instance": "${{parent.inputs.test}}"}

    def test_dsl_pipeline_without_setting_binding_node(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import pipeline_without_setting_binding_node

        pipeline = pipeline_without_setting_binding_node()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.training_input.uri",
            "properties.jobs.train_with_sample_data.componentId",
            "properties.jobs.train_with_sample_data._source",
            "properties.jobs.train_with_sample_data.properties",
            "properties.settings._source",
        ]
        dsl_pipeline_job_dict = pydash.omit(dsl_pipeline_job_dict, omit_fields)
        assert dsl_pipeline_job_dict == {
            "properties": {
                "description": "E2E dummy pipeline with components defined via yaml.",
                "properties": {},
                "tags": {},
                "compute_id": "cpu-cluster",
                "display_name": "e2e_local_components",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "training_input": {"job_input_type": "uri_folder"},
                    "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
                        "type": "command",
                        "name": "train_with_sample_data",
                        "inputs": {
                            "training_data": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_input}}",
                            },
                            "max_epochs": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        "outputs": {"model_output": {"value": "${{parent.outputs.trained_model}}", "type": "literal"}},
                    }
                },
                "outputs": {"trained_model": {"job_output_type": "uri_folder"}},
                "settings": {},
            }
        }

    def test_dsl_pipeline_with_only_setting_pipeline_level(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_only_setting_pipeline_level,
        )

        pipeline = pipeline_with_only_setting_pipeline_level()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.training_input.uri",
            "properties.jobs.train_with_sample_data.componentId",
            "properties.jobs.train_with_sample_data._source",
            "properties.jobs.train_with_sample_data.properties",
            "properties.settings._source",
        ]
        dsl_pipeline_job_dict = pydash.omit(dsl_pipeline_job_dict, omit_fields)
        assert dsl_pipeline_job_dict == {
            "properties": {
                "description": "E2E dummy pipeline with components defined via yaml.",
                "properties": {},
                "tags": {},
                "compute_id": "cpu-cluster",
                "display_name": "e2e_local_components",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "training_input": {"mode": "ReadOnlyMount", "job_input_type": "uri_folder"},
                    "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
                        "type": "command",
                        "name": "train_with_sample_data",
                        "inputs": {
                            "training_data": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_input}}",
                            },
                            "max_epochs": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # todo: need update here when update literal output output
                        "outputs": {"model_output": {"value": "${{parent.outputs.trained_model}}", "type": "literal"}},
                    }
                },
                "outputs": {"trained_model": {"mode": "Upload", "job_output_type": "uri_folder"}},
                "settings": {},
            }
        }

    def test_dsl_pipeline_with_only_setting_binding_node(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import pipeline_with_only_setting_binding_node

        pipeline = pipeline_with_only_setting_binding_node()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.training_input.uri",
            "properties.jobs.train_with_sample_data.componentId",
            "properties.jobs.train_with_sample_data._source",
            "properties.jobs.train_with_sample_data.properties",
            "properties.settings._source",
        ]
        dsl_pipeline_job_dict = pydash.omit(dsl_pipeline_job_dict, omit_fields)
        assert dsl_pipeline_job_dict == {
            "properties": {
                "description": "E2E dummy pipeline with components defined via yaml.",
                "properties": {},
                "tags": {},
                "compute_id": "cpu-cluster",
                "display_name": "e2e_local_components",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "training_input": {"job_input_type": "uri_folder"},
                    "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
                        "type": "command",
                        "name": "train_with_sample_data",
                        "inputs": {
                            "training_data": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "max_epochs": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "model_output": {
                                "value": "${{parent.outputs.trained_model}}",
                                "type": "literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"trained_model": {"job_output_type": "uri_folder", "mode": "Upload"}},
                "settings": {},
            }
        }

    def test_dsl_pipeline_with_setting_binding_node_and_pipeline_level(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_setting_binding_node_and_pipeline_level,
        )

        pipeline = pipeline_with_setting_binding_node_and_pipeline_level()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.training_input.uri",
            "properties.jobs.train_with_sample_data.componentId",
            "properties.jobs.train_with_sample_data._source",
            "properties.jobs.train_with_sample_data.properties",
            "properties.settings._source",
        ]
        dsl_pipeline_job_dict = pydash.omit(dsl_pipeline_job_dict, omit_fields)
        assert dsl_pipeline_job_dict == {
            "properties": {
                "description": "E2E dummy pipeline with components defined via yaml.",
                "properties": {},
                "tags": {},
                "compute_id": "cpu-cluster",
                "display_name": "e2e_local_components",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "training_input": {"mode": "Download", "job_input_type": "uri_folder"},
                    "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
                        "type": "command",
                        "name": "train_with_sample_data",
                        "inputs": {
                            "training_data": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "max_epochs": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "model_output": {
                                "value": "${{parent.outputs.trained_model}}",
                                "type": "literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
                "settings": {},
            }
        }

    @patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"})
    def test_nested_dsl_pipeline(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(source=path)

        @dsl.pipeline(name="sub_pipeline")
        def sub_pipeline(component_in_number: int, component_in_path: str):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(
                component_in_number=component_in_number, component_in_path=node1.outputs.component_out_path
            )
            return {"sub_pipeline_out": node2.outputs.component_out_path}

        @dsl.pipeline(name="root_pipeline")
        def root_pipeline(component_in_number: int, component_in_path: str):
            node1 = sub_pipeline(component_in_number=component_in_number, component_in_path=component_in_path)
            node1.compute = "will be ignored"
            node2 = sub_pipeline(
                component_in_number=component_in_number, component_in_path=node1.outputs.sub_pipeline_out
            )
            return node2.outputs

        pipeline = root_pipeline(1, "test")
        assert pipeline is not None
        expected_sub_dict = {
            "name": "sub_pipeline",
            "display_name": "sub_pipeline",
            "inputs": {"component_in_number": {"type": "integer"}, "component_in_path": {"type": "string"}},
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
            "type": "pipeline",
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "type": "command",
                },
                "node2": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.component_out_path}}"},
                    },
                    "outputs": {"component_out_path": "${{parent.outputs.sub_pipeline_out}}"},
                    "type": "command",
                },
            },
        }
        omit_fields = [
            "component",
            "jobs.node1.component",
            "jobs.node2.component",
            "jobs.node1.properties",
            "jobs.node2.properties",
        ]
        actual_dict = pydash.omit(
            pipeline.jobs["node1"].component._to_dict(),
            *omit_fields,
        )
        assert actual_dict == expected_sub_dict
        expected_root_dict = {
            "display_name": "root_pipeline",
            "type": "pipeline",
            "inputs": {"component_in_number": 1, "component_in_path": "test"},
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "type": "pipeline",
                },
                "node2": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.sub_pipeline_out}}"},
                    },
                    "outputs": {"sub_pipeline_out": "${{parent.outputs.sub_pipeline_out}}"},
                    "type": "pipeline",
                },
            },
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
        }
        actual_dict = pipeline._to_dict()
        actual_dict = pydash.omit(actual_dict, *omit_fields)
        assert actual_dict == expected_root_dict

    def test_dsl_pipeline_with_command_builder_setting_binding_node_and_pipeline_level(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_command_builder_setting_binding_node_and_pipeline_level,
        )

        pipeline = pipeline_with_command_builder_setting_binding_node_and_pipeline_level()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.training_input.uri",
            "properties.jobs.train_with_sample_data.componentId",
            "properties.jobs.train_with_sample_data._source",
            "properties.jobs.train_with_sample_data.properties",
            "properties.settings._source",
            "type",
        ]
        dsl_pipeline_job_dict = pydash.omit(dsl_pipeline_job_dict, omit_fields)
        assert dsl_pipeline_job_dict == {
            "properties": {
                "description": "E2E dummy pipeline with components defined via yaml.",
                "properties": {},
                "tags": {},
                "compute_id": "cpu-cluster",
                "display_name": "e2e_local_components",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "training_input": {"mode": "Download", "job_input_type": "uri_folder"},
                    "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
                        "type": "command",
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "name": "train_with_sample_data",
                        "inputs": {
                            "training_data": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "max_epochs": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "model_output": {
                                "value": "${{parent.outputs.trained_model}}",
                                "type": "literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
                "settings": {},
            }
        }

    def test_nested_dsl_pipeline_with_setting_binding_node_and_pipeline_level(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            nested_dsl_pipeline_with_setting_binding_node_and_pipeline_level,
        )

        pipeline = nested_dsl_pipeline_with_setting_binding_node_and_pipeline_level()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.pipeline_training_input.uri",
            "properties.jobs.subgraph1.componentId",
            "properties.jobs.subgraph1._source",
            "properties.jobs.subgraph1.properties",
            "properties.settings._source",
        ]
        dsl_pipeline_job_dict = pydash.omit(dsl_pipeline_job_dict, omit_fields)
        assert dsl_pipeline_job_dict == {
            "properties": {
                "description": "E2E dummy pipeline with components defined via yaml.",
                "properties": {},
                "tags": {},
                "compute_id": "cpu-cluster",
                "display_name": "e2e_local_components",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "pipeline_training_input": {"mode": "Download", "job_input_type": "uri_folder"},
                    "pipeline_training_max_epochs": {"job_input_type": "literal", "value": "20"},
                    "pipeline_training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                    "pipeline_learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
                },
                "jobs": {
                    "subgraph1": {
                        "name": "subgraph1",
                        "type": "pipeline",
                        "inputs": {
                            "training_input": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.pipeline_training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "training_max_epocs": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.pipeline_training_max_epochs}}",
                            },
                            "training_learning_rate": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.pipeline_training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.pipeline_learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "output": {
                                "value": "${{parent.outputs.pipeline_trained_model}}",
                                "type": "literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"pipeline_trained_model": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
                "settings": {},
            }
        }

    def test_dsl_pipeline_build_component(self):
        component_path = (
            "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/component/component.yml"
        )
        component_path2 = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline(name="pipeline_comp", version="2", continue_on_step_failure=True, tags={"key": "val"})
        def pipeline_func(path: Input):
            component_func = load_component(source=component_path)
            r_iris_example = component_func(iris=path)
            r_iris_example.compute = "cpu-cluster"
            component_func = load_component(source=component_path2)
            node = component_func(component_in_number="mock_data", component_in_path="mock_data")
            node.outputs.component_out_path.mode = "upload"
            return node.outputs

        component = pipeline_func._pipeline_builder.build(user_provided_kwargs={})

        expected_dict = {
            "name": "pipeline_comp",
            "tags": {"key": "val"},
            "version": "2",
            "display_name": "pipeline_comp",
            "inputs": {"path": {"type": "uri_folder"}},
            "outputs": {"component_out_path": {"type": "uri_folder"}},
            "type": "pipeline",
            "jobs": {},
        }
        actual_dict = component._to_dict()
        actual_dict["jobs"] = {}
        assert expected_dict == actual_dict

    def test_concatenation_of_pipeline_input_with_str(self) -> None:
        echo_string_func = load_component(source=str(components_dir / "echo_string_component.yml"))

        @dsl.pipeline(name="concatenation_of_pipeline_input_with_str")
        def concatenation_in_pipeline(str_param: str):
            echo_string_func(component_in_string=str_param + " right")
            echo_string_func(component_in_string="left " + str_param)
            echo_string_func(component_in_string=str_param + str_param)

        pipeline = concatenation_in_pipeline(str_param="string value")
        for node_name, expected_value in (
            ("microsoft_samples_echo_string", "${{parent.inputs.str_param}} right"),
            ("microsoft_samples_echo_string_1", "left ${{parent.inputs.str_param}}"),
            ("microsoft_samples_echo_string_2", "${{parent.inputs.str_param}}${{parent.inputs.str_param}}"),
        ):
            assert pipeline.jobs[node_name].inputs.component_in_string._data == expected_value

    def test_nested_dsl_pipeline_with_use_node_pipeline_as_input(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)

        @dsl.pipeline(name="sub_pipeline")
        def sub_pipeline(component_in_number: int, component_in_path: str):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(
                component_in_number=component_in_number, component_in_path=node1  # use a node as the input
            )
            return {"sub_pipeline_out": node2.outputs.component_out_path}

        @dsl.pipeline(name="root_pipeline")
        def root_pipeline(component_in_number: int, component_in_path: str):
            node1 = sub_pipeline(component_in_number=component_in_number, component_in_path=component_in_path)
            node1.compute = "will be ignored"
            node2 = sub_pipeline(
                component_in_number=component_in_number, component_in_path=node1  # use a pipeline node as the input
            )
            return node2.outputs

        pipeline = root_pipeline(1, "test")
        assert pipeline is not None
        expected_sub_dict = {
            "name": "sub_pipeline",
            "display_name": "sub_pipeline",
            "inputs": {"component_in_number": {"type": "integer"}, "component_in_path": {"type": "string"}},
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
            "type": "pipeline",
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "type": "command",
                },
                "node2": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.component_out_path}}"},
                    },
                    "outputs": {"component_out_path": "${{parent.outputs.sub_pipeline_out}}"},
                    "type": "command",
                },
            },
        }
        omit_fields = [
            "component",
            "jobs.node1.component",
            "jobs.node2.component",
            "jobs.node1.properties",
            "jobs.node2.properties",
        ]
        actual_dict = pydash.omit(pipeline.jobs["node1"].component._to_dict(), *omit_fields)
        assert actual_dict == expected_sub_dict
        expected_root_dict = {
            "display_name": "root_pipeline",
            "type": "pipeline",
            "inputs": {"component_in_number": 1, "component_in_path": "test"},
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "type": "pipeline",
                },
                "node2": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.sub_pipeline_out}}"},
                    },
                    "outputs": {"sub_pipeline_out": "${{parent.outputs.sub_pipeline_out}}"},
                    "type": "pipeline",
                },
            },
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
        }
        actual_dict = pydash.omit(pipeline._to_dict(), *omit_fields)
        assert actual_dict == expected_root_dict

    def test_nested_dsl_pipeline_with_use_node_pipeline_to_set_input(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)

        @dsl.pipeline(name="sub_pipeline")
        def sub_pipeline(component_in_number: int, component_in_path: str):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2.inputs.component_in_path = node1  # use a node to set the input
            return {"sub_pipeline_out": node2.outputs.component_out_path}

        @dsl.pipeline(name="root_pipeline")
        def root_pipeline(component_in_number: int, component_in_path: str):
            node1 = sub_pipeline(component_in_number=component_in_number, component_in_path=component_in_path)
            node1.compute = "will be ignored"
            node2 = sub_pipeline(component_in_number=component_in_number, component_in_path=component_in_path)
            node2.inputs.component_in_path = node1  # use a pipeline node to set the input
            return node2.outputs

        pipeline = root_pipeline(1, "test")
        assert pipeline is not None
        expected_sub_dict = {
            "name": "sub_pipeline",
            "display_name": "sub_pipeline",
            "inputs": {"component_in_number": {"type": "integer"}, "component_in_path": {"type": "string"}},
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
            "type": "pipeline",
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "type": "command",
                },
                "node2": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.component_out_path}}"},
                    },
                    "outputs": {"component_out_path": "${{parent.outputs.sub_pipeline_out}}"},
                    "type": "command",
                },
            },
        }
        actual_dict = pydash.omit(
            pipeline.jobs["node1"].component._to_dict(),
            *["jobs.node1.component", "jobs.node2.component", "jobs.node1.properties", "jobs.node2.properties"],
        )
        assert actual_dict == expected_sub_dict
        expected_root_dict = {
            "display_name": "root_pipeline",
            "type": "pipeline",
            "inputs": {"component_in_number": 1, "component_in_path": "test"},
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "type": "pipeline",
                },
                "node2": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.sub_pipeline_out}}"},
                    },
                    "outputs": {"sub_pipeline_out": "${{parent.outputs.sub_pipeline_out}}"},
                    "type": "pipeline",
                },
            },
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
        }
        actual_dict = pydash.omit(
            pipeline._to_dict(),
            "jobs.node1.properties",
            "jobs.node2.properties",
            "jobs.node1.component",
            "jobs.node2.component",
        )
        assert actual_dict == expected_root_dict

    def test_pipeline_decorator_without_brackets(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)

        def my_pipeline(component_in_number: int, component_in_path: str):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(
                component_in_number=component_in_number, component_in_path=node1  # use a node as the input
            )
            return {"pipeline_out": node2.outputs.component_out_path}

        # decorate my_pipeline with 2 different styles
        pipeline_0 = dsl.pipeline(my_pipeline)
        pipeline_1 = dsl.pipeline()(my_pipeline)

        pipeline_job_0 = pipeline_0(1, "test")
        pipeline_job_1 = pipeline_1(1, "test")

        assert pipeline_job_0 is not pipeline_job_1
        assert pipeline_job_0._to_dict() == pipeline_job_1._to_dict()
        assert pipeline_job_0._to_rest_object() == pipeline_job_1._to_rest_object()

    def test_dsl_pipeline_with_component_from_container_data(self):
        container_rest_object = ComponentContainerData(properties=ComponentContainerDetails())
        # Set read only fields
        container_rest_object.name = "component"
        container_rest_object.id = "mock_id"
        container_rest_object.system_data = SystemData(created_by="user")
        component_func = Component._from_container_rest_object(container_rest_object)

        @dsl.pipeline
        def pipeline_func():
            component_func()

        with pytest.raises(ValidationException) as e:
            pipeline_func()
        assert "Component returned by 'list' is abbreviated" in str(e.value)

    def test_data_as_pipeline_inputs(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(path)

        @dsl.pipeline
        def pipeline_func(component_in_path):
            node = component_func(
                component_in_number=1, component_in_path=Data(name="test", version="1", type=AssetTypes.MLTABLE)
            )
            node.compute = "cpu-cluster"
            node2 = component_func(component_in_number=1, component_in_path=component_in_path)
            node2.compute = "cpu-cluster"

        pipeline_job = pipeline_func(component_in_path=Data(name="test", version="1", type=AssetTypes.MLTABLE))
        result = pipeline_job._validate()
        assert result._to_dict() == {"result": "Succeeded"}

    def test_pipeline_node_identity_with_component(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(path)

        @dsl.pipeline
        def pipeline_func(component_in_path):
            node1 = component_func(component_in_number=1, component_in_path=component_in_path)
            node1.identity = AmlTokenConfiguration()

            node2 = component_func(component_in_number=1, component_in_path=component_in_path)
            node2.identity = UserIdentityConfiguration()

            node3 = component_func(component_in_number=1, component_in_path=component_in_path)
            node3.identity = ManagedIdentityConfiguration()

        pipeline = pipeline_func(component_in_path=Data(name="test", version="1", type=AssetTypes.MLTABLE))
        omit_fields = ["jobs.*.componentId", "jobs.*._source"]
        actual_dict = omit_with_wildcard(pipeline._to_rest_object().as_dict()["properties"], *omit_fields)

        assert actual_dict["jobs"] == {
            "node1": {
                "identity": {"identity_type": "AMLToken"},
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "1"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.component_in_path}}"},
                },
                "name": "node1",
                "type": "command",
            },
            "node2": {
                "identity": {"identity_type": "UserIdentity"},
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "1"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.component_in_path}}"},
                },
                "name": "node2",
                "type": "command",
            },
            "node3": {
                "identity": {"identity_type": "Managed"},
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "1"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.component_in_path}}"},
                },
                "name": "node3",
                "type": "command",
            },
        }

    def test_pipeline_with_non_pipeline_inputs(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": "component_name_1"}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": "component_name_2"}])

        @dsl.pipeline(
            non_pipeline_inputs=["other_params", "is_add_component", "param_with_annotation", "param_with_default"]
        )
        def pipeline_func(
            job_in_number,
            job_in_path,
            other_params,
            is_add_component,
            param_with_annotation: Dict[str, str],
            param_with_default: int = 1,
        ):
            assert param_with_default == 1
            assert param_with_annotation == {"mock": "dict"}
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=other_params, component_in_path=job_in_path)
            if is_add_component:
                component_func2(component_in_number=other_params, component_in_path=job_in_path)

        pipeline = pipeline_func(10, Input(path="/a/path/on/ds"), 15, False, {"mock": "dict"})
        assert len(pipeline.jobs) == 2
        assert "other_params" not in pipeline.inputs
        assert isinstance(pipeline.jobs[component_func1.name].inputs["component_in_number"]._data, PipelineInput)
        assert pipeline.jobs[component_func2.name].inputs["component_in_number"]._data == 15

        pipeline = pipeline_func(10, Input(path="/a/path/on/ds"), 15, True, {"mock": "dict"})
        assert len(pipeline.jobs) == 3

        @dsl.pipeline(non_pipeline_parameters=["other_params", "is_add_component"])
        def pipeline_func(job_in_number, job_in_path, other_params, is_add_component):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=other_params, component_in_path=job_in_path)
            if is_add_component:
                component_func2(component_in_number=other_params, component_in_path=job_in_path)

        pipeline = pipeline_func(10, Input(path="/a/path/on/ds"), 15, True)
        assert len(pipeline.jobs) == 3

    def test_pipeline_with_invalid_non_pipeline_inputs(self):
        @dsl.pipeline(non_pipeline_inputs=[123])
        def pipeline_func():
            pass

        with pytest.raises(UserErrorException) as error_info:
            pipeline_func()
        assert "Type of 'non_pipeline_parameter' in dsl.pipeline should be a list of string" in str(error_info)

        @dsl.pipeline(non_pipeline_inputs=["non_exist_param1", "non_exist_param2"])
        def pipeline_func():
            pass

        with pytest.raises(ParamValueNotExistsError) as error_info:
            pipeline_func()
        assert (
            "pipeline_func() got unexpected params in non_pipeline_inputs ['non_exist_param1', 'non_exist_param2']"
            in str(error_info)
        )

    def test_component_func_as_non_pipeline_inputs(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": "component_name_1"}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": "component_name_2"}])

        @dsl.pipeline(non_pipeline_inputs=["component_func"])
        def pipeline_func(job_in_number, job_in_path, component_func):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func(component_in_number=job_in_number, component_in_path=job_in_path)

        pipeline = pipeline_func(
            job_in_number=10, job_in_path=Input(path="/a/path/on/ds"), component_func=component_func2
        )
        assert len(pipeline.jobs) == 2
        assert component_func2.name in pipeline.jobs

    def test_pipeline_with_variable_inputs(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)
        data = Data(name="test", version="1", type=AssetTypes.MLTABLE)

        @dsl.pipeline
        def pipeline_with_variable_args(**kwargs):
            node_kwargs = component_func1(
                component_in_number=kwargs["component_in_number1"], component_in_path=kwargs["component_in_path1"]
            )

        @dsl.pipeline
        def root_pipeline(component_in_number: int, component_in_path: Input, **kwargs):
            """A pipeline with detailed docstring, including descriptions for inputs and outputs.

            In this pipeline docstring, there are descriptions for inputs and outputs, via pipeline decorator,
            Input/Output descriptions can infer from these descriptions.

            Args:
                component_in_number: component_in_number description
                component_in_path: component_in_path description
                component_in_number1: component_in_number1 description
                component_in_path1: component_in_path1 description
                args_0: args_0 description
            """
            node = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node_kwargs = component_func1(
                component_in_number=kwargs["component_in_number1"], component_in_path=kwargs["component_in_path1"]
            )
            node_with_arg_kwarg = pipeline_with_variable_args(**kwargs)

        pipeline = root_pipeline(10, data, component_in_number1=12, component_in_path1=data)

        assert pipeline.component.inputs["component_in_number"].description == "component_in_number description"
        assert pipeline.component.inputs["component_in_path"].description == "component_in_path description"
        assert pipeline.component.inputs["component_in_number1"].description == "component_in_number1 description"
        assert pipeline.component.inputs["component_in_path1"].description == "component_in_path1 description"

        omit_fields = ["jobs.*.componentId", "jobs.*._source"]
        actual_dict = omit_with_wildcard(pipeline._to_rest_object().as_dict()["properties"], *omit_fields)

        assert actual_dict["inputs"] == {
            "component_in_number": {"job_input_type": "literal", "value": "10"},
            "component_in_path": {"uri": "test:1", "job_input_type": "mltable"},
            "component_in_number1": {"job_input_type": "literal", "value": "12"},
            "component_in_path1": {"uri": "test:1", "job_input_type": "mltable"},
        }
        assert actual_dict["jobs"] == {
            "node": {
                "name": "node",
                "type": "command",
                "inputs": {
                    "component_in_number": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.component_in_number}}",
                    },
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.component_in_path}}"},
                },
            },
            "node_kwargs": {
                "name": "node_kwargs",
                "type": "command",
                "inputs": {
                    "component_in_number": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.component_in_number1}}",
                    },
                    "component_in_path": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.component_in_path1}}",
                    },
                },
            },
            "node_with_arg_kwarg": {
                "name": "node_with_arg_kwarg",
                "type": "pipeline",
                "inputs": {
                    "component_in_number1": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.component_in_number1}}",
                    },
                    "component_in_path1": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.component_in_path1}}",
                    },
                },
            },
        }

        with pytest.raises(
            UnsupportedParameterKindError, match="dsl pipeline does not accept \*custorm_args as parameters\."
        ):

            @dsl.pipeline
            def pipeline_with_variable_args(*custorm_args):
                pass

            pipeline_with_variable_args(1, 2, 3)

        with mock.patch("azure.ai.ml.dsl._pipeline_decorator.is_private_preview_enabled", return_value=False):
            with pytest.raises(
                UnsupportedParameterKindError, match="dsl pipeline does not accept \*args or \*\*kwargs as parameters\."
            ):
                root_pipeline(10, data, 11, data, component_in_number1=11, component_in_path1=data)

    def test_pipeline_with_dumplicate_variable_inputs(self):
        @dsl.pipeline
        def pipeline_with_variable_args(key_1: int, **kargs):
            pass

        with pytest.raises(
            MultipleValueError, match="pipeline_with_variable_args\(\) got multiple values for argument 'key_1'\."
        ):
            pipeline_with_variable_args(10, key_1=10)

    def test_pipeline_with_output_binding_in_dynamic_args(self):
        hello_world_func = load_component(components_dir / "helloworld_component.yml")
        hello_world_no_inputs_func = load_component(components_dir / "helloworld_component_no_inputs.yml")

        @dsl.pipeline
        def pipeline_func_consume_dynamic_arg(**kwargs):
            hello_world_func(component_in_number=kwargs["int_param"], component_in_path=kwargs["path_param"])

        @dsl.pipeline
        def root_pipeline_func():
            node = hello_world_no_inputs_func()
            kwargs = {"int_param": 0, "path_param": node.outputs.component_out_path}
            pipeline_func_consume_dynamic_arg(**kwargs)

        pipeline_job = root_pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        assert pipeline_job._customized_validate().passed is True

    def test_condition_node_consumption(self):
        from azure.ai.ml.dsl._condition import condition

        component_yaml = components_dir / "helloworld_component_no_paths.yml"
        component_func = load_component(component_yaml)

        # consume expression (also component with only one output)
        @dsl.pipeline
        def pipeline_func_consume_expression(int_param: int):
            node1 = component_func()
            node2 = component_func()
            expression = int_param == 0
            control_node = condition(expression, true_block=node1, false_block=node2)  # noqa: F841

        pipeline_job = pipeline_func_consume_expression(int_param=1)
        assert pipeline_job.jobs["control_node"]._to_rest_object() == {
            "_source": "DSL",
            "type": "if_else",
            "condition": "${{parent.jobs.expression_component.outputs.output}}",
            "true_block": "${{parent.jobs.node1}}",
            "false_block": "${{parent.jobs.node2}}",
        }

        # consume component with not one output
        @dsl.pipeline
        def pipeline_func_consume_invalid_component():
            node0 = component_func()
            node1 = component_func()
            node2 = component_func()
            control_node = condition(node0, true_block=node1, false_block=node2)  # noqa: F841

        with pytest.raises(UserErrorException) as e:
            pipeline_func_consume_invalid_component()
        assert str(e.value) == "Exactly one output is expected for condition node, 0 outputs found."

    def test_dsl_pipeline_with_spark_hobo(self) -> None:
        add_greeting_column_func = load_component(
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        )
        count_by_row_func = load_component(
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/count_by_row_component.yml"
        )

        @dsl.pipeline(description="submit a pipeline with spark job")
        def spark_pipeline_from_yaml(iris_data):
            add_greeting_column = add_greeting_column_func(file_input=iris_data)
            add_greeting_column.resources = {"instance_type": "Standard_E8S_V3", "runtime_version": "3.3.0"}
            count_by_row = count_by_row_func(file_input=iris_data)
            count_by_row.resources = {"instance_type": "Standard_E8S_V3", "runtime_version": "3.3.0"}
            count_by_row.identity = {"type": "managed"}

            return {"output": count_by_row.outputs.output}

        dsl_pipeline: PipelineJob = spark_pipeline_from_yaml(
            iris_data=Input(
                path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                type=AssetTypes.URI_FILE,
                mode=InputOutputModes.DIRECT,
            ),
        )
        dsl_pipeline.outputs.output.mode = "Direct"

        spark_node = dsl_pipeline.jobs["add_greeting_column"]
        job_data_path_input = spark_node.inputs["file_input"]._meta
        assert job_data_path_input
        # spark_node.component._id = "azureml:test_component:1"
        spark_node_dict = spark_node._to_dict()

        spark_node_rest_obj = spark_node._to_rest_object()
        regenerated_spark_node = Spark._from_rest_object(spark_node_rest_obj)

        spark_node_dict_from_rest = regenerated_spark_node._to_dict()
        omit_fields = []
        assert pydash.omit(spark_node_dict, *omit_fields) == pydash.omit(spark_node_dict_from_rest, *omit_fields)
        omit_fields = [
            "jobs.add_greeting_column.componentId",
            "jobs.count_by_row.componentId",
            "jobs.add_greeting_column.properties",
            "jobs.count_by_row.properties",
        ]
        actual_job = pydash.omit(dsl_pipeline._to_rest_object().properties.as_dict(), *omit_fields)
        assert actual_job == {
            "description": "submit a pipeline with spark job",
            "properties": {},
            "tags": {},
            "display_name": "spark_pipeline_from_yaml",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "iris_data": {
                    "mode": "Direct",
                    "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                    "job_input_type": "uri_file",
                }
            },
            "jobs": {
                "add_greeting_column": {
                    "type": "spark",
                    "resources": {"instance_type": "Standard_E8S_V3", "runtime_version": "3.3.0"},
                    "entry": {"file": "add_greeting_column.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                    "py_files": ["utils.zip"],
                    "files": ["my_files.txt"],
                    "identity": {"identity_type": "UserIdentity"},
                    "conf": {
                        "spark.driver.cores": 2,
                        "spark.driver.memory": "1g",
                        "spark.executor.cores": 1,
                        "spark.executor.memory": "1g",
                        "spark.executor.instances": 1,
                    },
                    "args": "--file_input ${{inputs.file_input}}",
                    "name": "add_greeting_column",
                    "inputs": {
                        "file_input": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"},
                    },
                    "_source": "YAML.COMPONENT",
                },
                "count_by_row": {
                    "_source": "YAML.COMPONENT",
                    "args": "--file_input ${{inputs.file_input}} " "--output ${{outputs.output}}",
                    "conf": {
                        "spark.driver.cores": 2,
                        "spark.driver.memory": "1g",
                        "spark.executor.cores": 1,
                        "spark.executor.instances": 1,
                        "spark.executor.memory": "1g",
                    },
                    "entry": {"file": "count_by_row.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                    "files": ["my_files.txt"],
                    "identity": {"identity_type": "Managed"},
                    "inputs": {"file_input": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"}},
                    "jars": ["scalaproj.jar"],
                    "name": "count_by_row",
                    "outputs": {"output": {"type": "literal", "value": "${{parent.outputs.output}}"}},
                    "resources": {"instance_type": "Standard_E8S_V3", "runtime_version": "3.3.0"},
                    "type": "spark",
                },
            },
            "outputs": {"output": {"job_output_type": "uri_folder", "mode": "Direct"}},
            "settings": {"_source": "DSL"},
        }

    def test_dsl_pipeline_with_data_transfer_copy_node(self) -> None:
        merge_files = load_component("./tests/test_configs/components/data_transfer/copy_files.yaml")

        @dsl.pipeline(description="submit a pipeline with data transfer copy job")
        def data_transfer_copy_pipeline_from_yaml(folder1):
            copy_files_node = merge_files(folder1=folder1)
            return {"output": copy_files_node.outputs.output_folder}

        dsl_pipeline: PipelineJob = data_transfer_copy_pipeline_from_yaml(
            folder1=Input(
                path="azureml://datastores/my_cosmos/paths/source_cosmos",
                type=AssetTypes.URI_FOLDER,
            ),
        )
        dsl_pipeline.outputs.output.path = "azureml://datastores/my_blob/paths/merged_blob"

        data_transfer_copy_node = dsl_pipeline.jobs["copy_files_node"]
        job_data_path_input = data_transfer_copy_node.inputs["folder1"]._meta
        assert job_data_path_input
        data_transfer_copy_node_dict = data_transfer_copy_node._to_dict()

        data_transfer_copy_node_rest_obj = data_transfer_copy_node._to_rest_object()
        regenerated_data_transfer_copy_node = DataTransferCopy._from_rest_object(data_transfer_copy_node_rest_obj)

        data_transfer_copy_node_dict_from_rest = regenerated_data_transfer_copy_node._to_dict()
        omit_fields = []
        assert pydash.omit(data_transfer_copy_node_dict, *omit_fields) == pydash.omit(
            data_transfer_copy_node_dict_from_rest, *omit_fields
        )
        omit_fields = [
            "jobs.copy_files_node.componentId",
        ]
        actual_job = pydash.omit(dsl_pipeline._to_rest_object().properties.as_dict(), *omit_fields)
        assert actual_job == {
            "description": "submit a pipeline with data transfer copy job",
            "display_name": "data_transfer_copy_pipeline_from_yaml",
            "inputs": {
                "folder1": {"job_input_type": "uri_folder", "uri": "azureml://datastores/my_cosmos/paths/source_cosmos"}
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "copy_files_node": {
                    "_source": "YAML.COMPONENT",
                    "data_copy_mode": "merge_with_overwrite",
                    "inputs": {"folder1": {"job_input_type": "literal", "value": "${{parent.inputs.folder1}}"}},
                    "name": "copy_files_node",
                    "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.output}}"}},
                    "task": "copy_data",
                    "type": "data_transfer",
                }
            },
            "outputs": {
                "output": {"job_output_type": "uri_folder", "uri": "azureml://datastores/my_blob/paths/merged_blob"}
            },
            "properties": {},
            "settings": {"_source": "DSL"},
            "tags": {},
        }

    def test_dsl_pipeline_with_data_transfer_merge_node(self) -> None:
        merge_files = load_component("./tests/test_configs/components/data_transfer/merge_files.yaml")

        @dsl.pipeline(description="submit a pipeline with data transfer copy job")
        def data_transfer_copy_pipeline_from_yaml(folder1, folder2):
            merge_files_node = merge_files(folder1=folder1, folder2=folder2)
            return {"output": merge_files_node.outputs.output_folder}

        dsl_pipeline: PipelineJob = data_transfer_copy_pipeline_from_yaml(
            folder1=Input(
                path="azureml://datastores/my_cosmos/paths/source_cosmos",
                type=AssetTypes.URI_FOLDER,
            ),
            folder2=Input(
                path="azureml://datastores/my_cosmos/paths/source_cosmos",
                type=AssetTypes.URI_FOLDER,
            ),
        )
        dsl_pipeline.outputs.output.path = "azureml://datastores/my_blob/paths/merged_blob"

        data_transfer_copy_node = dsl_pipeline.jobs["merge_files_node"]
        job_data_path_input = data_transfer_copy_node.inputs["folder1"]._meta
        assert job_data_path_input
        data_transfer_copy_node_dict = data_transfer_copy_node._to_dict()

        data_transfer_copy_node_rest_obj = data_transfer_copy_node._to_rest_object()
        regenerated_data_transfer_copy_node = DataTransferCopy._from_rest_object(data_transfer_copy_node_rest_obj)

        data_transfer_copy_node_dict_from_rest = regenerated_data_transfer_copy_node._to_dict()
        omit_fields = []
        assert pydash.omit(data_transfer_copy_node_dict, *omit_fields) == pydash.omit(
            data_transfer_copy_node_dict_from_rest, *omit_fields
        )
        omit_fields = [
            "jobs.merge_files_node.componentId",
        ]
        actual_job = pydash.omit(dsl_pipeline._to_rest_object().properties.as_dict(), *omit_fields)
        assert actual_job == {
            "description": "submit a pipeline with data transfer copy job",
            "display_name": "data_transfer_copy_pipeline_from_yaml",
            "inputs": {
                "folder1": {
                    "job_input_type": "uri_folder",
                    "uri": "azureml://datastores/my_cosmos/paths/source_cosmos",
                },
                "folder2": {
                    "job_input_type": "uri_folder",
                    "uri": "azureml://datastores/my_cosmos/paths/source_cosmos",
                },
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "merge_files_node": {
                    "_source": "YAML.COMPONENT",
                    "data_copy_mode": "merge_with_overwrite",
                    "inputs": {
                        "folder1": {"job_input_type": "literal", "value": "${{parent.inputs.folder1}}"},
                        "folder2": {"job_input_type": "literal", "value": "${{parent.inputs.folder2}}"},
                    },
                    "name": "merge_files_node",
                    "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.output}}"}},
                    "task": "copy_data",
                    "type": "data_transfer",
                }
            },
            "outputs": {
                "output": {"job_output_type": "uri_folder", "uri": "azureml://datastores/my_blob/paths/merged_blob"}
            },
            "properties": {},
            "settings": {"_source": "DSL"},
            "tags": {},
        }

    def test_dsl_pipeline_with_data_transfer_import_component(self) -> None:
        s3_blob = load_component("./tests/test_configs/components/data_transfer/import_file_to_blob.yaml")
        path_source_s3 = "test1/*"
        connection_target = "azureml:my-s3-connection"
        source = {"type": "file_system", "connection": connection_target, "path": path_source_s3}

        with pytest.raises(ValidationException) as e:

            @dsl.pipeline
            def data_transfer_copy_pipeline_from_yaml():
                s3_blob(source=source)

            data_transfer_copy_pipeline_from_yaml()
            assert "DataTransfer component is not callable for import task." in str(e.value)

    def test_dsl_pipeline_with_data_transfer_export_component(self) -> None:
        blob_azuresql = load_component("./tests/test_configs/components/data_transfer/export_blob_to_database.yaml")

        my_cosmos_folder = Input(type=AssetTypes.URI_FILE, path="/data/testFile_ForSqlDB.parquet")
        connection_target_azuresql = "azureml:my_export_azuresqldb_connection"
        table_name = "dbo.Persons"
        sink = {"type": "database", "connection": connection_target_azuresql, "table_name": table_name}

        with pytest.raises(ValidationException) as e:

            @dsl.pipeline
            def data_transfer_copy_pipeline_from_yaml():
                blob_azuresql_node = blob_azuresql(source=my_cosmos_folder)
                blob_azuresql_node.sink = sink

            data_transfer_copy_pipeline_from_yaml()
            assert "DataTransfer component is not callable for import task." in str(e.value)

    def test_node_sweep_with_optional_input(self) -> None:
        component_yaml = components_dir / "helloworld_component_optional_input.yml"
        component_func = load_component(component_yaml)

        @dsl.pipeline
        def pipeline_func():
            node1 = component_func(required_input=1, optional_input=2)  # noqa: F841
            node2 = component_func(required_input=1)  # noqa: F841
            node3 = component_func(required_input=1)
            node_sweep = node3.sweep(
                primary_metric="training_f1_score",
                goal="minimize",
                sampling_algorithm="random",
            )
            node_sweep.set_limits(
                max_total_trials=20,
                max_concurrent_trials=10,
            )

        pipeline_job = pipeline_func()
        jobs_dict = pipeline_job._to_rest_object().as_dict()["properties"]["jobs"]
        # for node1 inputs, should contain required_input and optional_input;
        # while for node2 and node_sweep, should only contain required_input.
        assert jobs_dict["node1"]["inputs"] == {
            "required_input": {"job_input_type": "literal", "value": "1"},
            "optional_input": {"job_input_type": "literal", "value": "2"},
        }
        assert jobs_dict["node2"]["inputs"] == {"required_input": {"job_input_type": "literal", "value": "1"}}
        assert jobs_dict["node_sweep"]["inputs"] == {"required_input": {"job_input_type": "literal", "value": "1"}}

    def test_dsl_pipeline_unprovided_required_input(self):
        component_yaml = components_dir / "helloworld_component_optional_input.yml"
        component_func = load_component(component_yaml)

        @dsl.pipeline
        def pipeline_func(required_input: int, optional_input: int = 2):
            component_func(required_input=required_input, optional_input=optional_input)

        # no error when calling dsl pipeline func
        pipeline_job = pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {
            "inputs.required_input": "Required input 'required_input' for pipeline " "'pipeline_func' not provided."
        }

        validate_result = pipeline_job.component._validate()
        assert validate_result.error_messages == {}

        # pipeline component has required inputs
        assert pipeline_job.component._to_dict()["inputs"] == {
            "optional_input": {"default": "2", "optional": True, "type": "integer"},
            "required_input": {"type": "integer"},
        }

        # setting _validate_required_input_not_provided to False will skip the unprovided input check
        @dsl.pipeline
        def outer_pipeline():
            node = pipeline_func()
            node._validate_required_input_not_provided = False

        pipeline_job = outer_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        validate_result = pipeline_job._validate()
        assert validate_result.passed

    def test_dsl_pipeline_with_unprovided_pipeline_optional_input(self, client: MLClient) -> None:
        component_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # optional pipeline input binding to optional node input
        @dsl.pipeline()
        def pipeline_func(optional_input: Input(optional=True, type="uri_file")):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_input=optional_input,
            )

        pipeline_job = pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {}

        # optional pipeline parameter binding to optional node parameter
        @dsl.pipeline()
        def pipeline_func(
            optional_param: Input(optional=True, type="string"),
            optional_param_duplicate: Input(optional=True, type="string"),
        ):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_param=optional_param,
                optional_param_with_default=optional_param_duplicate,
            )

        pipeline_job = pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {}

    def test_dsl_pipeline_with_unprovided_pipeline_required_input(self, client: MLClient) -> None:
        component_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # required pipeline input binding to optional node input
        @dsl.pipeline()
        def pipeline_func(required_input: Input(optional=False, type="uri_file")):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_input=required_input,
            )

        pipeline_job = pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {
            "inputs.required_input": "Required input 'required_input' for pipeline " "'pipeline_func' not provided."
        }

        # required pipeline parameter binding to optional node parameter
        @dsl.pipeline()
        def pipeline_func(
            required_param: Input(optional=False, type="string"),
            required_param_duplicate: Input(optional=False, type="string"),
        ):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_param=required_param,
                optional_param_with_default=required_param_duplicate,
            )

        pipeline_job = pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {
            "inputs.required_param": "Required input 'required_param' for pipeline " "'pipeline_func' not provided.",
            "inputs.required_param_duplicate": "Required input 'required_param_duplicate' for pipeline "
            "'pipeline_func' not provided.",
        }

        # required pipeline parameter with default value binding to optional node parameter
        @dsl.pipeline()
        def pipeline_func(required_param: Input(optional=False, type="string", default="pipeline_required_param")):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param=required_param,
                optional_param=required_param,
                optional_param_with_default=required_param,
            )

        pipeline_job = pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {}

    def test_dsl_pipeline_with_pipeline_component_unprovided_pipeline_optional_input(self, client: MLClient) -> None:
        component_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # optional pipeline input binding to optional node input
        @dsl.pipeline()
        def subgraph_pipeline(optional_input: Input(optional=True, type="uri_file")):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_input=optional_input,
            )

        @dsl.pipeline()
        def root_pipeline():
            subgraph_node = subgraph_pipeline()

        pipeline_job = root_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {}

        # optional pipeline parameter binding to optional node parameter
        @dsl.pipeline()
        def subgraph_pipeline(
            optional_parameter: Input(optional=True, type="string"),
            optional_parameter_duplicate: Input(optional=True, type="string"),
        ):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_param=optional_parameter,
                optional_param_with_default=optional_parameter_duplicate,
            )

        @dsl.pipeline()
        def root_pipeline():
            subgraph_node = subgraph_pipeline()

        pipeline_job = root_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {}

    def test_dsl_pipeline_with_pipeline_component_unprovided_pipeline_required_input(self, client: MLClient) -> None:
        component_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # required pipeline input binding to optional node input
        @dsl.pipeline()
        def subgraph_pipeline(required_input: Input(optional=False, type="uri_file")):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_input=required_input,
            )

        @dsl.pipeline()
        def root_pipeline():
            subgraph_node = subgraph_pipeline()

        pipeline_job = root_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {
            "jobs.subgraph_node.inputs.required_input": "Required input 'required_input' for component 'subgraph_node'"
            " not provided."
        }

        @dsl.pipeline()
        def root_pipeline(required_input: Input(optional=False, type="uri_file")):
            subgraph_node = subgraph_pipeline(required_input=required_input)

        pipeline_job = root_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {
            "inputs.required_input": "Required input 'required_input' for pipeline 'root_pipeline' not provided."
        }

        # required pipeline parameter binding to optional node parameter
        @dsl.pipeline()
        def subgraph_pipeline(required_parameter: Input(optional=False, type="string")):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_param=required_parameter,
            )

        @dsl.pipeline()
        def root_pipeline():
            subgraph_node = subgraph_pipeline()

        pipeline_job = root_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {
            "jobs.subgraph_node.inputs.required_parameter": "Required input 'required_parameter' for component "
            "'subgraph_node' not provided."
        }

        # required pipeline parameter with default value binding to optional node parameter
        @dsl.pipeline()
        def subgraph_pipeline(required_parameter: Input(optional=False, type="string", default="subgraph_pipeline")):
            component_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param="def",
                optional_param=required_parameter,
            )

        @dsl.pipeline()
        def root_pipeline():
            subgraph_node = subgraph_pipeline()

        pipeline_job = root_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {}

    def test_dsl_pipeline_with_return_annotation(self, client: MLClient) -> None:
        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @dsl.pipeline()
        def my_pipeline() -> Output(type="uri_folder", description="new description", mode="upload"):
            node = hello_world_component_func(component_in_path=Input(path="path/on/ds"), component_in_number=10)
            return {"output": node.outputs.component_out_path}

        pipeline_job = my_pipeline()
        expected_outputs = {
            "output": {"description": "new description", "job_output_type": "uri_folder", "mode": "Upload"}
        }
        assert pipeline_job._to_rest_object().as_dict()["properties"]["outputs"] == expected_outputs

    def test_dsl_pipeline_run_settings(self) -> None:
        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @dsl.pipeline()
        def my_pipeline() -> Output(type="uri_folder", description="new description", mode="upload"):
            node = hello_world_component_func(component_in_path=Input(path="path/on/ds"), component_in_number=10)
            return {"output": node.outputs.component_out_path}

        pipeline_job: PipelineJob = my_pipeline()
        pipeline_job.settings = {
            "default_compute": "cpu-cluster",
            "continue_on_step_failure": True,
            "continue_run_on_failed_optional_input": False,
        }

        assert pipeline_job._to_rest_object().properties.settings == {
            PipelineConstants.DEFAULT_COMPUTE: "cpu-cluster",
            PipelineConstants.CONTINUE_ON_STEP_FAILURE: True,
            PipelineConstants.CONTINUE_RUN_ON_FAILED_OPTIONAL_INPUT: False,
            "_source": "DSL",
        }

    def test_register_output_without_name_sdk(self):
        component = load_component(source="./tests/test_configs/components/helloworld_component.yml")
        component_input = Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv")

        @dsl.pipeline()
        def register_node_output():
            node = component(component_in_path=component_input)
            node.outputs.component_out_path.version = 1

        pipeline = register_node_output()
        pipeline.settings.default_compute = "azureml:cpu-cluster"
        with pytest.raises(UserErrorException) as e:
            pipeline._validate()
        assert "Output name is required when output version is specified." in str(e.value)

        @dsl.pipeline()
        def register_pipeline_output():
            node = component(component_in_path=component_input)
            return {"pipeine_a_output": node.outputs.component_out_path}

        pipeline = register_pipeline_output()
        pipeline.outputs.pipeine_a_output.version = 1
        pipeline.settings.default_compute = "azureml:cpu-cluster"
        with pytest.raises(UserErrorException) as e:
            pipeline._validate()
        assert "Output name is required when output version is specified." in str(e.value)

    def test_register_output_with_invalid_name_sdk(self):
        component = load_component(source="./tests/test_configs/components/helloworld_component.yml")
        component_input = Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv")

        @dsl.pipeline()
        def register_node_output():
            node = component(component_in_path=component_input)
            node.outputs.component_out_path.name = "@"
            node.outputs.component_out_path.version = "1"

        pipeline = register_node_output()
        pipeline.settings.default_compute = "azureml:cpu-cluster"
        with pytest.raises(UserErrorException) as e:
            pipeline._validate()
        assert (
            "The output name @ can only contain alphanumeric characters, dashes and underscores, with a limit of 255 characters."
            in str(e.value)
        )

    def test_pipeline_output_settings_copy(self):
        component_yaml = components_dir / "helloworld_component.yml"
        params_override = [{"outputs": {"component_out_path": {"type": "uri_file"}}}]
        component_func1 = load_component(source=component_yaml, params_override=params_override)

        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            node1.outputs.component_out_path.path = "path1"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        pipeline_job2 = my_pipeline()

        pipeline_job1.outputs.component_out_path.path = "new_path"

        # modified pipeline output setting won't affect pipeline component or other nodes.
        assert pipeline_job1.outputs.component_out_path.path == "new_path"
        assert pipeline_job1.component.outputs["component_out_path"].path == "path1"
        assert pipeline_job2.outputs.component_out_path.path == "path1"
        assert pipeline_job2.component.outputs["component_out_path"].path == "path1"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()
        # type will be preserved & path will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "uri": "new_path",
        }

        pipeline_dict = pipeline_job2._to_rest_object().as_dict()
        # type will be preserved & path will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "uri": "path1",
        }

        # newly create pipeline job instance won't be affected
        pipeline_job3 = my_pipeline()
        assert pipeline_job3.outputs.component_out_path.path == "path1"
        assert pipeline_job3.component.outputs["component_out_path"].path == "path1"

        pipeline_dict = pipeline_job3._to_rest_object().as_dict()
        # type will be preserved & path will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "uri": "path1",
        }

    def test_node_path_promotion(self):
        component_yaml = components_dir / "helloworld_component.yml"
        params_override = [{"outputs": {"component_out_path": {"type": "uri_file"}}}]
        component_func1 = load_component(source=component_yaml, params_override=params_override)

        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            node1.outputs.component_out_path = Output(
                # the following settings will be copied to pipeline level
                path="path",
            )
            return node1.outputs

        pipeline_job1 = my_pipeline()
        assert pipeline_job1.outputs.component_out_path.path == "path"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()
        # type will be preserved & path will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_folder",
            "uri": "path",
        }

        @dsl.pipeline()
        def outer_pipeline():
            node1 = my_pipeline()
            assert node1.outputs.component_out_path.path == "path"
            node1.outputs.component_out_path.path = "new_path"
            assert node1.outputs.component_out_path.path == "new_path"
            return node1.outputs

        pipeline_job2 = outer_pipeline()
        assert pipeline_job2.outputs.component_out_path.path == "new_path"
        pipeline_dict = pipeline_job2._to_rest_object().as_dict()
        # type will be preserved & path will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_folder",
            "uri": "new_path",
        }

    def test_node_output_type_promotion(self):
        component_yaml = components_dir / "helloworld_component.yml"
        params_override = [{"outputs": {"component_out_path": {"type": "uri_file"}}}]
        component_func1 = load_component(source=component_yaml, params_override=params_override)

        # without node level setting, node should have same type with component
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            assert node1.outputs.component_out_path.type == "uri_file"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        assert pipeline_job1.outputs.component_out_path.type == "uri_file"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["outputs"]["component_out_path"]["job_output_type"] == "uri_file"

        # when node level has output setting except type, node should have same type with component
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            node1.outputs.component_out_path.mode = "mount"
            assert node1.outputs.component_out_path.type == "uri_file"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        assert pipeline_job1.outputs.component_out_path.type == "uri_file"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()["properties"]
        # pipeline level should have correct type & copied mode
        assert pipeline_dict["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "mode": "ReadWriteMount",
        }
        # node level will have a binding
        assert pipeline_dict["jobs"]["node1"]["outputs"]["component_out_path"] == {
            "mode": "ReadWriteMount",
            "type": "literal",
            "value": "${{parent.outputs.component_out_path}}",
        }

        # when node level has setting, node should respect the setting
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            assert node1.outputs.component_out_path.type == "uri_file"
            node1.outputs.component_out_path.type = "mlflow_model"
            assert node1.outputs.component_out_path.type == "mlflow_model"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        # assert pipeline_job1.outputs.component_out_path.type == "mlflow_model"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["outputs"]["component_out_path"]["job_output_type"] == "mlflow_model"

        # when pipeline level has setting, node should respect the setting
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            assert node1.outputs.component_out_path.type == "uri_file"
            node1.outputs.component_out_path.type = "mlflow_model"
            assert node1.outputs.component_out_path.type == "mlflow_model"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        pipeline_job1.outputs.component_out_path.type = "custom_model"
        assert pipeline_job1.outputs.component_out_path.type == "custom_model"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["outputs"]["component_out_path"]["job_output_type"] == "custom_model"

    def test_node_output_mode_promotion(self):
        component_yaml = components_dir / "helloworld_component.yml"
        params_override = [{"outputs": {"component_out_path": {"mode": "mount", "type": "uri_file"}}}]
        component_func1 = load_component(source=component_yaml, params_override=params_override)

        # without node level setting, node should have same type with component
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            # assert node1.outputs.component_out_path.mode == "mount"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        # assert pipeline_job1.outputs.component_out_path.mode == "mount"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["outputs"]["component_out_path"]["mode"] == "ReadWriteMount"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()
        # type will be preserved & mode will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "mode": "ReadWriteMount",
        }

        # when node level has setting, node should respect the setting
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            # assert node1.outputs.component_out_path.mode == "mount"
            node1.outputs.component_out_path.mode = "upload"
            assert node1.outputs.component_out_path.mode == "upload"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        # assert pipeline_job1.outputs.component_out_path.mode == "upload"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["outputs"]["component_out_path"]["mode"] == "Upload"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()
        # type will be preserved & mode will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "mode": "Upload",
        }

        # when pipeline level has setting, node should respect the setting
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            # assert node1.outputs.component_out_path.mode == "mount"
            node1.outputs.component_out_path.mode = "upload"
            assert node1.outputs.component_out_path.mode == "upload"
            return node1.outputs

        pipeline_job1 = my_pipeline()
        pipeline_job1.outputs.component_out_path.mode = "direct"
        assert pipeline_job1.outputs.component_out_path.mode == "direct"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["outputs"]["component_out_path"]["mode"] == "Direct"
        pipeline_dict = pipeline_job1._to_rest_object().as_dict()
        # type will be preserved & mode will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "mode": "Direct",
        }

        # when component has default mode & type, configuring it should keep them
        @dsl.pipeline()
        def my_pipeline():
            node1 = component_func1(component_in_number=1)
            # assert node1.outputs.component_out_path.mode == "mount"
            node1.outputs.component_out_path.path = "path"
            return node1.outputs

        pipeline_job1 = my_pipeline()

        pipeline_dict = pipeline_job1._to_rest_object().as_dict()
        # type will be preserved
        # mode will be dropped and leave it to service side resolve
        # path will be promoted to pipeline level
        assert pipeline_dict["properties"]["outputs"]["component_out_path"] == {
            "job_output_type": "uri_file",
            "uri": "path",
        }
        assert pipeline_dict["properties"]["jobs"]["node1"]["outputs"]["component_out_path"] == {
            "type": "literal",
            "value": "${{parent.outputs.component_out_path}}",
        }

    def test_validate_pipeline_node_io_name_has_keyword(self, caplog):
        # Refresh logger for pytest to capture log, otherwise the result is empty.
        from azure.ai.ml.dsl import _pipeline_component_builder

        _pipeline_component_builder.module_logger = logging.getLogger(__file__)
        with caplog.at_level(logging.WARNING):
            from test_configs.dsl_pipeline.pipeline_with_keyword_in_node_io.pipeline import pipeline_job

            # validation should pass
            assert pipeline_job._customized_validate().passed

        warning_template = (
            'Reserved word "{io_name}" is used as {io} name in node "{node_name}", '
            "can only be accessed with '{node_name}.{io}s[\"{io_name}\"]'"
        )
        assert caplog.messages == [
            warning_template.format(io_name="__contains__", io="output", node_name="node"),
            warning_template.format(io_name="items", io="output", node_name="upstream_node"),
            warning_template.format(io_name="keys", io="input", node_name="downstream_node"),
            warning_template.format(io_name="__hash__", io="output", node_name="pipeline_component_func"),
        ]

    def test_pass_pipeline_inpute_to_environment_variables(self):
        component_yaml = r"./tests/test_configs/components/helloworld_component_no_paths.yml"
        component_func = load_component(source=component_yaml)

        @dsl.pipeline(
            name="pass_pipeline_inpute_to_environment_variables",
        )
        def pipeline(job_in_number: int, environment_variables: str):
            hello_world_component = component_func(component_in_number=job_in_number)
            hello_world_component.environment_variables = environment_variables

        pipeline_job = pipeline()
        assert pipeline_job.jobs["hello_world_component"].environment_variables
        pipeline_dict = pipeline_job._to_rest_object().as_dict()["properties"]
        assert (
            pipeline_dict["jobs"]["hello_world_component"]["environment_variables"]
            == "${{parent.inputs.environment_variables}}"
        )

    def test_node_name_underscore(self):
        component_yaml = r"./tests/test_configs/components/helloworld_component_no_paths.yml"
        component_func = load_component(source=component_yaml)

        @dsl.pipeline()
        def my_pipeline():
            _ = component_func(component_in_number=1)

        pipeline_job = my_pipeline()
        assert pipeline_job.jobs.keys() == {"microsoftsamplescommandcomponentbasic_nopaths_test"}
        assert (
            pipeline_job.jobs["microsoftsamplescommandcomponentbasic_nopaths_test"].name
            == "microsoftsamplescommandcomponentbasic_nopaths_test"
        )

        @dsl.pipeline()
        def my_pipeline():
            _ = component_func(component_in_number=1)
            _ = component_func(component_in_number=2)

        pipeline_job = my_pipeline()
        assert pipeline_job.jobs.keys() == {
            "microsoftsamplescommandcomponentbasic_nopaths_test",
            "microsoftsamplescommandcomponentbasic_nopaths_test_1",
        }

        @dsl.pipeline()
        def my_pipeline():
            _ = component_func(component_in_number=1)
            component_func(component_in_number=2)
            _ = component_func(component_in_number=3)

        pipeline_job = my_pipeline()
        assert pipeline_job.jobs.keys() == {
            "microsoftsamplescommandcomponentbasic_nopaths_test",
            "microsoftsamplescommandcomponentbasic_nopaths_test_1",
            "microsoftsamplescommandcomponentbasic_nopaths_test_2",
        }

        @dsl.pipeline()
        def my_pipeline():
            _ = component_func(component_in_number=1)
            component_func(component_in_number=2)
            _ = component_func(component_in_number=3)
            node = component_func(component_in_number=4)

        pipeline_job = my_pipeline()
        assert pipeline_job.jobs.keys() == {"node", "node_1", "node_2", "node_3"}

        @dsl.pipeline()
        def my_pipeline():
            node = component_func(component_in_number=1)
            component_func(component_in_number=2)
            _ = component_func(component_in_number=3)
            component_func(component_in_number=4)

        pipeline_job = my_pipeline()
        assert pipeline_job.jobs.keys() == {"node", "node_1", "node_2", "node_3"}

    def test_pipeline_input_binding_limits_timeout(self):
        component_yaml = r"./tests/test_configs/components/helloworld_component_no_paths.yml"
        component_func = load_component(source=component_yaml)

        @dsl.pipeline
        def my_pipeline(timeout) -> PipelineJob:
            # case 1: if timeout is PipelineInput
            node_0 = component_func(component_in_number=1)
            node_0.set_limits(timeout=timeout)
            # case 2: if timeout is not PipelineInput
            node_1 = component_func(component_in_number=1)
            node_1.set_limits(timeout=1)

        pipeline = my_pipeline(2)
        pipeline.settings.default_compute = "cpu-cluster"
        pipeline_dict = pipeline._to_rest_object().as_dict()
        assert pipeline_dict["properties"]["jobs"]["node_0"]["limits"]["timeout"] == "${{parent.inputs.timeout}}"
        assert pipeline_dict["properties"]["jobs"]["node_1"]["limits"]["timeout"] == "PT1S"

    @pytest.mark.parametrize(
        "component_path, fields_to_test, fake_inputs",
        [
            pytest.param(
                "./tests/test_configs/components/helloworld_component.yml",
                {
                    "resources.instance_count": JobResourceConfiguration(instance_count=1),
                    # do not support data binding expression on queue_settings as it involves value mapping in
                    # _to_rest_object
                    # "queue_settings.priority": QueueSettings(priority="low"),
                },
                {},
                id="command",
            ),
            pytest.param(
                "./tests/test_configs/components/basic_parallel_component_score.yml",
                {
                    "resources.instance_count": JobResourceConfiguration(instance_count=1),
                },
                {},
                id="parallel.resources",
            ),
            pytest.param(
                "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml",
                {
                    "resources.runtime_version": SparkResourceConfiguration(runtime_version="2.4"),
                    # seems that `type` is the only field for `identity` and hasn't been exposed to user
                    # "identity.type": AmlTokenConfiguration(),
                    # spark.entry doesn't support overwrite from node level for now, more details in
                    # entities._builders.spark.Spark.__init__, around line 211
                    # "entry.entry": SparkJobEntry(entry="main.py"),
                },
                {
                    "file_input": Input(path="./tests/test_configs/data"),
                },
                id="spark",
            ),
        ],
    )
    def test_data_binding_expression_on_node_runsettings(
        self, component_path: str, fields_to_test: Dict[str, Any], fake_inputs: Dict[str, Input]
    ):
        component = load_component(component_path)

        @dsl.pipeline()
        def pipeline_func(param: str = "2"):
            node = component(**fake_inputs)
            for field, value in fields_to_test.items():
                attr, sub_attr = field.split(".")
                setattr(node, attr, value)
                setattr(getattr(node, attr), sub_attr, param)

        pipeline_job: PipelineJob = pipeline_func()
        rest_object = pipeline_job._to_rest_object()
        regenerated_job = PipelineJob._from_rest_object(rest_object)
        expected_dict, actual_dict = pipeline_job._to_dict(), regenerated_job._to_dict()

        # TODO: node level task is not necessary and with issue in serialization/de-serialization
        for skip_dot_key in ["jobs.node.task.code"]:
            pydash.set_(expected_dict, skip_dot_key, "placeholder")
            pydash.set_(actual_dict, skip_dot_key, "placeholder")
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

    def test_get_predecessors(self):
        component_yaml = components_dir / "2in2out.yaml"
        component_func = load_component(source=component_yaml)

        # case1.1: predecessor from same node
        @dsl.pipeline()
        def pipeline1():
            node1 = component_func()
            node1.name = "node1"
            assert get_predecessors(node1) == []
            node2 = component_func(input1=node1.outputs.output1, input2=node1.outputs.output2)
            assert ["node1"] == [n.name for n in get_predecessors(node2)]
            return node1.outputs

        pipeline1()

        # case1.2: predecessor from different node
        @dsl.pipeline()
        def pipeline2():
            node1 = component_func()
            node1.name = "node1"
            assert get_predecessors(node1) == []

            node2 = component_func()
            node2.name = "node2"
            assert get_predecessors(node2) == []

            node2 = component_func(input1=node1.outputs.output1, input2=node2.outputs.output2)
            assert ["node1", "node2"] == [n.name for n in get_predecessors(node2)]
            return node2.outputs

        pipeline2()

        # case 2.1: predecessor from same sub pipeline
        @dsl.pipeline()
        def pipeline3():
            sub1 = pipeline1()
            node3 = component_func(input1=sub1.outputs.output1, input2=sub1.outputs.output2)
            assert ["node1"] == [n.name for n in get_predecessors(node3)]

        pipeline3()

        # case 2.2: predecessor from different sub pipeline
        @dsl.pipeline()
        def pipeline4():
            sub1 = pipeline1()
            sub2 = pipeline2()
            node3 = component_func(input1=sub1.outputs.output1, input2=sub2.outputs.output2)
            assert ["node1", "node2"] == [n.name for n in get_predecessors(node3)]

        pipeline4()

        # case 3.1: predecessor from different outer node
        @dsl.pipeline()
        def sub_pipeline_1(input1: Input, input2: Input):
            node1 = component_func(input1=input1, input2=input2)
            assert ["outer1", "outer2"] == [n.name for n in get_predecessors(node1)]

        @dsl.pipeline()
        def pipeline5():
            outer1 = component_func()
            outer1.name = "outer1"
            outer2 = component_func()
            outer2.name = "outer2"
            sub_pipeline_1(input1=outer1.outputs.output1, input2=outer2.outputs.output2)

        pipeline5()

        # case 3.2: predecessor from same outer node
        @dsl.pipeline()
        def sub_pipeline_2(input1: Input, input2: Input):
            node1 = component_func(input1=input1, input2=input2)
            assert ["outer1"] == [n.name for n in get_predecessors(node1)]

        @dsl.pipeline()
        def pipeline6():
            outer1 = component_func()
            outer1.name = "outer1"
            sub_pipeline_2(input1=outer1.outputs.output1, input2=outer1.outputs.output2)

        pipeline6()

        # case 3.3: predecessor from outer literal value
        @dsl.pipeline()
        def sub_pipeline_3(input1: Input, input2: Input):
            node1 = component_func(input1=input1, input2=input2)
            assert [] == [n.name for n in get_predecessors(node1)]

        @dsl.pipeline()
        def pipeline7():
            sub_pipeline_3(input1=Input(), input2=Input())

        pipeline7()

        # case 3.4: predecessor from outer subgraph
        @dsl.pipeline()
        def sub_pipeline_4(input1: Input, input2: Input):
            node1 = component_func(input1=input1, input2=input2)
            assert ["node1", "node2"] == [n.name for n in get_predecessors(node1)]

        @dsl.pipeline()
        def pipeline8():
            sub1 = pipeline1()
            sub2 = pipeline2()
            sub_pipeline_4(input1=sub1.outputs.output1, input2=sub2.outputs.output2)

        pipeline8()

    def test_pipeline_singularity_strong_type(self, mock_singularity_arm_id: str):
        component_yaml = "./tests/test_configs/components/helloworld_component_singularity.yml"
        component_func = load_component(component_yaml)

        instance_type = "Singularity.ND40rs_v2"

        @dsl.pipeline
        def pipeline_func():
            # basic job_tier + Low priority
            basic_low_node = component_func()
            basic_low_node.resources = JobResourceConfiguration(instance_count=2, instance_type=instance_type)
            basic_low_node.queue_settings = QueueSettings(job_tier="basic", priority="low")
            # standard job_tier + Medium priority
            standard_medium_node = component_func()
            standard_medium_node.resources = JobResourceConfiguration(instance_count=2, instance_type=instance_type)
            standard_medium_node.queue_settings = QueueSettings(job_tier="standard", priority="medium")
            # premium job_tier + High priority
            premium_high_node = component_func()
            premium_high_node.resources = JobResourceConfiguration(instance_count=2, instance_type=instance_type)
            premium_high_node.queue_settings = QueueSettings(job_tier="premium", priority="high")
            # properties
            node_with_properties = component_func()
            properties = {"Singularity": {"imageVersion": "", "interactive": False}}
            node_with_properties.resources = JobResourceConfiguration(
                instance_count=2, instance_type=instance_type, properties=properties
            )

        pipeline_job = pipeline_func()
        pipeline_job.settings.default_compute = mock_singularity_arm_id

        pipeline_job_dict = pipeline_job._to_rest_object().as_dict()
        # basic job_tier + Low priority
        basic_low_node_dict = pipeline_job_dict["properties"]["jobs"]["basic_low_node"]
        assert basic_low_node_dict["queue_settings"] == {"job_tier": "Basic", "priority": 1}
        assert basic_low_node_dict["resources"] == {"instance_count": 2, "instance_type": instance_type}
        # standard job_tier + Medium priority
        standard_medium_node_dict = pipeline_job_dict["properties"]["jobs"]["standard_medium_node"]
        assert standard_medium_node_dict["queue_settings"] == {"job_tier": "Standard", "priority": 2}
        assert standard_medium_node_dict["resources"] == {"instance_count": 2, "instance_type": instance_type}
        # premium job_tier + High priority
        premium_high_node_dict = pipeline_job_dict["properties"]["jobs"]["premium_high_node"]
        assert premium_high_node_dict["queue_settings"] == {"job_tier": "Premium", "priority": 3}
        assert premium_high_node_dict["resources"] == {"instance_count": 2, "instance_type": instance_type}
        # properties
        node_with_properties_dict = pipeline_job_dict["properties"]["jobs"]["node_with_properties"]
        assert node_with_properties_dict["resources"] == {
            "instance_count": 2,
            "instance_type": instance_type,
            # the mapping Singularity => AISuperComputer is expected
            "properties": {"AISuperComputer": {"imageVersion": "", "interactive": False}},
        }
