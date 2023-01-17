from functools import partial
from pathlib import Path

import pytest

from azure.ai.ml import dsl, load_component, load_job
from azure.ai.ml.entities import PipelineJob

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

    def test_init_finalize_job_from_yaml(self) -> None:
        pipeline_job = load_job("./tests/test_configs/pipeline_jobs/pipeline_job_init_finalize.yaml")
        assert pipeline_job._validate_init_finalize_job().passed
        assert pipeline_job.settings.on_init == "a"
        assert pipeline_job.settings.on_finalize == "c"
        pipeline_job_dict = pipeline_job._to_rest_object().as_dict()
        assert pipeline_job_dict["properties"]["settings"]["on_init"] == "a"
        assert pipeline_job_dict["properties"]["settings"]["on_finalize"] == "c"

    def test_init_finalize_job_from_sdk(self) -> None:
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

    def test_invalid_init_finalize_job_from_yaml(self) -> None:
        pipeline_job = load_job("./tests/test_configs/pipeline_jobs/pipeline_job_init_finalize_invalid.yaml")
        validation_result = pipeline_job._validate_init_finalize_job()
        assert not validation_result.passed
        assert (
            validation_result.error_messages["settings.on_finalize"]
            == "On_finalize job should not have connection to other execution node."
        )

    def test_invalid_init_finalize_job_from_sdk(self) -> None:
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

    def test_init_finalize_with_group(self) -> None:
        from test_configs.dsl_pipeline.pipeline_component_with_group.pipeline import pipeline_job

        assert pipeline_job._validate().passed
        assert pipeline_job.settings.on_init == "init_job"
        assert pipeline_job.settings.on_finalize == "finalize_job"
