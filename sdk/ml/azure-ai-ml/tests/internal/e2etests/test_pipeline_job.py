# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from pathlib import Path
from typing import Callable

import pydash
import pytest
from azure.ai.ml import Input, MLClient, Output, load_component
from azure.ai.ml._internal.entities.component import InternalComponent
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import Data, PipelineJob
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import assert_job_cancel, sleep_if_live

from .._utils import (
    DATA_VERSION,
    PARAMETERS_TO_TEST,
    TEST_CASE_NAME_ENUMERATE,
    get_expected_runsettings_items,
    set_run_settings,
)

_dependent_datasets = {}

PARAMETERS_TO_TEST_WITH_OUTPUT_OUTPUT_RELATED = [
    ("output_path", "Distributed_output", "1"),
    ("scored_dataset", "Parallel_output", "1"),
    ("SSPath", "Scope_output", "1"),
    ("output_path", "HDInsight_output", "1"),
    ("output1", "Hemera_output", "1"),
    ("destination_data", "DataTransfer_output", "1"),
    ("CosmosPath", "Starlite_output", "1"),
    ("outputfolderEnc", "Ae365expool_output", "1"),
]
PARAMETERS_TO_TEST_WITH_OUTPUT = []
# don't use PARAMETERS_TO_TEST[0] because this component doesn't have output
for ori_tuple, output_tuple in zip(PARAMETERS_TO_TEST[1:], PARAMETERS_TO_TEST_WITH_OUTPUT_OUTPUT_RELATED):
    PARAMETERS_TO_TEST_WITH_OUTPUT.append(ori_tuple + output_tuple)


