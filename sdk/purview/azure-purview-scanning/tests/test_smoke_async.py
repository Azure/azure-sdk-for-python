# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.identity.aio import DefaultAzureCredential
from azure.purview.scanning.aio import AzurePurviewScanningClient
from azure.purview.scanning.rest import *

client = AzurePurviewScanningClient(credential=DefaultAzureCredential(), account_name="llcpurview")

@pytest.mark.asyncio
async def test_basic_smoke_test():
    request = build_datasources_list_by_account_request()
    async with DefaultAzureCredential() as credential:
        async with AzurePurviewScanningClient(credential=credential, account_name="llcpurview") as client:
            response = await client.send_request(request)
            response.raise_for_status()
            assert response.status_code == 200
            await response.load_body()
            json_response = response.json()
            assert set(json_response.keys()) == set(['value', 'count'])
            assert len(json_response['value']) == json_response['count']
