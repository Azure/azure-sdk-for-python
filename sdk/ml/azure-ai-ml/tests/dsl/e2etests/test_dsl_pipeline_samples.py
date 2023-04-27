"""
This file covers all sample pipeline in https://github.com/Azure/azureml-previews/tree/main/previews/pipelines/samples
in dsl.pipeline.
The samples are copied to test_configs/dsl_pipeline_samples
"""
import json
import sys
from pathlib import Path

import pydash
import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel

from azure.ai.ml import MLClient, load_job
from azure.ai.ml.entities import Component as ComponentEntity
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.operations._run_history_constants import JobStatus

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_root_dir / "test_configs"))
samples_dir = tests_root_dir / "test_configs/dsl_pipeline/"


def assert_job_completed(pipeline, client: MLClient):
    job = client.jobs.create_or_update(pipeline)
    client.jobs.stream(job.name)
    assert client.jobs.get(job.name).status == JobStatus.COMPLETED


def assert_dsl_curated(pipeline: PipelineJob, job_yaml, omit_fields):
    dsl_pipeline_job_dict = pipeline._to_rest_object().as_dict()
    pipeline_job_dict = load_job(source=job_yaml)._to_rest_object().as_dict()

    dsl_pipeline_job_dict = pydash.omit(dsl_pipeline_job_dict, omit_fields)
    pipeline_job_dict = pydash.omit(pipeline_job_dict, omit_fields)
    print(json.dumps(dsl_pipeline_job_dict, indent=2))
    print(json.dumps(pipeline_job_dict, indent=2))
    assert dsl_pipeline_job_dict == pipeline_job_dict


