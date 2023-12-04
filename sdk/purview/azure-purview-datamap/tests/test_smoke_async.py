# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from testcase import PurviewDataMapTest, PurviewDataMapPowerShellPreparer
from testcase_async import PurviewDataMapTestAsync
from devtools_testutils.aio import recorded_by_proxy_async


class TestPurviewDataMapSmokeAsync(PurviewDataMapTestAsync):
    @PurviewDataMapPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_basic_smoke_test(self, purviewdatamap_endpoint):
        client = self.create_async_client(endpoint=purviewdatamap_endpoint)
        response = await client.type.list(include_term_template = True)

        # cspell: disable-next-line
        assert set(response.keys()) == set(
            ["enumDefs", "structDefs", "classificationDefs", "entityDefs", "relationshipDefs", "businessMetadataDefs","termTemplateDefs"]
        )
