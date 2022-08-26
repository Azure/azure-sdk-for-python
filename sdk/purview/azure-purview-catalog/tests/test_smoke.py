# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from testcase import PurviewCatalogTest, PurviewCatalogPowerShellPreparer
from urllib.parse import urlparse
from azure.purview.catalog.operations._operations import build_entity_delete_by_guids_request, build_entity_list_by_guids_request
from azure.purview.catalog.operations._patch import build_glossary_import_glossary_terms_via_csv_request_initial, build_entity_import_business_metadata_request
from devtools_testutils import recorded_by_proxy

class TestPurviewCatalogSmoke(PurviewCatalogTest):
    @PurviewCatalogPowerShellPreparer()
    @recorded_by_proxy
    def test_basic_smoke_test(self, purviewcatalog_endpoint):
        client = self.create_client(endpoint=purviewcatalog_endpoint)
        response = client.types.get_all_type_definitions()
        assert set(response.keys()) == set(['enumDefs', 'structDefs', 'classificationDefs', 'entityDefs', 'relationshipDefs','businessMetadataDefs'])

    @recorded_by_proxy
    def test_delete_by_guids(self):
        request = build_entity_delete_by_guids_request(guids=["foo", "bar"])
        assert urlparse(request.url).query == "guid=foo&guid=bar"

    @recorded_by_proxy
    def test_list_by_guids(self):
        request = build_entity_list_by_guids_request(guids=["foo", "bar"])
        assert "guid=foo&guid=bar" in urlparse(request.url).query

    @recorded_by_proxy
    def test_glossary_import(self):
        request = build_glossary_import_glossary_terms_via_csv_request_initial(glossary_guid="111",api_version="2022-03-01-preview",files={},include_term_hierarchy=False)
        assert "/glossary/111/terms/import" in urlparse(request.url)

    @recorded_by_proxy
    def test_businessmetadata_import(self):
        request = build_entity_import_business_metadata_request(files={})
        assert "/atlas/v2/entity/businessmetadata/import" in urlparse(request.url)
