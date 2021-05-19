# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from testcase import PurviewCatalogTest, PurviewCatalogPowerShellPreparer
from azure.purview.catalog.rest.types import build_get_all_type_definitions_request

class PurviewCatalogSmokeTest(PurviewCatalogTest):

    @PurviewCatalogPowerShellPreparer()
    def test_basic_smoke_test(self, purviewcatalog_endpoint):
        client = self.create_client(endpoint=purviewcatalog_endpoint)
        request = build_get_all_type_definitions_request()
        response = client.send_request(request)
        response.raise_for_status()
        assert response.status_code == 200
        json_response = response.json()

        # assert that the keys we expect are there
        assert set(json_response.keys()) == set(['enumDefs', 'structDefs', 'classificationDefs', 'entityDefs', 'relationshipDefs'])
