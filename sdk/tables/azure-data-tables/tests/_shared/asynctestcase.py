# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division
from datetime import datetime
from dateutil.tz import tzutc
import uuid

from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceExistsError
from azure.data.tables import (
    EntityProperty,
    EdmType,
)
from azure.data.tables.aio import TableServiceClient
from azure.identity.aio import DefaultAzureCredential

from devtools_testutils import is_live

from .testcase import TableTestCase, SLEEP_DELAY


TEST_TABLE_PREFIX = "pytableasync"


class AsyncFakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    async def get_token(self, *args, **kwargs):
        return self.token


class AsyncTableTestCase(TableTestCase):
    def get_token_credential(self):
        if is_live():
            return DefaultAzureCredential()
        return self.generate_fake_token()

    def generate_fake_token(self):
        return AsyncFakeTokenCredential()

    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        return table_name

    async def _create_table(self, ts, prefix=TEST_TABLE_PREFIX, table_list=None):
        table_name = self._get_table_reference(prefix)
        try:
            table = await ts.create_table(table_name)
            if table_list is not None:
                table_list.append(table)
        except ResourceExistsError:
            table = ts.get_table_client(table_name)
        return table

    async def _delete_all_tables(self, account_name, key):
        client = TableServiceClient(self.account_url(account_name, "cosmos"), credential=key)
        async for table in client.list_tables():
            await client.delete_table(table.name)

        if self.is_live:
            self.sleep(10)

    async def _tear_down(self):
        if is_live():
            async for table in self.ts.list_tables():
                await self.ts.delete_table(table.name)
            self.test_tables = []
            await self.ts.close()

    async def _create_query_table(self, entity_count):
        """
        Creates a table with the specified name and adds entities with the
        default set of values. PartitionKey is set to 'MyPartition' and RowKey
        is set to a unique counter value starting at 1 (as a string).
        """
        table_name = self.get_resource_name("querytable")
        table = await self.ts.create_table(table_name)
        self.query_tables.append(table_name)
        client = self.ts.get_table_client(table_name)
        entity = self._create_random_entity_dict()
        for i in range(1, entity_count + 1):
            entity["RowKey"] = entity["RowKey"] + str(i)
            await client.create_entity(entity=entity)
        return client

    async def _insert_two_opposite_entities(self, pk=None, rk=None):
        entity1 = self._create_random_entity_dict()
        resp = await self.table.create_entity(entity1)

        partition, row = self._create_pk_rk(pk, rk)
        properties = {
            "PartitionKey": partition + u"1",
            "RowKey": row + u"1",
            "age": 49,
            "sex": u"female",
            "married": False,
            "deceased": True,
            "optional": None,
            "ratio": 5.2,
            "evenratio": 6.0,
            "large": 39999011,
            "Birthday": datetime(1993, 4, 1, tzinfo=tzutc()),
            "birthday": datetime(1990, 4, 1, tzinfo=tzutc()),
            "binary": b"binary-binary",
            "other": EntityProperty(40, EdmType.INT32),
            "clsid": uuid.UUID("c8da6455-213e-42d9-9b79-3f9149a57833"),
        }
        await self.table.create_entity(properties)
        return entity1, resp

    async def _insert_random_entity(self, pk=None, rk=None):
        entity = self._create_random_entity_dict(pk, rk)
        metadata = await self.table.create_entity(entity=entity)
        return entity, metadata["etag"]

    async def _set_up(self, account_name, credential, url="table"):
        account_url = self.account_url(account_name, url)
        self.ts = TableServiceClient(account_url, credential=credential)
        self.table_name = self.get_resource_name("uttable")
        self.table = self.ts.get_table_client(self.table_name)
        if self.is_live:
            try:
                await self.ts.create_table(table_name=self.table_name)
            except ResourceExistsError:
                pass

        self.query_tables = []
