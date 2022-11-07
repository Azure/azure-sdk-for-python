import os
from io import StringIO
from pathlib import Path
from unittest import mock
from unittest.mock import patch

import pydash
import pytest
from test_configs.dsl_pipeline import data_binding_expression
from test_utilities.utils import omit_with_wildcard, prepare_dsl_curated

from azure.ai.ml import Input, MLClient, MpiDistribution, Output, command, dsl, load_component, load_job, spark, \
    AmlTokenConfiguration, UserIdentityConfiguration, ManagedIdentityConfiguration
from azure.ai.ml._restclient.v2022_05_01.models import ComponentContainerData, ComponentContainerDetails, SystemData
from azure.ai.ml.constants._common import (
    AZUREML_PRIVATE_FEATURES_ENV_VAR,
    AZUREML_RESOURCE_PROVIDER,
    NAMED_RESOURCE_ID_FORMAT,
    VERSIONED_RESOURCE_ID_FORMAT,
    AssetTypes,
    AzureMLResourceType,
)
from azure.ai.ml.entities import (
    Component,
    Data,
    JobResourceConfiguration,
    PipelineJob,
)
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function
from azure.ai.ml.exceptions import UserErrorException, ValidationException, ParamValueNotExistsError

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
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

        # un-configured output is None
        assert pipeline1._build_outputs() == {"pipeline_output": None}

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
            hello_world_component_1.outputs.component_out_path.mode = "Upload"
            hello_world_component_2.outputs.component_out_path.mode = "Upload"

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
            "display_name": None,
            "distribution": None,
            "environment_variables": {},
            "inputs": {
                "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
            },
            "limits": None,
            "name": "hello_world_component_1",
            "outputs": {"component_out_path": {"job_output_type": "uri_folder", "mode": "Upload"}},
            "resources": None,
            "tags": {},
            "type": "command",
        }
        omit_fields = ["componentId", "properties"]
        assert pydash.omit(component_from_dsl._to_rest_object(), *omit_fields) == expected_component
        assert pydash.omit(component_from_sdk._to_rest_object(), *omit_fields) == expected_component
        expected_component.update({"_source": "REMOTE.WORKSPACE.COMPONENT"})
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
                    "azure.ai.ml._restclient.v2022_05_01.operations.ComponentVersionsOperations.create_or_update",
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

    def test_command_function_reuse(self, mock_machinelearning_client: MLClient):
        path = "./tests/test_configs/components/helloworld_component.yml"
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
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
                        "resources": None,
                        "distribution": None,
                        "limits": None,
                        "environment_variables": {},
                        "name": "train_with_sample_data",
                        "display_name": None,
                        "tags": {},
                        "computeId": None,
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
                        "resources": None,
                        "distribution": None,
                        "limits": None,
                        "environment_variables": {},
                        "name": "train_with_sample_data",
                        "display_name": None,
                        "tags": {},
                        "computeId": None,
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
                        "resources": None,
                        "distribution": None,
                        "limits": None,
                        "environment_variables": {},
                        "name": "train_with_sample_data",
                        "display_name": None,
                        "tags": {},
                        "computeId": None,
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
                "outputs": {"trained_model": {"job_output_type": "uri_folder"}},
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
                        "resources": None,
                        "distribution": None,
                        "limits": None,
                        "environment_variables": {},
                        "name": "train_with_sample_data",
                        "display_name": None,
                        "tags": {},
                        "computeId": None,
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
            "tags": {},
            "inputs": {"component_in_number": {"type": "integer"}, "component_in_path": {"type": "string"}},
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
            "type": "pipeline",
            "jobs": {
                "node1": {
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
                    "type": "command",
                },
                "node2": {
                    "environment_variables": {},
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
            "tags": {},
            "properties": {},
            "type": "pipeline",
            "settings": {},
            "inputs": {"component_in_number": 1, "component_in_path": "test"},
            "outputs": {"sub_pipeline_out": None},
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
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
                        "resources": None,
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "limits": None,
                        "environment_variables": {},
                        "name": "train_with_sample_data",
                        "display_name": None,
                        "tags": {},
                        "computeId": None,
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
                        "display_name": None,
                        "tags": {},
                        "computeId": None,
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
                            "trained_model": {
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
            "tags": {},
            "inputs": {"component_in_number": {"type": "integer"}, "component_in_path": {"type": "string"}},
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
            "type": "pipeline",
            "jobs": {
                "node1": {
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
                    "type": "command",
                },
                "node2": {
                    "environment_variables": {},
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
            "tags": {},
            "properties": {},
            "type": "pipeline",
            "settings": {},
            "inputs": {"component_in_number": 1, "component_in_path": "test"},
            "outputs": {"sub_pipeline_out": None},
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
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
            "tags": {},
            "inputs": {"component_in_number": {"type": "integer"}, "component_in_path": {"type": "string"}},
            "outputs": {"sub_pipeline_out": {"type": "uri_folder"}},
            "type": "pipeline",
            "jobs": {
                "node1": {
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
                    "type": "command",
                },
                "node2": {
                    "environment_variables": {},
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
            "tags": {},
            "properties": {},
            "type": "pipeline",
            "settings": {},
            "inputs": {"component_in_number": 1, "component_in_path": "test"},
            "outputs": {"sub_pipeline_out": None},
            "jobs": {
                "node1": {
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
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
            node1 = component_func(
                component_in_number=1, component_in_path=component_in_path
            )
            node1.identity = AmlTokenConfiguration()

            node2 = component_func(
                component_in_number=1, component_in_path=component_in_path
            )
            node2.identity = UserIdentityConfiguration()

            node3 = component_func(
                component_in_number=1, component_in_path=component_in_path
            )
            node3.identity = ManagedIdentityConfiguration()

        pipeline = pipeline_func(component_in_path=Data(name="test", version="1", type=AssetTypes.MLTABLE))
        omit_fields = [
            "jobs.*.componentId",
            "jobs.*._source"
        ]
        actual_dict = omit_with_wildcard(pipeline._to_rest_object().as_dict()["properties"], *omit_fields)

        assert actual_dict["jobs"] == {
            'node1': {'computeId': None,
                      'display_name': None,
                      'distribution': None,
                      'environment_variables': {},
                      'identity': {'type': 'aml_token'},
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '1'},
                                 'component_in_path': {'job_input_type': 'literal',
                                                       'value': '${{parent.inputs.component_in_path}}'}},
                      'limits': None,
                      'name': 'node1',
                      'outputs': {},
                      'properties': {},
                      'resources': None,
                      'tags': {},
                      'type': 'command'},
            'node2': {'computeId': None,
                      'display_name': None,
                      'distribution': None,
                      'identity': {'type': 'user_identity'},
                      'environment_variables': {},
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '1'},
                                 'component_in_path': {'job_input_type': 'literal',
                                                       'value': '${{parent.inputs.component_in_path}}'}},
                      'limits': None,
                      'name': 'node2',
                      'outputs': {},
                      'properties': {},
                      'resources': None,
                      'tags': {},
                      'type': 'command'},
            'node3': {'computeId': None,
                      'display_name': None,
                      'distribution': None,
                      'environment_variables': {},
                      'identity': {'type': 'managed_identity'},
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '1'},
                                 'component_in_path': {'job_input_type': 'literal',
                                                       'value': '${{parent.inputs.component_in_path}}'}},
                      'limits': None,
                      'name': 'node3',
                      'outputs': {},
                      'properties': {},
                      'resources': None,
                      'tags': {},
                      'type': 'command'}
        }

    def test_pipeline_with_non_pipeline_inputs(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": "component_name_1"}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": "component_name_2"}])

        @dsl.pipeline(non_pipeline_inputs=["other_params", "is_add_component"])
        def pipeline_func(job_in_number, job_in_path, other_params, is_add_component):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=other_params, component_in_path=job_in_path)
            if is_add_component:
                component_func2(component_in_number=other_params, component_in_path=job_in_path)

        pipeline = pipeline_func(10, Input(path="/a/path/on/ds"), 15, False)
        assert len(pipeline.jobs) == 2
        assert "other_params" not in pipeline.inputs
        assert isinstance(pipeline.jobs[component_func1.name].inputs["component_in_number"]._data, PipelineInput)
        assert pipeline.jobs[component_func2.name].inputs["component_in_number"]._data == 15

        pipeline = pipeline_func(10, Input(path="/a/path/on/ds"), 15, True)
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
        assert "pipeline_func() got unexpected params in non_pipeline_inputs ['non_exist_param1', 'non_exist_param2']" in str(error_info)

    def test_component_func_as_non_pipeline_inputs(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": "component_name_1"}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": "component_name_2"}])

        @dsl.pipeline(non_pipeline_inputs=["component_func"])
        def pipeline_func(job_in_number, job_in_path, component_func):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func(component_in_number=job_in_number, component_in_path=job_in_path)

        pipeline = pipeline_func(
            job_in_number=10,
            job_in_path=Input(path="/a/path/on/ds"),
            component_func=component_func2)
        assert len(pipeline.jobs) == 2
        assert component_func2.name in pipeline.jobs
