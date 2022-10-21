import pytest
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD

from azure.ai.ml import MLClient, load_component
from azure.core.exceptions import HttpResponseError

from .._util import _DSL_TIMEOUT_SECOND

from devtools_testutils import AzureRecordedTestCase


@pytest.mark.usefixtures("enable_pipeline_private_preview_features", "recorded_test")
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.skip(reason="not able to re-record")
class TestDSLPipelineOnRegistry(AzureRecordedTestCase):
    def test_pipeline_job_create_with_registered_component_on_registry(
        self,
        registry_client: MLClient,
    ) -> None:
        from azure.ai.ml.dsl import pipeline

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
