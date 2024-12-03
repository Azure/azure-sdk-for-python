from azure.mgmt.automation import AutomationClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import pytest

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestMgmtRunbook(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(AutomationClient)

    def create_automation_account(self, group_name, location, account_name):
        automation_account_creation = self.mgmt_client.automation_account.create_or_update(
            group_name,
            account_name,
            {"location": location, "name": account_name, "properties": {"sku": {"name": "Free"}}},
        )
        return automation_account_creation.name

    def create_runbook(self, group_name, location, account_name, runbook_name):
        runbook_creation = self.mgmt_client.runbook.create_or_update(
            group_name,
            account_name,
            runbook_name,
            {
                "location": location,
                "name": runbook_name,
                "properties": {
                    "publishContentLink": {
                        "uri": "https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.automation/101-automation/scripts/AzureAutomationTutorial.ps1"
                    },
                    "runbookType": "PowerShell",
                },
            },
        )
        return runbook_creation.name

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_get_runbook_content(self, resource_group):
        ACCOUNT_NAME = self.get_resource_name("automationtest07")
        RUNBOOK_NAME = self.get_resource_name("runbooktest07")

        account_name = self.create_automation_account(resource_group.name, AZURE_LOCATION, ACCOUNT_NAME)
        runbook_name = self.create_runbook(resource_group.name, AZURE_LOCATION, account_name, RUNBOOK_NAME)

        result = self.mgmt_client.runbook.get_content(resource_group.name, account_name, runbook_name)
