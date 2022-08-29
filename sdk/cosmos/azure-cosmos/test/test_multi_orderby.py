# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import uuid
import pytest
import random
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
import test_config

pytestmark = pytest.mark.cosmosEmulator

# IMPORTANT NOTES:

#      Most test cases in this file create collections in your Azure Cosmos account.
#      Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.

#      To Run the test, replace the two member fields (masterKey and host) with values
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown")
class MultiOrderbyTests(unittest.TestCase):
    """Multi Orderby and Composite Indexes Tests.
    """

    NUMBER_FIELD = "numberField"
    STRING_FIELD = "stringField"
    NUMBER_FIELD_2 = "numberField2"
    STRING_FIELD_2 = "stringField2"
    BOOL_FIELD = "boolField"
    NULL_FIELD = "nullField"
    OBJECT_FIELD = "objectField"
    ARRAY_FIELD = "arrayField"
    SHORT_STRING_FIELD = "shortStringField"
    MEDIUM_STRING_FIELD = "mediumStringField"
    LONG_STRING_FIELD = "longStringField"
    PARTITION_KEY = "pk"
    items = []
    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, consistency_level="Session", connection_policy=cls.connectionPolicy)
        cls.database = test_config._test_config.create_database_if_not_exist(cls.client)

    def generate_multi_orderby_item(self):
        item = {}
        item['id'] = str(uuid.uuid4())
        item[self.NUMBER_FIELD] = random.randint(0, 5)
        item[self.NUMBER_FIELD_2] = random.randint(0, 5)
        item[self.BOOL_FIELD] = random.randint(0, 2) % 2 == 0
        item[self.STRING_FIELD] = str(random.randint(0, 5))
        item[self.STRING_FIELD_2] = str(random.randint(0, 5))
        item[self.NULL_FIELD] = None
        item[self.OBJECT_FIELD] = ""
        item[self.ARRAY_FIELD] = []
        item[self.SHORT_STRING_FIELD] = "a" + str(random.randint(0, 100))
        item[self.MEDIUM_STRING_FIELD] = "a" + str(random.randint(0, 128) + 100)
        item[self.LONG_STRING_FIELD] = "a" + str(random.randint(0, 255) + 128)
        item[self.PARTITION_KEY] = random.randint(0, 5)
        return item

    def create_random_items(self, container, number_of_items, number_of_duplicates):
        # type: (CosmosContainer, int, int) -> None

        for i in range(0, number_of_items):
            multi_orderby_item = self.generate_multi_orderby_item()
            for j in range(0, number_of_duplicates):
                # Add the item itself for exact duplicates
                clone = multi_orderby_item.copy()
                clone['id'] = str(uuid.uuid4())
                self.items.append(clone)

                # Permute all the fields so that there are duplicates with tie breaks
                number_clone = multi_orderby_item.copy()
                number_clone[self.NUMBER_FIELD] = random.randint(0, 5)
                number_clone['id'] = str(uuid.uuid4())
                self.items.append(number_clone)

                string_clone = multi_orderby_item.copy()
                string_clone[self.STRING_FIELD] = str(random.randint(0, 5))
                string_clone['id'] = str(uuid.uuid4())
                self.items.append(string_clone)

                bool_clone = multi_orderby_item.copy()
                bool_clone[self.BOOL_FIELD] = random.randint(0, 2) % 2 == 0
                bool_clone['id'] = str(uuid.uuid4())
                self.items.append(bool_clone)

                # Also fuzz what partition it goes to
                partition_clone = multi_orderby_item.copy()
                partition_clone[self.PARTITION_KEY] = random.randint(0, 5)
                partition_clone['id'] = str(uuid.uuid4())
                self.items.append(partition_clone)

        for item in self.items:
            container.create_item(body=item)

    def test_multi_orderby_queries(self):
        indexingPolicy = {
            "indexingMode": "consistent",
            "automatic": True,
            "includedPaths": [
                {
                    "path": "/*",
                    "indexes": []
                }
            ],
            "excludedPaths": [
                {
                    "path": "/\"_etag\"/?"
                }
            ],
            "compositeIndexes": [
                [
                    {
                        "path": "/numberField",
                        "order": "ascending"
                    },
                    {
                        "path": "/stringField",
                        "order": "descending"
                    }
                ],
                [
                    {
                        "path": "/numberField",
                        "order": "descending"
                    },
                    {
                        "path": "/stringField",
                        "order": "ascending"
                    },
                    {
                        "path": "/numberField2",
                        "order": "descending"
                    },
                    {
                        "path": "/stringField2",
                        "order": "ascending"
                    }
                ],
                [
                    {
                        "path": "/numberField",
                        "order": "descending"
                    },
                    {
                        "path": "/stringField",
                        "order": "ascending"
                    },
                    {
                        "path": "/boolField",
                        "order": "descending"
                    },
                    {
                        "path": "/nullField",
                        "order": "ascending"
                    }
                ],
                [
                    {
                        "path": "/stringField",
                        "order": "ascending"
                    },
                    {
                        "path": "/shortStringField",
                        "order": "ascending"
                    },
                    {
                        "path": "/mediumStringField",
                        "order": "ascending"
                    },
                    {
                        "path": "/longStringField",
                        "order": "ascending"
                    }
                ]
            ]
        }

        options = {'offerThroughput': 25100}
        created_container = self.database.create_container(
            id='multi_orderby_container' + str(uuid.uuid4()),
            indexing_policy=indexingPolicy,
            partition_key=PartitionKey(path='/pk'),
            request_options=options
        )

        number_of_items = 5
        self.create_random_items(created_container, number_of_items, number_of_items)

        bool_vals = [True, False]
        composite_indexes = indexingPolicy['compositeIndexes']
        for composite_index in composite_indexes:
            # for every order
            for invert in bool_vals:
                # for normal and inverted order
                for has_top in bool_vals:
                    # with and without top
                    for has_filter in bool_vals:
                        # with and without filter
                        # Generate a multi order by from that index
                        orderby_items = []
                        select_items = []
                        for composite_path in composite_index:
                            is_desc = True if composite_path['order'] == "descending" else False
                            if invert:
                                is_desc = not is_desc

                            is_desc_string = "DESC" if is_desc else "ASC"
                            composite_path_name = composite_path['path'].replace("/", "")
                            orderby_items_string = "root." + composite_path_name + " " + is_desc_string
                            select_items_string = "root." + composite_path_name
                            orderby_items.append(orderby_items_string)
                            select_items.append(select_items_string)

                        top_count = 10
                        select_item_builder = ""
                        for select_item in select_items:
                            select_item_builder += select_item + ","
                        select_item_builder = select_item_builder[:-1]

                        orderby_item_builder = ""
                        for orderby_item in orderby_items:
                            orderby_item_builder += orderby_item + ","
                        orderby_item_builder = orderby_item_builder[:-1]

                        top_string = "TOP " + str(top_count) if has_top else ""
                        where_string = "WHERE root." + self.NUMBER_FIELD + " % 2 = 0" if has_filter else ""
                        query = "SELECT " + top_string + " [" + select_item_builder + "] " + \
                                "FROM root " + where_string + " " + \
                                "ORDER BY " + orderby_item_builder  # nosec

                        expected_ordered_list = self.top(self.sort(self.filter(self.items, has_filter), composite_index, invert), has_top, top_count)

                        result_ordered_list = list(created_container.query_items(query=query, enable_cross_partition_query=True))

                        self.validate_results(expected_ordered_list, result_ordered_list, composite_index)

    def top(self, items, has_top, top_count):
        return items[0:top_count] if has_top else items

    def sort(self, items, composite_index, invert):
        current_docs = items
        for composite_path in reversed(composite_index):
            order = composite_path['order']
            if invert:
                order = "ascending" if order == "descending" else "descending"
            path = composite_path['path'].replace("/", "")
            if self.NULL_FIELD not in path:
                current_docs = sorted(current_docs, key=lambda x: x[path], reverse=True if order == "descending" else False)
        return current_docs

    def filter(self, items, has_filter):
        return [x for x in items if x[self.NUMBER_FIELD] % 2 == 0] if has_filter else items

    def validate_results(self, expected_ordered_list, result_ordered_list, composite_index):
        self.assertEqual(len(expected_ordered_list), len(result_ordered_list))

        for i in range(0, len(expected_ordered_list)):
            result_values = result_ordered_list[i]['$1']
            self.assertEqual(len(result_values), len(composite_index))

            for j in range(0, len(composite_index)):
                path = composite_index[j]['path'].replace("/", "")
                if self.NULL_FIELD in path:
                    self.assertIsNone(expected_ordered_list[i][path])
                    self.assertIsNone(result_values[j])
                else:
                    self.assertEqual(expected_ordered_list[i][path], result_values[j])
