import logging
from io import StringIO
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pydash
import pytest
from azure.ai.ml import (
    Input,
    MLClient,
    MpiDistribution,
    Output,
    PyTorchDistribution,
    TensorFlowDistribution,
    command,
    dsl,
    load_component, AmlTokenConfiguration, UserIdentityConfiguration, ManagedIdentityConfiguration,
)
from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource
from azure.ai.ml.constants._common import AssetTypes, InputOutputModes
from azure.ai.ml.constants._job.pipeline import PipelineConstants
from azure.ai.ml.dsl._load_import import to_component
from azure.ai.ml.dsl._parameter_group_decorator import parameter_group
from azure.ai.ml.entities import CommandComponent, CommandJob
from azure.ai.ml.entities import Component
from azure.ai.ml.entities import Component as ComponentEntity
from azure.ai.ml.entities import Data, PipelineJob
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.parallel import ParallelJob, RunFunction, parallel_run_function
from devtools_testutils import AzureRecordedTestCase
from pipeline_job.e2etests.test_pipeline_job import assert_job_input_output_types
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, omit_with_wildcard, assert_job_cancel, sleep_if_live

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"
job_input = Input(
    type=AssetTypes.URI_FILE,
    path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
)
experiment_name = "dsl_pipeline_e2e"
common_omit_fields = [
    "properties",
    "display_name",
    "experiment_name",
    "jobs.*.componentId",
    "inputs.*.uri",
    "jobs.*._source",
    "jobs.*.properties",
    "settings._source",
    "source_job_id",
]


