# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta

from devtools_testutils import AzureTestCase

from azure.data.tables import (
    TableServiceClient,
    TableClient,
    TableAnalyticsLogging,
    TableMetrics,
    TableRetentionPolicy
)

from _shared.testcase import TableTestCase
from preparers import tables_decorator, tables_decorator

# ------------------------------------------------------------------------------

class StorageTableTest(AzureTestCase, TableTestCase):
    @tables_decorator
    def test_aad_create_table(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name = self._get_table_reference()
            ts.create_table(table_name)

            if table_name not in [t.name for t in ts.list_tables()]:
                raise AssertionError("Table could not be found")

            ts.delete_table(table_name)
            if table_name in [t.name for t in ts.list_tables()]:
                raise AssertionError("Table was not deleted")

        finally:
            ts.delete_table(table_name)

    @tables_decorator
    def test_aad_query_list_tables(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name1 = self._get_table_reference(prefix="table1")
            table_name2 = self._get_table_reference(prefix="table2")
            table_name3 = self._get_table_reference(prefix="table3")
            table_name4 = self._get_table_reference(prefix="table4")
            ts.create_table(table_name1)
            ts.create_table(table_name2)
            ts.create_table(table_name3)
            ts.create_table(table_name4)

            count = 0
            for table in ts.list_tables():
                count += 1

            assert count == 4

            query_filter = "TableName eq '{}'".format(table_name2)
            count = 0
            for table in ts.query_tables(query_filter):
                count += 1
                assert table.name == table_name2
            assert count == 1

        finally:
            for table in ts.list_tables():
                ts.delete_table(table.name)

    @tables_decorator
    def test_aad_create_table_tc(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name = self._get_table_reference()
            table_client = TableClient(credential=self.get_token_credential(), endpoint=account_url, table_name=table_name)
            table_client.create_table()

            if table_name not in [t.name for t in ts.list_tables()]:
                raise AssertionError("Table could not be found")

            table_client.delete_table()
            if table_name in [t.name for t in ts.list_tables()]:
                raise AssertionError("Table was not deleted")

        finally:
            ts.delete_table(table_name)

    @tables_decorator
    def test_aad_service_properties(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name = self._get_table_reference()
            # Act
            created = ts.create_table(table_name)

            # Assert
            assert created.table_name == table_name

            properties = ts.get_service_properties()
            ts.set_service_properties(analytics_logging=TableAnalyticsLogging(write=True))
            # have to wait for return to service
            p = ts.get_service_properties()
            # have to wait for return to service
            ts.set_service_properties(
                minute_metrics=TableMetrics(
                    enabled=True,
                    include_apis=True,
                    retention_policy=TableRetentionPolicy(enabled=True, days=5)
                )
            )

            ps = ts.get_service_properties()
        finally:
            ts.delete_table(table_name)

    @tables_decorator
    def test_aad_table_service_stats(self, tables_storage_account_name):
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=self.get_token_credential())
        stats = tsc.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)
        self._assert_stats_default(stats)

    @tables_decorator
    def test_aad_insert_entity_dictionary(self, tables_storage_account_name):
        # Arrange
        self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity = self._create_random_entity_dict()

            # Act
            resp = self.table.create_entity(entity=entity)

            # Assert
            self._assert_valid_metadata(resp)
        finally:
            self._tear_down()

    @tables_decorator
    def test_aad_query_user_filter(self, tables_storage_account_name):
        # Arrange
        self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity, _ = self._insert_two_opposite_entities()

            # Act
            entities = self.table.query_entities(
                "married eq @my_param",
                parameters={'my_param': entity['married']}
            )

            assert entities is not None
            length = 0
            for e in entities:
                self._assert_default_entity(e)
                length += 1

            assert length == 1
        finally:
            self._tear_down()