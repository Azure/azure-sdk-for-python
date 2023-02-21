import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_data_import


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash",
    "enable_environment_id_arm_expansion",
)
@pytest.mark.timeout(600)
@pytest.mark.e2etest
@pytest.mark.data_import_test
class TestDataImport(AzureRecordedTestCase):
    # Please set ML_TENANT_ID in your environment variables when recording this test.
    # It will to help sanitize RequestBody.Studio.endpoint for job creation request.
    def test_data_import(self, client: MLClient) -> None:
        data_import = load_data_import(
            source="./tests/test_configs/data_import/data_import_database.yaml",
        )
        pipeline_job = client.data.import_data(data_import)
