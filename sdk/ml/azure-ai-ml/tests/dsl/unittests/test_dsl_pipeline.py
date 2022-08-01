import os
from io import StringIO
import pydash
import pytest
from pathlib import Path
from unittest import mock
from unittest.mock import patch
from typing import Callable

from azure.ai.ml import dsl, command, MLClient, Input, Output, load_component, load_job

# from azure.ai.ml.entities._builders.parallel_func import parallel_run_function
from azure.ai.ml import MpiDistribution
from azure.ai.ml.automl import classification, regression
from azure.ai.ml.dsl._load_import import to_component
from azure.ai.ml.entities import (
    PipelineJob,
    Component,
    ResourceConfiguration,
    CommandJob,
    CommandComponent,
    ParallelTask,
)
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.parallel import RunFunction, ParallelJob, parallel_run_function
from azure.ai.ml.entities._job.automl.tabular import ClassificationJob
from azure.ai.ml.sweep import (
    Choice,
    BanditPolicy,
    Randint,
    QUniform,
    QLogNormal,
    QLogUniform,
    QNormal,
    LogNormal,
    LogUniform,
    Normal,
    Uniform,
)
from azure.ai.ml.entities._builders import Command, Parallel
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml.constants import (
    AssetTypes,
    InputOutputModes,
    NAMED_RESOURCE_ID_FORMAT,
    AZUREML_RESOURCE_PROVIDER,
    AzureMLResourceType,
    VERSIONED_RESOURCE_ID_FORMAT,
    AZUREML_PRIVATE_FEATURES_ENV_VAR,
)
from azure.ai.ml.entities._builders import Sweep
from azure.ai.ml._ml_exceptions import ValidationException


from test_utilities.utils import prepare_dsl_curated, omit_with_wildcard
from test_configs.dsl_pipeline import data_binding_expression
from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


