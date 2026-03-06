# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resource.databoundaries import DataBoundaryMgmtClient
from azure.mgmt.resource.databoundaries.models import DataBoundaryDefinition, DataBoundaryProperties, DataBoundary, ProvisioningState

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

@pytest.mark.live_test_only
class TestDataBoundaryScenario(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(DataBoundaryMgmtClient)

    @recorded_by_proxy
    def test_get_data_boundary_tenant(self):
        result = self.client.data_boundaries.get_tenant(default="default")
        
        # Based on .NET test: Assert.AreEqual(DataBoundaryRegion.EU, resourceData.Properties.DataBoundary);
        # In this environment/recording, it is 'Global'.
        assert result.properties.data_boundary == DataBoundary.GLOBAL

    @recorded_by_proxy
    def test_get_data_boundary_scoped(self):
        subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
        scope = "/subscriptions/{}".format(subscription_id)
        
        result = self.client.data_boundaries.get_scope(scope=scope, default="default")
        
        assert result.properties.data_boundary == DataBoundary.GLOBAL
        assert result.properties.provisioning_state == ProvisioningState.SUCCEEDED

    @recorded_by_proxy
    def test_get_data_boundary_scoped_collection(self):
        subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
        scope = "/subscriptions/{}".format(subscription_id)
        
        result = self.client.data_boundaries.get_scope(scope=scope, default="default")
        
        assert result.properties.data_boundary == DataBoundary.GLOBAL
        assert result.properties.provisioning_state == ProvisioningState.SUCCEEDED

    @recorded_by_proxy
    def test_put_data_boundary(self):
        data_boundary_definition = DataBoundaryDefinition(
            properties=DataBoundaryProperties(data_boundary=DataBoundary.EU)
        )
        
        with pytest.raises(HttpResponseError) as excinfo:
            self.client.data_boundaries.put(
                default="default",
                data_boundary_definition=data_boundary_definition
            )
        
        assert "does not have authorization" in str(excinfo.value)
