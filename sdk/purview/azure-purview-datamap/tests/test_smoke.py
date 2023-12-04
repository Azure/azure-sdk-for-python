# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from testcase import PurviewDataMapTest, PurviewDataMapPowerShellPreparer
from urllib.parse import urlparse
from azure.purview.datamap.operations._operations import build_entity_list_by_guids_request
from devtools_testutils import recorded_by_proxy

class TestPurviewDataMapSmoke(PurviewDataMapTest):
    @PurviewDataMapPowerShellPreparer()
    @recorded_by_proxy
    def test_basic_smoke_test(self, purviewdatamap_endpoint):
        client = self.create_client(endpoint=purviewdatamap_endpoint)
        response = client.type.list()
        # cspell: disable-next-line
        assert set(response.keys()) == set(['enumDefs', 'structDefs', 'classificationDefs', 'entityDefs', 'relationshipDefs','businessMetadataDefs'])

    @recorded_by_proxy
    def test_list_by_guids(self):
        request = build_entity_list_by_guids_request(guid=["foo", "bar"])
        assert "guid=foo&guid=bar" in urlparse(request.url).query

