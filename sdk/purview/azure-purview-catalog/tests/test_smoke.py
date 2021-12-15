# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from testcase import PurviewCatalogTest, PurviewCatalogPowerShellPreparer


class PurviewCatalogSmokeTest(PurviewCatalogTest):

    @PurviewCatalogPowerShellPreparer()
    def test_basic_smoke_test(self, purviewcatalog_endpoint):
        client = self.create_client(endpoint=purviewcatalog_endpoint)
        response = client.types.get_all_type_definitions()

        assert set(response.keys()) == set(['enumDefs', 'structDefs', 'classificationDefs', 'entityDefs', 'relationshipDefs'])
