# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from testcase import DataMapTest, DataMapPowerShellPreparer
from urllib.parse import urlparse
from devtools_testutils import recorded_by_proxy


class TestDataMapSmoke(DataMapTest):
    @DataMapPowerShellPreparer()
    @recorded_by_proxy
    def test_basic_smoke_test(self, purviewdatamap_endpoint):
        client = self.create_client(endpoint=purviewdatamap_endpoint)
        assert client is not None
        response = client.type_definition.get()
        # cspell: disable-next-line
        assert set(response.keys()) == set(
            [
                "enumDefs",
                "structDefs",
                "classificationDefs",
                "entityDefs",
                "relationshipDefs",
                "businessMetadataDefs",
                "termTemplateDefs",
            ]
        )
