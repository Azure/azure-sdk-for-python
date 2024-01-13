# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import time
from wsgiref.handlers import format_date_time
from devtools_testutils.perfstress_tests import get_random_bytes, WriteStream

from azure.core.exceptions import (
    HttpResponseError,
    map_error,
)
from azure.storage.blob._generated.operations._block_blob_operations import (
    build_upload_request
)
from ._test_base import _BlobTest


class UploadBinaryDataTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "uploadtest"
        self.blob_endpoint = f"{self.account_endpoint}{self.container_name}/{blob_name}"
        self.error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }

    async def global_setup(self):
        await super().global_setup()
        self.data = get_random_bytes(self.args.size)

    def run_sync(self):
        current_time = format_date_time(time())
        request = build_upload_request(
            url=self.blob_endpoint,
            content=self.data,
            content_length=self.args.size,
            content_type='application/octet-stream',
            headers={
                'x-ms-version': self.api_version,
                'x-ms-date': current_time,
            },
        )
        response = self.pipeline_client._pipeline.run(
            request,
            stream=False
        ).http_response
        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def run_async(self):
        current_time = format_date_time(time())
        request = build_upload_request(
            url=self.blob_endpoint,
            content=self.data,
            content_length=self.args.size,
            content_type='application/octet-stream',
            headers={
                'x-ms-version': self.api_version,
                'x-ms-date': current_time,
            },
        )
        response = (await self.async_pipeline_client._pipeline.run(
            request,
            stream=False
        )).http_response
        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def close(self):
        await super().close()
