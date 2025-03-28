# coding=utf-8
import pytest
from azure.mgmt.containerorchestratorruntime import ContainerOrchestratorRuntimeMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestContainerOrchestratorRuntimeMgmtServicesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ContainerOrchestratorRuntimeMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_services_get(self, resource_group):
        response = self.client.services.get(
            resource_uri="str",
            service_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_services_create_or_update(self, resource_group):
        response = self.client.services.create_or_update(
            resource_uri="str",
            service_name="str",
            resource={
                "id": "str",
                "name": "str",
                "properties": {"provisioningState": "str", "rpObjectId": "str"},
                "systemData": {
                    "createdAt": "2020-02-20 00:00:00",
                    "createdBy": "str",
                    "createdByType": "str",
                    "lastModifiedAt": "2020-02-20 00:00:00",
                    "lastModifiedBy": "str",
                    "lastModifiedByType": "str",
                },
                "type": "str",
            },
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_services_delete(self, resource_group):
        response = self.client.services.delete(
            resource_uri="str",
            service_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_services_list(self, resource_group):
        response = self.client.services.list(
            resource_uri="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