@pytest.mark.usefixtures(
    "enable_environment_id_arm_expansion",
    "enable_pipeline_private_preview_features",
    "mock_code_hash",
    "mock_component_hash",
    "mock_set_headers_with_user_aml_token",
    "recorded_test",
    "mock_asset_name",
    "mock_anon_component_version",
)
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestDSLPipelineSamples(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_e2e_local_components(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.e2e_local_components.pipeline import (
            generate_dsl_pipeline as e2e_local_components,
        )

        pipeline = e2e_local_components()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_e2e_registered_components(
        self,
        client: MLClient,
        pipeline_samples_e2e_registered_train_components: ComponentEntity,
        pipeline_samples_e2e_registered_score_components: ComponentEntity,
        pipeline_samples_e2e_registered_eval_components: ComponentEntity,
    ) -> None:
        from test_configs.dsl_pipeline.e2e_registered_components.pipeline import (
            generate_dsl_pipeline as e2e_registered_components,
        )

        pipeline = e2e_registered_components(
            client=client,
            pipeline_samples_e2e_registered_train_components=pipeline_samples_e2e_registered_train_components,
            pipeline_samples_e2e_registered_score_components=pipeline_samples_e2e_registered_score_components,
            pipeline_samples_e2e_registered_eval_components=pipeline_samples_e2e_registered_eval_components,
        )
        assert_job_cancel(pipeline, client)
        # move unit test here due to permission problem
        job_yaml = str(samples_dir / "e2e_registered_components/pipeline.yml")
        omit_fields = [
            "properties.experiment_name",
            "name",
            "properties.jobs.train_job.componentId",
            "properties.jobs.score_job.componentId",
            "properties.jobs.evaluate_job.componentId",
            "properties.jobs.train_job.resources",  # job yaml won't have resources but we will pass them
            "properties.jobs.score_job.resources",
            "properties.jobs.evaluate_job.resources",
            "properties.inputs.pipeline_job_training_input.uri",
            "properties.inputs.pipeline_job_test_input.uri",
            "properties.properties",
            "properties.compute_id",
            "properties.settings",
        ]
        assert_dsl_curated(pipeline, job_yaml, omit_fields)

    @pytest.mark.e2etest
    def test_basic_component(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.basic_component.pipeline import generate_dsl_pipeline as basic_component

        pipeline = basic_component()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_component_with_input_output(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.component_with_input_output.pipeline import (
            generate_dsl_pipeline as component_with_input_output,
        )

        pipeline = component_with_input_output()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_basic_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.basic_pipeline.pipeline import generate_dsl_pipeline as basic_pipeline

        pipeline = basic_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_pipeline_with_data(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pipline_with_data.pipeline import generate_dsl_pipeline as pipline_with_data

        pipeline = pipline_with_data()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_local_data_input(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.local_data_input.pipeline import generate_dsl_pipeline as local_data_input

        pipeline = local_data_input()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_datastore_datapath_uri_folder(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.datastore_datapath_uri_folder.pipeline import (
            generate_dsl_pipeline as datastore_datapath_uri_folder,
        )

        pipeline = datastore_datapath_uri_folder()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_datastore_datapath_uri_file(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.datastore_datapath_uri_file.pipeline import (
            generate_dsl_pipeline as datastore_datapath_uri_file,
        )

        pipeline = datastore_datapath_uri_file()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_dataset_input(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.dataset_input.pipeline import generate_dsl_pipeline as dataset_input

        pipeline = dataset_input(client)
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_web_url_input(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.web_url_input.pipeline import generate_dsl_pipeline as web_url_input

        pipeline = web_url_input()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_env_public_docker_image(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.env_public_docker_image.pipeline import (
            generate_dsl_pipeline as env_public_docker_image,
        )

        pipeline = env_public_docker_image()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_env_registered(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.env_registered.pipeline import generate_dsl_pipeline as env_registered

        pipeline = env_registered()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_env_conda_file(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.env_conda_file.pipeline import generate_dsl_pipeline as env_conda_file

        pipeline = env_conda_file()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_tf_hello_world(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.tf_hello_world.pipeline import generate_dsl_pipeline as tf_hello_world

        pipeline = tf_hello_world()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_mpi_hello_world(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.mpi_hello_world.pipeline import generate_dsl_pipeline as mpi_hello_world

        pipeline = mpi_hello_world()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_pytorch_hello_world(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pytorch_hello_world.pipeline import generate_dsl_pipeline as pytorch_hello_world

        pipeline = pytorch_hello_world()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_nyc_taxi_data_regression(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.nyc_taxi_data_regression.pipeline import (
            generate_dsl_pipeline as nyc_taxi_data_regression,
        )

        pipeline = nyc_taxi_data_regression()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_tf_mnist(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.tf_mnist.pipeline import generate_dsl_pipeline as tf_mnist

        pipeline = tf_mnist()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_e2e_inline_components(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.e2e_inline_components.pipeline import (
            generate_dsl_pipeline as e2e_inline_components,
        )

        pipeline = e2e_inline_components()
        assert_job_cancel(pipeline, client)

    @pytest.mark.usefixtures("mock_asset_name")
    @pytest.mark.e2etest
    def test_command_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.command_job_in_pipeline.pipeline import (
            generate_dsl_pipeline as command_job_in_pipeline,
        )

        pipeline = command_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_multi_parallel_components_with_file_input_pipeline_output(
        self,
        client: MLClient,
    ) -> None:
        from test_configs.dsl_pipeline.parallel_component_with_file_input.pipeline import (
            generate_dsl_pipeline as pipeline_with_parallel_components,
        )

        pipeline = pipeline_with_parallel_components()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_parallel_components_with_tabular_input_pipeline_output(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.parallel_component_with_tabular_input.pipeline import (
            generate_dsl_pipeline as pipeline_with_parallel_components,
        )

        pipeline = pipeline_with_parallel_components()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_parallel_components(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.parallel_component.pipeline import (
            generate_dsl_pipeline as pipeline_with_parallel_components,
        )

        pipeline = pipeline_with_parallel_components()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_automl_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.automl_job_in_pipeline.pipeline import (
            generate_dsl_pipeline as automl_job_in_pipeline,
        )

        pipeline = automl_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_pipeline_with_pipeline_component(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pipeline_with_pipeline_component.pipeline import (
            generate_dsl_pipeline as pipeline_with_pipeline_component,
        )

        pipeline = pipeline_with_pipeline_component()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_pipeline_with_data_as_inputs_for_pipeline_component(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.pipeline_with_pipeline_component.pipeline_with_data_as_input import (
            generate_dsl_pipeline as pipeline_with_pipeline_component,
        )

        pipeline = pipeline_with_pipeline_component(client)
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_spark_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.spark_job_in_pipeline.pipeline import (
            generate_dsl_pipeline_from_yaml as spark_job_in_pipeline,
        )

        pipeline = spark_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_spark_job_with_builder_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.spark_job_in_pipeline.pipeline import (
            generate_dsl_pipeline_from_builder as spark_job_in_pipeline,
        )

        pipeline = spark_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_spark_job_with_multiple_node_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.spark_job_in_pipeline.kmeans_sample.pipeline import (
            generate_dsl_pipeline_from_yaml as spark_job_in_pipeline,
        )

        pipeline = spark_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_spark_job_with_builder_in_pipeline_without_entry(
        self,
        client: MLClient,
    ) -> None:
        from test_configs.dsl_pipeline.spark_job_in_pipeline.invalid_pipeline import (
            generate_dsl_pipeline_from_builder_without_entry as spark_job_in_pipeline,
        )

        pipeline = spark_job_in_pipeline()
        with pytest.raises(Exception) as ex:
            created_job = client.jobs.create_or_update(pipeline)

        assert (
            '{\n  "result": "Failed",\n  "errors": [\n    {\n      "message": "Missing data for required field.",'
            '\n      "path": "jobs.add_greeting_column.component.entry",\n      "value": null\n    }\n  ]\n}'
            == str(ex.value)
        )

        validation_result = client.jobs.validate(pipeline)
        assert validation_result.passed is False
        assert validation_result.error_messages == {
            "jobs.add_greeting_column.component.entry": "Missing data for required field.",
        }

    @pytest.mark.e2etest
    def test_spark_job_with_builder_in_pipeline_with_dynamic_allocation_disabled(
        self,
        client: MLClient,
    ) -> None:
        from test_configs.dsl_pipeline.spark_job_in_pipeline.invalid_pipeline import (
            generate_dsl_pipeline_from_builder_with_dynamic_allocation_disabled as spark_job_in_pipeline,
        )

        pipeline = spark_job_in_pipeline()
        with pytest.raises(Exception) as ex:
            created_job = client.jobs.create_or_update(pipeline)

        assert (
            '{\n  "result": "Failed",\n  "errors": [\n    {\n      "message": "Should not specify min or max '
            'executors when dynamic allocation is disabled.",\n' in str(ex.value)
        )

        validation_result = client.jobs.validate(pipeline)
        assert validation_result.passed is False
        assert validation_result.error_messages == {
            "jobs.add_greeting_column": "Should not specify min or max executors when dynamic allocation is disabled.",
        }

    @pytest.mark.e2etest
    def test_data_transfer_copy_2urifolder_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.copy_data.pipeline import (
            generate_dsl_pipeline_from_yaml as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client, skip_cancel=True)

    @pytest.mark.e2etest
    def test_data_transfer_copy_2urifolder_job_with_builder_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.copy_data.pipeline import (
            generate_dsl_pipeline_from_builder as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_copy_mixtype_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.copy_data.pipeline import (
            generate_dsl_pipeline_copy_mixtype_from_yaml as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_copy_urifile_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.copy_data.pipeline import (
            generate_dsl_pipeline_copy_urifile_from_yaml as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_copy_urifolder_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.copy_data.pipeline import (
            generate_dsl_pipeline_copy_urifolder_from_yaml as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_import_filesystem_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.import_file_system.pipeline import (
            generate_dsl_pipeline_from_builder as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_import_sql_database_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.import_database.pipeline import (
            generate_dsl_pipeline_from_builder_sql as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_import_snowflake_database_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.import_database.pipeline import (
            generate_dsl_pipeline_from_builder as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_export_sql_database_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.export_database.pipeline import (
            generate_dsl_pipeline_from_builder as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)

    @pytest.mark.e2etest
    def test_data_transfer_multi_job_in_pipeline(self, client: MLClient) -> None:
        from test_configs.dsl_pipeline.data_transfer_job_in_pipeline.pipeline import (
            generate_dsl_pipeline as data_transfer_job_in_pipeline,
        )

        pipeline = data_transfer_job_in_pipeline()
        assert_job_cancel(pipeline, client)
