# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import inspect
import pytest
from azure.mgmt.compute import ComputeManagementClient

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestMgmtComputeApiVersion:

    def client(self, api_version):
        return ComputeManagementClient(credential="fake_cred", subscription_id="fake_sub_id", api_version=api_version)

    def test_api_version(self):
        # expect to raise error when method is not supported for the api version
        with pytest.raises(ValueError):
            client = self.client(api_version="1000-01-01")
            client.availability_sets.list_by_subscription()

        # expect to raise error when method signatue is not supported for the api version
        client = self.client(api_version="2016-04-30-preview")
        signature = inspect.signature(client.availability_sets.list_by_subscription)
        result = "expand" in signature.parameters.keys()
        try:
            # old package structure
            assert result == False
        except AssertionError:
            # new package structure
            with pytest.raises(ValueError):
                client.availability_sets.list_by_subscription(expand="fake_expand")
