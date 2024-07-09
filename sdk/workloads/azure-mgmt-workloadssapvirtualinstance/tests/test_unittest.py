# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.mgmt.workloadssapvirtualinstance import WorkloadsSapVirtualInstanceMgmtClient
from azure.identity import DefaultAzureCredential


def test_unittest_model():
    client = WorkloadsSapVirtualInstanceMgmtClient(DefaultAzureCredential(), "12345")
    body = {"configurationType": "DeploymentWithOSConfig"}
    result1 = client._deserialize("SAPConfiguration", body)
    result2 = client._deserialize("SAPConfiguration", body)
    assert result1.configuration_type == result2.configuration_type
    assert body["configurationType"] == "DeploymentWithOSConfig"
