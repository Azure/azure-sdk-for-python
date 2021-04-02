# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
from azure.identity import DefaultAzureCredential
from azure.purview.scanning import AzurePurviewScanningClient
from azure.purview.scanning.rest import *
from azure.identity import DefaultAzureCredential


client = AzurePurviewScanningClient(credential=DefaultAzureCredential(), account_name="llcpurview")

def test_basic_smoke_test():
    request = build_azurekeyvaults_head_request(azure_key_vault_name="hello")
    response = client.send_request(request)
    assert response.status_code == 404
    assert response.reason == "Not Found"
