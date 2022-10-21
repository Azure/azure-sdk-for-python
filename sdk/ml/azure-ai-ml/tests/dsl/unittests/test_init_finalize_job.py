from functools import partial
from pathlib import Path

import pydash
import pytest
from azure.ai.ml import Input, dsl, load_component
from azure.ai.ml.constants._common import (
    AssetTypes,
    InputOutputModes,
)
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._builders import Spark

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestInitFinalizeJob:
    component_func = partial(
        load_component(str(components_dir / "echo_string_component.yml")),
        component_in_string="not important",
    )
    hello_world_func = load_component(str(components_dir / "helloworld_component.yml"))

    def test_init_finalize_job(self) -> None:
        from azure.ai.ml._internal.dsl import set_pipeline_settings
        from azure.ai.ml.dsl import pipeline

        def assert_pipeline_job_init_finalize_job(pipeline_job: PipelineJob):
            assert pipeline_job._validate_init_finalize_job().passed
            assert pipeline_job.settings.on_init == "init_job"
            assert pipeline_job.settings.on_finalize == "finalize_job"
            pipeline_job_dict = pipeline_job._to_rest_object().as_dict()
            assert pipeline_job_dict["properties"]["settings"]["on_init"] == "init_job"
            assert pipeline_job_dict["properties"]["settings"]["on_finalize"] == "finalize_job"

        # pipeline.settings.on_init/on_finalize
        @pipeline()
        def job_settings_func():
            init_job = self.component_func()  # noqa: F841
            work1 = self.component_func()  # noqa: F841
            work2 = self.component_func()  # noqa: F841
            finalize_job = self.component_func()  # noqa: F841

        pipeline1 = job_settings_func()
        pipeline1.settings.on_init = "init_job"
        pipeline1.settings.on_finalize = "finalize_job"
        assert_pipeline_job_init_finalize_job(pipeline1)

        # dsl.settings()
        @pipeline()
        def dsl_settings_func():
            init_job = self.component_func()
            work1 = self.component_func()  # noqa: F841
            work2 = self.component_func()  # noqa: F841
            finalize_job = self.component_func()  # noqa: F841
            # `set_pipeline_settings` can receive either `BaseNode` or str, both should work
            set_pipeline_settings(on_init=init_job, on_finalize="finalize_job")

        pipeline2 = dsl_settings_func()
        assert_pipeline_job_init_finalize_job(pipeline2)

        # @pipeline(on_init, on_finalize)
        @pipeline(
            on_init="init_job",
            on_finalize="finalize_job",
        )
        def in_decorator_func():
            init_job = self.component_func()  # noqa: F841
            work1 = self.component_func()  # noqa: F841
            work2 = self.component_func()  # noqa: F841
            finalize_job = self.component_func()  # noqa: F841

        pipeline3 = in_decorator_func()
        assert_pipeline_job_init_finalize_job(pipeline3)

    def test_invalid_init_finalize_job(self) -> None:
        # invalid case: job name not exists
        @dsl.pipeline()
        def invalid_init_finalize_job_func():
            self.component_func()

        invalid_pipeline1 = invalid_init_finalize_job_func()
        invalid_pipeline1.settings.on_init = "init_job"
        invalid_pipeline1.settings.on_finalize = "finalize_job"
        validation_result1 = invalid_pipeline1._validate_init_finalize_job()
        assert not validation_result1.passed
        assert validation_result1.error_messages["settings.on_init"] == "On_init job name init_job not exists in jobs."
        assert (
            validation_result1.error_messages["settings.on_finalize"]
            == "On_finalize job name finalize_job not exists in jobs."
        )

        # invalid case: no normal node, on_init/on_finalize job is not isolated
        @dsl.pipeline()
        def init_finalize_with_invalid_connection_func(int_param: int, str_param: str):
            node1 = self.hello_world_func(component_in_number=int_param, component_in_path=str_param)
            node2 = self.hello_world_func(  # noqa: F841
                component_in_number=int_param,
                component_in_path=node1.outputs.component_out_path,
            )

        invalid_pipeline2 = init_finalize_with_invalid_connection_func(int_param=0, str_param="str")
        invalid_pipeline2.settings.on_init = "node2"
        invalid_pipeline2.settings.on_finalize = "node1"
        validation_result2 = invalid_pipeline2._validate_init_finalize_job()
        assert not validation_result2.passed
        assert validation_result2.error_messages["jobs"] == "No other job except for on_init/on_finalize job."
        assert (
            validation_result2.error_messages["settings.on_init"]
            == "On_init job should not have connection to other execution node."
        )
        assert (
            validation_result2.error_messages["settings.on_finalize"]
            == "On_finalize job should not have connection to other execution node."
        )

        # invalid case: call `set_pipeline_settings` out of `pipeline` decorator
        from azure.ai.ml._internal.dsl import set_pipeline_settings
        from azure.ai.ml.exceptions import UserErrorException

        with pytest.raises(UserErrorException) as e:
            set_pipeline_settings(on_init="init_job", on_finalize="finalize_job")
        assert str(e.value) == "Please call `set_pipeline_settings` inside a `pipeline` decorated function."

        # invalid case: set on_init for pipeline component
        @dsl.pipeline
        def subgraph_func():
            node = self.component_func()
            set_pipeline_settings(on_init=node)  # set on_init for subgraph (pipeline component)

        @dsl.pipeline
        def subgraph_with_init_func():
            subgraph_func()
            self.component_func()

        with pytest.raises(UserErrorException) as e:
            subgraph_with_init_func()
        assert str(e.value) == "On_init/on_finalize is not supported for pipeline component."

    def test_init_finalize_job_with_subgraph(self) -> None:
        from azure.ai.ml._internal.dsl import set_pipeline_settings

        # happy path
        @dsl.pipeline()
        def subgraph_func():
            node = self.component_func()
            node.compute = "cpu-cluster"

        @dsl.pipeline()
        def subgraph_init_finalize_job_func():
            init_job = subgraph_func()
            subgraph_work = subgraph_func()  # noqa: F841
            finalize_job = subgraph_func()
            set_pipeline_settings(on_init=init_job, on_finalize=finalize_job)

        valid_pipeline = subgraph_init_finalize_job_func()
        assert valid_pipeline._validate().passed
        assert valid_pipeline.settings.on_init == "init_job"
        assert valid_pipeline.settings.on_finalize == "finalize_job"

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
            add_greeting_column.resources = {"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"}
            count_by_row = count_by_row_func(file_input=iris_data)
            count_by_row.resources = {"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"}
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
                    "resources": {"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"},
                    "entry": {"file": "add_greeting_column.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                    "py_files": ["utils.zip"],
                    "files": ["my_files.txt"],
                    "archives": None,
                    "jars": None,
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
                    "display_name": None,
                    "tags": {},
                    "computeId": None,
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
                    "computeId": None,
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
                    "resources": {"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"},
                    "tags": {},
                    "type": "spark",
                },
            },
            "outputs": {"output": {"job_output_type": "uri_folder", "mode": "Direct"}},
            "settings": {"_source": "DSL"},
        }
