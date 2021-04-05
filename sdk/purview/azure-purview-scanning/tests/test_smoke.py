# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.identity import DefaultAzureCredential
from azure.purview.scanning import AzurePurviewScanningClient
from azure.purview.scanning.rest import *

client = AzurePurviewScanningClient(credential=DefaultAzureCredential(), account_name="llcpurview")

def test_basic_smoke_test():
    request = build_datasources_list_by_account_request()
    response = client.send_request(request)
    response.raise_for_status()
    assert response.status_code == 200
    json_response = response.json()
    assert set(json_response.keys()) == set(['value', 'count'])
    assert len(json_response['value']) == json_response['count']
