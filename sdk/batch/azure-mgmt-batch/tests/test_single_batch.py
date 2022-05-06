import azure.mgmt.batch
from azure.mgmt.batch import models

from azure_devtools.scenario_tests.recording_processors import GeneralNameReplacer
from devtools_testutils import (
    AzureMgmtRecordedTestCase, recorded_by_proxy,
    ResourceGroupPreparer,
    StorageAccountPreparer
)

AZURE_ARM_ENDPOINT = "https://centraluseuap.management.azure.com"
AZURE_LOCATION = 'eastus'

class TestMgmtBatch(AzureMgmtRecordedTestCase):
    scrubber = GeneralNameReplacer()

    def setup_method(self, method):
        self.mgmt_batch_client = self.create_mgmt_client(
            azure.mgmt.batch.BatchManagementClient,
            base_url=AZURE_ARM_ENDPOINT)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix='batch', location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mgmt_batch_applications(self, resource_group, location, storage_account, storage_account_key):
        # Test Create Account with Auto-Storage
        storage_resource = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}'.format(
            self.get_settings_value("SUBSCRIPTION_ID"),
            resource_group.name,
            storage_account.name
        )
        batch_account = models.BatchAccountCreateParameters(
            location=location,
            auto_storage=models.AutoStorageBaseProperties(storage_account_id=storage_resource)
        )
        account_name = "testbatch"
        account_setup = self.mgmt_batch_client.batch_account.begin_create(
            resource_group.name,
            account_name,
            batch_account).result()
        assert account_setup.name == account_name

        # Test Sync AutoStorage Keys
        response = self.mgmt_batch_client.batch_account.synchronize_auto_storage_keys(
            resource_group.name, account_name)
        assert response is None
