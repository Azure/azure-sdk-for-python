"""
This file contains the comparison between dsl and curated job in
https://github.com/Azure/azureml-previews/tree/main/previews/pipelines/samples
The samples are copied to test_configs/dsl_pipeline_samples
"""
import pydash
import sys
from unittest import mock
from pathlib import Path
import pytest
from pytest_mock import MockFixture

from azure.ai.ml import MLClient, load_job
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AssetTypes, InputOutputModes
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException

from .._util import _DSL_TIMEOUT_SECOND
from test_utilities.utils import omit_with_wildcard

context = {BASE_PATH_CONTEXT_KEY: "./"}

tests_root_dir = Path(__file__).parent.parent.parent
samples_dir = tests_root_dir / "test_configs/dsl_pipeline/"
sys.path.insert(0, str(tests_root_dir / "test_configs"))


def assert_dsl_curated(pipeline, job_yaml, omit_fields):
    omit_fields.extend(["properties.jobs.*._source", "properties.settings._source"])
    dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
    pipeline_from_yaml = load_job(path=job_yaml)
    pipeline_job_dict = pipeline_from_yaml._to_rest_object().as_dict()

    dsl_pipeline_job_dict = omit_with_wildcard(dsl_pipeline_job_dict, *omit_fields)
    pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
    assert dsl_pipeline_job_dict == pipeline_job_dict


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestDSLPipelineSamples:
    def test_e2e_local_components(self) -> None:
        from dsl_pipeline.e2e_local_components.pipeline import generate_dsl_pipeline as e2e_local_components

        pipeline = e2e_local_components()
        job_yaml = str(samples_dir / "e2e_local_components/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.jobs.score_job.inputs.test_data.uri",
            "properties.inputs.pipeline_job_training_input.uri",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_basic_component(self) -> None:
        from dsl_pipeline.basic_component.pipeline import generate_dsl_pipeline as basic_component

        pipeline = basic_component()
        job_yaml = str(samples_dir / "basic_component/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_component_with_input_output(self) -> None:
        from dsl_pipeline.component_with_input_output.pipeline import (
            generate_dsl_pipeline as component_with_input_output,
        )

        pipeline = component_with_input_output()
        job_yaml = str(samples_dir / "component_with_input_output/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.inputs.pipeline_sample_input_data.uri",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_basic_pipeline(self) -> None:
        from dsl_pipeline.basic_pipeline.pipeline import generate_dsl_pipeline as basic_pipeline

        pipeline = basic_pipeline()
        job_yaml = str(samples_dir / "basic_pipeline/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_pipeline_with_data(self) -> None:
        from dsl_pipeline.pipline_with_data.pipeline import generate_dsl_pipeline as pipline_with_data

        pipeline = pipline_with_data()
        job_yaml = str(samples_dir / "pipline_with_data/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.inputs.pipeline_sample_input_data.uri",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_local_data_input(self) -> None:
        from dsl_pipeline.local_data_input.pipeline import generate_dsl_pipeline as local_data_input

        pipeline = local_data_input()
        job_yaml = str(samples_dir / "local_data_input/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.inputs.pipeline_sample_input_data.uri",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_datastore_datapath_uri_folder(self) -> None:
        from dsl_pipeline.datastore_datapath_uri_folder.pipeline import (
            generate_dsl_pipeline as datastore_datapath_uri_folder,
        )

        pipeline = datastore_datapath_uri_folder()
        job_yaml = str(samples_dir / "datastore_datapath_uri_folder/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_datastore_datapath_uri_file(self) -> None:
        from dsl_pipeline.datastore_datapath_uri_file.pipeline import (
            generate_dsl_pipeline as datastore_datapath_uri_file,
        )

        pipeline = datastore_datapath_uri_file()
        job_yaml = str(samples_dir / "datastore_datapath_uri_file/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_dataset_input(self, mock_machinelearning_client: MLClient) -> None:
        from dsl_pipeline.dataset_input.pipeline import generate_dsl_pipeline as dataset_input

        def get_dataset(*args, **kwargs):
            return "sampledata1235:2"

        # change internal assets into arm id
        with mock.patch("azure.ai.ml._ml_client.DataOperations.get", side_effect=get_dataset):
            pipeline = dataset_input(mock_machinelearning_client)
        job_yaml = str(samples_dir / "dataset_input/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.jobs.mltable_job.componentId",
            # TODO: find a way to resolve the difference, currently:
            # dsl-pipeline remove the azureml: prefix in get_asset_arm_id
            # yaml remove the azureml: prefix in yaml schema load
            "properties.inputs.pipeline_sample_input_data.uri",
            "properties.jobs.mltable_job.inputs.sample_input_data.uri",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_web_url_input(self) -> None:
        from dsl_pipeline.web_url_input.pipeline import generate_dsl_pipeline as web_url_input

        pipeline = web_url_input()
        job_yaml = str(samples_dir / "web_url_input/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_env_public_docker_image(self) -> None:
        from dsl_pipeline.env_public_docker_image.pipeline import (
            generate_dsl_pipeline as env_public_docker_image,
        )

        pipeline = env_public_docker_image()
        job_yaml = str(samples_dir / "env_public_docker_image/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_env_registered(self) -> None:
        from dsl_pipeline.env_registered.pipeline import generate_dsl_pipeline as env_registered

        pipeline = env_registered()
        job_yaml = str(samples_dir / "env_registered/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_env_conda_file(self) -> None:
        from dsl_pipeline.env_conda_file.pipeline import generate_dsl_pipeline as env_conda_file

        pipeline = env_conda_file()
        job_yaml = str(samples_dir / "env_conda_file/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.hello_python_world_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_tf_hello_world(self) -> None:
        from dsl_pipeline.tf_hello_world.pipeline import generate_dsl_pipeline as tf_hello_world

        pipeline = tf_hello_world()
        job_yaml = str(samples_dir / "tf_hello_world/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.tf_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_mpi_hello_world(self) -> None:
        from dsl_pipeline.mpi_hello_world.pipeline import generate_dsl_pipeline as mpi_hello_world

        pipeline = mpi_hello_world()
        job_yaml = str(samples_dir / "mpi_hello_world/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.tf_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_pytorch_hello_world(self) -> None:
        from dsl_pipeline.pytorch_hello_world.pipeline import generate_dsl_pipeline as pytorch_hello_world

        pipeline = pytorch_hello_world()
        job_yaml = str(samples_dir / "pytorch_hello_world/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.pytorch_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_nyc_taxi_data_regression(self) -> None:
        from dsl_pipeline.nyc_taxi_data_regression.pipeline import (
            generate_dsl_pipeline as nyc_taxi_data_regression,
        )

        pipeline = nyc_taxi_data_regression()
        job_yaml = str(samples_dir / "nyc_taxi_data_regression/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.inputs.pipeline_job_input.uri",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_tf_mnist(self) -> None:
        from dsl_pipeline.tf_mnist.pipeline import generate_dsl_pipeline as tf_mnist

        pipeline = tf_mnist()
        job_yaml = str(samples_dir / "tf_mnist/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.tf_job.componentId",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_e2e_inline_components(self) -> None:
        from dsl_pipeline.e2e_inline_components.pipeline_mldesigner_component import (
            generate_dsl_pipeline as e2e_inline_components,
        )

        pipeline = e2e_inline_components()
        job_yaml = str(samples_dir / "e2e_inline_components/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.inputs.pipeline_job_test_input.uri",
            "properties.inputs.pipeline_job_training_input.uri",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_command_job_in_pipeline(self) -> None:
        from dsl_pipeline.command_job_in_pipeline.pipeline import generate_dsl_pipeline as command_job_in_pipeline

        pipeline = command_job_in_pipeline()
        job_yaml = str(samples_dir / "command_job_in_pipeline/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.jobs.evaluate_job.inputs.scoring_result",
            "properties.jobs.score_job.inputs.model_input",
            "properties.jobs.score_job.inputs.test_data",
            "properties.jobs.train_job.inputs.training_data",
            "properties.jobs.evaluate_job.outputs.eval_output",
            "properties.jobs.score_job.outputs.score_output",
            "properties.jobs.train_job.outputs.model_output",
            "properties.inputs.pipeline_job_test_input.uri",
            "properties.inputs.pipeline_job_training_input.uri",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_multi_parallel_components_with_file_input(self) -> None:
        from dsl_pipeline.parallel_component_with_file_input.pipeline import (
            generate_dsl_pipeline as pipeline_with_parallel_components,
        )

        pipeline = pipeline_with_parallel_components()
        job_yaml = str(samples_dir / "parallel_component_with_file_input/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.inputs.pipeline_job_data_path.uri",
            "properties.jobs.*.componentId",
            "properties.settings.force_rerun",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_parallel_components_with_tabular_input(
        self,
    ) -> None:
        from dsl_pipeline.parallel_component_with_tabular_input.pipeline import (
            generate_dsl_pipeline as pipeline_with_parallel_components,
        )

        pipeline = pipeline_with_parallel_components()
        job_yaml = str(samples_dir / "parallel_component_with_tabular_input/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.inputs.pipeline_job_data_path.uri",
            "properties.inputs.pipeline_score_model.uri",
            "properties.jobs.batch_inference_node1.componentId",
            "properties.jobs.batch_inference_node2.componentId",
            "properties.settings.force_rerun",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_parallel_components(self) -> None:
        from dsl_pipeline.parallel_component.pipeline import (
            generate_dsl_pipeline as pipeline_with_parallel_components,
        )

        pipeline = pipeline_with_parallel_components()
        job_yaml = str(samples_dir / "parallel_component/pipeline.yml")
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.inputs.pipeline_job_data_path.uri",
            "properties.inputs.pipeline_score_model.uri",
            "properties.jobs.*.componentId",
            "properties.settings.force_rerun",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    def test_automl_job_in_pipeline(self) -> None:
        from dsl_pipeline.automl_job_in_pipeline.pipeline import generate_dsl_pipeline as automl_job_in_pipeline

        pipeline = automl_job_in_pipeline()
        job_yaml = str(samples_dir / "automl_job_in_pipeline/pipeline.yml")
        omit_fields = [
            "name",
            "properties.experiment_name",
            "properties.jobs.hello_automl_regression.display_name",
            "properties.jobs.hello_automl_regression.experiment_name",
            "properties.settings",
            # TODO: we are passing default value for settings.force_rerun now, should not pass if user did not specify
            "properties.inputs.automl_train_data.uri",
            "properties.inputs.automl_validate_data.uri",
            "properties.inputs.automl_test_data.uri",
            "properties.jobs.show_output.componentId",
            "properties.jobs.show_output.display_name",
            "properties.display_name",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)
