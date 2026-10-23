# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Self-contained TOP/ORDER BY copy with preserved public paging assertions.

The original method and document definitions are retained. Owned setup omits
the original 30,000-RU/s provisioning, so this is not proof of distributed
merging. The helper omits only the private legacy QueryIterable identity
assertion; ItemPaged, IDs, ordering, page sizes, counts, and exhaustion remain.
No original test module is imported.
"""

import os
import unittest
import uuid

import pytest
from azure.core.paging import ItemPaged
from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosEmulator
class TestCrossPartitionTopOrderBy(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
        )
        self.addCleanup(self.client.close)
        self.database_id = "legacy_query_top_" + uuid.uuid4().hex
        database = self.client.create_database(self.database_id)
        self.addCleanup(self._delete_owned_database)
        print(f"\nOwned TOP database: {self.database_id}")
        self.created_container = database.create_container(
            id="orders", partition_key=PartitionKey(path="/id"),
        )
        self.document_definitions = []
        for i in range(20):
            d = {'id': str(i),
                 'name': 'sample document',
                 'spam': 'eggs' + str(i),
                 'cnt': i,
                 'key': 'value',
                 'spam2': 'eggs' + str(i) if (i == 3) else i,
                 'boolVar': (i % 2 == 0),
                 'number': 1.1 * i
                 }
            self.created_container.create_item(d)
            self.document_definitions.append(d)

    def _delete_owned_database(self):
        self.client.delete_database(self.database_id)
        print(f"\nDeleted owned TOP database: {self.database_id}")

    def test_orderby_top_query_rust(self):
        # Source: tests/test_orderby.py::TestCrossPartitionTopOrderBy.test_orderby_top_query
        # test an order by query combined with top

        top_count = 9
        # sanity check
        self.assertLess(top_count, len(self.document_definitions))

        # an order by query with top, total existing docs more than requested top count
        query = {
            'query': 'SELECT top %d * FROM root r order by r.spam' % top_count  # nosec
        }

        def get_order_by_key(r):
            return r['spam']

        expected_ordered_ids = [r['id'] for r in sorted(self.document_definitions, key=get_order_by_key)[:top_count]]

        self.execute_query_and_validate_results(query, expected_ordered_ids)

    def execute_query_and_validate_results(self, query, expected_ordered_ids):
        # Source helper: tests/test_orderby.py::TestCrossPartitionTopOrderBy.execute_query_and_validate_results
        page_size = 2

        result_iterable = self.created_container.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=page_size
        )

        self.assertTrue(isinstance(result_iterable, ItemPaged))

        it = result_iterable.__iter__()

        def invokeNext():
            return next(it)

        for i in range(len(expected_ordered_ids)):
            item = invokeNext()
            self.assertEqual(item['id'], expected_ordered_ids[i])

        results = {}
        cnt = 0
        page_iter = result_iterable.by_page()
        for page in page_iter:
            fetched_res = list(page)
            fetched_size = len(fetched_res)

            for item in fetched_res:
                self.assertEqual(item['id'], expected_ordered_ids[cnt])
                results[cnt] = item
                cnt = cnt + 1
            if (cnt < len(expected_ordered_ids)):
                self.assertEqual(fetched_size, page_size, "page size")
            else:
                if cnt == len(expected_ordered_ids):
                    self.assertTrue(fetched_size <= page_size, "last page size")
                    break
                else:
                    self.fail("more results than expected")

        self.assertEqual(len(results), len(expected_ordered_ids))

        with self.assertRaises(StopIteration):
            next(page_iter)
