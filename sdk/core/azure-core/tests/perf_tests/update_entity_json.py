# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
from time import time
from wsgiref.handlers import format_date_time

from azure.core.rest import HttpRequest
from azure.core.exceptions import (
    HttpResponseError,
    map_error,
)
from ._test_base import _TableTest


class UpdateEntityJSONTest(_TableTest):
    partition_key = str(uuid.uuid4())
    row_key = str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        # base entity
        self.base_entity = self.get_base_entity(
            UpdateEntityJSONTest.partition_key, UpdateEntityJSONTest.row_key, self.args.size
        )
        self.url = f"{self.account_endpoint}{self.table_name}(PartitionKey='{UpdateEntityJSONTest.partition_key}',RowKey='{UpdateEntityJSONTest.row_key}')"

    async def global_setup(self):
        await super().global_setup()
        # create entity to be updated
        await self.async_table_client.create_entity(self.base_entity)

    def run_sync(self):
        current_time = format_date_time(time())
        request = HttpRequest(
            method="PUT",
            url=self.url,
            params={},
            headers={
                "x-ms-version": self.api_version,
                "DataServiceVersion": self.data_service_version,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "If-Match": "*",
                "x-ms-date": current_time,
            },
            json=self.base_entity,
            content=None,
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
                "x-ms-version": self.api_version,
                "DataServiceVersion": self.data_service_version,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "If-Match": "*",
                "x-ms-date": current_time,
            },
            json=self.base_entity,
            content=None,
        )
        response = (
            await self.async_pipeline_client._pipeline.run(
                request,
            )
        ).http_response
        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def close(self):
        await self.async_table_client.close()
        await super().close()
