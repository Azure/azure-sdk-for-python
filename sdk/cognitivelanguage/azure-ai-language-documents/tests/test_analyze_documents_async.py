# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from urllib.parse import urlparse

import pytest
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.ai.language.documents.aio import AnalyzeDocumentsClient
from testpreparer import AnalyzeDocumentsPreparer


class AnalyzeDocumentsAsyncClientTestBase(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential(AnalyzeDocumentsClient, is_async=True)
        return self.create_client_from_credential(
            AnalyzeDocumentsClient,
            credential=credential,
            endpoint=endpoint,
        )


class TestAnalyzeDocumentsAsync(AnalyzeDocumentsAsyncClientTestBase):
    @AnalyzeDocumentsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_get_job_state(
        self,
        analyzedocuments_endpoint,
        analyzedocuments_source_location,
        analyzedocuments_target_location,
    ):
        client = self.create_client(endpoint=analyzedocuments_endpoint)

        operation_location = {}

        def _raw_response_hook(response):
            operation_location["value"] = response.http_response.headers.get("Operation-Location")

        async with client:
            poller = await client.begin_submit_job(
                body={
                    "displayName": "Document Analysis.",
                    "analysisInput": {
                        "documents": [
                            {
                                "language": "en",
                                "id": "1",
                                "source": {
                                    "location": analyzedocuments_source_location
                                },
                                "target": {
                                    "location": analyzedocuments_target_location
                                },
                            }
                        ]
                    },
                    "tasks": [
                        {
                            "kind": "PiiEntityRecognition",
                            "parameters": {
                                "redactionPolicies": [
                                    {
                                        "policyName": "defaultPolicy",
                                        "policyKind": "EntityMask",
                                        "isDefault": True,
                                    }
                                ]
                            },
                        }
                    ],
                },
                raw_response_hook=_raw_response_hook,
            )

            assert poller is not None
            assert operation_location["value"]

            parsed = urlparse(operation_location["value"])
            job_id = parsed.path.rstrip("/").split("/")[-1]

            response = await client.get_job_state(job_id=job_id)

            assert response is not None
            assert response["jobId"] == job_id
            assert response["status"] is not None

    @AnalyzeDocumentsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_begin_submit_job(
        self,
        analyzedocuments_endpoint,
        analyzedocuments_source_location,
        analyzedocuments_target_location,
    ):
        client = self.create_client(endpoint=analyzedocuments_endpoint)

        async with client:
            poller = await client.begin_submit_job(
                body={
                    "displayName": "Document Analysis.",
                    "analysisInput": {
                        "documents": [
                            {
                                "language": "en",
                                "id": "1",
                                "source": {
                                    "location": analyzedocuments_source_location
                                },
                                "target": {
                                    "location": analyzedocuments_target_location
                                },
                            }
                        ]
                    },
                    "tasks": [
                        {
                            "kind": "PiiEntityRecognition",
                            "parameters": {
                                "redactionPolicies": [
                                    {
                                        "policyName": "defaultPolicy",
                                        "policyKind": "EntityMask",
                                        "isDefault": True,
                                    }
                                ]
                            },
                        }
                    ],
                },
            )

            assert poller is not None
            assert poller.continuation_token()
            assert poller.status()

    @AnalyzeDocumentsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_begin_cancel_job(
        self,
        analyzedocuments_endpoint,
        analyzedocuments_source_location,
        analyzedocuments_target_location,
    ):
        client = self.create_client(endpoint=analyzedocuments_endpoint)

        operation_location = {}

        def _raw_response_hook(response):
            operation_location["value"] = response.http_response.headers.get("Operation-Location")

        async with client:
            submit_poller = await client.begin_submit_job(
                body={
                    "displayName": "Document Analysis.",
                    "analysisInput": {
                        "documents": [
                            {
                                "language": "en",
                                "id": "1",
                                "source": {
                                    "location": analyzedocuments_source_location
                                },
                                "target": {
                                    "location": analyzedocuments_target_location
                                },
                            }
                        ]
                    },
                    "tasks": [
                        {
                            "kind": "PiiEntityRecognition",
                            "parameters": {
                                "redactionPolicies": [
                                    {
                                        "policyName": "defaultPolicy",
                                        "policyKind": "EntityMask",
                                        "isDefault": True,
                                    }
                                ]
                            },
                        }
                    ],
                },
                raw_response_hook=_raw_response_hook,
            )

            assert submit_poller is not None
            assert operation_location["value"]

            parsed = urlparse(operation_location["value"])
            job_id = parsed.path.rstrip("/").split("/")[-1]

            cancel_poller = await client.begin_cancel_job(job_id=job_id)
            assert cancel_poller is not None
            assert cancel_poller.continuation_token()
            await cancel_poller.result()

            response = await client.get_job_state(job_id=job_id)
            assert response is not None
            assert response["jobId"] == job_id
            assert response["status"] in ["cancelled", "cancelling", "notStarted"]