@pytest.fixture
def create_internal_sample_dependent_datasets(client: MLClient):
    for dataset_name in [
        # folder
        "mltable_mnist_model",
        "mltable_mnist",
        # file
        "mltable_imdb_reviews_train",
        # adls folders
        "mltable_Adls_Tsv",
        "mltable_aml_component_datatransfer_folder",
        "mltable_reghits",
        "mltable_starlite_sample_output",
    ]:
        if dataset_name not in _dependent_datasets:
            try:
                _dependent_datasets[dataset_name] = client.data.get(name=dataset_name, version=DATA_VERSION)
            except HttpResponseError:
                _dependent_datasets[dataset_name] = client.data.create_or_update(
                    Data(
                        name=dataset_name,
                        version=DATA_VERSION,
                        type=AssetTypes.MLTABLE,  # should be MLTable
                        skip_validation=True,
                        path="./tests/test_configs/dataset/mnist-data",
                    )
                )


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash",
    "mock_set_headers_with_user_aml_token",
    "enable_pipeline_private_preview_features",
    "create_internal_sample_dependent_datasets",
    "enable_internal_components",
)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestPipelineJob(AzureRecordedTestCase):
    @classmethod
    def _test_component(cls, node_func, inputs, runsettings_dict, pipeline_runsettings_dict, client: MLClient):
        @pipeline()
        def pipeline_func():
            node = node_func(**inputs)
            set_run_settings(node, runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        set_run_settings(dsl_pipeline.settings, pipeline_runsettings_dict)
        result = dsl_pipeline._validate()
        assert result._to_dict() == {"result": "Succeeded"}

        created_pipeline: PipelineJob = assert_job_cancel(dsl_pipeline, client)

        node_rest_dict = created_pipeline._to_rest_object().properties.jobs["node"]
        del node_rest_dict["componentId"]  # delete component spec to make it a pure dict
        mismatched_runsettings = {}
        for dot_key, expected_value in get_expected_runsettings_items(runsettings_dict, client):
            value = pydash.get(node_rest_dict, dot_key)
            if value != expected_value:
                mismatched_runsettings[dot_key] = (value, expected_value)
        assert not mismatched_runsettings, "Current value:\n{}\nMismatched fields:\n{}".format(
            json.dumps(node_rest_dict, indent=2), json.dumps(mismatched_runsettings, indent=2)
        )

    @pytest.mark.parametrize(
        "test_case",
        PARAMETERS_TO_TEST_WITH_OUTPUT,
    )
    @pytest.mark.disable_mock_code_hash
    def test_register_output_for_anonymous_internal_component(
        self,
        client: MLClient,
        test_case: tuple,
    ):
        (
            yaml_path,
            inputs,
            runsettings_dict,
            pipeline_runsettings_dict,
            output_port_name,
            output_name,
            output_version,
        ) = test_case
        node_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func():
            node = node_func(**inputs)
            node.outputs[output_port_name].type = "uri_file"  # use this, in case that the type is path
            node.outputs[output_port_name].name = output_name
            node.outputs[output_port_name].version = output_version
            set_run_settings(node, runsettings_dict)

        dsl_pipeline: PipelineJob = pipeline_func()
        set_run_settings(dsl_pipeline.settings, pipeline_runsettings_dict)
        dsl_pipeline.settings.default_compute = "cpu-cluster"

        result = dsl_pipeline._validate()
        assert result._to_dict() == {"result": "Succeeded"}

        pipeline_job = assert_job_cancel(dsl_pipeline, client)

        assert pipeline_job.jobs["node"].outputs[output_port_name].name == output_name
        assert pipeline_job.jobs["node"].outputs[output_port_name].version == output_version

    @pytest.mark.parametrize(
        "test_case_i,test_case_name",
        TEST_CASE_NAME_ENUMERATE,
    )
    def test_pipeline_job_with_anonymous_internal_component(
        self,
        client: MLClient,
        test_case_i: int,
        test_case_name: str,
    ):
        yaml_path, inputs, runsettings_dict, pipeline_runsettings_dict = PARAMETERS_TO_TEST[test_case_i]
        # curated env with name & version
        node_func: InternalComponent = load_component(yaml_path)

        self._test_component(node_func, inputs, runsettings_dict, pipeline_runsettings_dict, client)

    @pytest.mark.parametrize(
        "test_case_i,test_case_name",
        TEST_CASE_NAME_ENUMERATE,
    )
    def test_pipeline_job_with_registered_internal_component(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        test_case_i: int,
        test_case_name: str,
    ):
        yaml_path, inputs, runsettings_dict, pipeline_runsettings_dict = PARAMETERS_TO_TEST[test_case_i]
        component_name = randstr("component_name")

        component_to_register = load_component(yaml_path, params_override=[{"name": component_name}])
        component_resource = client.components.create_or_update(component_to_register)
        sleep_if_live(5)
        created_component = client.components.get(component_name, component_resource.version)

        self._test_component(created_component, inputs, runsettings_dict, pipeline_runsettings_dict, client)

    def test_data_as_node_inputs(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ):
        yaml_path = "./tests/test_configs/internal/distribution-component/component_spec.yaml"
        node_func: InternalComponent = load_component(yaml_path)
        inputs = {
            "input_path": _dependent_datasets["mltable_imdb_reviews_train"],
        }

        self._test_component(node_func, inputs, {"compute": "cpu-cluster"}, {}, client)

    def test_data_as_pipeline_inputs(self, client: MLClient, randstr: Callable[[], str]):
        yaml_path = "./tests/test_configs/internal/distribution-component/component_spec.yaml"
        node_func: InternalComponent = load_component(yaml_path)

        @pipeline()
        def pipeline_func(pipeline_input):
            node = node_func(input_path=pipeline_input)
            node.compute = "cpu-cluster"

        dsl_pipeline: PipelineJob = pipeline_func(
            pipeline_input=client.data.get("mltable_imdb_reviews_train", label="latest")
        )

        assert_job_cancel(dsl_pipeline, client)

    # TODO: Enable this when type fixed on master.
    @pytest.mark.skip(reason="marshmallow.exceptions.ValidationError: miss required jobs.node.component")
    @pytest.mark.parametrize(
        "test_case_i,test_case_name",
        TEST_CASE_NAME_ENUMERATE,
    )
    def test_pipeline_component_with_anonymous_internal_component(
        self,
        client: MLClient,
        test_case_i: int,
        test_case_name: str,
    ):
        yaml_path, inputs, runsettings_dict, pipeline_runsettings_dict = PARAMETERS_TO_TEST[test_case_i]
        component_func = load_component(yaml_path)

        @pipeline()
        def sub_pipeline_func():
            node = component_func(**inputs)
            set_run_settings(node, runsettings_dict)
            return node.outputs

        @pipeline()
        def pipeline_func():
            node = sub_pipeline_func()
            return node.outputs

        dsl_pipeline: PipelineJob = pipeline_func()
        set_run_settings(dsl_pipeline.settings, pipeline_runsettings_dict)
        assert_job_cancel(dsl_pipeline, client)

    @pytest.mark.skipif(condition=not is_live(), reason="unknown recording error to further investigate")
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

        assert_job_cancel(pipeline_job, client, experiment_name="v15_v2_interop")

    def test_pipeline_with_setting_node_output_mode(self, client: MLClient):
        # get dataset
        training_data = Input(type=AssetTypes.URI_FILE, path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv")
        test_data = Input(type=AssetTypes.URI_FILE, path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv")

        component_dir = (
            Path(__file__).parent.parent.parent / "test_configs" / "internal" / "get_started_train_score_eval"
        )
        train_component_func = load_component(component_dir / "train.yaml")
        score_component_func = load_component(component_dir / "score.yaml")
        eval_component_func = load_component(component_dir / "eval.yaml")

        @pipeline()
        def training_pipeline_with_components_in_registry(input_data, test_data, learning_rate):
            # we don't link node output with pipeline output, because pipeline output will override node output in
            # backend and backend will set pipeline output mode as mount according to contract
            train = train_component_func(training_data=input_data, max_epochs=5, learning_rate=learning_rate)
            train.outputs.model_output.mode = InputOutputModes.UPLOAD
            score = score_component_func(model_input=train.outputs.model_output, test_data=test_data)
            eval = eval_component_func(scoring_result=score.outputs.score_output)
            eval.outputs.eval_output.mode = InputOutputModes.UPLOAD

        pipeline_job = training_pipeline_with_components_in_registry(
            input_data=training_data, test_data=test_data, learning_rate=0.1
        )
        pipeline_job.settings.default_compute = "cpu-cluster"
        assert_job_cancel(pipeline_job, client, experiment_name="v15_v2_interop")

    def test_internal_component_node_output_type(self, client):
        from azure.ai.ml._utils.utils import try_enable_internal_components

        # force register internal components after partially reload schema files
        try_enable_internal_components(force=True)
        yaml_path = "./tests/test_configs/internal/command-component-single-file-output/component_spec.yaml"
        component_func = load_component(yaml_path)

        @pipeline
        def pipeline_func():
            node = component_func()
            # node level should have correct output type when type not configured
            node.outputs.output.mode = "mount"

        pipeline_job = pipeline_func()
        rest_pipeline_job_dict = pipeline_job._to_rest_object().as_dict()
        assert rest_pipeline_job_dict["properties"]["jobs"]["node"]["outputs"] == {
            "output": {"job_output_type": "uri_file", "mode": "ReadWriteMount"}
        }
        assert_job_cancel(pipeline_job, client)
