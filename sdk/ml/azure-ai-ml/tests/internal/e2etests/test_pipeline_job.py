# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import time
from typing import Callable
from pathlib import Path

import pydash
import pytest
from azure.ai.ml import MLClient, load_component, Output
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import PipelineJob
from tests.internal._utils import PARAMETERS_TO_TEST, set_run_settings

from devtools_testutils import AzureRecordedTestCase


@pytest.mark.usefixtures(
    "enable_internal_components",
    "recorded_test",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash"
)
@pytest.mark.e2etest
class TestPipelineJob(AzureRecordedTestCase):
    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_anonymous_internal_component_in_pipeline(self, client: MLClient, yaml_path, inputs, runsettings_dict):
        # curated env with name & version
        node_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func():
            node = node_func(**inputs)
            set_run_settings(node, runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        created_pipeline: PipelineJob = client.jobs.create_or_update(dsl_pipeline)

        node_dict = created_pipeline.jobs["node"]._to_dict()
        for dot_key, value in runsettings_dict.items():
            assert (
                pydash.get(node_dict, dot_key) == value
            ), f"{dot_key} is expected to be {value} but got {pydash.get(node_dict, dot_key)}"
        client.jobs.cancel(created_pipeline.name)

    @pytest.mark.skip(reason="TODO: can't find newly registered component?")
    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_created_internal_component_in_pipeline(
        self, client: MLClient, randstr: Callable[[str], str], yaml_path, inputs, runsettings_dict
    ):
        component_to_register = load_component(yaml_path, params_override=[{"name": randstr("name")}])
        component_name = randstr("component_name")
        component_resource = client.components.create_or_update(component_to_register)
        # hack to wait till the component is registered
        time.sleep(60)
        created_component = client.components.get(component_name, component_resource.version)

        @pipeline()
        def pipeline_func():
            node = created_component(**inputs)
            node.runsettings.configure(**runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        created_pipeline: PipelineJob = client.jobs.create_or_update(dsl_pipeline)
        client.jobs.cancel(created_pipeline.name)

    def test_pipeline_with_setting_node_output(self, client: MLClient) -> None:
        component_dir = Path(__file__).parent.parent.parent / "test_configs" / "internal" / "command-component"
        tsv_func = load_component(component_dir / "command-linux/one-line-tsv/component.yaml")
        copy_func = load_component(component_dir / "command-linux/copy/component.yaml")
        ls_func = load_component(component_dir / "command-linux/ls/ls.yaml")

        @pipeline()
        def pipeline_with_command_components(tsv_file, content):
            """Pipeline with command components"""
            write_tsv = tsv_func(
                tsv_file=tsv_file,
                content=content,
            )
            copy_file = copy_func(
                input_dir=write_tsv.outputs.output_dir,
                file_names=tsv_file,
            )
            ls_file = ls_func(input_dir=copy_file.outputs.output_dir)

            write_tsv.compute = "cpu-cluster"
            copy_file.compute = "cpu-cluster"
            ls_file.compute = "cpu-cluster"

            ls_file.environment_variables = {"verbose": "DEBUG"}

            copy_file.outputs.output_dir = Output(
                path="azureml://datastores/workspaceblobstore/paths/azureml/copy_file/outputs/output_dir"
            )

        pipeline_job = pipeline_with_command_components(tsv_file="out.tsv", content="1\t2\t3\t4")

        pipeline_job = client.jobs.create_or_update(pipeline_job, experiment_name="v15_v2_interop")
