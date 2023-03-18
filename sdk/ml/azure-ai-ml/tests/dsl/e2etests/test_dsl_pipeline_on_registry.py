from pathlib import Path

import pytest
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.ml import Input, MLClient, load_component, load_model
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.dsl import pipeline
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel
from .._util import _DSL_TIMEOUT_SECOND


def assert_pipeline_job_cancel(client: MLClient, score_func, pipeline_model_input, pipeline_test_data):
    @pipeline
    def score_pipeline(model_input, test_data):
        score = score_func(model_input=model_input, test_data=test_data)  # noqa: F841
        score_duplicate = score_func(model_input=model_input, test_data=test_data)  # noqa: F841

    pipeline_job = score_pipeline(model_input=pipeline_model_input, test_data=pipeline_test_data)
    pipeline_job.settings.default_compute = "cpu-cluster"
    assert_job_cancel(pipeline_job, client)


@pytest.mark.skipif(condition=not is_live(), reason="registry test, may fail in playback mode")
@pytest.mark.usefixtures("enable_pipeline_private_preview_features", "recorded_test")
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestDSLPipelineOnRegistry(AzureRecordedTestCase):
    test_data = Input(
        type=AssetTypes.URI_FILE,
        path="./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/data/sample1.csv",
    )

    def test_pipeline_job_create_with_registered_component_on_registry(self, pipelines_registry_client: MLClient):
        local_component = load_component("./tests/test_configs/components/basic_component_code_local_path.yml")
        try:
            created_component = pipelines_registry_client.components.get(
                local_component.name, version=local_component.version
            )
        except ResourceNotFoundError:
            created_component = pipelines_registry_client.components.create_or_update(local_component)

        @pipeline
        def sample_pipeline():
            created_component()

        pipeline_job = sample_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"
        assert pipelines_registry_client.jobs.validate(pipeline_job).passed

    # this test will break in playback mode, so include it in live test only
    def test_pipeline_with_local_component_and_registry_model_as_input(self, client: MLClient):
        # load_component
        score_func = load_component("./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/score.yml")

        pipeline_score_model = Input(
            type="custom_model", path="azureml://registries/sdk-test/models/iris_model/versions/1"
        )

        assert_pipeline_job_cancel(client, score_func, pipeline_score_model, self.test_data)

    def test_pipeline_with_local_component_and_registry_model_as_input_with_model_input(
        self, client: MLClient, pipelines_registry_client: MLClient
    ):
        # load_component
        score_func = load_component("./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/score.yml")

        model_path = Path("./tests/test_configs/model/model_iris.yml")
        model_entity = load_model(model_path)
        try:
            pipeline_score_model = pipelines_registry_client.models.get(
                name=model_entity.name, version=model_entity.version
            )
        except ResourceNotFoundError:
            model_entity = pipelines_registry_client.models.create_or_update(model_entity)
            pipeline_score_model = pipelines_registry_client.models.get(
                name=model_entity.name, version=model_entity.version
            )

        assert_pipeline_job_cancel(client, score_func, pipeline_score_model, self.test_data)

    def test_pipeline_with_registry_component_and_model_as_input(
        self, client: MLClient, pipelines_registry_client: MLClient
    ):
        # load_component
        score_component_name, component_version = "score_component", "2"
        score_func = pipelines_registry_client.components.get(name=score_component_name, version=component_version)

        pipeline_score_model = Input(
            type="mlflow_model", path="azureml://registries/sdk-test/models/iris_model/versions/1"
        )

        assert_pipeline_job_cancel(client, score_func, pipeline_score_model, self.test_data)
