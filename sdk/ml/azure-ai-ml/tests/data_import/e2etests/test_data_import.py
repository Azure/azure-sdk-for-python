import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_data
from azure.ai.ml.entities import PipelineJob, DataImport
from azure.ai.ml.entities._inputs_outputs.external_data import Database


@pytest.mark.timeout(600)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash", "mock_set_headers_with_user_aml_token")
@pytest.mark.data_import_test
class TestDataImport(AzureRecordedTestCase):
    # Please set ML_TENANT_ID in your environment variables when recording this test.
    # It will to help sanitize RequestBody.Studio.endpoint for job creation request.
    def test_data_import(self, client: MLClient) -> None:
        data_import = load_data(
            source="./tests/test_configs/data_import/data_import_e2e.yaml",
        )
        pipeline_job: PipelineJob = client.data.import_data(data_import)

        key = "data_import_" + data_import.name
        assert key in pipeline_job.jobs

        job = pipeline_job.jobs[key]
        assert isinstance(data_import, DataImport)
        assert data_import.name == job.outputs["sink"].name
        assert data_import.path == job.outputs["sink"].path
        assert data_import.path == "azureml://datastores/workspaceblobstore/paths/${{name}}"

        assert isinstance(data_import.source, Database)
        assert isinstance(job.source, Database)
        assert data_import.source.type == job.source.type
        assert data_import.source.query == job.source.query
        assert data_import.source.connection == job.source.connection
