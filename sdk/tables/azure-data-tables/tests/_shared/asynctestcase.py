
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.data.tables import TableServiceClient

from .testcase import TableTestCase


TEST_TABLE_PREFIX = 'pytableasync'


class AsyncFakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    async def get_token(self, *args):
        return self.token


class AsyncTableTestCase(TableTestCase):

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

    async def _delete_table(self, ts, table):
        if table is None:
            return
        await ts.delete_table(table.name)

    async def _delete_all_tables(self, account_name, key):
        client = TableServiceClient(self.account_url(account_name, "cosmos"), key)
        async for table in client.list_tables():
            await client.delete_table(table.name)

        if self.is_live:
            self.sleep(10)

    async def _tear_down(self):
        async for table in self.ts.list_tables():
            await self.ts.delete_table(table.name)
        if u"cosmos" in self.ts.endpoint:
            self.sleep(10)
        self.test_tables = []
        await self.ts.close()