def mock_create_job(job, *args, **kwargs):
    return job


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestDSLPipeline:
    def test_dsl_pipeline(self) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline_no_arg():
            component_func = load_component(path=path)
            component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline1 = pipeline_no_arg()
        assert len(pipeline1.component.jobs) == 1, pipeline1.component.jobs

    def test_dsl_pipeline_name_and_display_name(self):
        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(path=hello_world_component_yaml)

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
        hello_world_component_func = load_component(path=hello_world_component_yaml)

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

    def test_dsl_pipeline_sweep_node(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline(name="train_with_sweep_in_pipeline", default_compute="cpu-cluster")
        def train_with_sweep_in_pipeline(raw_data, primary_metric: str = "AUC", max_total_trials: int = 10):
            component_to_sweep: CommandComponent = load_component(path=yaml_file)
            cmd_node1: Command = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            )

            sweep_job1: Sweep = cmd_node1.sweep(
                primary_metric="AUC",  # primary_metric,
                goal="maximize",
                sampling_algorithm="random",
            )
            sweep_job1.compute = "gpu-cluster"
            sweep_job1.set_limits(max_total_trials=10)  # max_total_trials

            cmd_node2: Command = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            )
            sweep_job2: Sweep = cmd_node2.sweep(
                primary_metric="AUC",
                goal="minimize",
                sampling_algorithm="random",
                max_total_trials=10,
            )
            sweep_job2.compute = "gpu-cluster"

            sweep_job3: Sweep = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            ).sweep(
                primary_metric="accuracy",
                goal="maximize",
                sampling_algorithm="random",
                max_total_trials=10,
            )

            component_to_link = load_component(path=yaml_file, params_override=[{"name": "node_to_link"}])
            link_node = component_to_link(
                component_in_number=2, component_in_path=sweep_job1.outputs.component_out_path
            )

            return {
                "pipeline_job_best_model1": sweep_job1.outputs.component_out_path,
                "pipeline_job_best_model2": sweep_job2.outputs.component_out_path,
                "pipeline_job_best_model3": sweep_job3.outputs.component_out_path,
                "pipeline_model_test_result": link_node.outputs.component_out_path,
            }

        pipeline: PipelineJob = train_with_sweep_in_pipeline(
            raw_data=Input(path="/a/path/on/ds", mode="ro_mount"), max_total_trials=100, primary_metric="accuracy"
        )
        assert len(pipeline.jobs) == 4, f"Expect 4 nodes are collected but got {len(pipeline.jobs)}"
        assert pipeline.component._source == "DSL"
        assert pipeline.component._job_types == {"sweep": 3, "command": 1}
        assert pipeline.component._job_sources == {"YAML.COMPONENT": 4}

        sweep_node: Sweep = pipeline.jobs["sweep_job1"]
        sweep_node.component._id = "azureml:test_component:1"
        sweep_node_dict = sweep_node._to_dict()
        assert pydash.get(sweep_node_dict, "limits.max_total_trials", None) == 10
        sweep_node_rest_obj = sweep_node._to_rest_object()
        sweep_node_dict_from_rest = Sweep._from_rest_object(sweep_node_rest_obj)._to_dict()
        omit_fields = ["trial"]
        assert pydash.omit(sweep_node_dict, *omit_fields) == pydash.omit(sweep_node_dict_from_rest, *omit_fields)

        pipeline_dict = pipeline._to_dict()
        for dot_key, expected_value in [
            ("jobs.sweep_job2.objective.goal", "minimize"),
            ("jobs.sweep_job3.objective.goal", "maximize"),
            ("jobs.sweep_job2.objective.primary_metric", "AUC"),
            ("jobs.sweep_job3.objective.primary_metric", "accuracy"),
            ("jobs.sweep_job2.compute", "azureml:gpu-cluster"),
            ("jobs.sweep_job3.compute", None),
        ]:
            assert (
                pydash.get(pipeline_dict, dot_key) == expected_value
            ), f"Expect {dot_key} to be {expected_value} but got {pydash.get(pipeline_dict, dot_key)}"

        pipeline_rest_obj = pipeline._to_rest_object()
        pipeline_regenerated_from_rest = PipelineJob._load_from_rest(pipeline_rest_obj)
        omit_fields = [
            "name",
            "display_name",
            "jobs.*.trial",
            "outputs",  # TODO: figure out why outputs can't be regenerated correctly
        ]
        assert omit_with_wildcard(pipeline_dict, *omit_fields) == omit_with_wildcard(
            pipeline_regenerated_from_rest._to_dict(), *omit_fields
        )

    def test_dsl_pipeline_sweep_distributions(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component_for_sweep.yml"

        @dsl.pipeline(name="OneJob_RuntimeSweepWithFullSearchSpaces")
        def train_with_sweep_in_pipeline():
            component_to_sweep: CommandComponent = load_component(path=yaml_file)
            cmd_node1: Command = component_to_sweep(
                batch_size=Choice([25, 35]),
                first_layer_neurons=Randint(upper=50),
                second_layer_neurons=QUniform(min_value=10, max_value=50, q=5),
                third_layer_neurons=QLogNormal(mu=5, sigma=1, q=5),
                epochs=QLogUniform(min_value=1, max_value=5, q=5),
                momentum=QNormal(mu=10, sigma=5, q=2),
                weight_decay=LogNormal(mu=0, sigma=1),
                learning_rate=LogUniform(min_value=-6, max_value=-1),
                f1=Normal(mu=0, sigma=1),
                f2=Uniform(min_value=10, max_value=20),
                data_folder=Input(
                    type=AssetTypes.MLTABLE,
                    path="https://dprepdata.blob.core.windows.net/demo/",
                    mode=InputOutputModes.RO_MOUNT,
                ),
            )

            hello_sweep: Sweep = cmd_node1.sweep(
                primary_metric="validation_acc",
                goal="maximize",
                sampling_algorithm="random",
            )
            hello_sweep.compute = "cpu-cluster"
            hello_sweep.set_limits(max_total_trials=2, max_concurrent_trials=3, timeout=600)
            hello_sweep.early_termination = BanditPolicy(evaluation_interval=2, slack_factor=0.1, delay_evaluation=1)

        dsl_pipeline: PipelineJob = train_with_sweep_in_pipeline()
        dsl_pipeline.jobs["hello_sweep"].outputs.trained_model_dir = Output(
            type=AssetTypes.MLFLOW_MODEL, mode=InputOutputModes.RW_MOUNT
        )

        sweep_node: Sweep = dsl_pipeline.jobs["hello_sweep"]
        random_seed_input = sweep_node.inputs["random_seed"]._meta
        assert random_seed_input
        assert random_seed_input.default == 42
        sweep_node.component._id = "azureml:test_component:1"
        sweep_node_dict = sweep_node._to_dict()
        sweep_node_rest_obj = sweep_node._to_rest_object()
        sweep_node_dict_from_rest = Sweep._from_rest_object(sweep_node_rest_obj)._to_dict()
        omit_fields = ["trial"]
        assert pydash.omit(sweep_node_dict, *omit_fields) == pydash.omit(sweep_node_dict_from_rest, *omit_fields)

    def test_dsl_pipeline_with_parallel(self) -> None:
        yaml_file = "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml"

        @dsl.pipeline(default_compute="cpu-cluster")
        def train_with_parallel_in_pipeline():
            parallel_component: ParallelComponent = load_component(path=yaml_file)
            node1: Parallel = parallel_component(
                job_data_path=Input(type=AssetTypes.MLTABLE, path="/a/path/on/ds", mode=InputOutputModes.EVAL_MOUNT),
            )
            node1.resources = {"instance_count": 2}

        dsl_pipeline: PipelineJob = train_with_parallel_in_pipeline()
        dsl_pipeline.jobs["node1"].outputs.job_output_path = Output(
            type=AssetTypes.MLFLOW_MODEL, mode=InputOutputModes.RW_MOUNT
        )

        parallel_node: Parallel = dsl_pipeline.jobs["node1"]
        job_data_path_input = parallel_node.inputs["job_data_path"]._meta
        assert job_data_path_input
        parallel_node.component._id = "azureml:test_component:1"
        parallel_node_dict = parallel_node._to_dict()

        parallel_node_rest_obj = parallel_node._to_rest_object()
        parallel_node_dict_from_rest = Parallel._from_rest_object(parallel_node_rest_obj)._to_dict()
        omit_fields = ["component"]
        assert pydash.omit(parallel_node_dict, *omit_fields) == pydash.omit(parallel_node_dict_from_rest, *omit_fields)

    def test_dsl_pipeline_distribution_as_command_inputs(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline(name="train_with_sweep_in_pipeline")
        def train_with_sweep_in_pipeline(raw_data):
            component_to_sweep: CommandComponent = load_component(path=yaml_file)
            cmd_node1 = component_to_sweep(component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data)
            return {
                "pipeline_job_model": cmd_node1.outputs.component_out_path,
            }

        pipeline = train_with_sweep_in_pipeline(raw_data=Input(path="/a/path/on/ds"))
        validate_result = pipeline._validate()
        assert validate_result.messages == {
            "jobs.cmd_node1.inputs.component_in_number": "Input of command cmd_node1 is a SweepDistribution, please use command.sweep to transform the command into a sweep node.",
            "jobs.cmd_node1.compute": "Compute not set",
        }

    def test_dsl_pipeline_input_output(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(number, path):
            component_func = load_component(path=yaml_file)
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
            component_func = load_component(path=yaml_file)
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
        pipeline_job = load_job(path=job_yaml)

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
        assert pipeline_job._build_outputs() == actual_outputs

        component_job = next(iter(pipeline_job.jobs.values()))._to_rest_object()
        component = next(iter(pipeline.jobs.values()))._to_rest_object()

        omit_fields = ["componentId", "_source"]
        actual_component = pydash.omit(component_job, *omit_fields)
        expected_component = pydash.omit(component, *omit_fields)
        assert actual_component == expected_component

    def test_dsl_pipeline_to_job(self) -> None:
        component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(path=component_yaml)

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
        pipeline_job_dict = load_job(path=job_yaml)._to_rest_object().as_dict()

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
        component_func = load_component(path=component_yaml)

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
            hello_world_component_2.resources = ResourceConfiguration()
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
        pipeline_job_dict = load_job(path=job_yaml)._to_rest_object().as_dict()

        omit_fields = ["name", "properties.display_name", "properties.jobs.*._source", "properties.settings._source"]
        dsl_pipeline_job = omit_with_wildcard(dsl_pipeline_job_dict, *omit_fields)
        yaml_pipeline_job = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert dsl_pipeline_job == yaml_pipeline_job

    def test_pipeline_variable_name(self):
        component_yaml = "./tests/test_configs/components/helloworld_component_no_paths.yml"
        component_func1 = load_component(path=component_yaml)
        component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        component_func2 = load_component(path=component_yaml)

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
        hello_world_component_func = load_component(path=hello_world_component_yaml)

        merge_outputs_component_yaml = "./tests/test_configs/components/merge_outputs_component.yml"
        merge_outputs_component_func = load_component(path=merge_outputs_component_yaml)

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
        pipeline_job_from_yaml = load_job(path="./tests/test_configs/pipeline_jobs/sample_pipeline_job.yml")

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
                    component=load_component(path=hello_world_component_yaml_path),
                    name="hello_world_component_1",
                    compute="cpu-cluster",
                    inputs={
                        "component_in_number": "${{parent.inputs.job_in_number}}",
                        "component_in_path": "${{parent.inputs.job_in_path}}",
                    },
                    outputs={"component_out_path": Output(mode="upload")},
                ),
                "hello_world_component_2": Command(
                    component=load_component(path=hello_world_component_yaml_path),
                    name="hello_world_component_2",
                    compute="cpu-cluster",
                    inputs={
                        "component_in_number": "${{parent.inputs.job_in_number}}",
                        "component_in_path": "${{parent.inputs.job_in_path}}",
                    },
                    outputs={"component_out_path": Output(mode="upload")},
                    resources=ResourceConfiguration(instance_count=2),
                ),
                "merge_component_outputs": Command(
                    component=load_component(path=merge_outputs_component_yaml_path),
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
        hello_world_component_func = load_component(path=hello_world_component_yaml_path)

        merge_outputs_component_func = load_component(path=merge_outputs_component_yaml_path)

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
            hello_world_component_2.resources = ResourceConfiguration()
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

    def test_pipeline_str(self):
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            component_func = load_component(path=path)
            component_func(component_in_number=component_in_number, component_in_path=component_in_path)

        test_job_input = Input(path="azureml:fake_data:1")
        pipeline1 = pipeline(10, test_job_input)
        assert str(pipeline1)
        pipeline2 = pipeline(None, None)
        validate_result = pipeline2._validate()
        assert validate_result.passed is False
        assert validate_result.messages == {
            "jobs.microsoftsamples_command_component_basic.compute": "Compute not set",
            "inputs.component_in_path": "Required input 'component_in_path' for pipeline 'pipeline' not provided.",
        }

    def test_pipeline_with_comma_after_pipeline_input_brackets(self):
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            component_func = load_component(path=path)
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
        component_func = load_component(path=yaml_file)

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

            component_entity = load_component(path=yaml_file, params_override=[{"name": "hello_world_component_1"}])
            component_func = _generate_component_function(component_entity)

            job_in_number = PipelineInput(name="job_in_number", owner="pipeline", meta=None)
            job_in_path = PipelineInput(name="job_in_path", owner="pipeline", meta=None)
            component_from_dsl = component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            component_from_dsl.compute = "cpu-cluster"
            component_from_dsl.outputs.component_out_path.mode = "upload"
            component_from_dsl.name = "hello_world_component_1"

            # YAML
            pipeline = load_job(path="./tests/test_configs/pipeline_jobs/sample_pipeline_job.yml")
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
                "component_in_number": {"job_input_type": "Literal", "value": "${{parent.inputs.job_in_number}}"},
                "component_in_path": {"job_input_type": "Literal", "value": "${{parent.inputs.job_in_path}}"},
            },
            "limits": None,
            "name": "hello_world_component_1",
            "outputs": {"component_out_path": {"job_output_type": "UriFolder", "mode": "Upload"}},
            "resources": None,
            "tags": {},
        }
        omit_fields = "componentId"
        assert pydash.omit(component_from_dsl._to_rest_object(), omit_fields) == expected_component
        assert pydash.omit(component_from_sdk._to_rest_object(), omit_fields) == expected_component
        expected_component.update({"_source": "REMOTE.WORKSPACE.COMPONENT"})
        assert pydash.omit(component_from_rest._to_rest_object(), omit_fields) == expected_component
        expected_component.update({"_source": "YAML.JOB"})
        assert pydash.omit(component_from_yaml._to_rest_object(), omit_fields) == expected_component

    def test_pipeline_with_command_function(self):
        # component func
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(path=yaml_file)

        # command job with dict distribution
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        expected_resources = {"instance_count": 2}
        expected_environment_variables = {"key": "val"}
        inputs = {
            "component_in_path": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
            "component_in_number": 0.01,
        }
        outputs = {"component_out_path": Output(type="mlflow_model", mode="rw_mount")}

        command_job = CommandJob(
            display_name="my-evaluate-job",
            environment=environment,
            command='echo "hello world"',
            distribution={"type": "Pytorch", "process_count_per_instance": 2},
            resources=expected_resources,
            environment_variables=expected_environment_variables,
            inputs=inputs,
            outputs=outputs,
        )
        command_job_func = to_component(job=command_job)

        # Command from command() function
        command_function = command(
            display_name="my-evaluate-job",
            environment=environment,
            command='echo "hello world"',
            distribution={"type": "Pytorch", "process_count_per_instance": 2},
            resources=expected_resources,
            environment_variables=expected_environment_variables,
            inputs=inputs,
            outputs=outputs,
        )

        data = Input(type=AssetTypes.URI_FOLDER, path="/a/path/on/ds", mode="ro_mount")

        @dsl.pipeline(experiment_name="test_pipeline_with_command_function")
        def pipeline(number, path):
            node1 = component_func(component_in_number=number, component_in_path=path)
            node2 = command_job_func(component_in_number=number, component_in_path=node1.outputs.component_out_path)
            node3 = command_function(component_in_number=number, component_in_path=node2.outputs.component_out_path)
            return {
                "pipeline_output1": node1.outputs.component_out_path,
                "pipeline_output2": node2.outputs.component_out_path,
                "pipeline_output3": node3.outputs.component_out_path,
            }

        omit_fields = [
            "name",
            "properties.jobs.node1.componentId",
            "properties.jobs.node2.componentId",
            "properties.jobs.node3.componentId",
        ]

        pipeline1 = pipeline(10, data)
        pipeline_job1 = pipeline1._to_rest_object().as_dict()
        pipeline_job1 = pydash.omit(pipeline_job1, omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_command_function",
                "inputs": {
                    "number": {"job_input_type": "Literal", "value": "10"},
                    "path": {"job_input_type": "UriFolder", "mode": "ReadOnlyMount", "uri": "/a/path/on/ds"},
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "node1": {
                        "_source": "YAML.COMPONENT",
                        "computeId": None,
                        "display_name": None,
                        "distribution": None,
                        "environment_variables": {},
                        "inputs": {
                            "component_in_number": {"job_input_type": "Literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {"job_input_type": "Literal", "value": "${{parent.inputs.path}}"},
                        },
                        "limits": None,
                        "name": "node1",
                        "outputs": {
                            "component_out_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_output1}}"}
                        },
                        "resources": None,
                        "tags": {},
                    },
                    "node2": {
                        "_source": "CLASS",
                        "computeId": None,
                        "display_name": None,
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {},
                        "inputs": {
                            "component_in_number": {"job_input_type": "Literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {
                                "job_input_type": "Literal",
                                "value": "${{parent.jobs.node1.outputs.component_out_path}}",
                            },
                        },
                        "limits": None,
                        "name": "node2",
                        "outputs": {
                            "component_out_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_output2}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                    },
                    "node3": {
                        "_source": "BUILDER",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {"key": "val"},
                        "inputs": {
                            "component_in_number": {"job_input_type": "Literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {
                                "job_input_type": "Literal",
                                "value": "${{parent.jobs.node2.outputs.component_out_path}}",
                            },
                        },
                        "limits": None,
                        "name": "node3",
                        "outputs": {
                            "component_out_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_output3}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                    },
                },
                "outputs": {
                    "pipeline_output1": {"job_output_type": "UriFolder"},
                    "pipeline_output2": {"job_output_type": "UriFolder"},
                    "pipeline_output3": {"job_output_type": "UriFolder"},
                },
                "properties": {},
                "settings": {"_source": "DSL"},
                "tags": {},
            }
        }

    def test_pipeline_with_parallel_job(self):
        # command job with dict distribution
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        inputs = {
            "job_data_path": Input(type=AssetTypes.MLTABLE, path="./tests/test_configs/data", mode="eval_mount"),
        }
        outputs = {"job_output_path": Output(type=AssetTypes.URI_FOLDER, mode="rw_mount")}
        expected_resources = {"instance_count": 2}
        expected_environment_variables = {"key": "val"}

        task = ParallelTask(
            type="run_function",
            code="./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
            entry_script="score.py",
            program_arguments="--job_output_path ${{outputs.job_output_path}}",
            environment=environment,
        )
        logging_level = "DEBUG"
        max_concurrency_per_instance = 1
        error_threshold = 1
        mini_batch_error_threshold = 1
        mini_batch_size = "5"
        input_data = "${{inputs.job_data_path}}"

        parallel_job = ParallelJob(
            display_name="my-evaluate-job",
            resources=expected_resources,
            mini_batch_size=mini_batch_size,
            task=task,
            input_data=input_data,
            logging_level=logging_level,
            max_concurrency_per_instance=max_concurrency_per_instance,
            error_threshold=error_threshold,
            mini_batch_error_threshold=mini_batch_error_threshold,
            inputs=inputs,
            outputs=outputs,
            environment_variables=expected_environment_variables,
        )

        parallel_job_func = to_component(job=parallel_job)
        data = Input(type=AssetTypes.MLTABLE, path="/a/path/on/ds", mode="eval_mount")

        @dsl.pipeline(experiment_name="test_pipeline_with_parallel_function")
        def pipeline(job_data_path):
            parallel_node = parallel_job_func(job_data_path=job_data_path)
            return {
                "pipeline_job_out": parallel_node.outputs.job_output_path,
            }

        omit_fields = [
            "name",
            "properties.jobs.parallel_node.componentId",
        ]

        pipeline1 = pipeline(data)
        pipeline_rest_obj = pipeline1._to_rest_object()
        pipeline_job1 = pipeline_rest_obj.as_dict()
        pipeline_regenerated_from_rest = PipelineJob._load_from_rest(pipeline_rest_obj)
        omit_field = [
            "jobs.parallel_node.task",
            "outputs",  # TODO: figure out why outputs can't be regenerated correctly
        ]

        assert pydash.omit(pipeline1._to_dict(), *omit_field) == pydash.omit(
            pipeline_regenerated_from_rest._to_dict(), *omit_field
        )

        pipeline_job1 = pydash.omit(pipeline_job1, *omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_parallel_function",
                "inputs": {
                    "job_data_path": {"job_input_type": "MLTable", "mode": "EvalMount", "uri": "/a/path/on/ds"},
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "parallel_node": {
                        "_source": "CLASS",
                        "type": "parallel",
                        "input_data": "${{inputs.job_data_path}}",
                        "computeId": None,
                        "display_name": None,
                        "inputs": {
                            "job_data_path": {"job_input_type": "Literal", "value": "${{parent.inputs.job_data_path}}"},
                        },
                        "name": "parallel_node",
                        "outputs": {
                            "job_output_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_job_out}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "mini_batch_size": 5,
                        "retry_settings": None,
                        "logging_level": None,
                        "max_concurrency_per_instance": 1,
                        "error_threshold": None,
                        "mini_batch_error_threshold": 1,
                        "tags": {},
                        "environment_variables": {},
                        "task": {
                            "program_arguments": "--job_output_path " "${{outputs.job_output_path}}",
                            "code": "azureml:./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
                            "entry_script": "score.py",
                            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                            "type": "run_function",
                        },
                    },
                },
                "outputs": {"pipeline_job_out": {"job_output_type": "UriFolder"}},
                "properties": {},
                "settings": {"_source": "DSL"},
                "tags": {},
            }
        }

    def test_pipeline_with_parallel_function_inside(self):
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        expected_environment_variables = {"key": "val"}
        expected_resources = {"instance_count": 2}
        inputs = {
            "job_data_path": Input(type=AssetTypes.MLTABLE, path="./tests/test_configs/data", mode="eval_mount"),
        }
        input_data = "${{inputs.job_data_path}}"
        outputs = {"job_output_path": Output(type=AssetTypes.URI_FOLDER, mode="rw_mount")}
        task = RunFunction(
            code="./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
            entry_script="score.py",
            program_arguments="--job_output_path ${{outputs.job_output_path}}",
            environment=environment,
        )
        logging_level = "DEBUG"
        max_concurrency_per_instance = 1
        error_threshold = 1
        mini_batch_error_threshold = 1
        mini_batch_size = "5"

        # parallel job
        @dsl.pipeline(experiment_name="test_pipeline_with_parallel_function_inside")
        def pipeline(path):
            # Parallel from parallel_run_function()
            parallel_function = parallel_run_function(
                display_name="my-evaluate-job",
                inputs=inputs,
                outputs=outputs,
                mini_batch_size=mini_batch_size,
                task=task,
                logging_level=logging_level,
                max_concurrency_per_instance=max_concurrency_per_instance,
                error_threshold=error_threshold,
                mini_batch_error_threshold=mini_batch_error_threshold,
                resources=expected_resources,
                input_data=input_data,
                environment_variables=expected_environment_variables,
            )
            node1 = parallel_function(job_data_path=path)
            node2 = parallel_function(job_data_path=Input(type=AssetTypes.MLTABLE, path="new_path", mode="eval_mount"))

            return {
                "pipeline_output1": node1.outputs.job_output_path,
                "pipeline_output2": node2.outputs.job_output_path,
            }

        omit_fields = [
            "name",
            "properties.jobs.node1.componentId",
            "properties.jobs.node2.componentId",
        ]

        data = Input(type=AssetTypes.MLTABLE, path="/a/path/on/ds", mode="eval_mount")
        pipeline1 = pipeline(data)
        pipeline_job1 = pipeline1._to_rest_object().as_dict()
        pipeline_job1 = pydash.omit(pipeline_job1, omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_parallel_function_inside",
                "inputs": {
                    "path": {"job_input_type": "MLTable", "mode": "EvalMount", "uri": "/a/path/on/ds"},
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "node1": {
                        "_source": "BUILDER",
                        "type": "parallel",
                        "input_data": "${{inputs.job_data_path}}",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "inputs": {
                            "job_data_path": {"job_input_type": "Literal", "value": "${{parent.inputs.path}}"},
                        },
                        "name": "node1",
                        "outputs": {
                            "job_output_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_output1}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "mini_batch_size": 5,
                        "task": {
                            "type": "run_function",
                            "code": "azureml:./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
                            "entry_script": "score.py",
                            "program_arguments": "--job_output_path ${{outputs.job_output_path}}",
                            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                        },
                        "retry_settings": None,
                        "logging_level": "DEBUG",
                        "max_concurrency_per_instance": 1,
                        "error_threshold": 1,
                        "mini_batch_error_threshold": 1,
                        "tags": {},
                        "environment_variables": {"key": "val"},
                    },
                    "node2": {
                        "_source": "BUILDER",
                        "type": "parallel",
                        "input_data": "${{inputs.job_data_path}}",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "inputs": {
                            "job_data_path": {
                                "job_input_type": "MLTable",
                                "mode": "EvalMount",
                                "uri": "new_path",
                            },
                        },
                        "name": "node2",
                        "outputs": {
                            "job_output_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_output2}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "mini_batch_size": 5,
                        "task": {
                            "type": "run_function",
                            "code": "azureml:./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
                            "entry_script": "score.py",
                            "program_arguments": "--job_output_path ${{outputs.job_output_path}}",
                            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                        },
                        "retry_settings": None,
                        "logging_level": "DEBUG",
                        "max_concurrency_per_instance": 1,
                        "error_threshold": 1,
                        "mini_batch_error_threshold": 1,
                        "tags": {},
                        "environment_variables": {"key": "val"},
                    },
                },
                "outputs": {
                    "pipeline_output1": {"job_output_type": "UriFolder"},
                    "pipeline_output2": {"job_output_type": "UriFolder"},
                },
                "properties": {},
                "settings": {"_source": "DSL"},
                "tags": {},
            }
        }

    def test_pipeline_with_command_function_inside(self):
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        expected_resources = {"instance_count": 2}
        expected_environment_variables = {"key": "val"}
        inputs = {
            "component_in_path": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
            "component_in_number": 0.01,
        }
        outputs = {"component_out_path": Output(type="mlflow_model", mode="rw_mount")}

        @dsl.pipeline(experiment_name="test_pipeline_with_command_function_inside")
        def pipeline(number, path):
            # Command from command() function
            command_function = command(
                display_name="my-evaluate-job",
                environment=environment,
                command='echo "hello world"',
                distribution={"type": "Pytorch", "process_count_per_instance": 2},
                resources=expected_resources,
                environment_variables=expected_environment_variables,
                inputs=inputs,
                outputs=outputs,
            )
            node1 = command_function(component_in_number=number, component_in_path=path)
            node2 = command_function(component_in_number=1, component_in_path=Input(path="new_path"))

            return {
                "pipeline_output1": node1.outputs.component_out_path,
                "pipeline_output2": node2.outputs.component_out_path,
            }

        omit_fields = [
            "name",
            "properties.jobs.node1.componentId",
            "properties.jobs.node2.componentId",
        ]

        data = Input(type=AssetTypes.URI_FOLDER, path="/a/path/on/ds")
        pipeline1 = pipeline(10, data)
        pipeline_job1 = pipeline1._to_rest_object().as_dict()
        pipeline_job1 = pydash.omit(pipeline_job1, omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_command_function_inside",
                "inputs": {
                    "number": {"job_input_type": "Literal", "value": "10"},
                    "path": {"job_input_type": "UriFolder", "uri": "/a/path/on/ds"},
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "node1": {
                        "_source": "BUILDER",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {"key": "val"},
                        "inputs": {
                            "component_in_number": {"job_input_type": "Literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {"job_input_type": "Literal", "value": "${{parent.inputs.path}}"},
                        },
                        "limits": None,
                        "name": "node1",
                        "outputs": {
                            "component_out_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_output1}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                    },
                    "node2": {
                        "_source": "BUILDER",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {"key": "val"},
                        "inputs": {
                            "component_in_number": {"job_input_type": "Literal", "value": "1"},
                            "component_in_path": {
                                "job_input_type": "UriFolder",
                                "uri": "new_path",
                            },
                        },
                        "limits": None,
                        "name": "node2",
                        "outputs": {
                            "component_out_path": {"type": "Literal", "value": "${{parent.outputs.pipeline_output2}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                    },
                },
                "outputs": {
                    "pipeline_output1": {"job_output_type": "UriFolder"},
                    "pipeline_output2": {"job_output_type": "UriFolder"},
                },
                "properties": {},
                "settings": {"_source": "DSL"},
                "tags": {},
            }
        }

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
            component_func1 = load_component(path=path)
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)

            component_func2 = load_component(path=path)
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

        component_func = load_component(path=path)
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
        one2one = load_component(path="./tests/test_configs/components/1in1out.yaml")
        one2two = load_component(path="./tests/test_configs/components/1in2out.yaml")

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

    def test_pipeline_with_none_parameter_no_default_optional_false(self) -> None:
        default_optional_func = load_component(path=str(components_dir / "default_optional_component.yml"))

        # None input is binding to a required input
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=None,
            required_param="hello",
            required_param_with_default=False,
        )
        validate_result = pipeline._validate()
        assert validate_result.messages == {
            "inputs.required_input": "Required input 'required_input' for pipeline 'pipeline_with_default_optional_parameters' not provided."
        }

        # None input is not binding to a required input
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_param,
            required_param_with_default,
        ):
            default_optional_func(
                required_input=None,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_param="hello",
            required_param_with_default=False,
        )
        validate_result = pipeline._validate()
        assert validate_result.messages == {
            "jobs.default_optional_component.inputs.required_input": "Required input 'required_input' for component 'default_optional_component' not provided."
        }

        # Not pass required parameter
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_param,
            required_param_with_default,
        ):
            default_optional_func(
                required_param=required_param,
                required_param_with_default=required_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_param="hello",
            required_param_with_default=False,
        )

        validate_result = pipeline._validate()
        assert validate_result.messages == {
            "jobs.default_optional_component.inputs.required_input": "Required input 'required_input' for component 'default_optional_component' not provided."
        }

    def test_pipeline_with_none_parameter_binding_to_two_component_inputs(self) -> None:
        default_optional_func = load_component(path=str(components_dir / "default_optional_component.yml"))

        # None pipeline parameter is binding to two component.

        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input, required_param, required_param_with_default, optional_param_with_default, optional_param
        ):
            # In the first component, optional_param_with_default is binding to two optional component inputs.
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param_with_default,
                optional_param_with_default=optional_param_with_default,
            )
            #  In the second component, optional_param_with_default is binding to one optional component input and one
            #  required component input.
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=optional_param_with_default,
                optional_param=optional_param,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param_with_default=None,
            optional_param="optional_param",
        )
        validate_result = pipeline._validate()
        assert validate_result.messages == {
            "inputs.optional_param_with_default": "Required input 'optional_param_with_default' for pipeline 'pipeline_with_default_optional_parameters' not provided."
        }

    def test_pipeline_optional_link_to_required(self):
        default_optional_func = load_component(path=str(components_dir / "default_optional_component.yml"))

        # None pipeline parameter is binding to two component.

        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input: Input(optional=True),
            required_param,
            required_param_with_default,
            optional_param_with_default,
            optional_param,
        ):
            # In the first component, optional_param_with_default is binding to two optional component inputs.
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param_with_default,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param_with_default=None,
            optional_param="optional_param",
        )
        validate_result = pipeline._validate()
        assert validate_result.messages == {
            "inputs.required_input": "Pipeline optional Input binding to required inputs: ['default_optional_component.inputs.required_input']"
        }

    def test_pipeline_job_help_function(self):
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(number, path):
            component_func = load_component(path=yaml_file)
            node1 = component_func(component_in_number=number, component_in_path=path)
            return {"pipeline_output": node1.outputs.component_out_path}

        pipeline1 = pipeline(10, Input(path="/a/path/on/ds"))
        with patch("sys.stdout", new=StringIO()) as std_out:
            print(pipeline1)
            assert (
                "$schema: '{}'\n    type: command\n    inputs:\n      component_in_number:\n        path: ${{parent.inputs.number}}"
                in std_out.getvalue()
            )

    def test_node_unknown_property_setting(self) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path=path)
        job_input = Input(
            type=AssetTypes.URI_FILE,
            path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
        )

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node1.jeff_special_option.foo = "bar"
            node1.compute = "cpu-cluster"

        dsl_pipeline: PipelineJob = pipeline(10, job_input)

        with patch("azure.ai.ml.entities._validation.module_logger.info") as mock_logging:
            dsl_pipeline._validate(raise_error=True)
            mock_logging.assert_called_with("Warnings: [jobs.node1.jeff_special_option: Unknown field.]")

    def test_node_required_field_missing(self) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path=path)
        job_input = Input(
            type=AssetTypes.URI_FILE,
            path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
        )

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)

            node2 = node1.sweep(
                goal="maximize",
                primary_metric="accuracy",
                sampling_algorithm="random",
            )
            node2.compute = "cpu-cluster"
            node2.jeff_special_option.foo = "bar"

        dsl_pipeline: PipelineJob = pipeline(10, job_input)

        with pytest.raises(
            ValidationException, match="jobs.node2.limits.max_total_trials: " "Missing data for required field."
        ):
            dsl_pipeline._validate(raise_error=True)

    def test_node_schema_validation(self) -> None:
        path = "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml"
        batch_inference1 = load_component(path=path)

        # Construct pipeline
        @dsl.pipeline(default_compute="cpu-cluster", experiment_name="sdk-cli-v2")
        def parallel_in_pipeline(job_data_path):
            batch_inference_node1 = batch_inference1(job_data_path=job_data_path)
            batch_inference_node1.outputs.job_output_path.type = AssetTypes.MLTABLE

            return {"job_out_data": batch_inference_node1.outputs.job_output_path}

        pipeline = parallel_in_pipeline(
            job_data_path=Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data/",
                mode=InputOutputModes.EVAL_MOUNT,
            ),
        )
        print(pipeline)
        with patch("azure.ai.ml.entities._validation.module_logger.info") as mock_logging:
            pipeline._validate()
            mock_logging.assert_not_called()

    def test_multi_parallel_components_with_file_input_pipeline_output(self, randstr: Callable[[], str]) -> None:
        components_dir = tests_root_dir / "test_configs/dsl_pipeline/parallel_component_with_file_input"
        batch_inference1 = load_component(path=str(components_dir / "score.yml"))
        batch_inference2 = load_component(path=str(components_dir / "score.yml"))
        convert_data = load_component(path=str(components_dir / "convert_data.yml"))

        # Construct pipeline
        @dsl.pipeline(default_compute="cpu-cluster", experiment_name="sdk-cli-v2")
        def parallel_in_pipeline(job_data_path):
            batch_inference_node1 = batch_inference1(job_data_path=job_data_path)
            convert_data_node = convert_data(input_data=batch_inference_node1.outputs.job_output_path)
            convert_data_node.outputs.file_output_data.type = AssetTypes.MLTABLE
            batch_inference_node2 = batch_inference2(job_data_path=convert_data_node.outputs.file_output_data)
            batch_inference_node2.inputs.job_data_path.mode = InputOutputModes.EVAL_MOUNT

            return {"job_out_data": batch_inference_node2.outputs.job_output_path}

        pipeline = parallel_in_pipeline(
            job_data_path=Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data/",
                mode=InputOutputModes.EVAL_MOUNT,
            ),
        )
        pipeline.outputs.job_out_data.mode = "upload"
        omit_fields = [
            "jobs.batch_inference_node1.componentId",
            "jobs.batch_inference_node2.componentId",
            "jobs.convert_data_node.componentId",
        ]
        actual_job = pydash.omit(pipeline._to_rest_object().properties.as_dict(), *omit_fields)
        assert actual_job == {
            "properties": {},
            "tags": {},
            "compute_id": "cpu-cluster",
            "display_name": "parallel_in_pipeline",
            "experiment_name": "sdk-cli-v2",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_data_path": {
                    "mode": "EvalMount",
                    "uri": "./tests/test_configs/dataset/mnist-data/",
                    "job_input_type": "MLTable",
                }
            },
            "jobs": {
                "batch_inference_node1": {
                    "_source": "YAML.COMPONENT",
                    "type": "parallel",
                    "name": "batch_inference_node1",
                    "display_name": None,
                    "tags": {},
                    "computeId": None,
                    "inputs": {
                        "job_data_path": {"job_input_type": "Literal", "value": "${{parent.inputs.job_data_path}}"}
                    },
                    "outputs": {},
                    "mini_batch_size": 1,
                    "task": {
                        "program_arguments": "--job_output_path " "${{outputs.job_output_path}}",
                        "code": "azureml:./src",
                        "entry_script": "score.py",
                        "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                        "type": "run_function",
                    },
                    "input_data": "${{inputs.job_data_path}}",
                    "retry_settings": None,
                    "logging_level": None,
                    "resources": {"instance_count": 2, "properties": {}},
                    "max_concurrency_per_instance": 1,
                    "error_threshold": None,
                    "mini_batch_error_threshold": 1,
                    "environment_variables": {},
                },
                "convert_data_node": {
                    "_source": "YAML.COMPONENT",
                    "computeId": None,
                    "display_name": None,
                    "distribution": None,
                    "environment_variables": {},
                    "inputs": {
                        "input_data": {
                            "job_input_type": "Literal",
                            "value": "${{parent.jobs.batch_inference_node1.outputs.job_output_path}}",
                        }
                    },
                    "limits": None,
                    "name": "convert_data_node",
                    "outputs": {"file_output_data": {"job_output_type": "MLTable"}},
                    "resources": None,
                    "tags": {},
                },
                "batch_inference_node2": {
                    "_source": "YAML.COMPONENT",
                    "type": "parallel",
                    "name": "batch_inference_node2",
                    "display_name": None,
                    "tags": {},
                    "computeId": None,
                    "inputs": {
                        "job_data_path": {
                            "job_input_type": "Literal",
                            "value": "${{parent.jobs.convert_data_node.outputs.file_output_data}}",
                            "mode": "EvalMount",
                        }
                    },
                    "outputs": {"job_output_path": {"value": "${{parent.outputs.job_out_data}}", "type": "Literal"}},
                    "mini_batch_size": 1,
                    "task": {
                        "program_arguments": "--job_output_path " "${{outputs.job_output_path}}",
                        "code": "azureml:./src",
                        "entry_script": "score.py",
                        "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                        "type": "run_function",
                    },
                    "input_data": "${{inputs.job_data_path}}",
                    "retry_settings": None,
                    "logging_level": None,
                    "resources": {"instance_count": 2, "properties": {}},
                    "max_concurrency_per_instance": 1,
                    "error_threshold": None,
                    "mini_batch_error_threshold": 1,
                    "environment_variables": {},
                },
            },
            "outputs": {"job_out_data": {"mode": "Upload", "job_output_type": "UriFolder"}},
            "settings": {"_source": "DSL"},
        }

    def test_automl_node_in_pipeline(self) -> None:
        # create ClassificationJob with classification func inside pipeline is also supported
        @dsl.pipeline(name="train_with_automl_in_pipeline", default_compute_target="cpu-cluster")
        def train_with_automl_in_pipeline(
            main_data_input, target_column_name_input: str, max_total_trials_input: int, validation_data_size: float
        ):
            automl_classif_job = classification(
                training_data=main_data_input,
                # validation_data_size="${{parent.inputs.validation_data_size}}",
                target_column_name=target_column_name_input,
                primary_metric="accuracy",
                enable_model_explainability=True,
                outputs={"best_model": Output(type="mlflow_model")},
            )

            automl_classif_job.set_limits(
                max_trials=max_total_trials_input,
                max_concurrent_trials=4,  # Matches number of cluster's nodes
                enable_early_termination=True,
            )

            automl_classif_job.set_training(enable_onnx_compatible_models=True)

        job_input = Input(
            type=AssetTypes.MLTABLE,
            path="fake_path",
        )
        pipeline1: PipelineJob = train_with_automl_in_pipeline(job_input, "target", 10, 0.2)

        pipeline_dict1 = pipeline1._to_rest_object().as_dict()
        pipeline_dict1 = pydash.omit(
            pipeline_dict1["properties"], ["jobs.automl_classif_job.display_name", "jobs.automl_classif_job.properties"]
        )

        expected_dict = {
            "compute_id": "cpu-cluster",
            "display_name": "train_with_automl_in_pipeline",
            "inputs": {
                "main_data_input": {"job_input_type": "MLTable", "uri": "fake_path"},
                "max_total_trials_input": {"job_input_type": "Literal", "value": "10"},
                "target_column_name_input": {"job_input_type": "Literal", "value": "target"},
                "validation_data_size": {"job_input_type": "Literal", "value": "0.2"},
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "automl_classif_job": {
                    "limits": {
                        "enable_early_termination": True,
                        "max_concurrent_trials": 4,
                        "max_trials": "${{parent.inputs.max_total_trials_input}}",
                    },
                    "log_verbosity": "info",
                    "name": "automl_classif_job",
                    "outputs": {"best_model": {"job_output_type": "MLFlowModel"}},
                    "primary_metric": "accuracy",
                    "tags": {},
                    "target_column_name": "${{parent.inputs.target_column_name_input}}",
                    "task": "classification",
                    "training": {"enable_model_explainability": True, "enable_onnx_compatible_models": True},
                    "training_data": "${{parent.inputs.main_data_input}}",
                    "type": "automl",
                }
            },
            "outputs": {},
            "settings": {"_source": "DSL"},
            "properties": {},
            "tags": {},
        }
        assert pipeline_dict1 == expected_dict

        # create ClassificationJob inside pipeline is NOT supported
        @dsl.pipeline(name="train_with_automl_in_pipeline", default_compute_target="cpu-cluster")
        def train_with_automl_in_pipeline(
            main_data_input, target_column_name_input: str, max_total_trials_input: int, validation_data_size: float
        ):
            automl_classif_job = ClassificationJob(
                primary_metric="accuracy",
                outputs={"best_model": Output(type="mlflow_model")},
            )
            automl_classif_job.set_data(
                training_data=main_data_input,
                target_column_name=target_column_name_input,
                validation_data_size="${{parent.inputs.validation_data_size}}",
            )

        pipeline = train_with_automl_in_pipeline(job_input, "target", 10, 0.2)
        # classification job defined with ClassificationJob won't be collected in pipeline job
        assert pipeline.jobs == {}

    def test_automl_node_with_command_node(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path=path)

        @dsl.pipeline(name="train_with_automl_in_pipeline", default_compute_target="cpu-cluster", force_rerun=False)
        def train_with_automl_in_pipeline(component_in_number, component_in_path, target_column_name_input: str):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)

            node2 = classification(
                training_data=node1.outputs.component_out_path,
                # validation_data_size="${{parent.inputs.validation_data_size}}",
                target_column_name=target_column_name_input,
                primary_metric="accuracy",
                enable_model_explainability=True,
                outputs=dict(best_model=Output(type="mlflow_model")),
            )
            node2.set_limits(max_concurrent_trials=1)

        job_input = Input(
            type=AssetTypes.MLTABLE,
            path="fake_path",
        )
        pipeline1: PipelineJob = train_with_automl_in_pipeline(10, job_input, "target")
        pipeline_dict1 = pipeline1._to_rest_object().as_dict()
        pipeline_dict1 = pydash.omit(
            pipeline_dict1["properties"],
            ["jobs.node1.componentId", "jobs.node2.display_name", "jobs.node2.properties"],
        )
        assert pipeline_dict1 == {
            "compute_id": "cpu-cluster",
            "display_name": "train_with_automl_in_pipeline",
            "inputs": {
                "component_in_number": {"job_input_type": "Literal", "value": "10"},
                "component_in_path": {"job_input_type": "MLTable", "uri": "fake_path"},
                "target_column_name_input": {"job_input_type": "Literal", "value": "target"},
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "node1": {
                    "_source": "YAML.COMPONENT",
                    "computeId": None,
                    "display_name": None,
                    "distribution": None,
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {
                            "job_input_type": "Literal",
                            "value": "${{parent.inputs.component_in_number}}",
                        },
                        "component_in_path": {
                            "job_input_type": "Literal",
                            "value": "${{parent.inputs.component_in_path}}",
                        },
                    },
                    "limits": None,
                    "name": "node1",
                    "outputs": {},
                    "resources": None,
                    "tags": {},
                },
                "node2": {
                    "limits": {"max_concurrent_trials": 1},
                    "log_verbosity": "info",
                    "name": "node2",
                    "outputs": {"best_model": {"job_output_type": "MLFlowModel"}},
                    "primary_metric": "accuracy",
                    "tags": {},
                    "target_column_name": "${{parent.inputs.target_column_name_input}}",
                    "task": "classification",
                    "training": {"enable_model_explainability": True},
                    "training_data": "${{parent.jobs.node1.outputs.component_out_path}}",
                    "type": "automl",
                },
            },
            "outputs": {},
            "properties": {},
            "settings": {"force_rerun": False, "_source": "DSL"},
            "tags": {},
        }

    def test_automl_node_with_pipeline_level_output(self):
        @dsl.pipeline(name="train_with_automl_in_pipeline", default_compute_target="cpu-cluster")
        def train_with_automl_in_pipeline(training_data, target_column_name_input: str):
            classification_node = classification(
                training_data=training_data,
                # validation_data_size="${{parent.inputs.validation_data_size}}",
                target_column_name=target_column_name_input,
                primary_metric="accuracy",
                enable_model_explainability=True,
                outputs=dict(best_model=Output(type="mlflow_model")),
            )
            return {"pipeline_job_out_best_model": classification_node.outputs.best_model}

        job_input = Input(
            type=AssetTypes.MLTABLE,
            path="fake_path",
        )
        pipeline1: PipelineJob = train_with_automl_in_pipeline(job_input, "target")

        pipeline_dict1 = pipeline1._to_rest_object().as_dict()
        pipeline_dict1 = pydash.omit(
            pipeline_dict1["properties"],
            ["jobs.classification_node.display_name", "jobs.classification_node.properties"],
        )
        expected_dict = {
            "compute_id": "cpu-cluster",
            "display_name": "train_with_automl_in_pipeline",
            "inputs": {
                "target_column_name_input": {"job_input_type": "Literal", "value": "target"},
                "training_data": {"job_input_type": "MLTable", "uri": "fake_path"},
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "classification_node": {
                    "log_verbosity": "info",
                    "name": "classification_node",
                    "outputs": {
                        "best_model": {"type": "Literal", "value": "${{parent.outputs.pipeline_job_out_best_model}}"}
                    },
                    "primary_metric": "accuracy",
                    "tags": {},
                    "target_column_name": "${{parent.inputs.target_column_name_input}}",
                    "task": "classification",
                    "training": {"enable_model_explainability": True},
                    "training_data": "${{parent.inputs.training_data}}",
                    "type": "automl",
                }
            },
            # default to uri folder with rwmount
            "outputs": {"pipeline_job_out_best_model": {"job_output_type": "UriFolder"}},
            "properties": {},
            "settings": {"_source": "DSL"},
            "tags": {},
        }
        assert pipeline_dict1 == expected_dict

        # in order to get right type, user need to specify it on pipeline level
        pipeline1.outputs.pipeline_job_out_best_model.type = "mlflow_model"
        pipeline1.outputs.pipeline_job_out_best_model.mode = "rw_mount"
        pipeline_dict2 = pipeline1._to_rest_object().as_dict()
        pipeline_dict2 = pydash.omit(
            pipeline_dict2["properties"],
            ["jobs.classification_node.display_name", "jobs.classification_node.properties"],
        )
        expected_dict.update(
            {
                "outputs": {
                    "pipeline_job_out_best_model": {"job_output_type": "MLFlowModel", "mode": "ReadWriteMount"}
                },
            }
        )
        assert pipeline_dict2 == expected_dict

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
        from azure.ai.ml._schema.job.distribution import MPIDistributionSchema
        from azure.ai.ml._schema._utils.data_binding_expression import support_data_binding_expression_for_fields

        schema = MPIDistributionSchema()
        support_data_binding_expression_for_fields(schema, ["type"])
        distribution = schema.load({"type": "mpi", "process_count_per_instance": "${{parent.inputs.test}}"})
        test_input = PipelineInput("test", None)
        assert distribution.distribution_type == "Mpi"
        assert distribution.process_count_per_instance == str(test_input)
        distribution.process_count_per_instance = test_input
        dumped = schema.dump(distribution)
        assert dumped == {"type": "mpi", "process_count_per_instance": "${{parent.inputs.test}}"}

    def test_automl_node_without_variable_name(self) -> None:
        @dsl.pipeline(name="train_with_automl_in_pipeline", default_compute_target="cpu-cluster")
        def train_with_automl_in_pipeline(training_data, target_column_name_input: str):
            classification(
                training_data=training_data,
                # validation_data_size="${{parent.inputs.validation_data_size}}",
                target_column_name=target_column_name_input,
                primary_metric="accuracy",
                enable_model_explainability=True,
                outputs=dict(best_model=Output(type="mlflow_model")),
            )
            classification(
                training_data=training_data,
                # validation_data_size="${{parent.inputs.validation_data_size}}",
                target_column_name=target_column_name_input,
                primary_metric="accuracy",
                enable_model_explainability=True,
                outputs=dict(best_model=Output(type="mlflow_model")),
            )
            regression(
                training_data=training_data,
                target_column_name="SalePrice",
                primary_metric="r2_score",
                outputs={"best_model": Output(type="mlflow_model")},
            )
            regression(
                training_data=training_data,
                target_column_name="SalePrice",
                primary_metric="r2_score",
                outputs={"best_model": Output(type="mlflow_model")},
            )

        job_input = Input(
            type=AssetTypes.MLTABLE,
            path="fake_path",
        )
        pipeline1: PipelineJob = train_with_automl_in_pipeline(job_input, "target")
        pipeline_dict1 = pipeline1._to_rest_object().as_dict()
        assert set(pipeline_dict1["properties"]["jobs"].keys()) == {
            "regressionjob",
            "regressionjob_1",
            "classificationjob_1",
            "classificationjob",
        }

    def test_node_base_path_resolution(self):
        component_path = (
            "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/component/component.yml"
        )

        @dsl.pipeline()
        def pipeline_no_arg():
            component_func = load_component(path=component_path)
            r_iris_example = component_func(iris=Input(path="/a/path/on/ds"))
            r_iris_example.compute = "cpu-cluster"

        pipeline_job = pipeline_no_arg()
        pipeline_job._validate(raise_error=True)
        # return origin value as no base path change
        assert pipeline_job.jobs["r_iris_example"].component.code == "../../../python"

    def test_dsl_pipeline_without_setting_binding_node(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_without_setting_binding_node,
        )

        pipeline = pipeline_without_setting_binding_node()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.training_input.uri",
            "properties.jobs.train_with_sample_data.componentId",
            "properties.jobs.train_with_sample_data._source",
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
                    "training_input": {"job_input_type": "UriFolder"},
                    "training_max_epochs": {"job_input_type": "Literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "Literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "Literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
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
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_input}}",
                            },
                            "max_epochs": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        "outputs": {"model_output": {"value": "${{parent.outputs.trained_model}}", "type": "Literal"}},
                    }
                },
                "outputs": {"trained_model": {"job_output_type": "UriFolder"}},
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
                    "training_input": {"mode": "ReadOnlyMount", "job_input_type": "UriFolder"},
                    "training_max_epochs": {"job_input_type": "Literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "Literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "Literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
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
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_input}}",
                            },
                            "max_epochs": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # todo: need update here when update literal output output
                        "outputs": {"model_output": {"value": "${{parent.outputs.trained_model}}", "type": "Literal"}},
                    }
                },
                "outputs": {"trained_model": {"mode": "Upload", "job_output_type": "UriFolder"}},
                "settings": {},
            }
        }

    def test_dsl_pipeline_with_only_setting_binding_node(self) -> None:
        from dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_only_setting_binding_node,
        )

        pipeline = pipeline_with_only_setting_binding_node()
        dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
        omit_fields = [
            "name",
            "properties.inputs.training_input.uri",
            "properties.jobs.train_with_sample_data.componentId",
            "properties.jobs.train_with_sample_data._source",
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
                    "training_input": {"job_input_type": "UriFolder"},
                    "training_max_epochs": {"job_input_type": "Literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "Literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "Literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
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
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "max_epochs": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "model_output": {
                                "value": "${{parent.outputs.trained_model}}",
                                "type": "Literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"trained_model": {"job_output_type": "UriFolder"}},
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
                    "training_input": {"mode": "Download", "job_input_type": "UriFolder"},
                    "training_max_epochs": {"job_input_type": "Literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "Literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "Literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
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
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "max_epochs": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "model_output": {
                                "value": "${{parent.outputs.trained_model}}",
                                "type": "Literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "UriFolder"}},
                "settings": {},
            }
        }

    @patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"})
    def test_nested_dsl_pipeline(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path=path)

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
            "is_deterministic": True,
            "inputs": {"component_in_number": {"type": "integer"}, "component_in_path": {"type": "string"}},
            "outputs": {"sub_pipeline_out": {}},
            "type": "pipeline",
            "jobs": {
                "node1": {
                    "$schema": "{}",
                    "command": "echo Hello World & echo [${{inputs.component_in_number}}] & echo ${{inputs.component_in_path}} & echo ${{outputs.component_out_path}} > ${{outputs.component_out_path}}/component_in_number",
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
                    "component": {},
                    "type": "command",
                },
                "node2": {
                    "$schema": "{}",
                    "command": "echo Hello World & echo [${{inputs.component_in_number}}] & echo ${{inputs.component_in_path}} & echo ${{outputs.component_out_path}} > ${{outputs.component_out_path}}/component_in_number",
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.component_out_path}}"},
                    },
                    "outputs": {"component_out_path": "${{parent.outputs.sub_pipeline_out}}"},
                    "component": {},
                    "type": "command",
                },
            },
        }
        actual_dict = pipeline.jobs["node1"].component._to_dict()
        actual_dict["jobs"]["node1"]["component"] = {}
        actual_dict["jobs"]["node2"]["component"] = {}
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
                    "$schema": "{}",
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
                    "component": {},
                    "type": "pipeline",
                },
                "node2": {
                    "$schema": "{}",
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.jobs.node1.outputs.sub_pipeline_out}}"},
                    },
                    "outputs": {"sub_pipeline_out": "${{parent.outputs.sub_pipeline_out}}"},
                    "component": {},
                    "type": "pipeline",
                },
            },
        }
        actual_dict = pipeline._to_dict()
        actual_dict["jobs"]["node1"]["component"] = {}
        actual_dict["jobs"]["node2"]["component"] = {}
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
                    "training_input": {"mode": "Download", "job_input_type": "UriFolder"},
                    "training_max_epochs": {"job_input_type": "Literal", "value": "20"},
                    "training_learning_rate": {"job_input_type": "Literal", "value": "1.8"},
                    "learning_rate_schedule": {"job_input_type": "Literal", "value": "time-based"},
                },
                "jobs": {
                    "train_with_sample_data": {
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
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "max_epochs": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_max_epochs}}",
                            },
                            "learning_rate": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "model_output": {
                                "value": "${{parent.outputs.trained_model}}",
                                "type": "Literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "UriFolder"}},
                "settings": {},
            }
        }

    @patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"})
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
                    "pipeline_training_input": {"mode": "Download", "job_input_type": "UriFolder"},
                    "pipeline_training_max_epochs": {"job_input_type": "Literal", "value": "20"},
                    "pipeline_training_learning_rate": {"job_input_type": "Literal", "value": "1.8"},
                    "pipeline_learning_rate_schedule": {"job_input_type": "Literal", "value": "time-based"},
                },
                "jobs": {
                    "subgraph1": {
                        "name": "subgraph1",
                        "display_name": None,
                        "tags": {},
                        "computeId": None,
                        "inputs": {
                            "training_input": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.pipeline_training_input}}",
                                "mode": "ReadOnlyMount",
                            },
                            "training_max_epocs": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.pipeline_training_max_epochs}}",
                            },
                            "training_learning_rate": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.pipeline_training_learning_rate}}",
                            },
                            "learning_rate_schedule": {
                                "job_input_type": "Literal",
                                "value": "${{parent.inputs.pipeline_learning_rate_schedule}}",
                            },
                        },
                        # add mode in rest if binding output set mode
                        "outputs": {
                            "trained_model": {
                                "value": "${{parent.outputs.pipeline_trained_model}}",
                                "type": "Literal",
                                "mode": "Upload",
                            }
                        },
                    }
                },
                "outputs": {"pipeline_trained_model": {"mode": "ReadWriteMount", "job_output_type": "UriFolder"}},
                "settings": {},
            }
        }

    def test_dsl_pipeline_build_component(self):
        component_path = (
            "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/component/component.yml"
        )

        @dsl.pipeline(name="pipeline_comp", version="2", continue_on_step_failure=True, tags={"key": "val"})
        def pipeline_func(path: Input):
            component_func = load_component(path=component_path)
            r_iris_example = component_func(iris=path)
            r_iris_example.compute = "cpu-cluster"

        component = pipeline_func._pipeline_builder.build()

        expected_dict = {
            "name": "pipeline_comp",
            "tags": {"key": "val"},
            "version": "2",
            "display_name": "pipeline_comp",
            "is_deterministic": True,
            "inputs": {"path": {"type": "uri_folder"}},
            "outputs": {},
            "type": "pipeline",
            "jobs": {},
        }
        actual_dict = component._to_dict()
        actual_dict["jobs"] = {}
        assert expected_dict == actual_dict

    def test_concatenation_of_pipeline_input_with_str(self) -> None:
        echo_string_func = load_component(path=str(components_dir / "echo_string_component.yml"))

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