@pytest.mark.usefixtures(
    "enable_environment_id_arm_expansion",
    "enable_pipeline_private_preview_features",
    "mock_code_hash",
    "mock_component_hash",
    "recorded_test",
)
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestDSLPipeline(AzureRecordedTestCase):
    def test_command_component_create(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name=experiment_name,
            continue_on_step_failure=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=job_in_other_number, component_in_path=job_in_path)

        pipeline = pipeline(10, 15, job_input)
        job = client.jobs.create_or_update(pipeline)
        # check required fields in job dict
        job_dict = job._to_dict()
        expected_keys = ["status", "properties", "tags", "creation_context"]
        for k in expected_keys:
            assert k in job_dict.keys(), f"failed to get {k} in {job_dict}"

        # original job did not change
        assert_job_input_output_types(job)
        assert job.settings.continue_on_step_failure is True
        assert job.compute == "cpu-cluster"

    def test_pipeline_job_create_with_resolve_reuse(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1: CommandComponent = load_component(source=component_yaml)
        component_func2: CommandComponent = load_component(source=component_yaml)
        component_func3: CommandComponent = component_func1

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name=experiment_name,
            continue_on_step_failure=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func3(component_in_number=job_in_other_number, component_in_path=job_in_path)
            component_func1(component_in_number=job_in_other_number, component_in_path=job_in_path)

            component_func2(component_in_number=job_in_other_number, component_in_path=job_in_path)

        dsl_pipeline = pipeline(10, 15, job_input)
        component_id_set = set(map(lambda x: id(x.component), dsl_pipeline.jobs.values()))
        assert len(component_id_set) == 2

        for job_instance in dsl_pipeline.jobs.values():
            assert job_instance.component.id is None, "component id won't be resolved before create_or_update"

        # TODO: need extra mock based tests to verify if the component is resolved only once
        _ = client.jobs.create_or_update(dsl_pipeline)
        for job_instance in dsl_pipeline.jobs.values():
            assert (
                isinstance(job_instance.component, str) or job_instance.component.id is not None
            ), "component id will be filled back to the instance during create_or_update"

    def test_command_component_create_with_output(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def pipeline_with_output(job_in_number, job_in_other_number, job_in_path):
            node1 = component_func1(component_in_number=job_in_number, component_in_path=job_in_path)

            node2 = component_func2(
                component_in_number=job_in_other_number,
                component_in_path=node1.outputs.component_out_path,
            )
            return {"job_out_data": node2.outputs.component_out_path}

        pipeline = pipeline_with_output(10, 15, job_input)
        pipeline.outputs.job_out_data = Output(dataset=Data(name="dsl_pipeline_output", version="1"))
        client.jobs.create_or_update(pipeline, experiment_name=experiment_name)

    def test_command_component_create_from_remote(
        self,
        client: MLClient,
        hello_world_component: ComponentEntity,
        randstr: Callable[[str], str],
    ) -> None:
        component_func = load_component(
            client=client,
            name=hello_world_component.name,
            version=hello_world_component.version,
        )

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def pipeline_remote_component(job_in_number, job_in_other_number, job_in_path):
            node1 = component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            # un-configured data binding is not supported
            node1.outputs.component_out_path = Output(dataset=Data(name="mldesigner_component_output"))

            node2 = component_func(
                component_in_number=job_in_other_number,
                component_in_path=node1.outputs.component_out_path,
            )
            return {"job_out_data": node2.outputs.component_out_path}

        pipeline = pipeline_remote_component(10, 15, job_input)
        client.jobs.create_or_update(pipeline, experiment_name=experiment_name)

    def test_component_load_from_remote(self, client: MLClient, hello_world_component: ComponentEntity) -> None:
        component_func = load_component(
            client=client,
            name=hello_world_component.name,
            version=hello_world_component.version,
        )

        component_node = component_func(component_in_number=10, component_in_path=job_input)

        component_job_dict = component_node._to_rest_object()
        assert is_ARM_id_for_resource(component_job_dict["componentId"])
        omit_fields = ["componentId", "_source", "properties"]
        component_job_dict = pydash.omit(component_job_dict, *omit_fields)
        assert component_job_dict == {
            "computeId": None,
            "display_name": None,
            "distribution": None,
            "environment_variables": {},
            "inputs": {
                "component_in_number": {"job_input_type": "literal", "value": "10"},
                "component_in_path": {
                    "job_input_type": "uri_file",
                    "uri": "https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
                },
            },
            "limits": None,
            "name": None,
            "outputs": {},
            "resources": {"instance_count": 1, "properties": {}},
            "tags": {},
            "type": "command",
        }

    @pytest.mark.skip(reason="migration skip: gpu-cluster is not available yet.")
    def test_distribution_components(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        mpi_func = load_component(source=str(components_dir / "helloworld_component_mpi.yml"))
        pytorch_func = load_component(source=str(components_dir / "helloworld_component_pytorch.yml"))
        tensorflow_func = load_component(source=str(components_dir / "helloworld_component_tensorflow.yml"))

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="gpu-cluster",
            experiment_name=experiment_name,
        )
        def pipeline_distribution_components(job_in_number, job_in_path):
            hello_world_component_mpi = mpi_func(component_in_number=job_in_number, component_in_path=job_in_path)
            hello_world_component_mpi.distribution = MpiDistribution()
            hello_world_component_mpi.distribution.process_count_per_instance = 2

            hello_world_component_pytorch = pytorch_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )
            hello_world_component_pytorch.distribution = PyTorchDistribution()
            hello_world_component_pytorch.distribution.process_count_per_instance = 2

            hello_world_component_tensorflow = tensorflow_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )
            hello_world_component_tensorflow.distribution = TensorFlowDistribution()
            hello_world_component_tensorflow.distribution.worker_count = 2

        pipeline = pipeline_distribution_components(10, job_input)
        client.jobs.create_or_update(pipeline, experiment_name=experiment_name)

    def test_component_with_binding(self, client: MLClient, randstr: Callable[[str], str]):
        hello_world_component_yaml = str(components_dir / "helloworld_component.yml")
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        merge_outputs_component_yaml = str(components_dir / "merge_outputs_component.yml")
        merge_outputs_component_func = load_component(source=merge_outputs_component_yaml)

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def pipeline_with_binding(job_in_number, job_in_other_number, job_in_path):
            hello_world_component_1 = hello_world_component_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )
            hello_world_component_2 = hello_world_component_func(
                component_in_number=job_in_number, component_in_path=job_in_path
            )

            # configure component overrides, curated SDK not supported yet
            # hello_world_component_2.resources.instance_count = 2

            # configure component outputs
            hello_world_component_1.outputs.component_out_path.mode = "Upload"
            hello_world_component_2.outputs.component_out_path.mode = "Upload"

            merge_component_outputs = merge_outputs_component_func(
                component_in_number=job_in_other_number,
                component_in_path_1=hello_world_component_1.outputs.component_out_path,
                component_in_path_2=hello_world_component_2.outputs.component_out_path,
            )
            return {
                "job_out_data_1": merge_component_outputs.outputs.component_out_path_1,
                "job_out_data_2": merge_component_outputs.outputs.component_out_path_2,
            }

        pipeline = pipeline_with_binding(10, 16, job_input)
        client.jobs.create_or_update(
            pipeline,
            experiment_name="dsl_pipeline_e2e",
        )

    def test_data_input(self, client: MLClient) -> None:
        parent_dir = str(tests_root_dir / "test_configs/dsl_pipeline/nyc_taxi_data_regression")

        def generate_dsl_pipeline():
            # 1. Load component funcs
            prep_func = load_component(source=parent_dir + "/prep.yml")
            transform_func = load_component(source=parent_dir + "/transform.yml")
            train_func = load_component(source=parent_dir + "/train.yml")
            predict_func = load_component(source=parent_dir + "/predict.yml")
            score_func = load_component(source=parent_dir + "/score.yml")

            # 2. Construct pipeline
            @dsl.pipeline(compute="cpu-cluster", default_datastore="workspaceblobstore")
            def sample_pipeline(pipeline_job_input):
                prep_job = prep_func(raw_data=pipeline_job_input)
                transform_job = transform_func(clean_data=prep_job.outputs.prep_data)
                train_job = train_func(training_data=transform_job.outputs.transformed_data)
                predict_job = predict_func(
                    model_input=train_job.outputs.model_output,
                    test_data=train_job.outputs.test_data,
                )
                score_job = score_func(
                    predictions=predict_job.outputs.predictions,
                    model=train_job.outputs.model_output,
                )
                return {
                    "pipeline_job_prepped_data": prep_job.outputs.prep_data,
                    "pipeline_job_transformed_data": transform_job.outputs.transformed_data,
                    "pipeline_job_trained_model": train_job.outputs.model_output,
                    "pipeline_job_test_data": train_job.outputs.test_data,
                    "pipeline_job_predictions": predict_job.outputs.predictions,
                    "pipeline_job_score_report": score_job.outputs.score_report,
                }

            pipeline = sample_pipeline(Input(type=AssetTypes.URI_FOLDER, path=parent_dir + "/data/"))
            pipeline.outputs.pipeline_job_prepped_data.data = "/prepped_data"
            pipeline.outputs.pipeline_job_prepped_data.mode = "rw_mount"
            pipeline.outputs.pipeline_job_transformed_data.data = "/transformed_data"
            pipeline.outputs.pipeline_job_transformed_data.mode = "rw_mount"
            pipeline.outputs.pipeline_job_trained_model.data = "/trained-model"
            pipeline.outputs.pipeline_job_trained_model.mode = "rw_mount"
            pipeline.outputs.pipeline_job_test_data.data = "/test_data"
            pipeline.outputs.pipeline_job_test_data.mode = "rw_mount"
            pipeline.outputs.pipeline_job_predictions.data = "/predictions"
            pipeline.outputs.pipeline_job_predictions.mode = "rw_mount"
            pipeline.outputs.pipeline_job_score_report.data = "/report"
            pipeline.outputs.pipeline_job_score_report.mode = "rw_mount"
            return pipeline

        # create pipeline instance
        pipeline = generate_dsl_pipeline()
        # submit job to workspace
        client.jobs.create_or_update(
            pipeline,
            experiment_name="nyc_taxi_data_regression",
        )

    def test_command_function(self, randstr: Callable[[str], str], client: MLClient):
        hello_world_component_yaml = str(components_dir / "helloworld_component.yml")
        hello_world_component_func = load_component(source=hello_world_component_yaml)
        # update component display name to work around same component register multiple time issue
        hello_world_component_func.display_name = "test_command_function_node"

        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        distribution = {"type": "Pytorch", "process_count_per_instance": 2}
        resources = {"instance_count": 2}
        environment_variables = {"environ": "val"}
        inputs = {
            "component_in_path": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
            "component_in_number": 0.01,
        }
        outputs = {"component_out_path": Output(type="mlflow_model", mode="rw_mount")}

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def mixed_pipeline(job_in_number, job_in_path):
            command_job = CommandJob(
                display_name="command-job",
                environment=environment,
                command='echo "hello world"',
                distribution=distribution,
                resources=resources,
                environment_variables=environment_variables,
                inputs=inputs,
                outputs=outputs,
            )
            command_job_func = to_component(job=command_job)

            # Command from command() function
            command_function = command(
                display_name="command-function-job",
                environment=environment,
                command='echo "hello world"',
                distribution=distribution,
                resources=resources,
                environment_variables=environment_variables,
                inputs=inputs,
                outputs=outputs,
            )

            node1 = hello_world_component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            node2 = command_job_func(
                component_in_path=node1.outputs.component_out_path,
                component_in_number=2,
            )
            node3 = command_function(
                component_in_path=node2.outputs.component_out_path,
                component_in_number=3,
            )

            return {
                "pipeline_job_out": node3.outputs.component_out_path,
            }

        pipeline = mixed_pipeline(16, job_input)
        # submit job to workspace
        pipeline_job = client.jobs.create_or_update(
            pipeline,
            experiment_name="mixed_pipeline",
        )
        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "compute_id": "cpu-cluster",
            "description": "The hello world pipeline job",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_in_number": {"job_input_type": "literal", "value": "16"},
                "job_in_path": {
                    "mode": "ReadOnlyMount",
                    "job_input_type": "uri_file",
                },
            },
            "jobs": {
                "node1": {
                    "type": "command",
                    "computeId": None,
                    "display_name": None,
                    "distribution": None,
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_in_number}}",
                        },
                        "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                    },
                    "limits": None,
                    "name": "node1",
                    "outputs": {},
                    "resources": None,
                    "tags": {},
                },
                "node2": {
                    "type": "command",
                    "computeId": None,
                    "display_name": None,
                    "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"job_input_type": "literal", "value": "2"},
                        "component_in_path": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.node1.outputs.component_out_path}}",
                        },
                    },
                    "limits": None,
                    "name": "node2",
                    "outputs": {},
                    "resources": {"instance_count": 2, "properties": {}},
                    "tags": {},
                },
                "node3": {
                    "computeId": None,
                    "display_name": "command-function-job",
                    "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                    "environment_variables": {"environ": "val"},
                    "inputs": {
                        "component_in_number": {"job_input_type": "literal", "value": "3"},
                        "component_in_path": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.node2.outputs.component_out_path}}",
                        },
                    },
                    "limits": None,
                    "name": "node3",
                    "outputs": {
                        "component_out_path": {"type": "literal", "value": "${{parent.outputs.pipeline_job_out}}"}
                    },
                    "resources": {"instance_count": 2, "properties": {}},
                    "tags": {},
                    "type": "command",
                },
            },
            "outputs": {
                "pipeline_job_out": {
                    "mode": "ReadWriteMount",
                    "job_output_type": "uri_folder",
                }
            },
            "settings": {},
        }
        assert expected_job == actual_job

    def test_command_with_optional_inputs(self, randstr: Callable[[str], str], client: MLClient):
        hello_world_component_yaml = str(components_dir / "helloworld_component_with_optional_inputs.yml")
        hello_world_component_func = load_component(source=hello_world_component_yaml)
        command_func = command(
            name=f"test_optional_input_component_" + randstr("component_name"),
            display_name="command_with_optional_inputs",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
            command=(
                'echo "hello world" '
                "& echo $[[${{inputs.float}}]] "
                "& echo $[[${{inputs.integer}}]] "
                "& echo $[[${{inputs.string}}]] "
                "& echo $[[${{inputs.boolean}}]] "
                "& echo ${{inputs.uri_folder}} "
                "& echo $[[${{inputs.optional_0}}]] "
                "& echo $[[${{inputs.optional_1}}]]"
                "& echo $[[${{inputs.optional_2}}]]"
            ),
            distribution={"type": "Pytorch", "process_count_per_instance": 2},
            resources={"instance_count": 2},
            environment_variables={"environ": "val"},
            inputs={
                "float": Input(type="number", default=1.1, min=0, max=5, optional=True),
                "integer": Input(type="integer", default=2, min=-1, max=4, optional=True),
                "string": Input(type="string", default="default_str", optional=True),
                "boolean": Input(type="boolean", default=False, optional=True),
                "uri_folder": Input(type="uri_folder"),
                "optional_0": Input(type="uri_file", optional=True),
                "optional_1": Input(type="number", optional=True),
                "optional_2": Input(type="number", optional=True, default=1.2),
            },
            outputs={"component_out_path": Output(type="uri_folder")},
        )

        component = client.components.create_or_update(command_func.component)
        assert component and component.version == "1"

        @dsl.pipeline(
            name=f"test_optional_input_component_pipeline_" + randstr("pipeline_name"),
            description="The command node with optional inputs",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def sample_pipeline(job_in_file):
            node1 = hello_world_component_func(component_in_path=job_in_file)
            node2 = command_func(uri_folder=node1.outputs.component_out_path)

            return {"pipeline_output": node2.outputs.component_out_path}

        pipeline = sample_pipeline(
            Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv")
        )
        pipeline_job = client.jobs.create_or_update(pipeline)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "description": "The command node with optional inputs",
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "compute_id": "cpu-cluster",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_in_file": {
                    "mode": "ReadOnlyMount",
                    "job_input_type": "uri_file",
                }
            },
            "jobs": {
                "node1": {
                    "computeId": None,
                    "display_name": None,
                    "distribution": None,
                    "environment_variables": {},
                    "inputs": {
                        "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_file}}"}
                    },
                    "limits": None,
                    "name": "node1",
                    "outputs": {},
                    "resources": None,
                    "tags": {},
                    "type": "command",
                },
                "node2": {
                    "computeId": None,
                    "display_name": "command_with_optional_inputs",
                    "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                    "environment_variables": {"environ": "val"},
                    "inputs": {
                        "uri_folder": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.node1.outputs.component_out_path}}",
                        }
                    },
                    "limits": None,
                    "name": "node2",
                    "outputs": {
                        "component_out_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output}}"}
                    },
                    "resources": {"instance_count": 2, "properties": {}},
                    "tags": {},
                    "type": "command",
                },
            },
            "outputs": {"pipeline_output": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
            "settings": {},
        }
        assert expected_job == actual_job

    @pytest.mark.skip("Skip for compute resource not ready.")
    def test_spark_with_optional_inputs(self, randstr: Callable[[str], str], client: MLClient):
        component_yaml = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/component_with_optional_inputs.yml"
        spark_with_optional_inputs_component_func = load_component(source=component_yaml)
        synapse_compute_name = "spark31"

        @dsl.pipeline(
            name=f"test_optional_input_component_pipeline_" + randstr("pipeline_name"),
            description="The spark node with optional inputs",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute=synapse_compute_name,
        )
        def sample_pipeline(job_in_file, sample_rate):
            node1 = spark_with_optional_inputs_component_func(input1=job_in_file, sample_rate=sample_rate)
            node1.compute = synapse_compute_name
            return {"pipeline_output": node1.outputs.output1}

        pipeline = sample_pipeline(
            job_in_file=Input(
                path="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/shakespeare.txt",
                type=AssetTypes.URI_FILE,
                mode=InputOutputModes.DIRECT,
            ),
            sample_rate=0.01,
        )
        pipeline.outputs.pipeline_output.mode = InputOutputModes.DIRECT
        pipeline_job = client.jobs.create_or_update(pipeline)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "description": "The spark node with optional inputs",
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "compute_id": "spark31",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_in_file": {"job_input_type": "uri_file", "mode": "Direct"},
                "sample_rate": {"job_input_type": "literal", "value": "0.01"},
            },
            "jobs": {
                "node1": {
                    "archives": None,
                    "args": "--input1 ${{inputs.input1}} --output2 "
                    "${{outputs.output1}} --my_sample_rate "
                    "${{inputs.sample_rate}} $[[--input_optional "
                    "${{inputs.input_optional}}]]",
                    "computeId": "spark31",
                    "conf": {
                        "spark.driver.cores": 1,
                        "spark.driver.memory": "2g",
                        "spark.dynamicAllocation.enabled": True,
                        "spark.dynamicAllocation.maxExecutors": 4,
                        "spark.dynamicAllocation.minExecutors": 1,
                        "spark.executor.cores": 2,
                        "spark.executor.instances": 1,
                        "spark.executor.memory": "2g",
                    },
                    "display_name": None,
                    "entry": {
                        "file": "sampleword_with_optional_input.py",
                        "spark_job_entry_type": "SparkJobPythonEntry",
                    },
                    "files": None,
                    "identity": {"identity_type": "Managed"},
                    "inputs": {
                        "input1": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_file}}"},
                        "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                    },
                    "jars": None,
                    "name": "node1",
                    "outputs": {"output1": {"type": "literal", "value": "${{parent.outputs.pipeline_output}}"}},
                    "py_files": None,
                    "resources": None,
                    "tags": {},
                    "type": "spark",
                }
            },
            "outputs": {"pipeline_output": {"mode": "Direct", "job_output_type": "uri_folder"}},
            "settings": {},
        }
        assert expected_job == actual_job

    def test_command_by_pass(self, randstr: Callable[[str], str], client: MLClient):
        hello_world_component_yaml = str(components_dir / "helloworld_component.yml")
        component_func = load_component(source=hello_world_component_yaml)
        # update component display name to work around same component register multiple time issue
        component_func.display_name = "test_command_by_pass"

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            default_compute="cpu-cluster",
            experiment_name=experiment_name,
            continue_on_step_failure=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            # dynamic fields will pass through to backend
            node1 = component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            node1.new_field = "val"
            node2 = component_func(component_in_number=job_in_other_number, component_in_path=job_in_path)
            node2.new_field = {}

        pipeline = pipeline(10, 20, job_input)
        pipeline_job = client.jobs.create_or_update(
            pipeline,
            experiment_name="dsl_exp",
        )
        pipeline_job.settings.force_rerun = False
        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "description": "The hello world pipeline job",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_in_number": {"job_input_type": "literal", "value": "10"},
                "job_in_other_number": {"job_input_type": "literal", "value": "20"},
                "job_in_path": {
                    "mode": "ReadOnlyMount",
                    "job_input_type": "uri_file",
                },
            },
            "jobs": {
                "node1": {
                    "type": "command",
                    "computeId": None,
                    "display_name": None,
                    "distribution": None,
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_in_number}}",
                        },
                        "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                    },
                    "limits": None,
                    "name": "node1",
                    "new_field": "val",
                    "outputs": {},
                    "resources": None,
                    "tags": {},
                },
                "node2": {
                    "type": "command",
                    "computeId": None,
                    "display_name": None,
                    "distribution": None,
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_in_other_number}}",
                        },
                        "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                    },
                    "limits": None,
                    "name": "node2",
                    "outputs": {},
                    "resources": None,
                    "tags": {},
                },
            },
            "outputs": {},
            "settings": {
                "continue_on_step_failure": True,
                "force_rerun": False,
                "default_compute": "cpu-cluster",
            },
        }
        assert expected_job == actual_job

    def test_pipeline_parameter_with_default_value(self, client: MLClient) -> None:
        input_types_func = load_component(source=str(components_dir / "input_types_component.yml"))

        # Construct pipeline
        @dsl.pipeline(
            default_compute="cpu-cluster",
            description="This is the basic pipeline with several input types",
        )
        def input_types_pipeline(
            component_in_string="component_in_string",
            component_in_ranged_integer=10,
            component_in_enum="world",
            component_in_boolean=True,
            component_in_ranged_number=8,
        ):
            input_types_func(
                component_in_string=component_in_string,
                component_in_ranged_integer=component_in_ranged_integer,
                component_in_enum=component_in_enum,
                component_in_boolean=component_in_boolean,
                component_in_ranged_number=component_in_ranged_number,
            )

        pipeline = input_types_pipeline()  # use default pipeline parameter
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="input_types_pipeline")

        assert pipeline_job.inputs.component_in_string._data == "component_in_string"
        assert pipeline_job.inputs.component_in_ranged_integer._data == "10"
        assert pipeline_job.inputs.component_in_enum._data == "world"
        assert pipeline_job.inputs.component_in_boolean._data == "True"
        assert pipeline_job.inputs.component_in_ranged_number._data == "8"

    def test_component_with_default_optional_input(self, client: MLClient) -> None:
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # Construct pipeline
        @dsl.pipeline(
            default_compute="cpu-cluster",
            description="This is the basic pipeline with several input types",
        )
        def default_optional_pipeline():
            default_optional_func(
                required_param="def",
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            )
            default_optional_func(
                required_param="def",
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                optional_input=None,
                required_param_with_default=None,
                optional_param=None,
                optional_param_with_default=None,
            )

        pipeline = default_optional_pipeline()  # use default pipeline parameter
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")

        # only the two required input exists
        assert len(pipeline_job.jobs["default_optional_component"].inputs) == 2
        # TODO: optional_param_with_default should also exists
        assert len(pipeline_job.jobs["default_optional_component_1"].inputs) == 2

    def test_pipeline_with_none_parameter_has_default_optional_false(self, client: MLClient) -> None:
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

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
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default=None,
        )
        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "inputs.required_param_with_default": "Required input 'required_param_with_default' for pipeline 'pipeline_with_default_optional_parameters' not provided."
        }

        # None input is not binding to a required input
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=None,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
        )
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")

        # only the two required input exists
        assert len(next(pipeline_job.jobs.values().__iter__()).inputs) == 2
        validate_result = pipeline._validate()
        assert validate_result.passed is True

        # Not pass required parameter with default value
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
        )
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        # only the two required input exists
        assert len(next(pipeline_job.jobs.values().__iter__()).inputs) == 2
        validate_result = pipeline._validate()
        assert validate_result.passed is True

    def test_pipeline_with_none_parameter_no_default_optional_true(self, client: MLClient) -> None:
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # None input is binding to a optional input

        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param=None,
            optional_param_with_default="optional_param_with_default",
        )
        # todo: uncomment this when backend remove component job optional input which is binding to a None pipeline
        #  input
        # pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "optional_param" not in pipeline.inputs

        # assert "optional_param" not in pipeline_job.inputs
        # assert "optional_param" not in next(pipeline_job.jobs.values().__iter__()).inputs

        # None input is not binding to a optional input
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=None,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param=None,
            optional_param_with_default="optional_param_with_default",
        )
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "optional_param" not in pipeline.inputs
        assert "optional_param" not in pipeline_job.inputs

        # Not pass required parameter with default value
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param=None,
            optional_param_with_default="optional_param_with_default",
        )
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "optional_param" not in pipeline.inputs
        assert "optional_param" not in pipeline_job.inputs

    def test_check_pipeline_component_parameter(self, client: MLClient):
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        @dsl.pipeline()
        def pipeline_missing_type(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param_with_default=optional_param_with_default,
            )

        with pytest.raises(ValidationException) as e:
            client.components.create_or_update(pipeline_missing_type)

        assert (
            "Unknown type of parameter ['required_input', 'required_param', 'required_param_with_default', 'optional_param', 'optional_param_with_default'] in pipeline func 'pipeline_missing_type'"
            in e.value.message
        )

        @dsl.pipeline(non_pipeline_inputs=['param'])
        def pipeline_with_non_pipeline_inputs(
            required_input: Input,
            required_param: str,
            param: str,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
            )

        with pytest.raises(ValidationException) as e:
            client.components.create_or_update(pipeline_with_non_pipeline_inputs)
        assert "Cannot register pipeline component 'pipeline_with_non_pipeline_inputs' with non_pipeline_inputs." in e.value.message

    def test_create_pipeline_component_by_dsl(self, caplog, client: MLClient):
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        @dsl.pipeline(continue_on_step_failure=True, force_rerun=True, default_datastore="test")
        def valid_pipeline_func(
            required_input: Input,
            required_param: str,
            node_compute: str = "cpu-cluster",
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
            )
            node2 = default_optional_func(
                required_input=required_input,
                required_param=required_param,
            )
            node2.compute = node_compute

        component = valid_pipeline_func._pipeline_builder.build(user_provided_kwargs={})
        assert component._auto_increment_version is True
        # Set original module_logger with pkg name to 'Operation' to enable caplog capture logs
        from azure.ai.ml.operations import _component_operations

        _component_operations.module_logger = logging.getLogger("Operation")

        # Assert binding on compute not changed after resolve dependencies
        client.components._resolve_arm_id_for_pipeline_component_jobs(
            component.jobs, resolver=client.components._orchestrators.get_asset_arm_id
        )
        assert component.jobs["node2"].compute == "${{parent.inputs.node_compute}}"

        with caplog.at_level(logging.WARNING):
            client.components.create_or_update(valid_pipeline_func)
        assert (
            "Job settings {'default_datastore': 'test', 'continue_on_step_failure': True, 'force_rerun': True} on pipeline function 'valid_pipeline_func' are ignored when creating PipelineComponent."
            in caplog.messages
        )

    def test_create_pipeline_with_parameter_group(self, client: MLClient) -> None:
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        @parameter_group
        class SubGroup:
            required_param: str

        @parameter_group
        class Group:
            sub: SubGroup
            node_compute: str = "cpu-cluster"

        @dsl.pipeline()
        def sub_pipeline_func(
            required_input: Input,
            group: Group,
            sub_group: SubGroup,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=group.sub.required_param,
            )
            node2 = default_optional_func(
                required_input=required_input,
                required_param=sub_group.required_param,
            )
            node2.compute = group.node_compute

        @dsl.pipeline(default_compute="cpu-cluster")
        def root_pipeline_with_group(
            r_required_input: Input,
            r_group: Group,
        ):
            sub_pipeline_func(required_input=r_required_input, group=r_group, sub_group=r_group.sub)

        job = root_pipeline_with_group(
            r_required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            r_group=Group(sub=SubGroup(required_param="hello")),
        )
        rest_job = assert_job_cancel(job, client)
        assert len(rest_job.inputs) == 2
        rest_job_dict = rest_job._to_dict()
        assert rest_job_dict["inputs"] == {
            "r_required_input": {
                "mode": "ro_mount",
                "type": "uri_file",
                "path": "azureml:https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
            },
            "r_group.sub.required_param": "hello",
            "r_group.node_compute": "cpu-cluster",
        }
        assert rest_job_dict["jobs"]["sub_pipeline_func"]["inputs"] == {
            "required_input": {"path": "${{parent.inputs.r_required_input}}"},
            "group.sub.required_param": {"path": "${{parent.inputs.r_group.sub.required_param}}"},
            "group.node_compute": {"path": "${{parent.inputs.r_group.node_compute}}"},
            "sub_group.required_param": {"path": "${{parent.inputs.r_group.sub.required_param}}"},
        }

    def test_pipeline_with_none_parameter_has_default_optional_true(self, client: MLClient) -> None:
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # None input is binding to a optional input

        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param="optional_param",
            optional_param_with_default=None,
        )
        # todo: uncomment this when backend remove component job optional input which is binding to a None pipeline
        #  input
        # pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "optional_param_with_default" not in pipeline.inputs

        # assert "optional_param_with_default" not in pipeline_job.inputs
        # assert "optional_param_with_default" not in next(pipeline_job.jobs.values().__iter__()).inputs

        # None input is not binding to a optional input
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param,
                optional_param_with_default=None,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param="optional_param",
            optional_param_with_default=None,
        )
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "optional_param_with_default" not in pipeline.inputs
        assert "optional_param_with_default" not in pipeline_job.inputs

        # Not pass required parameter with default value
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param="optional_param",
            optional_param_with_default=None,
        )
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "optional_param_with_default" not in pipeline.inputs
        assert "optional_param_with_default" not in pipeline_job.inputs

        # Pass not-none value to component func directly but set none in pipeline parameter
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
                required_param=required_param,
                required_param_with_default="required_param_with_default",
                optional_param="optional_param",
                optional_param_with_default="optional_param_with_default",
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=None,
            required_param="hello",
            required_param_with_default=None,
            optional_param=None,
            optional_param_with_default=None,
        )
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "required_input" not in pipeline.inputs
        assert "required_input" not in pipeline_job.inputs
        assert "required_param_with_default" not in pipeline.inputs
        assert "required_param_with_default" not in pipeline_job.inputs
        assert "optional_param" not in pipeline.inputs
        assert "optional_param" not in pipeline_job.inputs
        assert "optional_param_with_default" not in pipeline.inputs
        assert "optional_param_with_default" not in pipeline_job.inputs

    def test_pipeline_with_none_parameter_binding_to_two_component_inputs(self, client: MLClient) -> None:
        default_optional_func = load_component(source=str(components_dir / "default_optional_component.yml"))

        # None pipeline parameter is binding to two optional component input, removed None input

        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
            optional_param,
            optional_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param,
                optional_param_with_default=optional_param_with_default,
            )
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param_with_default,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param="optional_param",
            optional_param_with_default=None,
        )
        # todo: uncomment this when backend remove component job optional input which is binding to a None pipeline
        #  input
        # pipeline_job = client.jobs.create_or_update(pipeline, experiment_name="default_optional_pipeline")
        assert "optional_param_with_default" not in pipeline.inputs
        # assert "optional_param_with_default" not in pipeline_job.inputs
        # assert "optional_param_with_default" not in next(pipeline_job.jobs.values().__iter__()).inputs

    def test_component_reuse(self, client: MLClient) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(source=path)

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)

            component_func2 = load_component(source=path)
            node3 = component_func2(component_in_number=component_in_number, component_in_path=component_in_path)

            node1.compute = "cpu-cluster"
            node2.compute = "cpu-cluster"
            node3.compute = "cpu-cluster"

        pipeline1 = pipeline(10, job_input)

        pipeline1 = client.create_or_update(pipeline1)

        component_ids = set()
        for _, job in pipeline1.jobs.items():
            component_id = job.component
            component_ids.add(component_id)

        assert len(component_ids) == 1, f"Got multiple component id: {component_ids} for same anon component."

    @pytest.mark.skip(reason="migration skip: need to discuss reuse in current test mechanism.")
    def test_pipeline_reuse(self, client: MLClient, randstr: Callable[[str], str], randint: Callable) -> None:
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name=experiment_name,
            continue_run_on_step_failure=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=job_in_other_number, component_in_path=job_in_path)

        input_number = randint()
        pipeline = pipeline(input_number, input_number, job_input)
        job = client.jobs.create_or_update(pipeline)
        while True:
            sleep_if_live(30)
            children = client.jobs.list(parent_job_name=job.name)
            children = list(children)
            if len(children) == 2:
                break

        assert len(children) == 2
        child0, child1 = children
        # children sequence is not guaranteed, so we need to check both
        if PipelineConstants.REUSED_FLAG_FIELD in child0.properties.keys():
            assert child0.properties[PipelineConstants.REUSED_FLAG_FIELD] == PipelineConstants.REUSED_FLAG_TRUE
        elif PipelineConstants.REUSED_FLAG_FIELD in child1.properties.keys():
            assert child1.properties[PipelineConstants.REUSED_FLAG_FIELD] == PipelineConstants.REUSED_FLAG_TRUE
        else:
            assert False, "Neither child reuses."

    def test_pipeline_with_component_input_name_case(self, client: MLClient) -> None:
        hello_world_component_func = load_component(
            source=str(components_dir / "helloworld_component_with_uppercase_input.yml")
        )

        # input name is the same with yaml definition
        @dsl.pipeline(default_compute="cpu-cluster")
        def hello_world_pipeline(component_in_number, component_in_path):
            hello_world_component_func(component_In_number=component_in_number, component_in_path=component_in_path)

        pipeline = hello_world_pipeline(component_in_number=10, component_in_path=job_input)
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name=experiment_name)
        assert "component_In_number" in next(pipeline_job.jobs.values().__iter__()).inputs

        # input name is lower case
        @dsl.pipeline(default_compute="cpu-cluster")
        def hello_world_pipeline(component_in_number, component_in_path):
            hello_world_component_func(component_in_number=component_in_number, component_in_path=component_in_path)

        pipeline = hello_world_pipeline(component_in_number=10, component_in_path=job_input)
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name=experiment_name)
        assert "component_In_number" in next(pipeline_job.jobs.values().__iter__()).inputs

        # input name is equal to yaml definition input if both change to lower case
        @dsl.pipeline(default_compute="cpu-cluster")
        def hello_world_pipeline(component_in_number, component_in_path):
            hello_world_component_func(component_In_Number=component_in_number, component_in_path=component_in_path)

        pipeline = hello_world_pipeline(component_in_number=10, component_in_path=job_input)
        pipeline_job = client.jobs.create_or_update(pipeline, experiment_name=experiment_name)
        assert "component_In_number" in next(pipeline_job.jobs.values().__iter__()).inputs

        # two identical input are given if ignore case
        @dsl.pipeline(default_compute="cpu-cluster")
        def hello_world_pipeline(component_in_number, component_in_path):
            hello_world_component_func(component_In_number=component_in_number, component_in_number=component_in_path)

        with pytest.raises(ValidationException) as ex:
            hello_world_pipeline(component_in_number=10, component_in_path=job_input)
        assert (
            "Invalid component input names 'component_in_number' and 'component_In_number', which are equal"
            in ex.value.message
        )

    def test_pipeline_job_help_function(self, client: MLClient):
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline(default_compute="cpu-cluster")
        def pipeline(number, path):
            component_func = load_component(source=yaml_file)
            node1 = component_func(component_in_number=number, component_in_path=path)
            return {"pipeline_output": node1.outputs.component_out_path}

        pipeline1 = pipeline(10, job_input)
        pipeline1 = client.create_or_update(pipeline1)
        with patch("sys.stdout", new=StringIO()) as std_out:
            print(pipeline1)
            assert (
                "display_name: pipeline\ntype: pipeline\ninputs:\n  number: '10'\n  path:\n    mode: ro_mount\n    type: uri_file\n    path:"
                in std_out.getvalue()
            )

    def test_node_property_setting_validation(self, client: MLClient) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(source=path)

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node1.jeff_special_option.foo = "bar"
            node1.compute = "cpu-cluster"

        dsl_pipeline: PipelineJob = pipeline(10, job_input)
        with patch("azure.ai.ml.entities._validation.module_logger.info") as mock_logging:
            _ = client.jobs.create_or_update(dsl_pipeline)
            mock_logging.assert_called_with("Warnings: [jobs.node1.jeff_special_option: Unknown field.]")

    @pytest.mark.skip(reason="migration skip: gpu-cluster is not available yet.")
    def test_anon_component_in_pipeline(
        self, client: MLClient, randstr: Callable[[str], str], hello_world_component: Component
    ) -> None:
        hello_world_func = load_component(
            client=client, name=hello_world_component.name, version=hello_world_component.version
        )
        origin_id = hello_world_func.id
        mpi_func = load_component(source=str(components_dir / "helloworld_component_mpi.yml"))
        assert mpi_func._validate().passed

        # name of anonymous component in pipeline job should be overwritten
        mpi_func.name = "_invalid"
        assert not mpi_func._validate().passed

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="gpu-cluster",
            experiment_name=experiment_name,
            continue_on_step_failure=False,
        )
        def pipeline_distribution_components(job_in_number, job_in_path):
            helloworld_component = hello_world_func(component_in_number=job_in_number, component_in_path=job_in_path)
            helloworld_component.outputs.component_out_path = Output(dataset=Data(name="mldesigner_component_output"))
            hello_world_component_mpi = mpi_func(component_in_number=job_in_number, component_in_path=job_in_path)
            hello_world_component_mpi.distribution = MpiDistribution()
            hello_world_component_mpi.distribution.process_count_per_instance = 2

        pipeline: PipelineJob = pipeline_distribution_components(10, job_input)
        assert mpi_func._is_anonymous is False
        assert pipeline.settings.continue_on_step_failure is False
        created_job: PipelineJob = client.jobs.create_or_update(
            pipeline, experiment_name=experiment_name, continue_on_step_failure=True
        )
        # continue_on_step_failure can't be set in create_or_update
        assert created_job.settings.continue_on_step_failure is False
        assert mpi_func._is_anonymous is True
        assert hello_world_func._is_anonymous is False
        assert origin_id == hello_world_func.id

    def test_pipeline_force_rerun(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name=experiment_name,
            continue_on_step_failure=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=job_in_other_number, component_in_path=job_in_path)

        pipeline = pipeline(10, 15, job_input)
        job = client.jobs.create_or_update(pipeline)
        assert job.settings.force_rerun is None

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name=experiment_name,
            continue_on_step_failure=True,
            force_rerun=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=job_in_other_number, component_in_path=job_in_path)

        pipeline = pipeline(10, 15, job_input)
        job = client.jobs.create_or_update(pipeline, force_rerun=True)
        assert job.settings.force_rerun is True

    def test_parallel_components_with_tabular_input(self, client: MLClient) -> None:
        components_dir = tests_root_dir / "test_configs/dsl_pipeline/parallel_component_with_tabular_input"

        batch_inference = load_component(source=str(components_dir / "tabular_input_e2e.yml"))

        # Construct pipeline
        @dsl.pipeline(default_compute="cpu-cluster")
        def parallel_in_pipeline(job_data_path, score_model):
            batch_inference_node = batch_inference(job_data_path=job_data_path, score_model=score_model)
            batch_inference_node.mini_batch_size = 5

        pipeline = parallel_in_pipeline(
            job_data_path=Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/neural-iris-mltable",
                mode=InputOutputModes.DIRECT,
            ),
            score_model=Input(
                path="./tests/test_configs/model", type=AssetTypes.URI_FOLDER, mode=InputOutputModes.DOWNLOAD
            ),
        )
        # submit pipeline job
        pipeline_job = assert_job_cancel(pipeline, client, experiment_name="parallel_in_pipeline")

        # check required fields in job dict
        job_dict = pipeline_job._to_dict()
        expected_keys = ["status", "properties", "tags", "creation_context"]
        for k in expected_keys:
            assert k in job_dict.keys(), f"failed to get {k} in {job_dict}"

        # original job did not change
        assert_job_input_output_types(pipeline_job)
        assert pipeline_job.settings.default_compute == "cpu-cluster"

    def test_parallel_components_with_file_input(self, client: MLClient) -> None:
        components_dir = tests_root_dir / "test_configs/dsl_pipeline/parallel_component_with_file_input"

        batch_inference = load_component(source=str(components_dir / "score.yml"))

        # Construct pipeline
        @dsl.pipeline(default_compute="cpu-cluster")
        def parallel_in_pipeline(job_data_path):
            batch_inference_node = batch_inference(job_data_path=job_data_path)
            batch_inference_node.mini_batch_size = 5

        pipeline = parallel_in_pipeline(
            job_data_path=Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data",
                mode=InputOutputModes.EVAL_MOUNT,
            ),
        )
        # submit pipeline job
        pipeline_job = assert_job_cancel(pipeline, client, experiment_name="parallel_in_pipeline")
        # check required fields in job dict
        job_dict = pipeline_job._to_dict()
        expected_keys = ["status", "properties", "tags", "creation_context"]
        for k in expected_keys:
            assert k in job_dict.keys(), f"failed to get {k} in {job_dict}"

        # original job did not change
        assert_job_input_output_types(pipeline_job)
        assert pipeline_job.settings.default_compute == "cpu-cluster"

    def test_parallel_run_function(self, client: MLClient):
        # command job with dict distribution
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        inputs = {
            "job_data_path": Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data",
                mode=InputOutputModes.EVAL_MOUNT,
            ),
            "job_data_path_optional": Input(
                type=AssetTypes.MLTABLE,
                mode=InputOutputModes.EVAL_MOUNT,
                optional=True,
            ),
        }
        input_data = "${{inputs.job_data_path}}"
        outputs = {"job_output_path": Output(type=AssetTypes.URI_FOLDER, mode="rw_mount")}
        expected_resources = {"instance_count": 2}

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
        )

        data = Input(
            type=AssetTypes.MLTABLE,
            path="./tests/test_configs/dataset/mnist-data",
            mode=InputOutputModes.EVAL_MOUNT,
        )

        @dsl.pipeline(experiment_name="test_pipeline_with_parallel_function", default_compute="cpu-cluster")
        def parallel_in_pipeline(job_data_path):
            node1 = parallel_function(job_data_path=job_data_path)
            return {
                "pipeline_output": node1.outputs.job_output_path,
            }

        pipeline = parallel_in_pipeline(data)

        pipeline_job = client.create_or_update(pipeline)  # submit pipeline job

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "tags": {},
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_data_path": {"job_input_type": "mltable", "mode": "EvalMount"},
            },
            "jobs": {
                "node1": {
                    "computeId": None,
                    "input_data": "${{inputs.job_data_path}}",
                    "display_name": "my-evaluate-job",
                    "inputs": {
                        "job_data_path": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_data_path}}",
                        }
                    },
                    "name": "node1",
                    "mini_batch_size": 5,
                    "partition_keys": None,
                    "retry_settings": None,
                    "logging_level": "DEBUG",
                    "max_concurrency_per_instance": 1,
                    "error_threshold": 1,
                    "mini_batch_error_threshold": 1,
                    "outputs": {"job_output_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output}}"}},
                    "resources": {"instance_count": 2, "properties": {}},
                    "type": "parallel",
                    "task": {
                        "type": "run_function",
                        "code": "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
                        "entry_script": "score.py",
                        "program_arguments": "--job_output_path ${{outputs.job_output_path}}",
                        "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                    },
                    "tags": {},
                    "environment_variables": {},
                },
            },
            "outputs": {
                "pipeline_output": {
                    "mode": "ReadWriteMount",
                    "job_output_type": "uri_folder",
                }
            },
            "settings": {"default_compute": "cpu-cluster"},
        }
        assert expected_job == actual_job

        # check required fields in job dict
        job_dict = pipeline_job._to_dict()
        expected_keys = ["status", "properties", "tags", "creation_context"]
        for k in expected_keys:
            assert k in job_dict.keys(), f"failed to get {k} in {job_dict}"

        # original job did not change
        assert_job_input_output_types(pipeline_job)
        assert pipeline_job.settings.default_compute == "cpu-cluster"

    @pytest.mark.skip("TODO: re-record since job is in terminal state before cancel")
    def test_parallel_job(self, randstr: Callable[[str], str], client: MLClient):
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        inputs = {
            "job_data_path": Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data",
                mode=InputOutputModes.EVAL_MOUNT,
            ),
        }
        input_data = "${{inputs.job_data_path}}"
        outputs = {"job_output_path": Output(type=AssetTypes.URI_FOLDER, mode="rw_mount")}
        resources = {"instance_count": 2}
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
        environment_variables = {"environment": "val"}

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The pipeline job with parallel function",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            default_compute="cpu-cluster",
        )
        def parallel_in_pipeline(job_data_path):
            parallel_job = ParallelJob(
                display_name="my-evaluate-job",
                resources=resources,
                mini_batch_size=mini_batch_size,
                task=task,
                input_data=input_data,
                logging_level=logging_level,
                max_concurrency_per_instance=max_concurrency_per_instance,
                error_threshold=error_threshold,
                mini_batch_error_threshold=mini_batch_error_threshold,
                environment_variables=environment_variables,
                inputs=inputs,
                outputs=outputs,
            )
            parallel_job_func = to_component(job=parallel_job)
            parallel_node = parallel_job_func(job_data_path=job_data_path)

            return {
                "pipeline_job_out": parallel_node.outputs.job_output_path,
            }

        pipeline = parallel_in_pipeline(
            Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data",
                mode=InputOutputModes.EVAL_MOUNT,
            ),
        )
        # submit job to workspace
        pipeline_job = assert_job_cancel(pipeline, client, experiment_name="parallel_in_pipeline")
        omit_fields = [
            "jobs.parallel_node.task.code",
            "jobs.parallel_node.task.environment",
        ] + common_omit_fields
        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *omit_fields)
        expected_job = {
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "description": "The pipeline job with parallel function",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_data_path": {"job_input_type": "mltable", "mode": "EvalMount"},
            },
            "jobs": {
                "parallel_node": {
                    "computeId": None,
                    "input_data": "${{inputs.job_data_path}}",
                    "display_name": None,
                    "inputs": {
                        "job_data_path": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_data_path}}",
                        }
                    },
                    "mini_batch_size": 5,
                    "retry_settings": None,
                    "logging_level": None,
                    "max_concurrency_per_instance": 1,
                    "error_threshold": None,
                    "mini_batch_error_threshold": 1,
                    "name": "parallel_node",
                    "outputs": {
                        "job_output_path": {"value": "${{parent.outputs.pipeline_job_out}}", "type": "literal"}
                    },
                    "resources": {"instance_count": 2, "properties": {}},
                    "type": "parallel",
                    "task": {
                        "type": "run_function",
                        "entry_script": "score.py",
                        "program_arguments": "--job_output_path ${{outputs.job_output_path}}",
                    },
                    "tags": {},
                    "environment_variables": {},
                },
            },
            "outputs": {
                "pipeline_job_out": {
                    "mode": "ReadWriteMount",
                    "job_output_type": "uri_folder",
                }
            },
            "settings": {"default_compute": "cpu-cluster"},
        }
        assert expected_job == actual_job

    def test_multi_parallel_components_with_file_input_pipeline_output(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        components_dir = tests_root_dir / "test_configs/dsl_pipeline/parallel_component_with_file_input"
        batch_inference1 = load_component(source=str(components_dir / "score.yml"))
        batch_inference2 = load_component(source=str(components_dir / "score.yml"))
        convert_data = load_component(source=str(components_dir / "convert_data.yml"))

        # Construct pipeline
        @dsl.pipeline(default_compute="cpu-cluster")
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

        # submit pipeline job
        pipeline_job = assert_job_cancel(pipeline, client, experiment_name="parallel_in_pipeline")

        omit_fields = [
            "jobs.*.task.code",
            "jobs.*.task.environment",
        ] + common_omit_fields
        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *omit_fields)
        expected_job = {
            "tags": {},
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {"job_data_path": {"mode": "EvalMount", "job_input_type": "mltable"}},
            "jobs": {
                "batch_inference_node1": {
                    "type": "parallel",
                    "name": "batch_inference_node1",
                    "display_name": None,
                    "tags": {},
                    "computeId": None,
                    "inputs": {
                        "job_data_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_data_path}}"}
                    },
                    "outputs": {},
                    "mini_batch_size": 1,
                    "partition_keys": None,
                    "task": {
                        "type": "run_function",
                        "entry_script": "score.py",
                        "program_arguments": "--job_output_path ${{outputs.job_output_path}}",
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
                    "environment_variables": {},
                    "name": "convert_data_node",
                    "display_name": None,
                    "tags": {},
                    "computeId": None,
                    "inputs": {
                        "input_data": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.batch_inference_node1.outputs.job_output_path}}",
                        }
                    },
                    "outputs": {"file_output_data": {"job_output_type": "mltable"}},
                    "resources": None,
                    "distribution": None,
                    "limits": None,
                    "type": "command",
                },
                "batch_inference_node2": {
                    "type": "parallel",
                    "name": "batch_inference_node2",
                    "display_name": None,
                    "tags": {},
                    "computeId": None,
                    "inputs": {
                        "job_data_path": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.convert_data_node.outputs.file_output_data}}",
                            "mode": "EvalMount",
                        }
                    },
                    "outputs": {"job_output_path": {"value": "${{parent.outputs.job_out_data}}", "type": "literal"}},
                    "mini_batch_size": 1,
                    "partition_keys": None,
                    "task": {
                        "type": "run_function",
                        "entry_script": "score.py",
                        "program_arguments": "--job_output_path ${{outputs.job_output_path}}",
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
            "outputs": {"job_out_data": {"mode": "Upload", "job_output_type": "uri_folder"}},
            "settings": {"default_compute": "cpu-cluster"},
        }
        assert expected_job == actual_job

    def test_get_child_job(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])
        component_func2 = load_component(source=component_yaml, params_override=[{"name": randstr("component_name")}])

        @dsl.pipeline(
            name=randstr("pipeline_name"),
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
            experiment_name=experiment_name,
            continue_on_step_failure=True,
        )
        def pipeline(job_in_number, job_in_other_number, job_in_path):
            component_func1(component_in_number=job_in_number, component_in_path=job_in_path)
            component_func2(component_in_number=job_in_other_number, component_in_path=job_in_path)

        pipeline = pipeline(10, 15, job_input)
        job = client.jobs.create_or_update(pipeline)
        client.jobs.get(job.name)
        client.jobs.get(job.name)._repr_html_()  # to test client.jobs.get() works in notebook

        children = list(client.jobs.list(parent_job_name=job.name))
        for child in children:
            client.jobs.get(child.name)
            client.jobs.get(child.name)._repr_html_()

    def test_dsl_pipeline_without_setting_binding_node(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_without_setting_binding_node,
        )

        pipeline = pipeline_without_setting_binding_node()
        pipeline_job = client.jobs.create_or_update(pipeline)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "description": "E2E dummy pipeline with components defined via yaml.",
            "tags": {},
            "compute_id": "cpu-cluster",
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
                        "training_data": {"job_input_type": "literal", "value": "${{parent.inputs.training_input}}"},
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
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
            "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
            "settings": {},
        }
        assert expected_job == actual_job

    def test_dsl_pipeline_with_only_setting_pipeline_level(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_only_setting_pipeline_level,
        )

        pipeline = pipeline_with_only_setting_pipeline_level()
        pipeline_job = client.jobs.create_or_update(pipeline)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "description": "E2E dummy pipeline with components defined via yaml.",
            "tags": {},
            "compute_id": "cpu-cluster",
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
                        "training_data": {"job_input_type": "literal", "value": "${{parent.inputs.training_input}}"},
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
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
            "outputs": {"trained_model": {"mode": "Upload", "job_output_type": "uri_folder"}},
            "settings": {},
        }
        assert expected_job == actual_job

    def test_dsl_pipeline_with_only_setting_binding_node(self, client: MLClient) -> None:
        # Todo: checkout run priority when backend is ready
        from test_configs.dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_only_setting_binding_node,
        )

        pipeline = pipeline_with_only_setting_binding_node()
        pipeline_job = client.jobs.create_or_update(pipeline)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "description": "E2E dummy pipeline with components defined via yaml.",
            "tags": {},
            "compute_id": "cpu-cluster",
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
                            "mode": "ReadOnlyMount",
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_input}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                    },
                    "outputs": {
                        "model_output": {
                            "mode": "Upload",
                            "value": "${{parent.outputs.trained_model}}",
                            "type": "literal",
                        }
                    },
                }
            },
            "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
            "settings": {},
        }
        assert expected_job == actual_job

    def test_dsl_pipeline_with_setting_binding_node_and_pipeline_level(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_setting_binding_node_and_pipeline_level,
        )

        pipeline = pipeline_with_setting_binding_node_and_pipeline_level()
        pipeline_job = client.jobs.create_or_update(pipeline)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job = {
            "description": "E2E dummy pipeline with components defined via yaml.",
            "tags": {},
            "compute_id": "cpu-cluster",
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
                            "mode": "ReadOnlyMount",
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_input}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                    },
                    "outputs": {
                        "model_output": {
                            "mode": "Upload",
                            "value": "${{parent.outputs.trained_model}}",
                            "type": "literal",
                        }
                    },
                }
            },
            "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
            "settings": {},
        }
        assert expected_job == actual_job

    def test_dsl_pipeline_with_command_builder_setting_binding_node_and_pipeline_level(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pipeline_with_set_binding_output_input.pipeline import (
            pipeline_with_command_builder_setting_binding_node_and_pipeline_level,
        )

        pipeline = pipeline_with_command_builder_setting_binding_node_and_pipeline_level()
        pipeline_job = client.jobs.create_or_update(pipeline)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)

        expected_job = {
            "description": "E2E dummy pipeline with components defined via yaml.",
            "tags": {},
            "compute_id": "cpu-cluster",
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
                            "mode": "ReadOnlyMount",
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_input}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                    },
                    "outputs": {
                        "model_output": {
                            "mode": "Upload",
                            "value": "${{parent.outputs.trained_model}}",
                            "type": "literal",
                        }
                    },
                }
            },
            "outputs": {"trained_model": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
            "settings": {},
        }
        assert expected_job == actual_job

    @pytest.mark.skip("Skip for compute resource not ready.")
    def test_spark_components(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        components_dir = tests_root_dir / "test_configs/dsl_pipeline/spark_job_in_pipeline"
        synapse_compute_name = "spark31"
        add_greeting_column = load_component(str(components_dir / "add_greeting_column_component.yml"))
        count_by_row = load_component(str(components_dir / "count_by_row_component.yml"))

        # Construct pipeline
        @dsl.pipeline(compute=synapse_compute_name)
        def spark_pipeline_from_yaml(iris_data):
            add_greeting_column_node = add_greeting_column(file_input=iris_data)
            add_greeting_column_node.compute = synapse_compute_name
            count_by_row_node = count_by_row(file_input=iris_data)
            count_by_row_node.compute = synapse_compute_name
            return {"output": count_by_row_node.outputs.output}

        pipeline = spark_pipeline_from_yaml(
            iris_data=Input(
                path="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/iris.csv",
                type=AssetTypes.URI_FILE,
                mode=InputOutputModes.DIRECT,
            ),
        )
        pipeline.outputs.output.mode = "Direct"
        pipeline.outputs.output.type = "uri_file"

        # submit pipeline job
        pipeline_job = assert_job_cancel(pipeline, client, experiment_name="spark_in_pipeline")
        # check required fields in job dict
        job_dict = pipeline_job._to_dict()
        expected_keys = ["status", "properties", "tags", "creation_context"]
        for k in expected_keys:
            assert k in job_dict.keys(), f"failed to get {k} in {job_dict}"

        # original job did not change
        assert_job_input_output_types(pipeline_job)
        assert pipeline_job.compute == synapse_compute_name

    def test_pipeline_with_group(self, client: MLClient):
        from enum import Enum

        class EnumOps(Enum):
            Option1 = "hello"
            Option2 = "world"

        hello_world_component_yaml = "./tests/test_configs/components/input_types_component.yml"
        hello_world_component_func = load_component(hello_world_component_yaml)
        from azure.ai.ml.dsl._parameter_group_decorator import parameter_group

        @parameter_group
        class ParamClass:
            int_param: Input(min=1.0, max=5.0, type="integer")
            enum_param: EnumOps
            str_param: str = "test"
            bool_param: bool = True
            number_param = 4.0

        default_param = ParamClass(int_param=2, enum_param=EnumOps.Option1, bool_param=False)

        @dsl.pipeline(default_compute_target="cpu-cluster")
        def pipeline_with_group(group: ParamClass):
            hello_world_component_func(
                component_in_string=group.str_param,
                component_in_ranged_number=group.number_param,
                component_in_enum=group.enum_param,
                component_in_boolean=group.bool_param,
                component_in_ranged_integer=group.int_param,
            )

        pipeline_job = pipeline_with_group(default_param)
        pipeline_job = client.jobs.create_or_update(pipeline_job)

        actual_job = omit_with_wildcard(pipeline_job._to_rest_object().properties.as_dict(), *common_omit_fields)
        expected_job_inputs = {
            "group.int_param": {"job_input_type": "literal", "value": "2"},
            "group.enum_param": {"job_input_type": "literal", "value": "hello"},
            "group.str_param": {"job_input_type": "literal", "value": "test"},
            "group.bool_param": {"job_input_type": "literal", "value": "False"},
            "group.number_param": {"job_input_type": "literal", "value": "4.0"},
        }
        expected_node_inputs = {
            "component_in_string": {"job_input_type": "literal", "value": "${{parent.inputs.group.str_param}}"},
            "component_in_ranged_integer": {"job_input_type": "literal", "value": "${{parent.inputs.group.int_param}}"},
            "component_in_enum": {"job_input_type": "literal", "value": "${{parent.inputs.group.enum_param}}"},
            "component_in_boolean": {"job_input_type": "literal", "value": "${{parent.inputs.group.bool_param}}"},
            "component_in_ranged_number": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.group.number_param}}",
            },
        }
        assert actual_job["inputs"] == expected_job_inputs
        assert actual_job["jobs"]["microsoft_samples_command_component_basic_inputs"]["inputs"] == expected_node_inputs

    def test_dsl_pipeline_with_default_component(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
    ) -> None:
        yaml_path: str = "./tests/test_configs/components/helloworld_component.yml"
        component_name = randstr("component_name")
        component: Component = load_component(source=yaml_path, params_override=[{"name": component_name}])
        client.components.create_or_update(component)

        default_component_func = client.components.get(component_name)

        @dsl.pipeline()
        def pipeline_with_default_component():
            node1 = default_component_func(component_in_path=job_input)
            node1.compute = "cpu-cluster"

        # component from client.components.get
        pipeline_job = client.jobs.create_or_update(pipeline_with_default_component())
        created_pipeline_job: PipelineJob = client.jobs.get(pipeline_job.name)
        assert created_pipeline_job.jobs["node1"].component == f"{component_name}@default"

    def test_pipeline_node_identity_with_component(self, client: MLClient):
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

        pipeline = pipeline_func(component_in_path=job_input)
        pipeline_job = client.jobs.create_or_update(pipeline, compute="cpu-cluster")
        omit_fields = [
            "jobs.*.componentId",
            "jobs.*._source"
        ]
        actual_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict()["properties"], *omit_fields)
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
                      'environment_variables': {},
                      'identity': {'type': 'user_identity'},
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
