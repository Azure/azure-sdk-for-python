# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) Python Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.cloudhealth import CloudHealthMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestCloudHealthMgmtEntitiesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(CloudHealthMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_entities_get(self, resource_group):
        response = self.client.entities.get(
            resource_group_name=resource_group.name,
            health_model_name="str",
            entity_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_entities_create_or_update(self, resource_group):
        response = self.client.entities.create_or_update(
            resource_group_name=resource_group.name,
            health_model_name="str",
            entity_name="str",
            resource={
                "id": "str",
                "name": "str",
                "properties": {
                    "alerts": {
                        "degraded": {"severity": "str", "actionGroupIds": ["str"], "description": "str"},
                        "unhealthy": {"severity": "str", "actionGroupIds": ["str"], "description": "str"},
                    },
                    "canvasPosition": {"x": 0.0, "y": 0.0},
                    "deletionDate": "2020-02-20 00:00:00",
                    "discoveredBy": "str",
                    "displayName": "str",
                    "healthObjective": 0.0,
                    "healthState": "str",
                    "icon": {"iconName": "str", "customData": "str"},
                    "impact": "str",
                    "kind": "str",
                    "labels": {"str": "str"},
                    "provisioningState": "str",
                    "signals": {
                        "azureLogAnalytics": {
                            "authenticationSetting": "str",
                            "logAnalyticsWorkspaceResourceId": "str",
                            "signalAssignments": [{"signalDefinitions": ["str"]}],
                        },
                        "azureMonitorWorkspace": {
                            "authenticationSetting": "str",
                            "azureMonitorWorkspaceResourceId": "str",
                            "signalAssignments": [{"signalDefinitions": ["str"]}],
                        },
                        "azureResource": {
                            "authenticationSetting": "str",
                            "azureResourceId": "str",
                            "signalAssignments": [{"signalDefinitions": ["str"]}],
                        },
                        "dependencies": {
                            "aggregationType": "str",
                            "degradedThreshold": "str",
                            "unhealthyThreshold": "str",
                        },
                    },
                },
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
    def test_entities_delete(self, resource_group):
        response = self.client.entities.delete(
            resource_group_name=resource_group.name,
            health_model_name="str",
            entity_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_entities_list_by_health_model(self, resource_group):
        response = self.client.entities.list_by_health_model(
            resource_group_name=resource_group.name,
            health_model_name="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
