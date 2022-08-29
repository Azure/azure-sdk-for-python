# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import time
from typing import Callable
from pathlib import Path

import pydash
import pytest
from azure.core.exceptions import HttpResponseError

from azure.ai.ml import MLClient, load_component, Output
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import PipelineJob, Data
from tests.internal._utils import PARAMETERS_TO_TEST, set_run_settings


@pytest.fixture
def create_internal_sample_dependent_datasets(client: MLClient):
    for dataset_name in [
        "mnist_model",
        "mnist",
        # adls folders
        "Adls_Tsv",
        "aml_component_datatransfer_folder",
        "reghits",
        "starlite_sample_output",
    ]:
        try:
            client.data.get(name=dataset_name, label="latest")
        except HttpResponseError:
            client.data.create_or_update(
                Data(
                    name=dataset_name,
                    version="1",
                    type=AssetTypes.URI_FOLDER,  # should be MLTable
                    skip_validation=True,
                    path="./tests/test_configs/data",
                )
            )

    for dataset_name in [
        "imdb_reviews_train",
    ]:
        try:
            client.data.get(name=dataset_name, label="latest")
        except HttpResponseError:
            client.data.create_or_update(
                Data(
                    name=dataset_name,
                    version="1",
                    type=AssetTypes.URI_FILE,  # should be MLTable
                    skip_validation=True,
                    path="./tests/test_configs/data/sample1.csv",
                )
            )


@pytest.mark.usefixtures("create_internal_sample_dependent_datasets")
@pytest.mark.usefixtures("enable_internal_components")
@pytest.mark.e2etest
class TestPipelineJob:
    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict,pipeline_runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_anonymous_internal_component_in_pipeline(
        self, client: MLClient, yaml_path, inputs, runsettings_dict, pipeline_runsettings_dict
    ):
        # curated env with name & version
        node_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func():
            node = node_func(**inputs)
            set_run_settings(node, runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        set_run_settings(dsl_pipeline.settings, pipeline_runsettings_dict)
        result = dsl_pipeline._validate()
        assert result._to_dict() == {"result": "Succeeded"}

        created_pipeline: PipelineJob = client.jobs.create_or_update(dsl_pipeline)
        try:
            client.jobs.cancel(created_pipeline.name)
        except HttpResponseError as ex:
            assert "CancelPipelineRunInTerminalStatus" in str(ex)

        node_rest_dict = created_pipeline._to_rest_object().properties.jobs["node"]
        del node_rest_dict["componentId"]  # delete component spec to make it a pure dict
        mismatched_runsettings = {}
        dot_key_map = {"compute": "computeId"}
        for dot_key, expected_value in runsettings_dict.items():
            if dot_key in dot_key_map:
                dot_key = dot_key_map[dot_key]

            # hack: timeout will be transformed into str
            if dot_key == "limits.timeout":
                expected_value = "PT5M"
            value = pydash.get(node_rest_dict, dot_key)
            if value != expected_value:
                mismatched_runsettings[dot_key] = (value, expected_value)
        assert not mismatched_runsettings, "Current value:\n{}\nMismatched fields:\n{}".format(
            json.dumps(node_rest_dict, indent=2), json.dumps(mismatched_runsettings, indent=2)
        )

    @pytest.mark.skip(reason="TODO: can't find newly registered component?")
    @pytest.mark.parametrize(
        "yaml_path,inputs,runsettings_dict,pipeline_runsettings_dict",
        PARAMETERS_TO_TEST,
    )
    def test_created_internal_component_in_pipeline(
        self,
        client: MLClient,
        randstr: Callable[[], str],
        yaml_path,
        inputs,
        runsettings_dict,
        pipeline_runsettings_dict,
    ):
        component_to_register = load_component(yaml_path, params_override=[{"name": randstr()}])
        component_name = randstr()
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
        client.jobs.cancel(pipeline_job.name)
