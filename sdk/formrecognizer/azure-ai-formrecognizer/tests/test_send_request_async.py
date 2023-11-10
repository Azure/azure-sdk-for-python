# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.core.rest import HttpRequest
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient, FormTrainingClient
from preparers import FormRecognizerPreparer, GlobalClientPreparer as _GlobalClientPreparer
from asynctestcase import AsyncFormRecognizerTest

DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)
FormTrainingClientPreparer = functools.partial(_GlobalClientPreparer, FormTrainingClient)


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
            assert received_info1["customDocumentModels"]["count"] == 0
            assert received_info1["customDocumentModels"]["limit"] == 250

            request = HttpRequest(
                method="GET",
                url="info?api-version=2022-08-31",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info2 = result.json()
            assert received_info2["customDocumentModels"]["count"] == received_info1["customDocumentModels"]["count"]
            assert received_info2["customDocumentModels"]["limit"] == received_info1["customDocumentModels"]["limit"]

            # test with absolute url
            request = HttpRequest(
                method="GET",
                url=f"{client._endpoint}/formrecognizer/info?api-version=2022-08-31",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info3 = result.json()
            assert received_info3["customDocumentModels"]["count"] == received_info1["customDocumentModels"]["count"]
            assert received_info3["customDocumentModels"]["limit"] == received_info1["customDocumentModels"]["limit"]

            # test with v2 API version
            request = HttpRequest(
                method="GET",
                url="v2.1/custom/models?op=summary",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info4 = result.json()
            assert received_info4
            assert received_info4["summary"]["count"] == 0
            assert received_info4["summary"]["limit"] == 250
            
            # test with v2 API version with absolute url
            request = HttpRequest(
                method="GET",
                url=f"{client._endpoint}/formrecognizer/v2.1/custom/models?op=summary",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info5 = result.json()
            assert received_info5["summary"]["count"] == received_info4["summary"]["count"]
            assert received_info5["summary"]["limit"] == received_info4["summary"]["limit"]

    @FormRecognizerPreparer()
    @FormTrainingClientPreparer(client_kwargs={"api_version": "2.1"})
    @recorded_by_proxy_async
    async def test_get_account_properties_v2(self, client):
        set_bodiless_matcher()
        async with client:
            request = HttpRequest(
                method="GET",
                url="custom/models?op=summary",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info1 = result.json()
            assert received_info1
            assert received_info1["summary"]
            assert received_info1["summary"]["count"] == 0
            assert received_info1["summary"]["limit"] == 250
            
            # test with absolute url
            request = HttpRequest(
                method="GET",
                url=f"{client._endpoint}/formrecognizer/v2.0/custom/models?op=summary",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info3 = result.json()
            assert received_info3["summary"]["count"] == received_info1["summary"]["count"]
            assert received_info3["summary"]["limit"] == received_info1["summary"]["limit"]
            
            # relative URLs can't override the API version on 2.x clients
            request = HttpRequest(
                method="GET",
                url="info?api-version=2022-08-31",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info4 = result.json()
            assert received_info4["error"]["code"] == "404"
            assert received_info4["error"]["message"] == "Resource not found"
            
            # test with v2 API version with absolute url
            request = HttpRequest(
                method="GET",
                url=f"{client._endpoint}/formrecognizer/info?api-version=2022-08-31",
                headers={"Accept": "application/json"},
            )
            result = await client.send_request(request)
            received_info5 = result.json()
            assert received_info5
            assert received_info5["customDocumentModels"]["count"] == 0
            assert received_info5["customDocumentModels"]["limit"] == 250
