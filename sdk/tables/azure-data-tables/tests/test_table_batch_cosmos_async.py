# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
import os
import sys
import pytest

from devtools_testutils import AzureRecordedTestCase, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError,
)
from azure.data.tables import (
    TableEntity,
    UpdateMode,
    EntityProperty,
    EdmType,
    TableTransactionError,
    RequestTooLargeError,
    TransactionOperation,
    TableSasPermissions,
    generate_table_sas,
    TableErrorCode,
)
from azure.data.tables.aio import TableServiceClient

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import cosmos_decorator_async

#------------------------------------------------------------------------------
TEST_TABLE_PREFIX = 'table'
#------------------------------------------------------------------------------

class TestTableBatchCosmosAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_single_insert(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            batch = [('create', entity)]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            e = await self.table.get_entity(row_key=entity['RowKey'], partition_key=entity['PartitionKey'])
            assert e['test'] ==  entity['test'].value
            assert e['test2'] ==  entity['test2']
            assert e['test3'] ==  entity['test3']
            assert e['test4'] ==  entity['test4'].value

        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_single_update(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            resp = await self.table.create_entity(entity)
            assert resp is not None

            entity['test3'] = 5
            entity['test5'] = datetime.utcnow()

            batch = [('update', entity, {'mode':UpdateMode.MERGE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            result = await self.table.get_entity(row_key=entity['RowKey'], partition_key=entity['PartitionKey'])
            assert result['PartitionKey'] ==  u'001'
            assert result['RowKey'] ==  u'batch_insert'
            assert result['test3'] ==  5
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_update(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_update'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = u'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()
            await self.table.create_entity(entity)

            entity = await self.table.get_entity(u'001', u'batch_update')
            assert 3 ==  entity['test3']
            entity['test2'] = u'value1'

            batch = [('update', entity)]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            result = await self.table.get_entity('001', 'batch_update')
            assert 'value1' ==  result['test2']
            assert entity['PartitionKey'] ==  u'001'
            assert entity['RowKey'] ==  u'batch_update'
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_merge(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_merge'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = u'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()
            await self.table.create_entity(entity)

            resp_entity = await self.table.get_entity(partition_key=u'001', row_key=u'batch_merge')
            assert 3 ==  entity['test3']
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_merge'
            entity['test2'] = u'value1'

            batch = [('update', entity, {'mode': UpdateMode.MERGE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            resp_entity = await self.table.get_entity(partition_key=u'001', row_key=u'batch_merge')
            assert entity['test2'] ==  resp_entity['test2']
            assert 1234567890 ==  resp_entity['test4']
            assert entity['PartitionKey'] ==  resp_entity['PartitionKey']
            assert entity['RowKey'] ==  resp_entity['RowKey']
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_update_if_match(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict()
            resp = await self.table.create_entity(entity=entity)
            etag = resp['etag']

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            batch = [(
                'update',
                sent_entity,
                {'etag': etag, 'match_condition':MatchConditions.IfNotModified, 'mode':UpdateMode.REPLACE}
            )]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            entity = await self.table.get_entity(partition_key=entity['PartitionKey'], row_key=entity['RowKey'])
            self._assert_updated_entity(entity)
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_update_if_doesnt_match(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict()
            resp = await self.table.create_entity(entity)
            assert resp is not None

            # Act
            sent_entity1 = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])

            batch = [(
                'update',
                sent_entity1,
                {'etag': u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"', 'match_condition':MatchConditions.IfNotModified}
            )]

            with pytest.raises(TableTransactionError) as error:
                await self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
            self._assert_default_entity(received_entity)
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_insert_replace(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert_replace'
            entity['test'] = True
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            batch = [('upsert', entity, {'mode': UpdateMode.REPLACE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            entity = await self.table.get_entity('001', 'batch_insert_replace')
            assert entity is not None
            assert 'value' ==  entity['test2']
            assert 1234567890 ==  entity['test4']
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_insert_merge(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert_merge'
            entity['test'] = True
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            batch = [('upsert', entity, {'mode':UpdateMode.MERGE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            entity = await self.table.get_entity('001', 'batch_insert_merge')
            assert entity is not None
            assert 'value' ==  entity['test2']
            assert 1234567890 ==  entity['test4']
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_delete(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_delete'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = u'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()
            await self.table.create_entity(entity)

            entity = await self.table.get_entity(partition_key=u'001', row_key=u'batch_delete')
            assert 3 ==  entity['test3']

            batch = [('delete', entity)]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' not in transaction_result[0]

            with pytest.raises(ResourceNotFoundError):
                entity = await self.table.get_entity(partition_key=entity['PartitionKey'], row_key=entity['RowKey'])
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_inserts(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = 'batch_inserts'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            transaction_count = 0

            batch = []
            for i in range(10):
                entity['RowKey'] = str(i)
                batch.append(('create', entity.copy()))
                transaction_count += 1
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert 'etag' in transaction_result[0]

            entities = self.table.query_entities("PartitionKey eq 'batch_inserts'")

            length = 0
            async for e in entities:
                length += 1

            # Assert
            assert entities is not None
            assert 10 == length
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_all_operations_together(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '003'
            entity['RowKey'] = 'batch_all_operations_together-1'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            await self.table.create_entity(entity)
            entity['RowKey'] = 'batch_all_operations_together-2'
            await self.table.create_entity(entity)
            entity['RowKey'] = 'batch_all_operations_together-3'
            await self.table.create_entity(entity)
            entity['RowKey'] = 'batch_all_operations_together-4'
            await self.table.create_entity(entity)

            transaction_count = 0

            batch = []
            entity['RowKey'] = 'batch_all_operations_together'
            batch.append((TransactionOperation.CREATE, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-1'
            batch.append((TransactionOperation.DELETE, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-2'
            entity['test3'] = 10
            batch.append((TransactionOperation.UPDATE, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-3'
            entity['test3'] = 100
            batch.append((TransactionOperation.UPDATE, entity.copy(), {'mode': UpdateMode.REPLACE}))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-4'
            entity['test3'] = 10
            batch.append((TransactionOperation.UPSERT, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-5'
            batch.append((TransactionOperation.UPSERT, entity.copy(), {'mode': UpdateMode.REPLACE}))
            transaction_count += 1

            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert 'etag' in transaction_result[0]
            assert 'etag' not in transaction_result[1]
            assert 'etag' in transaction_result[2]
            assert 'etag' in transaction_result[3]
            assert 'etag' in transaction_result[4]
            assert 'etag' in transaction_result[5]

            entities = self.table.query_entities("PartitionKey eq '003'")
            length = 0
            async for e in entities:
                length += 1
            assert 5 ==  length
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_different_partition_operations_fail(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            await self.table.create_entity(entity)

            # Act
            batch = []

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            batch.append(('update', entity.copy()))

            entity = self._create_random_entity_dict(
                '002', 'batch_negative_1')
            batch.append(('update', entity.copy(), {'mode': UpdateMode.REPLACE}))

            # Assert
            with pytest.raises(ValueError):
                await self.table.submit_transaction(batch)
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_new_non_existent_table(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')

            tc = self.ts.get_table_client("doesntexist")

            batch = [('create', entity)]

            with pytest.raises(TableTransactionError):
                resp = await tc.submit_transaction(batch)
            # Assert
        finally:
            await self._tear_down()

    @pytest.mark.live_test_only
    @cosmos_decorator_async
    async def test_new_invalid_key(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        invalid_key = tables_primary_cosmos_account_key.named_key.key[0:-6] + "==" # cut off a bit from the end to invalidate
        tables_primary_cosmos_account_key = AzureNamedKeyCredential(tables_cosmos_account_name, invalid_key)
        credential = AzureNamedKeyCredential(name=tables_cosmos_account_name, key=tables_primary_cosmos_account_key.named_key.key)
        self.ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "table"), credential=credential)
        self.table_name = self.get_resource_name('uttable')
        self.table = self.ts.get_table_client(self.table_name)

        entity = self._create_random_entity_dict('001', 'batch_negative_1')

        batch = [('create', entity)]
        with pytest.raises(ClientAuthenticationError):
            resp = await self.table.submit_transaction(batch)

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_new_delete_nonexistent_entity(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')

            batch = [('delete', entity)]
            with pytest.raises(TableTransactionError):
                resp = await self.table.submit_transaction(batch)

        finally:
            await self._tear_down()

    @pytest.mark.live_test_only  # Request bodies are very large
    @cosmos_decorator_async
    async def test_batch_request_too_large(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:

            batch = []
            entity = {
                'PartitionKey': 'pk001',
                'Foo': os.urandom(1024*64),
                'Bar': os.urandom(1024*64),
                'Baz': os.urandom(1024*64)
            }
            for i in range(20):
                entity['RowKey'] = str(i)
                batch.append(('create', entity.copy()))

            with pytest.raises(RequestTooLargeError):
                await self.table.submit_transaction(batch)

        finally:
            await self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_delete_batch_with_bad_kwarg(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            await self.table.create_entity(entity)

            received = await self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            good_etag = received.metadata["etag"]
            received.metadata["etag"] = u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"'

            batch = [('delete', received, {"match_condition": MatchConditions.IfNotModified})]

            with pytest.raises(TableTransactionError) as error:
                await self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            received.metadata["etag"] = good_etag
            batch = [('delete', received, {"match_condition": MatchConditions.IfNotModified})]
            resp = await self.table.submit_transaction(batch)

            assert resp is not None
        finally:
            await self._tear_down()

    @pytest.mark.live_test_only
    @cosmos_decorator_async
    async def test_batch_sas_auth(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True, read=True, update=True, delete=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )
            token = AzureSasCredential(token)

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)

            entity = TableEntity()
            entity['PartitionKey'] = 'batch_inserts'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)

            batch = []
            transaction_count = 0
            for i in range(10):
                entity['RowKey'] = str(i)
                batch.append(('create', entity.copy()))
                transaction_count += 1
            transaction_result = await table.submit_transaction(batch)

            assert transaction_result is not None

            total_entities = 0
            async for e in table.list_entities():
                total_entities += 1

            assert total_entities == transaction_count
        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_batch_with_specialchar_partitionkey(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            table2_name = self._get_table_reference('table2')
            table2 = self.ts.get_table_client(table2_name)
            await table2.create_table()

            # Act
            entity1 = {
                'PartitionKey': "A'aaa\"_bbbb2",
                'RowKey': '"A\'aaa"_bbbb2',
                'test': '"A\'aaa"_bbbb2'
            }
            await self.table.submit_transaction([("create", entity1)])
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            await self.table.submit_transaction([("upsert", entity1, {'mode': 'merge'})])
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            await self.table.submit_transaction([("upsert", entity1, {'mode': 'replace'})])
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            await self.table.submit_transaction([("update", entity1, {'mode': 'merge'})])
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            await self.table.submit_transaction([("update", entity1, {'mode': 'replace'})])
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            entity_results = self.table.list_entities()
            async for entity in entity_results:
                assert entity == entity1
                get_entity = await self.table.get_entity(
                    partition_key=entity['PartitionKey'],
                    row_key=entity['RowKey'])
                assert get_entity == entity1

            await self.table.submit_transaction([("delete", entity1)])

        finally:
            await self._tear_down()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_async_batch_inserts(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            # Act
            transaction_count = 10
            async def generate_entities(count):
                for i in range(count):
                    yield ("upsert", {'PartitionKey': 'async_inserts', 'RowKey': str(i)})

            batch = generate_entities(transaction_count)
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert 'etag' in transaction_result[0]

            entities = self.table.query_entities("PartitionKey eq 'async_inserts'")
            entities = [e async for e in entities]

            # Assert
            assert len(entities) ==  transaction_count
        finally:
            await self._tear_down()
