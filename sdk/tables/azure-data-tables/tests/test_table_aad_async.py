# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta

from devtools_testutils import AzureTestCase

from azure.data.tables.aio import (
    TableServiceClient,
)
from azure.identity.aio import DefaultAzureCredential

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async

# ------------------------------------------------------------------------------

class TableTestAsync(AzureTestCase, AsyncTableTestCase):
    @tables_decorator_async
    async def test_create_table_aad(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name = self._get_table_reference()
            await ts.create_table(table_name)

            if table_name not in [t.name async for t in ts.list_tables()]:
                raise AssertionError("Table could not be found")

        finally:
            await ts.delete_table(table_name)

    @tables_decorator_async
    async def test_insert_entity_dictionary(self, tables_storage_account_name):
        # Arrange
        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity = self._create_random_entity_dict()

            # Act
            resp = await self.table.create_entity(entity=entity)

            # Assert
            assert resp is not None
        finally:
            await self._tear_down()