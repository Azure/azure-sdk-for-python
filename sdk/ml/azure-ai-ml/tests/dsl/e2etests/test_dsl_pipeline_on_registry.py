import pytest
from pathlib import Path
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel

from azure.ai.ml import MLClient, load_component, Input, load_model
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.constants import AssetTypes
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from .._util import _DSL_TIMEOUT_SECOND

from devtools_testutils import AzureRecordedTestCase


@pytest.mark.usefixtures("enable_pipeline_private_preview_features", "recorded_test")
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestDSLPipelineOnRegistry(AzureRecordedTestCase):
    @pytest.mark.skip(reason="not able to re-record")
    def test_pipeline_job_create_with_registered_component_on_registry(
        self,
        registry_client: MLClient,
    ) -> None:
        local_component = load_component("./tests/test_configs/components/basic_component_code_local_path.yml")
        try:
            created_component = registry_client.components.get(local_component.name, version=local_component.version)
        except HttpResponseError:
            created_component = registry_client.components.create_or_update(local_component)

        @pipeline()
        def sample_pipeline():
            node = created_component()
            node.compute = "cpu-cluster"

        pipeline_job = sample_pipeline()
        assert registry_client.jobs.validate(pipeline_job).passed
        # TODO: add test for pipeline job create with registered component on registry after support is ready on canary

    @pytest.mark.skip(reason="request body still exits when re-record and will raise error "
                             "'Unable to find a record for the request' in playback mode")
    def test_pipeline_with_local_component_and_registry_model_as_input(self, registry_client: MLClient, client: MLClient):
        # get dataset
        test_data = Input(
            type=AssetTypes.URI_FILE,
            path="./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/data/sample1.csv"
        )

        # load_component
        score_func = load_component("./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/score.yml")

        pipeline_score_model = Input(
            type='mlflow_model',
            path='azureml://registries/testFeed/models/iris_model/versions/1'
        )

        @pipeline()
        def score_pipeline_with_registry_model(model_input, test_data):
            score = score_func(model_input=model_input, test_data=test_data)
            score_duplicate = score_func(model_input=pipeline_score_model, test_data=test_data)

        pipeline_job = score_pipeline_with_registry_model(
            model_input=pipeline_score_model,
            test_data=test_data
        )
        pipeline_job.settings.default_compute = "cpu-cluster"
        assert_job_cancel(pipeline_job, client)

    @pytest.mark.skip(reason="request body still exits when re-record and will raise error "
                             "'Unable to find a record for the request' in playback mode")
    def test_pipeline_with_local_component_and_registry_model_as_input_with_model_input(
            self,
            registry_client: MLClient,
            client: MLClient):
        # get dataset
        test_data = Input(
            type=AssetTypes.URI_FILE,
            path="./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/data/sample1.csv"
        )

        # load_component
        score_func = load_component("./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/score.yml")

        model_path = Path("./tests/test_configs/model/model_iris.yml")
        model_entity = load_model(model_path)
        try:
            pipeline_score_model = registry_client.models.get(name=model_entity.name, version=model_entity.version)
        except ResourceNotFoundError:
            model_entity = registry_client.models.create_or_update(model_entity)
            pipeline_score_model = registry_client.models.get(name=model_entity.name, version=model_entity.version)

        @pipeline()
        def score_pipeline_with_registry_model(model_input, test_data):
            score = score_func(model_input=model_input, test_data=test_data)
            score_duplicate = score_func(model_input=pipeline_score_model, test_data=test_data)

        pipeline_job = score_pipeline_with_registry_model(
            model_input=pipeline_score_model, test_data=test_data
        )
        pipeline_job.settings.default_compute = "cpu-cluster"
        assert_job_cancel(pipeline_job, client)

    @pytest.mark.skip(reason="request body still exits when re-record and will raise error "
                             "'Unable to find a record for the request' in playback mode")
    def test_pipeline_with_registry_component_and_model_as_input(self, registry_client: MLClient, client: MLClient):
        # get dataset
        test_data = Input(
            type=AssetTypes.URI_FILE,
            path="./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/data/sample1.csv"
        )

        # load_component
        score_component_name = "v2_dsl_score_component"
        component_version = "0.0.8"
        score_func = registry_client.components.get(
            name=score_component_name, version=component_version
        )

        pipeline_score_model = Input(
            type='mlflow_model',
            path='azureml://registries/testFeed/models/iris_model/versions/1'
        )

        @pipeline()
        def score_pipeline_with_registry_model(model_input, test_data):
            score = score_func(model_input=model_input, test_data=test_data)
            score_duplicate = score_func(model_input=pipeline_score_model, test_data=test_data)

        pipeline_job = score_pipeline_with_registry_model(
            model_input=pipeline_score_model,
            test_data=test_data
        )
        pipeline_job.settings.default_compute = "cpu-cluster"
        assert_job_cancel(pipeline_job, client)
