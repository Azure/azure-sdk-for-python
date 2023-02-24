import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_data_import
from azure.ai.ml.entities import PipelineJob, DataImport
from azure.ai.ml.entities._inputs_outputs.external_data import Database


@pytest.mark.timeout(600)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
@pytest.mark.data_import_test
class TestDataImport(AzureRecordedTestCase):
    # Please set ML_TENANT_ID in your environment variables when recording this test.
    # It will to help sanitize RequestBody.Studio.endpoint for job creation request.
    def test_data_import(self, client: MLClient) -> None:
        data_import = load_data_import(
            source="./tests/test_configs/data_import/data_import_e2e.yaml",
        )
        pipeline_job: PipelineJob = client.data.import_data(data_import)

        key = "data_import_" + data_import.name
        assert key in pipeline_job.jobs
        assert isinstance(data_import, DataImport)
        assert data_import.name == pipeline_job.jobs[key].outputs["sink"].name
        assert data_import.path == pipeline_job.jobs[key].outputs["sink"].path

        assert isinstance(data_import.source, Database)
        assert isinstance(pipeline_job.jobs[key].source, Database)
        assert data_import.source.type == pipeline_job.jobs[key].source.type
        assert data_import.source.query == pipeline_job.jobs[key].source.query
        assert data_import.source.connection == pipeline_job.jobs[key].source.connection
