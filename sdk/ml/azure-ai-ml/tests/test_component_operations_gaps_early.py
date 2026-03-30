import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.entities import PipelineComponent
from azure.ai.ml.exceptions import ValidationException, ComponentException


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestComponentOperationsGapsGenerated(AzureRecordedTestCase):
    def test_resolve_dependencies_for_pipeline_component_jobs_unsupported_job_type_raises(self, client: MLClient) -> None:
        ops = client.components
        pc = PipelineComponent()
        # insert an unsupported job type (int) to trigger ComponentException
        # use internal constructor arg to set jobs without relying on setter
        try:
            pc = PipelineComponent(jobs={"bad_job": 123})
        except (TypeError, ValidationException):
            # fallback if PipelineComponent constructor doesn't accept jobs param or validates job types
            setattr(pc, "_jobs", {"bad_job": 123})

        # simple resolver that just echoes back the input; behavior not reached due to unsupported job type
        def resolver(x, azureml_type=None):
            return x

        with pytest.raises(ComponentException) as excinfo:
            ops._resolve_dependencies_for_pipeline_component_jobs(pc, resolver)
        assert "Non supported job type in Pipeline" in str(excinfo.value)
