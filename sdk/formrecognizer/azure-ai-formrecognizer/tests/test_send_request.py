# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.core.rest import HttpRequest
from azure.ai.formrecognizer import DocumentModelAdministrationClient, FormTrainingClient
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer, get_sync_client

get_dma_client = functools.partial(get_sync_client, DocumentModelAdministrationClient)
get_ft_client = functools.partial(get_sync_client, FormTrainingClient)


class TestSendRequest(FormRecognizerTest):
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_get_resource_details(self, **kwargs):
        client = get_dma_client()
        set_bodiless_matcher()
        resource_details = client.get_resource_details()

        request = HttpRequest(
            method="GET",
            url="info",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info1 = result.json()
        assert received_info1
        assert received_info1["customDocumentModels"]
        assert received_info1["customDocumentModels"]["count"] == resource_details.custom_document_models.count
        assert received_info1["customDocumentModels"]["limit"] == resource_details.custom_document_models.limit

        request = HttpRequest(
            method="GET",
            url="info?api-version=2022-08-31",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info2 = result.json()
        assert received_info2["customDocumentModels"]["count"] == received_info1["customDocumentModels"]["count"]
        assert received_info2["customDocumentModels"]["limit"] == received_info1["customDocumentModels"]["limit"]

        # test with absolute url
        request = HttpRequest(
            method="GET",
            url=f"{client._endpoint}/formrecognizer/info?api-version=2022-08-31",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info3 = result.json()
        assert received_info3["customDocumentModels"]["count"] == received_info1["customDocumentModels"]["count"]
        assert received_info3["customDocumentModels"]["limit"] == received_info1["customDocumentModels"]["limit"]

        # test with v2 API version
        request = HttpRequest(
            method="GET",
            url="v2.1/custom/models?op=summary",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info4 = result.json()
        assert received_info4
        assert received_info4["summary"]["count"] == resource_details.custom_document_models.count
        assert received_info4["summary"]["limit"] == resource_details.custom_document_models.limit

        # test with v2 API version with absolute url
        request = HttpRequest(
            method="GET",
            url=f"{client._endpoint}/formrecognizer/v2.1/custom/models?op=summary",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info5 = result.json()
        assert received_info5["summary"]["count"] == received_info4["summary"]["count"]
        assert received_info5["summary"]["limit"] == received_info4["summary"]["limit"]

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_get_account_properties_v2(self):
        client = get_ft_client(api_version="2.1")
        set_bodiless_matcher()
        account_properties = client.get_account_properties()

        request = HttpRequest(
            method="GET",
            url="custom/models?op=summary",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info1 = result.json()
        assert received_info1
        assert received_info1["summary"]
        assert received_info1["summary"]["count"] == account_properties.custom_model_count
        assert received_info1["summary"]["limit"] == account_properties.custom_model_limit

        # test with absolute url
        request = HttpRequest(
            method="GET",
            url=f"{client._endpoint}/formrecognizer/v2.0/custom/models?op=summary",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info3 = result.json()
        assert received_info3["summary"]["count"] == received_info1["summary"]["count"]
        assert received_info3["summary"]["limit"] == received_info1["summary"]["limit"]

        # relative URLs can't override the API version on 2.x clients
        request = HttpRequest(
            method="GET",
            url="info?api-version=2022-08-31",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info4 = result.json()
        assert received_info4["error"]["code"] == "404"
        assert received_info4["error"]["message"] == "Resource not found"

        # test with v2 API version with absolute url
        request = HttpRequest(
            method="GET",
            url=f"{client._endpoint}/formrecognizer/info?api-version=2022-08-31",
            headers={"Accept": "application/json"},
        )
        result = client.send_request(request)
        received_info5 = result.json()
        assert received_info5
        assert received_info5["customDocumentModels"]["count"] == account_properties.custom_model_count
        assert received_info5["customDocumentModels"]["limit"] == account_properties.custom_model_limit
