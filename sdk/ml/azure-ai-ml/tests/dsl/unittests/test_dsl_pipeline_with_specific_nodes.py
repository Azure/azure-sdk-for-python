from pathlib import Path

import pydash
import pytest
from test_utilities.utils import omit_with_wildcard

from azure.ai.ml import Input, Output, command, dsl, load_component, spark
from azure.ai.ml.automl import classification, regression
from azure.ai.ml.constants._common import (
    AssetTypes,
    InputOutputModes,
)
from azure.ai.ml.dsl._load_import import to_component
from azure.ai.ml.entities import (
    CommandComponent,
    CommandJob,
    Data,
    ParallelTask,
    PipelineJob,
    SparkJob,
)
from azure.ai.ml.entities._builders import Command, Parallel, Spark, Sweep
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._job.automl.tabular import ClassificationJob
from azure.ai.ml.entities._job.job_service import JobService
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.parallel import ParallelJob, RunFunction, parallel_run_function
from azure.ai.ml.sweep import (
    BanditPolicy,
    Choice,
    LogNormal,
    LogUniform,
    Normal,
    QLogNormal,
    QLogUniform,
    QNormal,
    QUniform,
    Randint,
    Uniform,
)

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestDSLPipelineWithSpecificNodes:
    def test_dsl_pipeline_sweep_node(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline(name="train_with_sweep_in_pipeline", default_compute="cpu-cluster")
        def train_with_sweep_in_pipeline(raw_data, primary_metric: str = "AUC", max_total_trials: int = 10):
            component_to_sweep: CommandComponent = load_component(source=yaml_file)
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

            component_to_link = load_component(source=yaml_file, params_override=[{"name": "node_to_link"}])
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
        # Change float to string to make dict from local and rest compatible
        pipeline_dict["inputs"]["max_total_trials"] = str(pipeline_dict["inputs"]["max_total_trials"])
        pipeline_dict["jobs"]["link_node"]["inputs"]["component_in_number"] = str(
            pipeline_dict["jobs"]["link_node"]["inputs"]["component_in_number"]
        )
        assert omit_with_wildcard(pipeline_dict, *omit_fields) == omit_with_wildcard(
            pipeline_regenerated_from_rest._to_dict(), *omit_fields
        )

    def test_dsl_pipeline_sweep_distributions(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component_for_sweep.yml"

        @dsl.pipeline(name="OneJob_RuntimeSweepWithFullSearchSpaces")
        def train_with_sweep_in_pipeline():
            component_to_sweep: CommandComponent = load_component(source=yaml_file)
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
            parallel_component: ParallelComponent = load_component(source=yaml_file)
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
        regenerated_parallel_node = Parallel._from_rest_object(parallel_node_rest_obj)
        # entity load from rest object is based on current working directory, while task.code is a local path based
        # on the yaml file in unit tests.
        regenerated_parallel_node._base_path = Path(yaml_file).parent
        parallel_node_dict_from_rest = regenerated_parallel_node._to_dict()
        omit_fields = ["component"]
        assert pydash.omit(parallel_node_dict, *omit_fields) == pydash.omit(parallel_node_dict_from_rest, *omit_fields)

    def test_dsl_pipeline_with_spark(self) -> None:
        add_greeting_column_func = load_component(
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        )
        count_by_row_func = load_component(
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/count_by_row_component.yml"
        )
        synapse_compute_name = "spark31"

        @dsl.pipeline(description="submit a pipeline with spark job")
        def spark_pipeline_from_yaml(iris_data):
            add_greeting_column = add_greeting_column_func(file_input=iris_data)
            add_greeting_column.compute = synapse_compute_name
            count_by_row = count_by_row_func(file_input=iris_data)
            count_by_row.compute = synapse_compute_name

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
            "jobs.add_greeting_column.properties",
            "jobs.count_by_row.componentId",
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
                    "resources": None,
                    "entry": {"file": "add_greeting_column.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                    "py_files": ["utils.zip"],
                    "files": ["my_files.txt"],
                    "archives": None,
                    "jars": None,
                    "identity": {"identity_type": "Managed"},
                    "conf": {
                        "spark.driver.cores": 2,
                        "spark.driver.memory": "1g",
                        "spark.executor.cores": 1,
                        "spark.executor.memory": "1g",
                        "spark.executor.instances": 1,
                    },
                    "args": "--file_input ${{inputs.file_input}}",
                    "name": "add_greeting_column",
                    "display_name": None,
                    "tags": {},
                    "computeId": "spark31",
                    "inputs": {
                        "file_input": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"},
                    },
                    "outputs": {},
                    "_source": "YAML.COMPONENT",
                },
                "count_by_row": {
                    "_source": "YAML.COMPONENT",
                    "archives": None,
                    "args": "--file_input ${{inputs.file_input}} " "--output ${{outputs.output}}",
                    "computeId": "spark31",
                    "conf": {
                        "spark.driver.cores": 2,
                        "spark.driver.memory": "1g",
                        "spark.executor.cores": 1,
                        "spark.executor.instances": 1,
                        "spark.executor.memory": "1g",
                    },
                    "display_name": None,
                    "entry": {"file": "count_by_row.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                    "files": ["my_files.txt"],
                    "identity": {"identity_type": "Managed"},
                    "inputs": {"file_input": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"}},
                    "jars": ["scalaproj.jar"],
                    "name": "count_by_row",
                    "outputs": {"output": {"type": "literal", "value": "${{parent.outputs.output}}"}},
                    "py_files": None,
                    "resources": None,
                    "tags": {},
                    "type": "spark",
                },
            },
            "outputs": {"output": {"job_output_type": "uri_folder", "mode": "Direct"}},
            "settings": {"_source": "DSL"},
        }

    def test_pipeline_with_command_function(self):
        # component func
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"
        component_func = load_component(source=yaml_file)

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
            "properties.jobs.*.componentId",
            "properties.jobs.*.properties",
            "properties.settings._source",
        ]

        pipeline1 = pipeline(10, data)
        pipeline_job1 = pipeline1._to_rest_object().as_dict()
        pipeline_job1 = omit_with_wildcard(pipeline_job1, *omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_command_function",
                "inputs": {
                    "number": {"job_input_type": "literal", "value": "10"},
                    "path": {"job_input_type": "uri_folder", "mode": "ReadOnlyMount", "uri": "/a/path/on/ds"},
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
                            "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.path}}"},
                        },
                        "limits": None,
                        "name": "node1",
                        "outputs": {
                            "component_out_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output1}}"}
                        },
                        "resources": None,
                        "tags": {},
                        "type": "command",
                    },
                    "node2": {
                        "_source": "CLASS",
                        "computeId": None,
                        "display_name": None,
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {},
                        "inputs": {
                            "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.node1.outputs.component_out_path}}",
                            },
                        },
                        "limits": None,
                        "name": "node2",
                        "outputs": {
                            "component_out_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output2}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                        "type": "command",
                    },
                    "node3": {
                        "_source": "BUILDER",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {"key": "val"},
                        "inputs": {
                            "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.node2.outputs.component_out_path}}",
                            },
                        },
                        "limits": None,
                        "name": "node3",
                        "outputs": {
                            "component_out_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output3}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                        "type": "command",
                    },
                },
                "outputs": {
                    "pipeline_output1": {"job_output_type": "uri_folder"},
                    "pipeline_output2": {"job_output_type": "uri_folder"},
                    "pipeline_output3": {"job_output_type": "uri_folder"},
                },
                "properties": {},
                "settings": {},
                "tags": {},
            }
        }

    def test_pipeline_with_spark_function(self):
        # component func
        yaml_file = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/sample_component.yml"
        component_func = load_component(yaml_file)

        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        iris_data = Input(
            path="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/shakespeare.txt",
            type=AssetTypes.URI_FILE,
            mode=InputOutputModes.DIRECT,
        )
        sample_rate = 0.01
        synapse_compute_name = "rezas-synapse-10"
        inputs = {
            "input1": iris_data,
            "sample_rate": sample_rate,
        }
        outputs = {"output1": Output(type="uri_folder", mode=InputOutputModes.DIRECT)}

        spark_job = SparkJob(
            code="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
            entry={"file": "sampleword.py"},
            driver_cores=2,
            driver_memory="1g",
            executor_cores=1,
            executor_memory="1g",
            executor_instances=1,
            environment=environment,
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
            compute=synapse_compute_name,
        )
        spark_job_func = to_component(job=spark_job)

        # Spark from spark() function
        spark_function = spark(
            code="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
            entry={"file": "sampleword.py"},
            driver_cores=2,
            driver_memory="1g",
            executor_cores=1,
            executor_memory="1g",
            executor_instances=1,
            environment=environment,
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
            compute=synapse_compute_name,
            # For HOBO spark, provide 'resources'
            # resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"}
        )

        @dsl.pipeline(experiment_name="test_pipeline_with_spark_function")
        def pipeline(iris_data, sample_rate):
            node1 = component_func(input1=iris_data, sample_rate=sample_rate)
            node1.compute = synapse_compute_name
            node2 = spark_job_func(input1=node1.outputs.output1, sample_rate=sample_rate)
            node2.compute = synapse_compute_name
            node3 = spark_function(input1=node2.outputs.output1, sample_rate=sample_rate)
            return {
                "pipeline_output1": node1.outputs.output1,
                "pipeline_output2": node2.outputs.output1,
                "pipeline_output3": node3.outputs.output1,
            }

        omit_fields = [
            "properties.jobs.*.componentId",
            "properties.jobs.*.code",
            "properties.jobs.*.properties",
            "properties.settings._source",
        ]

        pipeline1 = pipeline(iris_data, sample_rate)
        pipeline_job1 = pipeline1._to_rest_object().as_dict()
        pipeline_job1 = omit_with_wildcard(pipeline_job1, *omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "properties": {},
                "tags": {},
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_spark_function",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "iris_data": {
                        "mode": "Direct",
                        "uri": "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/shakespeare.txt",
                        "job_input_type": "uri_file",
                    },
                    "sample_rate": {"job_input_type": "literal", "value": "0.01"},
                },
                "jobs": {
                    "node1": {
                        "type": "spark",
                        "resources": None,
                        "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                        "py_files": None,
                        "jars": None,
                        "files": None,
                        "archives": None,
                        "identity": {"identity_type": "Managed"},
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
                        "args": "--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
                        "name": "node1",
                        "display_name": None,
                        "tags": {},
                        "computeId": "rezas-synapse-10",
                        "inputs": {
                            "input1": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"},
                            "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                        },
                        "outputs": {"output1": {"type": "literal", "value": "${{parent.outputs.pipeline_output1}}"}},
                        "_source": "YAML.COMPONENT",
                    },
                    "node2": {
                        "type": "spark",
                        "resources": None,
                        "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                        "py_files": None,
                        "jars": None,
                        "files": None,
                        "archives": None,
                        "identity": {"identity_type": "Managed"},
                        "conf": {
                            "spark.driver.cores": 2,
                            "spark.driver.memory": "1g",
                            "spark.executor.cores": 1,
                            "spark.executor.memory": "1g",
                            "spark.executor.instances": 1,
                        },
                        "args": "--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
                        "name": "node2",
                        "display_name": None,
                        "tags": {},
                        "computeId": "rezas-synapse-10",
                        "inputs": {
                            "input1": {"job_input_type": "literal", "value": "${{parent.jobs.node1.outputs.output1}}"},
                            "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                        },
                        "outputs": {"output1": {"value": "${{parent.outputs.pipeline_output2}}", "type": "literal"}},
                        "_source": "CLASS",
                    },
                    "node3": {
                        "type": "spark",
                        "resources": None,
                        "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                        "py_files": None,
                        "jars": None,
                        "files": None,
                        "archives": None,
                        "identity": {"identity_type": "Managed"},
                        "conf": {
                            "spark.driver.cores": 2,
                            "spark.driver.memory": "1g",
                            "spark.executor.cores": 1,
                            "spark.executor.memory": "1g",
                            "spark.executor.instances": 1,
                        },
                        "args": "--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
                        "name": "node3",
                        "display_name": None,
                        "tags": {},
                        "computeId": "rezas-synapse-10",
                        "inputs": {
                            "input1": {"job_input_type": "literal", "value": "${{parent.jobs.node2.outputs.output1}}"},
                            "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                        },
                        "outputs": {"output1": {"type": "literal", "value": "${{parent.outputs.pipeline_output3}}"}},
                        "_source": "BUILDER",
                    },
                },
                "outputs": {
                    "pipeline_output1": {"job_output_type": "uri_folder"},
                    "pipeline_output2": {"job_output_type": "uri_folder"},
                    "pipeline_output3": {"job_output_type": "uri_folder"},
                },
                "settings": {},
            }
        }

    def test_pipeline_with_spark_function_by_setting_conf(self, client):
        # component func
        yaml_file = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/sample_component.yml"
        component_func = load_component(yaml_file)

        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        iris_data = Input(
            path="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/shakespeare.txt",
            type=AssetTypes.URI_FILE,
            mode=InputOutputModes.DIRECT,
        )
        sample_rate = 0.01
        synapse_compute_name = "rezas-synapse-10"
        inputs = {
            "input1": iris_data,
            "sample_rate": sample_rate,
        }
        outputs = {"output1": Output(type="uri_folder", mode=InputOutputModes.DIRECT)}

        spark_job = SparkJob(
            code="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
            entry={"file": "sampleword.py"},
            conf={
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.memory": "1g",
                "spark.executor.instances": 1,
            },
            environment=environment,
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
            compute=synapse_compute_name,
        )
        spark_job_func = to_component(job=spark_job)

        # Spark from spark() function
        spark_function = spark(
            code="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
            entry={"file": "sampleword.py"},
            conf={
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.memory": "1g",
                "spark.executor.instances": 1,
            },
            environment=environment,
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
            compute=synapse_compute_name,
            # For HOBO spark, provide 'resources'
            # resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"}
        )

        @dsl.pipeline(experiment_name="test_pipeline_with_spark_function")
        def pipeline(iris_data, sample_rate):
            node1 = component_func(input1=iris_data, sample_rate=sample_rate)
            node1.compute = synapse_compute_name
            node2 = spark_job_func(input1=node1.outputs.output1, sample_rate=sample_rate)
            node2.compute = synapse_compute_name
            node3 = spark_function(input1=node2.outputs.output1, sample_rate=sample_rate)
            return {
                "pipeline_output1": node1.outputs.output1,
                "pipeline_output2": node2.outputs.output1,
                "pipeline_output3": node3.outputs.output1,
            }

        omit_fields = [
            "properties.jobs.*.componentId",
            "properties.jobs.*.code",
            "properties.jobs.*.properties",
            "properties.settings._source",
        ]

        pipeline1 = pipeline(iris_data, sample_rate)
        pipeline_job1 = pipeline1._to_rest_object().as_dict()
        pipeline_job1 = omit_with_wildcard(pipeline_job1, *omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "properties": {},
                "tags": {},
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_spark_function",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "iris_data": {
                        "mode": "Direct",
                        "uri": "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/shakespeare.txt",
                        "job_input_type": "uri_file",
                    },
                    "sample_rate": {"job_input_type": "literal", "value": "0.01"},
                },
                "jobs": {
                    "node1": {
                        "type": "spark",
                        "resources": None,
                        "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                        "py_files": None,
                        "jars": None,
                        "files": None,
                        "archives": None,
                        "identity": {"identity_type": "Managed"},
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
                        "args": "--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
                        "name": "node1",
                        "display_name": None,
                        "tags": {},
                        "computeId": "rezas-synapse-10",
                        "inputs": {
                            "input1": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"},
                            "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                        },
                        "outputs": {"output1": {"type": "literal", "value": "${{parent.outputs.pipeline_output1}}"}},
                        "_source": "YAML.COMPONENT",
                    },
                    "node2": {
                        "type": "spark",
                        "resources": None,
                        "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                        "py_files": None,
                        "jars": None,
                        "files": None,
                        "archives": None,
                        "identity": {"identity_type": "Managed"},
                        "conf": {
                            "spark.driver.cores": 2,
                            "spark.driver.memory": "1g",
                            "spark.executor.cores": 1,
                            "spark.executor.memory": "1g",
                            "spark.executor.instances": 1,
                        },
                        "args": "--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
                        "name": "node2",
                        "display_name": None,
                        "tags": {},
                        "computeId": "rezas-synapse-10",
                        "inputs": {
                            "input1": {"job_input_type": "literal", "value": "${{parent.jobs.node1.outputs.output1}}"},
                            "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                        },
                        "outputs": {"output1": {"value": "${{parent.outputs.pipeline_output2}}", "type": "literal"}},
                        "_source": "CLASS",
                    },
                    "node3": {
                        "type": "spark",
                        "resources": None,
                        "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                        "py_files": None,
                        "jars": None,
                        "files": None,
                        "archives": None,
                        "identity": {"identity_type": "Managed"},
                        "conf": {
                            "spark.driver.cores": 2,
                            "spark.driver.memory": "1g",
                            "spark.executor.cores": 1,
                            "spark.executor.memory": "1g",
                            "spark.executor.instances": 1,
                        },
                        "args": "--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
                        "name": "node3",
                        "display_name": None,
                        "tags": {},
                        "computeId": "rezas-synapse-10",
                        "inputs": {
                            "input1": {"job_input_type": "literal", "value": "${{parent.jobs.node2.outputs.output1}}"},
                            "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                        },
                        "outputs": {"output1": {"type": "literal", "value": "${{parent.outputs.pipeline_output3}}"}},
                        "_source": "BUILDER",
                    },
                },
                "outputs": {
                    "pipeline_output1": {"job_output_type": "uri_folder"},
                    "pipeline_output2": {"job_output_type": "uri_folder"},
                    "pipeline_output3": {"job_output_type": "uri_folder"},
                },
                "settings": {},
            }
        }

    def test_pipeline_with_spark_job_dynamic_allocation_disabled(self, client):
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        iris_data = Input(
            path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
            type=AssetTypes.URI_FILE,
            mode=InputOutputModes.DIRECT,
        )
        synapse_compute_name = "rezas-synapse-10"
        inputs = {
            "file_input1": iris_data,
            "file_input2": iris_data,
        }
        outputs = {"output": Output(type="uri_folder", mode=InputOutputModes.DIRECT)}

        spark_job = SparkJob(
            code="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
            entry={"file": "sampleword.py"},
            conf={
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.memory": "1g",
                "spark.executor.instances": 1,
                "spark.dynamicAllocation.minExecutors": 1,
                "spark.dynamicAllocation.maxExecutors": 2,
            },
            environment=environment,
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
            compute=synapse_compute_name,
        )

        spark_job_func = to_component(job=spark_job)

        @dsl.pipeline(experiment_name="test_pipeline_with_spark_function")
        def pipeline(iris_data):
            node = spark_job_func(file_input1=iris_data, file_input2=iris_data)
            node.compute = synapse_compute_name
            return {
                "pipeline_output": node.outputs.output,
            }

        pipeline1 = pipeline(iris_data)
        with pytest.raises(ValidationException) as ve:
            pipeline1._to_rest_object().as_dict()
            assert ve.message == "Should not specify min or max executors when dynamic allocation is disabled."

    def test_pipeline_with_spark_job(self):
        environment = "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5"
        iris_data = Input(
            path="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/shakespeare.txt",
            type=AssetTypes.URI_FILE,
            mode=InputOutputModes.DIRECT,
        )
        sample_rate = 0.01
        synapse_compute_name = "rezas-synapse-10"
        inputs = {
            "input1": iris_data,
            "sample_rate": sample_rate,
        }
        outputs = {"output1": Output(type="uri_folder", mode=InputOutputModes.DIRECT)}

        spark_job = SparkJob(
            code="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
            entry={"file": "sampleword.py"},
            conf={
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.memory": "1g",
                "spark.executor.instances": 1,
            },
            environment=environment,
            inputs=inputs,
            outputs=outputs,
            args="--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
            compute=synapse_compute_name,
        )

        spark_job_func = to_component(job=spark_job)

        @dsl.pipeline(experiment_name="test_pipeline_with_spark_job")
        def pipeline(iris_data, sample_rate):
            spark_node = spark_job_func(input1=iris_data, sample_rate=sample_rate)
            spark_node.compute = synapse_compute_name
            return {
                "pipeline_output1": spark_node.outputs.output1,
            }

        pipeline1 = pipeline(iris_data, sample_rate)
        pipeline_rest_obj = pipeline1._to_rest_object()
        pipeline_job1 = pipeline_rest_obj.as_dict()

        pipeline_regenerated_from_rest = PipelineJob._load_from_rest(pipeline_rest_obj)
        omit_field = [
            "outputs",  # TODO: figure out why outputs can't be regenerated correctly
        ]

        pipeline1_dict = pipeline1._to_dict()
        # Change float to string to make dict from local and rest compatible
        pipeline1_dict["inputs"]["sample_rate"] = str(pipeline1_dict["inputs"]["sample_rate"])
        assert pydash.omit(pipeline1_dict, *omit_field) == pydash.omit(
            pipeline_regenerated_from_rest._to_dict(), *omit_field
        )
        omit_fields = [
            "properties.jobs.spark_node.componentId",
            "properties.jobs.spark_node.properties",
        ]
        pipeline_job1 = pydash.omit(pipeline_job1, *omit_fields)
        assert pipeline_job1 == {
            "properties": {
                "properties": {},
                "tags": {},
                "display_name": "pipeline",
                "experiment_name": "test_pipeline_with_spark_job",
                "is_archived": False,
                "job_type": "Pipeline",
                "inputs": {
                    "iris_data": {
                        "mode": "Direct",
                        "uri": "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/dataset/shakespeare.txt",
                        "job_input_type": "uri_file",
                    },
                    "sample_rate": {"job_input_type": "literal", "value": "0.01"},
                },
                "settings": {"_source": "DSL"},
                "jobs": {
                    "spark_node": {
                        "_source": "CLASS",
                        "type": "spark",
                        "resources": None,
                        "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                        "py_files": None,
                        "jars": None,
                        "files": None,
                        "archives": None,
                        "identity": {"identity_type": "Managed"},
                        "conf": {
                            "spark.driver.cores": 2,
                            "spark.driver.memory": "1g",
                            "spark.executor.cores": 1,
                            "spark.executor.memory": "1g",
                            "spark.executor.instances": 1,
                        },
                        "args": "--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
                        "name": "spark_node",
                        "display_name": None,
                        "tags": {},
                        "computeId": "rezas-synapse-10",
                        "inputs": {
                            "input1": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"},
                            "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                        },
                        "outputs": {"output1": {"type": "literal", "value": "${{parent.outputs.pipeline_output1}}"}},
                    },
                },
                "outputs": {"pipeline_output1": {"job_output_type": "uri_folder"}},
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
            "properties.jobs.parallel_node.properties",
        ]

        pipeline1 = pipeline(data)
        pipeline_rest_obj = pipeline1._to_rest_object()
        pipeline_job1 = pipeline_rest_obj.as_dict()
        pipeline_regenerated_from_rest = PipelineJob._load_from_rest(pipeline_rest_obj)
        omit_field = [
            "jobs.parallel_node.task",
            "jobs.*.properties",
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
                    "job_data_path": {"job_input_type": "mltable", "mode": "EvalMount", "uri": "/a/path/on/ds"},
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
                            "job_data_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_data_path}}"},
                        },
                        "name": "parallel_node",
                        "outputs": {
                            "job_output_path": {"type": "literal", "value": "${{parent.outputs.pipeline_job_out}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "mini_batch_size": 5,
                        "partition_keys": None,
                        "retry_settings": None,
                        "logging_level": None,
                        "max_concurrency_per_instance": 1,
                        "error_threshold": None,
                        "mini_batch_error_threshold": 1,
                        "tags": {},
                        "environment_variables": {},
                        "task": {
                            "program_arguments": "--job_output_path " "${{outputs.job_output_path}}",
                            "code": "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
                            "entry_script": "score.py",
                            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
                            "type": "run_function",
                        },
                    },
                },
                "outputs": {"pipeline_job_out": {"job_output_type": "uri_folder"}},
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
            "properties.jobs.node1.properties",
            "properties.jobs.node2.properties",
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
                    "path": {"job_input_type": "mltable", "mode": "EvalMount", "uri": "/a/path/on/ds"},
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
                            "job_data_path": {"job_input_type": "literal", "value": "${{parent.inputs.path}}"},
                        },
                        "name": "node1",
                        "outputs": {
                            "job_output_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output1}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "mini_batch_size": 5,
                        "partition_keys": None,
                        "task": {
                            "type": "run_function",
                            "code": "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
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
                                "job_input_type": "mltable",
                                "mode": "EvalMount",
                                "uri": "new_path",
                            },
                        },
                        "name": "node2",
                        "outputs": {
                            "job_output_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output2}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "mini_batch_size": 5,
                        "partition_keys": None,
                        "task": {
                            "type": "run_function",
                            "code": "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/src/",
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
                    "pipeline_output1": {"job_output_type": "uri_folder"},
                    "pipeline_output2": {"job_output_type": "uri_folder"},
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
            "properties.jobs.node1.properties",
            "properties.jobs.node2.properties",
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
                    "number": {"job_input_type": "literal", "value": "10"},
                    "path": {"job_input_type": "uri_folder", "uri": "/a/path/on/ds"},
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "node1": {
                        "type": "command",
                        "_source": "BUILDER",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {"key": "val"},
                        "inputs": {
                            "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.number}}"},
                            "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.path}}"},
                        },
                        "limits": None,
                        "name": "node1",
                        "outputs": {
                            "component_out_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output1}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                    },
                    "node2": {
                        "type": "command",
                        "_source": "BUILDER",
                        "computeId": None,
                        "display_name": "my-evaluate-job",
                        "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
                        "environment_variables": {"key": "val"},
                        "inputs": {
                            "component_in_number": {"job_input_type": "literal", "value": "1"},
                            "component_in_path": {
                                "job_input_type": "uri_folder",
                                "uri": "new_path",
                            },
                        },
                        "limits": None,
                        "name": "node2",
                        "outputs": {
                            "component_out_path": {"type": "literal", "value": "${{parent.outputs.pipeline_output2}}"}
                        },
                        "resources": {"instance_count": 2, "properties": {}},
                        "tags": {},
                    },
                },
                "outputs": {
                    "pipeline_output1": {"job_output_type": "uri_folder"},
                    "pipeline_output2": {"job_output_type": "uri_folder"},
                },
                "properties": {},
                "settings": {"_source": "DSL"},
                "tags": {},
            }
        }

    def test_multi_parallel_components_with_file_input_pipeline_output(self) -> None:
        components_dir = tests_root_dir / "test_configs/dsl_pipeline/parallel_component_with_file_input"
        batch_inference1 = load_component(source=str(components_dir / "score.yml"))
        batch_inference2 = load_component(source=str(components_dir / "score.yml"))
        convert_data = load_component(source=str(components_dir / "convert_data.yml"))

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
            "jobs.batch_inference_node1.properties",
            "jobs.convert_data_node.componentId",
            "jobs.convert_data_node.properties",
            "jobs.batch_inference_node2.componentId",
            "jobs.batch_inference_node2.properties",
        ]
        actual_job = pydash.omit(pipeline._to_rest_object().properties.as_dict(), *omit_fields)
        assert actual_job == {
            "properties": {},
            "tags": {},
            "display_name": "parallel_in_pipeline",
            "experiment_name": "sdk-cli-v2",
            "is_archived": False,
            "job_type": "Pipeline",
            "inputs": {
                "job_data_path": {
                    "mode": "EvalMount",
                    "uri": "./tests/test_configs/dataset/mnist-data/",
                    "job_input_type": "mltable",
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
                        "job_data_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_data_path}}"}
                    },
                    "outputs": {},
                    "mini_batch_size": 1,
                    "partition_keys": None,
                    "task": {
                        "program_arguments": "--job_output_path " "${{outputs.job_output_path}}",
                        "code": "./src",
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
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.batch_inference_node1.outputs.job_output_path}}",
                        }
                    },
                    "limits": None,
                    "name": "convert_data_node",
                    "outputs": {"file_output_data": {"job_output_type": "mltable"}},
                    "resources": None,
                    "tags": {},
                    "type": "command",
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
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.convert_data_node.outputs.file_output_data}}",
                            "mode": "EvalMount",
                        }
                    },
                    "outputs": {"job_output_path": {"value": "${{parent.outputs.job_out_data}}", "type": "literal"}},
                    "mini_batch_size": 1,
                    "partition_keys": None,
                    "task": {
                        "program_arguments": "--job_output_path " "${{outputs.job_output_path}}",
                        "code": "./src",
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
            "outputs": {"job_out_data": {"mode": "Upload", "job_output_type": "uri_folder"}},
            "settings": {"_source": "DSL", "default_compute": "cpu-cluster"},
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
            "display_name": "train_with_automl_in_pipeline",
            "inputs": {
                "main_data_input": {"job_input_type": "mltable", "uri": "fake_path"},
                "max_total_trials_input": {"job_input_type": "literal", "value": "10"},
                "target_column_name_input": {"job_input_type": "literal", "value": "target"},
                "validation_data_size": {"job_input_type": "literal", "value": "0.2"},
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
                    "outputs": {"best_model": {"job_output_type": "mlflow_model"}},
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
            "settings": {"_source": "DSL", "default_compute": "cpu-cluster"},
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
        component_func1 = load_component(source=path)

        @dsl.pipeline(name="train_with_automl_in_pipeline", force_rerun=False)
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
        pipeline1.compute = "cpu-cluster"
        pipeline_dict1 = pipeline1._to_rest_object().as_dict()
        pipeline_dict1 = pydash.omit(
            pipeline_dict1["properties"],
            "jobs.node1.componentId",
            "jobs.node2.display_name",
            "jobs.node1.properties",
            "jobs.node2.properties",
        )
        assert pipeline_dict1 == {
            "compute_id": "cpu-cluster",
            "display_name": "train_with_automl_in_pipeline",
            "inputs": {
                "component_in_number": {"job_input_type": "literal", "value": "10"},
                "component_in_path": {"job_input_type": "mltable", "uri": "fake_path"},
                "target_column_name_input": {"job_input_type": "literal", "value": "target"},
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "node1": {
                    "type": "command",
                    "_source": "YAML.COMPONENT",
                    "computeId": None,
                    "display_name": None,
                    "distribution": None,
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.component_in_number}}",
                        },
                        "component_in_path": {
                            "job_input_type": "literal",
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
                    "outputs": {"best_model": {"job_output_type": "mlflow_model"}},
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
        @dsl.pipeline(name="train_with_automl_in_pipeline")
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
        pipeline1.compute = "cpu-cluster"

        pipeline_dict1 = pipeline1._to_rest_object().as_dict()
        pipeline_dict1 = pydash.omit(
            pipeline_dict1["properties"],
            ["jobs.classification_node.display_name", "jobs.classification_node.properties"],
        )
        expected_dict = {
            "compute_id": "cpu-cluster",
            "display_name": "train_with_automl_in_pipeline",
            "inputs": {
                "target_column_name_input": {"job_input_type": "literal", "value": "target"},
                "training_data": {"job_input_type": "mltable", "uri": "fake_path"},
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "classification_node": {
                    "log_verbosity": "info",
                    "name": "classification_node",
                    "outputs": {
                        "best_model": {"type": "literal", "value": "${{parent.outputs.pipeline_job_out_best_model}}"}
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
            "outputs": {"pipeline_job_out_best_model": {"job_output_type": "uri_folder"}},
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
                    "pipeline_job_out_best_model": {"job_output_type": "mlflow_model", "mode": "ReadWriteMount"}
                },
            }
        )
        assert pipeline_dict2 == expected_dict

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

    def test_pipeline_with_command_services(self):
        services = {
            "my_ssh": JobService(job_service_type="ssh"),
            "my_tensorboard": JobService(
                job_service_type="tensor_board",
                properties={
                    "logDir": "~/tblog",
                },
            ),
            "my_jupyterlab": JobService(job_service_type="jupyter_lab"),
        }
        rest_services = {
            "my_ssh": {"job_service_type": "SSH"},
            "my_tensorboard": {
                "job_service_type": "TensorBoard",
                "properties": {
                    "logDir": "~/tblog",
                },
            },
            "my_jupyterlab": {"job_service_type": "JupyterLab"},
        }

        command_func = command(
            name="test_component_with_services",
            display_name="command_with_services",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
            command=('echo "hello world" & sleep 1h'),
            environment_variables={"key": "val"},
            inputs={},
            outputs={"component_out_path": Output(type="uri_folder")},
            services=services,
        )

        @dsl.pipeline(
            name="test_component_with_services_pipeline",
            description="The command node with services",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def sample_pipeline():
            node = command_func()
            return {"pipeline_output": node.outputs.component_out_path}

        pipeline = sample_pipeline()
        node_services = pipeline.jobs["node"].services

        assert len(node_services) == 3
        for name, service in node_services.items():
            assert isinstance(service, JobService)

        job_rest_obj = pipeline._to_rest_object()
        assert job_rest_obj.properties.jobs["node"]["services"] == rest_services

        recovered_obj = PipelineJob._from_rest_object(job_rest_obj)
        node_services = recovered_obj.jobs["node"].services

        assert len(node_services) == 3
        for name, service in node_services.items():
            assert isinstance(service, JobService)

        # test set services in pipeline
        new_services = {"my_jupyter": JobService(job_service_type="jupyter_lab")}
        rest_new_services = {"my_jupyter": {"job_service_type": "JupyterLab"}}

        @dsl.pipeline()
        def sample_pipeline_with_new_services():
            node = command_func()
            node.services = new_services

        pipeline = sample_pipeline_with_new_services()
        node_services = pipeline.jobs["node"].services

        assert len(node_services) == 1
        for name, service in node_services.items():
            assert isinstance(service, JobService)

        job_rest_obj = pipeline._to_rest_object()
        assert job_rest_obj.properties.jobs["node"]["services"] == rest_new_services

    def test_pipeline_with_pipeline_component_entity(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)
        data = Data(name="test", version="1", type=AssetTypes.MLTABLE)

        @dsl.pipeline
        def sub_pipeline(component_in_number, component_in_path):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            return {"pipeline_out": node1.outputs.component_out_path}

        @dsl.pipeline
        def root_pipeline(component_in_number, component_in_path):
            node1 = sub_pipeline(component_in_number=component_in_number, component_in_path=component_in_path)
            sub_pipeline(component_in_number=2, component_in_path=data)
            return {"pipeline_out": node1.outputs.pipeline_out}

        pipeline = root_pipeline(1, data)
        pipeline_dict = pipeline._to_dict()
        assert pipeline_dict["jobs"]["node1"]["inputs"] == {
            "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
            "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
        }
        assert pipeline_dict["jobs"]["node1_1"]["inputs"] == {
            "component_in_number": 2,
            "component_in_path": {"type": "mltable", "path": "azureml:test:1"},
        }
