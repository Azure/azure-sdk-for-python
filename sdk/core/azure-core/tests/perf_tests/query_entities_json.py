# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from time import time
from wsgiref.handlers import format_date_time
from urllib.parse import quote

from azure.core.rest import HttpRequest
from azure.core.exceptions import (
    HttpResponseError,
    map_error,
)
from ._test_base import _TableTest


class QueryEntitiesJSONTest(_TableTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        # query params
        self.select = quote("Property2")
        self.filter = quote("Property1 eq 'a'")
        self.url = f"{self.account_endpoint}{self.table_name}"

    async def global_setup(self):
        await super().global_setup()
        # create entity to be queried
        entity = self.get_entity()
        await self.async_table_client.create_entity(entity)

    def run_sync(self):
        current_time = format_date_time(time())
        request = HttpRequest(
            method="GET",
            url=self.url,
            params={"$select": self.select, "$filter": self.filter},
            headers={
                "x-ms-version": self.api_version,
                "DataServiceVersion": self.data_service_version,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-ms-date": current_time,
            },
        )
        response = self.pipeline_client._pipeline.run(
            request,
        ).http_response
        response.json()
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def run_async(self):
        current_time = format_date_time(time())
        request = HttpRequest(
            method="GET",
            url=self.url,
            params={"$select": self.select, "$filter": self.filter},
            headers={
                "x-ms-version": self.api_version,
                "DataServiceVersion": self.data_service_version,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-ms-date": current_time,
            },
        )
        response = (
            await self.async_pipeline_client._pipeline.run(
                request,
            )
        ).http_response
        response.json()
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=self.error_map)
            raise HttpResponseError(response=response)

    async def close(self):
        await self.async_table_client.close()
        await super().close()
