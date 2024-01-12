# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
from random import randint
from time import time
from wsgiref.handlers import format_date_time

from azure.core.rest import HttpRequest
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.storage.blob._generated.operations._block_blob_operations import (
    build_upload_request
)
from azure.data.tables.aio import TableClient
from ._test_base import _TableTest

import logging
import sys
handler = logging.StreamHandler(stream=sys.stdout)
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

class UpdateEntityJSONTest(_TableTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.table_name = f"updateentitytest{randint(1, 1000)}"
        self.connection_string = self.get_from_env("AZURE_STORAGE_CONN_STR")
        self.async_table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        self.error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }

        # base entity
        partition_key = str(uuid.uuid4())
        row_key = str(uuid.uuid4())
        self.base_entity = self.get_base_entity(partition_key, row_key, self.args.size)
        self.url = f"{self.account_endpoint}{self.table_name}(PartitionKey='{partition_key}',RowKey='{row_key}')"

    async def global_setup(self):
        await super().global_setup()
        await self.async_table_client.create_table()
        # create entity to be updated
        await self.async_table_client.create_entity(self.base_entity)


    def run_sync(self):
        current_time = format_date_time(time())
        request = HttpRequest(
            method="PUT",
            url=self.url,
            params={},
            headers={
                'x-ms-version': self.api_version,
                'DataServiceVersion': self.data_service_version,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'If-Match': '*',
                'x-ms-date': current_time
            },
            json=self.base_entity,
            content=None
        )
        response = self.pipeline_client._pipeline.run(
            request,
        ).http_response
        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def run_async(self):
        current_time = format_date_time(time())
        request = HttpRequest(
            method="PUT",
            url=self.url,
            params={},
            headers={
                'x-ms-version': self.api_version,
                'DataServiceVersion': self.data_service_version,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'If-Match': '*',
                'x-ms-date': current_time
            },
            json=self.base_entity,
            content=None
        )
        response = (await self.async_pipeline_client._pipeline.run(
            request,
        )).http_response
        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def global_cleanup(self):
        await self.async_table_client.delete_table()

    async def close(self):
        await super().close()
