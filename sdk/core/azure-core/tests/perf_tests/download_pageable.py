# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import asyncio
import itertools
from time import time
from wsgiref.handlers import format_date_time
from uuid import uuid4

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.core.paging import ItemPaged
from azure.core.async_paging import AsyncItemPaged

from azure.storage.blob.aio import BlobServiceClient
from .custom_iterator import CustomIterator, AsyncCustomIterator
from ._test_base import _ServiceTest


class DownloadPageableTest(_ServiceTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        storage_conn_str = os.environ["AZURE_STORAGE_CONN_STR"]
        self.async_service_client = BlobServiceClient.from_connection_string(storage_conn_str)
        self.container_name = f"downloadpageblobtest{uuid4()}"

        self.async_container_client = self.async_service_client.get_container_client(self.container_name)
        self.blob_endpoint = f"{self.account_endpoint}{self.container_name}"
        self.error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }

    async def global_setup(self):
        await super().global_setup()
        await self.async_container_client.create_container()
        pending = (asyncio.ensure_future(self.async_container_client.upload_blob("listtest" + str(i), data=b"")) for i in range(self.args.count))
        running = list(itertools.islice(pending, 16))
        while True:
            # Wait for some upload to finish before adding a new one
            done, running = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
            try:
                for _ in range(0, len(done)):
                    next_upload = next(pending)
                    running.add(next_upload)
            except StopIteration:
                if running:
                    await asyncio.wait(running, return_when=asyncio.ALL_COMPLETED)
                break
 
    def _get_list_blobs(self, **kwargs):
        list_blobs_params = {'restype': 'container', 'comp': 'list'}
        marker = kwargs.get("marker")
        if marker:
            list_blobs_params['marker'] = marker
        max_results = kwargs.get("maxresults")
        if max_results:
            list_blobs_params['maxresults'] = max_results

        current_time = format_date_time(time())
        pipeline_response = self.pipeline_client._pipeline.run(
            HttpRequest(
                'GET',
                self.blob_endpoint,
                params=list_blobs_params,
                headers={
                    'x-ms-version': '2023-11-03',
                    'Accept': 'application/xml',
                    'x-ms-date': current_time,
                    'Content-Type': 'application/octet-stream'
                }
            ),
            stream=False
        )
        response = pipeline_response.http_response
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)
        return response

    async def _get_list_blobs_async(self, **kwargs):
        list_blobs_params = {'restype': 'container', 'comp': 'list'}
        marker = kwargs.get("marker")
        if marker:
            list_blobs_params['marker'] = marker
        max_results = kwargs.get("maxresults")
        if max_results:
            list_blobs_params['maxresults'] = max_results

        current_time = format_date_time(time())
        pipeline_response = await self.async_pipeline_client._pipeline.run(
            HttpRequest(
                'GET',
                self.blob_endpoint,
                params=list_blobs_params,
                headers={
                    'x-ms-version': '2023-11-03',
                    'Accept': 'application/xml',
                    'x-ms-date': current_time,
                    'Content-Type': 'application/octet-stream'
                }
            ),
            stream=False
        )
        response = pipeline_response.http_response
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)
        return response

    def run_sync(self):
        for _ in ItemPaged(
            self._get_list_blobs,
            max_results=self.args.max_results,
            page_iterator_class=CustomIterator,
        ):

            pass

    async def run_async(self):
        async for _ in AsyncItemPaged(
            self._get_list_blobs_async,
            max_results=self.args.max_results,
            page_iterator_class=AsyncCustomIterator,
        ):
            pass
    
    async def global_cleanup(self):
        await self.async_container_client.delete_container()
        await super().global_cleanup()

    async def close(self):
        await self.async_container_client.close()
        await self.async_service_client.close()
        await super().close()
    
    @staticmethod
    def add_arguments(parser):
        super(DownloadPageableTest, DownloadPageableTest).add_arguments(parser)
        parser.add_argument('--max-results', nargs='?', type=str, help='Max results to return.  Default is None.', default=None)
        parser.add_argument('-c', '--count', nargs='?', type=int, help='Number of blobs to list. Defaults to 100', default=100)


