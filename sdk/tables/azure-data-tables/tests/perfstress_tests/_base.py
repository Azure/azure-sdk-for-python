# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import os
import uuid
from datetime import timezone, datetime
import string
import random
from urllib.parse import urljoin
from unittest.mock import Mock

from devtools_testutils.perfstress_tests import PerfStressTest

from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncAzureCredential
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.pipeline.transport import (
    RequestsTransport,
    AioHttpTransport,
    HttpResponse,
    AsyncHttpResponse,
)
from azure.data.tables import EdmType, EntityProperty
from azure.data.tables import TableServiceClient as SyncTableServiceClient
from azure.data.tables.aio import TableServiceClient as AsyncTableServiceClient


_LETTERS = string.ascii_letters

_FULL_EDM_ENTITY = {
    "PartitionKey": "",
    "RowKey": "",
    "StringTypeProperty": "StringTypeProperty",
    "DatetimeTypeProperty": datetime(1970, 10, 4, tzinfo=timezone.utc),
    "GuidTypeProperty": uuid.UUID("c9da6455-213d-42c9-9a79-3e9149a57833"),
    "BinaryTypeProperty": b"BinaryTypeProperty",
    "Int64TypeProperty": EntityProperty(2 ^ 32 + 1, EdmType.INT64),
    "DoubleTypeProperty": 200.23,
    "IntTypeProperty": 5,
}

_STRING_ENTITY = {
    "PartitionKey": "",
    "RowKey": "",
    "StringTypeProperty1": "StringTypeProperty",
    "StringTypeProperty2": "1970-10-04T00:00:00+00:00",
    "StringTypeProperty3": "c9da6455-213d-42c9-9a79-3e9149a57833",
    "StringTypeProperty4": "BinaryTypeProperty",
    "StringTypeProperty5": str(2 ^ 32 + 1),
    "StringTypeProperty6": "200.23",
    "StringTypeProperty7": "5",
}


def get_base_entity(full_edm):
    if full_edm:
        return dict(_FULL_EDM_ENTITY)
    return dict(_STRING_ENTITY)


class _TableTest(PerfStressTest):
    table_name = "".join(random.choice(_LETTERS) for i in range(30))
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        endpoint = self.get_from_env("AZURE_TABLES_ENDPOINT") if self.args.online else "https://127.0.0.1:10002/devstoreaccount1"
        credential = DefaultAzureCredential() if self.args.online else AzureNamedKeyCredential("devstoreaccount1", "fake")
        async_credential = AsyncAzureCredential() if self.args.online else AzureNamedKeyCredential("devstoreaccount1", "fake")
        transport = TestTransport(mock=(not self.args.online), tablename=self.table_name, endpoint=endpoint)
        async_transport = AsyncTestTransport(mock=(not self.args.online), tablename=self.table_name, endpoint=endpoint)
        if self.args.no_client_share:
            self.service_client = SyncTableServiceClient(
                endpoint=endpoint,
                credential=credential,
                transport=transport
            )
            self.async_service_client = AsyncTableServiceClient(
                endpoint=endpoint,
                credential=async_credential,
                transport=async_transport
            )
        else:
            if not _TableTest.service_client:
                _TableTest.service_client = SyncTableServiceClient(
                    endpoint=endpoint,
                    credential=credential,
                    transport=transport
                )
                _TableTest.async_service_client = AsyncTableServiceClient(
                    endpoint=endpoint,
                    credential=async_credential,
                    transport=async_transport
                )
            self.service_client = _TableTest.service_client
            self.async_service_client = _TableTest.async_service_client
        self.table_client = self.service_client.get_table_client(self.table_name)
        self.async_table_client = self.async_service_client.get_table_client(self.table_name)

    async def close(self):
        await self.async_table_client.close()
        await self.async_service_client.close()
        await super().close()

    async def global_setup(self):
        await super().global_setup()
        if self.args.online:
            await self.async_table_client.create_table()

    async def global_cleanup(self):
        if self.args.online:
            await self.async_table_client.delete_table()
        await super().global_cleanup()

    @staticmethod
    def add_arguments(parser):
        super(_TableTest, _TableTest).add_arguments(parser)
        parser.add_argument(
            "--no-client-share",
            action="store_true",
            help="Create one ServiceClient per test instance.  Default is to share a single ServiceClient.",
            default=False,
        )
        parser.add_argument(
            "--full-edm",
            action="store_true",
            help="Whether to use entities that utilize all EDM types for serialization/deserialization, or only strings. Default is False (only strings).",
            default=False,
        )
        parser.add_argument(
            "--online",
            action="store_true",
            help="Whether to run using a live endpoint. The default behaviour is to mock requests/responses.",
            default=False,
        )


