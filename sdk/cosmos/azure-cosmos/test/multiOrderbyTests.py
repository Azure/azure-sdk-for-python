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
    documents = []
    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        
        cls.client = cosmos_client.CosmosClient(cls.host, {'masterKey': cls.masterKey}, cls.connectionPolicy)
        cls.database = test_config._test_config.create_database_if_not_exist(cls.client)


    def generate_multi_orderby_document(self):
        document = {}
        document['id'] = str(uuid.uuid4())
        document[self.NUMBER_FIELD] = random.randint(0, 5)
        document[self.NUMBER_FIELD_2] = random.randint(0, 5)
        document[self.BOOL_FIELD] = random.randint(0, 2) % 2 == 0
        document[self.STRING_FIELD] = str(random.randint(0, 5))
        document[self.STRING_FIELD_2] = str(random.randint(0, 5))
        document[self.NULL_FIELD] = None
        document[self.OBJECT_FIELD] = ""
        document[self.ARRAY_FIELD] = []
        document[self.SHORT_STRING_FIELD] = "a" + str(random.randint(0, 100))
        document[self.MEDIUM_STRING_FIELD] = "a" + str(random.randint(0, 128) + 100)
        document[self.LONG_STRING_FIELD] = "a" + str(random.randint(0, 255) + 128)
        document[self.PARTITION_KEY] = random.randint(0, 5)
        return document

    def create_random_documents(self, container, number_of_documents, number_of_duplicates):
        for i in range(0, number_of_documents):
            multi_orderby_document = self.generate_multi_orderby_document()
            for j in range(0, number_of_duplicates):
                # Add the document itself for exact duplicates
                clone = multi_orderby_document.copy()
                clone['id'] = str(uuid.uuid4())
                self.documents.append(clone)

                # Permute all the fields so that there are duplicates with tie breaks
                number_clone = multi_orderby_document.copy()
                number_clone[self.NUMBER_FIELD] = random.randint(0, 5)
                number_clone['id'] = str(uuid.uuid4())
                self.documents.append(number_clone)

                string_clone = multi_orderby_document.copy()
                string_clone[self.STRING_FIELD] = str(random.randint(0, 5))
                string_clone['id'] = str(uuid.uuid4())
                self.documents.append(string_clone)

                bool_clone = multi_orderby_document.copy()
                bool_clone[self.BOOL_FIELD] = random.randint(0, 2) % 2 == 0
                bool_clone['id'] = str(uuid.uuid4())
                self.documents.append(bool_clone)

                # Also fuzz what partition it goes to
                partition_clone = multi_orderby_document.copy()
                partition_clone[self.PARTITION_KEY] = random.randint(0, 5)
                partition_clone['id'] = str(uuid.uuid4())
                self.documents.append(partition_clone)

        for document in self.documents:
            self.client.CreateItem(container['_self'], document)

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
        partitionKey = {
            "paths": [
                "/pk"
            ],
            "kind": "Hash"
        }
        container_id = 'multi_orderby_container' + str(uuid.uuid4())
        container_definition = {
            'id': container_id,
            'indexingPolicy': indexingPolicy,
            'partitionKey': partitionKey
        }
        options = { 'offerThroughput': 25100 }
        created_container = self.client.CreateContainer(self.database['_self'], container_definition, options)

        number_of_documents = 4
        number_of_duplicates = 5
        self.create_random_documents(created_container, number_of_documents, number_of_duplicates)

        feed_options = { 'enableCrossPartitionQuery': True }
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
                                "ORDER BY " + orderby_item_builder

                        expected_ordered_list = self.top(self.sort(self.filter(self.documents, has_filter), composite_index, invert), has_top, top_count)

                        result_ordered_list = list(self.client.QueryItems(created_container['_self'], query, feed_options))

                        self.validate_results(expected_ordered_list, result_ordered_list, composite_index)

    def top(self, documents, has_top, top_count):
        return documents[0:top_count] if has_top else documents

    def sort(self, documents, composite_index, invert):
        current_docs = documents
        for composite_path in reversed(composite_index):
            order = composite_path['order']
            if invert:
                order = "ascending" if order == "descending" else "descending"
            path = composite_path['path'].replace("/", "")
            if self.NULL_FIELD not in path:
                current_docs = sorted(current_docs, key=lambda x: x[path], reverse=True if order == "descending" else False)
        return current_docs

    def filter(self, documents, has_filter):
        return [x for x in documents if x[self.NUMBER_FIELD] % 2 == 0] if has_filter else documents

    def validate_results(self, expected_ordered_list, result_ordered_list, composite_index):
        self.assertEquals(len(expected_ordered_list), len(result_ordered_list))

        for i in range(0, len(expected_ordered_list)):
            result_values = result_ordered_list[i]['$1']
            self.assertEquals(len(result_values), len(composite_index))

            for j in range(0, len(composite_index)):
                path = composite_index[j]['path'].replace("/", "")
                if self.NULL_FIELD in path:
                    self.assertIsNone(expected_ordered_list[i][path])
                    self.assertIsNone(result_values[j])
                else:
                    self.assertEquals(expected_ordered_list[i][path], result_values[j])
