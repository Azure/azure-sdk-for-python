# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.core.rest import HttpRequest
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
from preparers import FormRecognizerPreparer, GlobalClientPreparer as _GlobalClientPreparer
from asynctestcase import AsyncFormRecognizerTest

DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)


class TestSendRequestAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_get_resource_details(self, client, **kwargs):
        set_bodiless_matcher()
        async with client:
            request = HttpRequest(
                method="GET",
                url="info",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info1 = result.json()
            assert received_info1
            assert received_info1["customDocumentModels"]
            assert received_info1["customDocumentModels"]["count"]
            assert received_info1["customDocumentModels"]["limit"]

            request = HttpRequest(
                method="GET",
                url="info?api-version=2022-08-31",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info2 = result.json()
            assert received_info2["customDocumentModels"]["count"] == received_info1["customDocumentModels"]["count"]
            assert received_info2["customDocumentModels"]["limit"] == received_info1["customDocumentModels"]["limit"]