entity1 = b'{"odata.etag":"W/\\"datetime\'2024-12-30T20%3A37%3A51.8896642Z\'\\"","PartitionKey":"96d5eb25-443f-42bd-bc8c-79fab90bd70c","RowKey":"1","Timestamp":"2024-12-30T20:37:51.8896642Z","StringTypeProperty1":"StringTypeProperty","StringTypeProperty2":"1970-10-04T00:00:00+00:00","StringTypeProperty3":"c9da6455-213d-42c9-9a79-3e9149a57833","StringTypeProperty4":"BinaryTypeProperty","StringTypeProperty5":"35","StringTypeProperty6":"200.23","StringTypeProperty7":"5"}'
entity2 = b'{"odata.etag":"W/\\"datetime\'2024-12-30T21%3A04%3A59.1599847Z\'\\"","PartitionKey":"b3af0127-8b56-4ebb-9220-fd89bc7a5352","RowKey":"0","Timestamp":"2024-12-30T21:04:59.1599847Z","StringTypeProperty":"StringTypeProperty","DatetimeTypeProperty@odata.type":"Edm.DateTime","DatetimeTypeProperty":"1970-10-04T00:00:00Z","GuidTypeProperty@odata.type":"Edm.Guid","GuidTypeProperty":"c9da6455-213d-42c9-9a79-3e9149a57833","BinaryTypeProperty@odata.type":"Edm.Binary","BinaryTypeProperty":"QmluYXJ5VHlwZVByb3BlcnR5","Int64TypeProperty@odata.type":"Edm.Int64","Int64TypeProperty":"35","DoubleTypeProperty":200.23,"IntTypeProperty":5}'


class TestTransport(RequestsTransport):
    def __init__(self, *, mock: bool, tablename: str, endpoint: str):
        self.mock = mock
        endpoint = endpoint.rstrip("/")
        self.entity_url = endpoint + "/", tablename
        self.tables_url = endpoint + "/Tables"
        self.batch_url = endpoint + "/$batch"
        super().__init__()

    def send(self, request, **kwargs):
        entity_count = kwargs.pop('entity_count', None)
        entity_metadata = kwargs.pop('entity_metadata', None)
        if not self.mock:
            response = super().send(request, **kwargs)
            return response

        if request.url.startswith(self.tables_url):
            if request.method == "POST":
                # create table
                response = HttpResponse(request, Mock())
                response.status_code = 201
                response.reason = 'Created'
                response.body = lambda: b""
                return response
            if request.method == "DELETE":
                # delete table
                response = HttpResponse(request, Mock())
                response.status_code = 204
                response.reason = 'No Content'
                response.body = lambda: b""
                return response

        if request.url.startswith(self.entity_url) and request.method=="PATCH":
            # upsert entity
            response = HttpResponse(request, Mock())
            response.status_code = 204
            response.reason = 'No Content'
            response.body = lambda: b""
            return response
        if request.url.startswith(self.entity_url) and request.method=="GET":
            # list entities
            response = HttpResponse(request, Mock())
            response.status_code = 200
            response.reason = 'OK'
            response.content_type = "application/json;odata=minimalmetadata;streaming=true;charset=utf-8"
            if entity_metadata:
                content = b",".join([entity2 for i in range(entity_count)])
            else:
                content = b",".join([entity1 for i in range(entity_count)])
            response.body = lambda: b'{"odata.metadata":"https://antischpytables.table.core.windows.net/$metadata#cTpCdzGhGwlYNaBVnNtxJHBHGTkTCl","value":[' + content + b']}'
            return response
        if request.url == self.batch_url:
            # batch upsert
            response = HttpResponse(request, Mock())
            response.status_code = 202
            response.reason = 'Accepted'
            response.content_type = "multipart/mixed; boundary=batchresponse_a1b0790f-0b91-451f-b4b1-c2b02a92cb93"
            response.body = lambda: b"--batchresponse_a1b0790f-0b91-451f-b4b1-c2b02a92cb93\r\nContent-Type: multipart/mixed; boundary=changesetresponse_fe280c7b-6c26-4d56-84e2-20ede1faa1ae\r\n\r\n--changesetresponse_fe280c7b-6c26-4d56-84e2-20ede1faa1ae\r\nContent-Type: application/http\r\nContent-Transfer-Encoding: binary\r\n\r\nHTTP/1.1 204 No Content\r\nX-Content-Type-Options: nosniff\r\nCache-Control: no-cache\r\nDataServiceVersion: 1.0;\r\nETag: W/\"datetime\'2024-12-23T02%3A56%3A27.1816179Z\'\"\r\n\r\n\r\n--changesetresponse_fe280c7b-6c26-4d56-84e2-20ede1faa1ae--\r\n--batchresponse_a1b0790f-0b91-451f-b4b1-c2b02a92cb93--\r\n"
            return response
        else:
            raise Exception("No idea!", request.url, request.method)


