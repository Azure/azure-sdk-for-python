# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import time
from wsgiref.handlers import format_date_time
from devtools_testutils.perfstress_tests import RandomStream, AsyncRandomStream
from ._async_iterator_random_stream import AsyncIteratorRandomStream

from corehttp.rest import HttpRequest
from corehttp.exceptions import (
    HttpResponseError,
    map_error,
)
from ._test_base import _BlobTest

import logging
import sys

handler = logging.StreamHandler(stream=sys.stdout)
logger = logging.getLogger("corehttp")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class UploadBinaryDataTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "uploadtest"
        self.blob_endpoint = f"{self.account_endpoint}{self.container_name}/{blob_name}"
        self.upload_stream = RandomStream(self.args.size)
        if self.args.transport == "httpx":
            self.upload_stream_async = AsyncIteratorRandomStream(self.args.size)
        else:
            self.upload_stream_async = AsyncRandomStream(self.args.size)

    def run_sync(self):
        self.upload_stream.reset()
        current_time = format_date_time(time())
        request = HttpRequest(
            method="PUT",
            url=self.blob_endpoint,
            params={},
            headers={
                "x-ms-date": current_time,
                "x-ms-blob-type": "BlockBlob",
                "Content-Length": str(self.args.size),
                "x-ms-version": self.api_version,
                "Content-Type": "application/octet-stream",
            },
            content=self.upload_stream,
        )
        # Many policies in Azure SDKs use the backcompatible attribute `query` on HttpRequest. This is not present in corehttp.HttpRequest, so we add it manually to make
        # Azure SDK policies work with corehttp.
        request.query = {}
        response = self.pipeline_client.pipeline.run(request).http_response
        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def run_async(self):
        self.upload_stream_async.reset()
        current_time = format_date_time(time())
        request = HttpRequest(
            method="PUT",
            url=self.blob_endpoint,
            params={},
            headers={
                "x-ms-date": current_time,
                "x-ms-blob-type": "BlockBlob",
                "Content-Length": str(self.args.size),
                "x-ms-version": self.api_version,
                "Content-Type": "application/octet-stream",
            },
            content=self.upload_stream_async,
        )
        # Many policies in Azure SDKs use the backcompatible attribute `query` on HttpRequest. This is not present in corehttp.HttpRequest, so we add it manually to make
        # Azure SDK policies work with corehttp.
        request.query = {}
        pipeline_response = await self.async_pipeline_client.pipeline.run(request)
        response = pipeline_response.http_response
        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def close(self):
        await super().close()
