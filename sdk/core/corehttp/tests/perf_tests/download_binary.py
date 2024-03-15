# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import time
from wsgiref.handlers import format_date_time
from devtools_testutils.perfstress_tests import get_random_bytes, WriteStream

from corehttp.exceptions import (
    HttpResponseError,
    map_error,
)
from corehttp.rest import HttpRequest
from azure.storage.blob._generated.operations._block_blob_operations import build_upload_request
from ._test_base import _BlobTest


class DownloadBinaryDataTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "streamdownloadtest"
        self.blob_endpoint = f"{self.account_endpoint}{self.container_name}/{blob_name}"

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        current_time = format_date_time(time())
        request = build_upload_request(
            url=self.blob_endpoint,
            content=data,
            content_length=self.args.size,
            content_type="application/octet-stream",
            headers={
                "x-ms-version": self.api_version,
                "x-ms-date": current_time,
            },
        )
        response = (await self.async_pipeline_client.pipeline.run(request, stream=False)).http_response

        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    def run_sync(self):
        current_time = format_date_time(time())
        request = HttpRequest(
            "GET",
            self.blob_endpoint,
            headers={
                "x-ms-version": self.api_version,
                "Accept": "application/octet-stream",
                "x-ms-date": current_time,
            },
        )
        # Many policies in Azure SDKs use the backcompatible attribute `query` on HttpRequest. This is not present in corehttp.HttpRequest, so we add it manually to make
        # Azure SDK policies work with corehttp.
        request.query = {}
        response = self.pipeline_client.pipeline.run(
            request,
            stream=True,
        ).http_response
        response.read()
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def run_async(self):
        current_time = format_date_time(time())
        request = HttpRequest(
            "GET",
            self.blob_endpoint,
            headers={
                "x-ms-version": self.api_version,
                "Accept": "application/octet-stream",
                "x-ms-date": current_time,
            },
        )
        # Many policies in Azure SDKs use the backcompatible attribute `query` on HttpRequest. This is not present in corehttp.HttpRequest, so we add it manually to make
        # Azure SDK policies work with corehttp.
        request.query = {}
        response = (
            await self.async_pipeline_client.pipeline.run(
                request,
                stream=True,
            )
        ).http_response
        await response.read()
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def close(self):
        await super().close()
