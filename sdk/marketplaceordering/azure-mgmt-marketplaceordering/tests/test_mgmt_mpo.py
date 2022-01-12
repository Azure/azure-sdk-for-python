# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import azure.mgmt.marketplaceordering

from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy


class TestMgmtMPO(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.marketplaceordering.MarketplaceOrderingAgreements
        )

    @recorded_by_proxy
    def test_basic(self):

        result = self.client.marketplace_agreements.get(
            offer_type="virtualmachine",
            publisher_id="intel-bigdl",
            offer_id="bigdl_vm",
            plan_id="bigdl_vm_0p4"
        )
        assert result.name == "bigdl_vm_0p4"
        assert result.plan == "bigdl_vm_0p4"
        assert result.product == "bigdl_vm"
        assert result.publisher == "intel-bigdl"
