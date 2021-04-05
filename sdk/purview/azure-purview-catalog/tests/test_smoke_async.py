# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.identity.aio import DefaultAzureCredential
from azure.purview.catalog.aio import AzurePurviewCatalogClient
from azure.purview.catalog.rest import *

@pytest.mark.asyncio
async def test_basic_smoke_test():
    request = build_typesrest_get_all_type_defs_request()

    async with DefaultAzureCredential() as credential:
        async with AzurePurviewCatalogClient(credential=credential, account_name="llcpurview") as client:
            response = await client.send_request(request)
            response.raise_for_status()
            assert response.status_code == 200
            await response.load_body()
            json_response = response.json()

            # first assert that the keys we expect are there
            assert set(json_response.keys()) == set(['enumDefs', 'structDefs', 'classificationDefs', 'entityDefs', 'relationshipDefs'])
