# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import time
from wsgiref.handlers import format_date_time
from devtools_testutils.perfstress_tests import get_random_bytes, WriteStream

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.storage.blob._generated.operations._block_blob_operations import (
    build_upload_request
)
from ._test_base import _ServiceTest


class PipelineDownloadTest(_ServiceTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "downloadtest"
        self.blob_endpoint = f"{self.account_endpoint}{self.container_name}/{blob_name}"
        self.error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        current_time = format_date_time(time())
        request = build_upload_request(
            url=self.blob_endpoint,
            content=data,
            content_length=self.args.size,
            content_type='application/octet-stream',
            headers={
                'x-ms-version': '2023-11-03',
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

    def run_sync(self):
        current_time = format_date_time(time())
        response = self.pipeline_client._pipeline.run(
            HttpRequest(
                'GET',
                self.blob_endpoint,
                params={'comp': 'blocklist', 'blocklisttype': 'committed'},
                headers={
                    'x-ms-version': '2023-11-03',
                    'Accept': 'application/xml',
                    'x-ms-date': current_time,
                }
            )
        ).http_response
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

    async def run_async(self):
        raise NotImplementedError()

    async def close(self):
        await self.async_blob_client.close()
        await super().close()
