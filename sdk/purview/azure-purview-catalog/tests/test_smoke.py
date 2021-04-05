# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.identity import DefaultAzureCredential
from azure.purview.catalog import AzurePurviewCatalogClient
from azure.purview.catalog.rest import *
from azure.identity import DefaultAzureCredential

def test_basic_smoke_test():
    client = AzurePurviewCatalogClient(credential=DefaultAzureCredential(), account_name="llcpurview")
    request = build_typesrest_get_all_type_defs_request()
    response = client.send_request(request)
    response.raise_for_status()
    assert response.status_code == 200
    json_response = response.json()

    # first assert that the keys we expect are there
    assert set(json_response.keys()) == set(['enumDefs', 'structDefs', 'classificationDefs', 'entityDefs', 'relationshipDefs'])
