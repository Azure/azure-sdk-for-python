from typing import Optional

import pytest

from azure.ai.ml import load_component, dsl
from azure.ai.ml._internal.utils import update_mode_for_promoted_outputs_in_pipeline
from azure.ai.ml.entities import PipelineJob


@pytest.mark.usefixtures("enable_internal_components")
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestMigrationUtils:
    def test_update_mode_for_promoted_outputs(self):
        yaml_path = "./tests/test_configs/internal/helloworld_program_on_linux/component_spec.yml"
        hello_program_on_linux = load_component(yaml_path)

        @dsl.pipeline(
            name="linux_hello",
            description="Hello world on Linux",
        )
        def linux_hello(name: str):
            hello_program_on_linux_step = hello_program_on_linux(name=name)  # noqa: F841
            hello_program_on_linux_step.outputs.output.mode = "mount"
            hello_program_on_linux_step1 = hello_program_on_linux(name=name)  # noqa: F841
            hello_program_on_linux_step1.outputs.output.mode = "mount"
            return {"output": hello_program_on_linux_step1.outputs.output}

        @dsl.pipeline(
            name="linux_hello",
            description="Hello world on Linux",
        )
        def sub_pipeline(name: str):
            hello_program_on_linux_step = linux_hello(name=name)  # noqa: F841
            # hello_program_on_linux_step.outputs.output.mode = "mount"
            return {"output": hello_program_on_linux_step.outputs.output}

        @dsl.pipeline(
            name="linux_hello",
            description="Hello world on Linux",
        )
        def parent_pipeline(name: str):
            hello_program_on_linux_step = sub_pipeline(name=name)  # noqa: F841
            print(hello_program_on_linux_step)
            # hello_program_on_linux_step.outputs.output.mode = "mount"

        def assert_output_mode(_pipeline_job: PipelineJob, _expected_mode: Optional[str]):
            node = _pipeline_job.jobs["hello_program_on_linux_step"]
            assert node.outputs["output"].mode == _expected_mode
            node = node.component.jobs["hello_program_on_linux_step"]
            assert node.outputs["output"].mode == _expected_mode

        local_pipeline_job: PipelineJob = parent_pipeline(name="test")
        assert_output_mode(local_pipeline_job, None)
        update_mode_for_promoted_outputs_in_pipeline(local_pipeline_job, "upload")
        assert_output_mode(local_pipeline_job, "upload")

        local_pipeline_job: PipelineJob = parent_pipeline(name="test")
        assert_output_mode(local_pipeline_job, None)
        update_mode_for_promoted_outputs_in_pipeline(local_pipeline_job)
        assert_output_mode(local_pipeline_job, "mount")
