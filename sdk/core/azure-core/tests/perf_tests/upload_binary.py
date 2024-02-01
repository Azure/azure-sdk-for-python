# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import time
from wsgiref.handlers import format_date_time
from devtools_testutils.perfstress_tests import RandomStream, AsyncRandomStream

from azure.core.rest import HttpRequest
from azure.core.exceptions import (
    HttpResponseError,
    map_error,
)
from azure.core.pipeline.transport import (
    RequestsTransport,
    AsyncioRequestsTransport,
)
from ._test_base import _BlobTest

class UploadBinaryDataTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "uploadtest"
        self.blob_endpoint = f"{self.account_endpoint}{self.container_name}/{blob_name}"
        self.upload_stream = RandomStream(self.args.size)
        self.upload_stream_async = AsyncRandomStream(self.args.size)
        # TODO: investigate size-1 issue for requests transports - https://github.com/Azure/azure-sdk-for-python/issues/33997
        if self.sync_transport == RequestsTransport:
            self.sync_size = self.args.size - 1
        else:
            self.sync_size = self.args.size
        if self.async_transport == AsyncioRequestsTransport:
            self.async_size = self.args.size - 1
        else:
            self.async_size = self.args.size

    # TODO: If seeing "the request verb is invalid" error frequently: https://github.com/Azure/azure-sdk-for-python/issues/33999
    def run_sync(self):
        self.upload_stream.reset()
        current_time = format_date_time(time())
        request = HttpRequest(
            method="PUT",
            url=self.blob_endpoint,
            params={},
            headers={
                'x-ms-date': current_time,
                'x-ms-blob-type': 'BlockBlob',
                'Content-Length': str(self.sync_size),
                'x-ms-version': self.api_version,
                'Content-Type': 'application/octet-stream',
            },
            content=self.upload_stream
        )
        response = self.pipeline_client._pipeline.run(
            request
        ).http_response
        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def run_async(self):
        # TODO: sync upload_stream should work for async as well
        self.upload_stream_async.reset()
        current_time = format_date_time(time())
        request = HttpRequest(
            method="PUT",
            url=self.blob_endpoint,
            params={},
            headers={
                'x-ms-date': current_time,
                'x-ms-blob-type': 'BlockBlob',
                'Content-Length': str(self.async_size),
                'x-ms-version': self.api_version,
                'Content-Type': 'application/octet-stream',
            },
            content=self.upload_stream_async
        )
        pipeline_response = await self.async_pipeline_client._pipeline.run(
            request
        )
        response = pipeline_response.http_response
        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def close(self):
        await super().close()