async def read_body(response):
    return response.body


async def async_range(count):
    for i in range(count):
        yield(i)
        await asyncio.sleep(0.0)


class AsyncTestTransport(AioHttpTransport):
    def __init__(self, *, mock: bool, tablename: str, endpoint: str):
        self.mock = mock
        endpoint = endpoint.rstrip("/")
        self.entity_url = endpoint + "/", tablename
        self.tables_url = endpoint + "/Tables"
        self.batch_url = endpoint + "/$batch"
        super().__init__()

    async def send(self, request, **kwargs):
        entity_count = kwargs.pop('entity_count', None)
        entity_metadata = kwargs.pop('entity_metadata', None)
        if not self.mock:
            response = await super().send(request, **kwargs)
            return response
        if request.url.startswith(self.tables_url):
            if request.method == "POST":
                # create table
                response = AsyncHttpResponse(request, Mock())
                response.status_code = 201
                response.reason = 'Created'
                response.body = lambda: b""
                response.read = lambda: response.body
                return response
            if request.method == "DELETE":
                # delete table
                response = AsyncHttpResponse(request, Mock())
                response.status_code = 204
                response.reason = 'No Content'
                response.body = lambda: b""
                response.read = lambda: response.body
                return response

        if request.url.startswith(self.entity_url) and request.method=="PATCH":
            # upsert entity
            response = AsyncHttpResponse(request, Mock())
            response.status_code = 204
            response.reason = 'No Content'
            response.body = lambda: b""
            response.read = lambda: response.body
            return response
        if request.url.startswith(self.entity_url) and request.method=="GET":
            # list entities
            response = AsyncHttpResponse(request, Mock())
            response.status_code = 200
            response.reason = 'OK'
            response.content_type = "application/json;odata=minimalmetadata;streaming=true;charset=utf-8"
            if entity_metadata:
                content = b",".join([entity2 for i in range(entity_count)])
            else:
                content = b",".join([entity1 for i in range(entity_count)])
            response.body = lambda: b'{"odata.metadata":"https://antischpytables.table.core.windows.net/$metadata#cTpCdzGhGwlYNaBVnNtxJHBHGTkTCl","value":[' + content + b']}'
            response.read = lambda: response.body
            return response
        if request.url == self.batch_url:
            # batch upsert
            response = AsyncHttpResponse(request, Mock())
            response.status_code = 202
            response.reason = 'Accepted'
            response.content_type = "multipart/mixed; boundary=batchresponse_a1b0790f-0b91-451f-b4b1-c2b02a92cb93"
            response.body = lambda: b"--batchresponse_a1b0790f-0b91-451f-b4b1-c2b02a92cb93\r\nContent-Type: multipart/mixed; boundary=changesetresponse_fe280c7b-6c26-4d56-84e2-20ede1faa1ae\r\n\r\n--changesetresponse_fe280c7b-6c26-4d56-84e2-20ede1faa1ae\r\nContent-Type: application/http\r\nContent-Transfer-Encoding: binary\r\n\r\nHTTP/1.1 204 No Content\r\nX-Content-Type-Options: nosniff\r\nCache-Control: no-cache\r\nDataServiceVersion: 1.0;\r\nETag: W/\"datetime\'2024-12-23T02%3A56%3A27.1816179Z\'\"\r\n\r\n\r\n--changesetresponse_fe280c7b-6c26-4d56-84e2-20ede1faa1ae--\r\n--batchresponse_a1b0790f-0b91-451f-b4b1-c2b02a92cb93--\r\n"
            response.read = lambda: read_body(response)
            response.parts = lambda: async_range(0)
            return response
        else:
            raise Exception("No idea!", request.url, request.method)
