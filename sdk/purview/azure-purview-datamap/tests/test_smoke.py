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
        response = client.type.list(include_term_template = True)
        # cspell: disable-next-line
        assert set(response.keys()) == set(
            ["enumDefs", "structDefs", "classificationDefs", "entityDefs", "relationshipDefs", "businessMetadataDefs","termTemplateDefs"]
        )

    @PurviewDataMapPowerShellPreparer()
    @recorded_by_proxy
    def test_list_by_guids(self, purviewdatamap_endpoint):
        client = self.create_client(endpoint=purviewdatamap_endpoint)
        request = build_entity_list_by_guids_request(guid=["5d22aee5-7da2-4724-8d19-43de53af8dcf", "b4423a6f-7309-4a71-8d0e-7bd381c2196f"])
        response = client.entity.list_by_guids(guid=["5d22aee5-7da2-4724-8d19-43de53af8dcf", "b4423a6f-7309-4a71-8d0e-7bd381c2196f"])
        assert "guid=5d22aee5-7da2-4724-8d19-43de53af8dcf&guid=b4423a6f-7309-4a71-8d0e-7bd381c2196f" in urlparse(request.url).query
        assert len(response.get("entities"))> 0
