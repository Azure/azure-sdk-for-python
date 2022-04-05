# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from testcase import PurviewCatalogTest, PurviewCatalogPowerShellPreparer
from urllib.parse import urlparse
from azure.purview.catalog.operations._operations import build_entity_delete_by_guids_request, build_entity_list_by_guids_request


class PurviewCatalogSmokeTest(PurviewCatalogTest):

    @PurviewCatalogPowerShellPreparer()
    def test_basic_smoke_test(self, purviewcatalog_endpoint):
        client = self.create_client(endpoint=purviewcatalog_endpoint)
        response = client.types.get_all_type_definitions()

        assert set(response.keys()) == set(['enumDefs', 'structDefs', 'classificationDefs', 'entityDefs', 'relationshipDefs'])

    def test_delete_by_guids(self):
        request = build_entity_delete_by_guids_request(guids=["foo", "bar"])
        assert urlparse(request.url).query == "guid=foo&guid=bar"

    def test_list_by_guids(self):
        request = build_entity_list_by_guids_request(guids=["foo", "bar"])
        assert "guid=foo&guid=bar" in urlparse(request.url).query
