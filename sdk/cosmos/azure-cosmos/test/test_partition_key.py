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
import pytest
import requests
import datetime
import six
import json
import uuid
from six.moves.urllib.parse import quote as urllib_quote
import azure.cosmos.auth as auth
import azure.cosmos.partition_key as partition_key
import azure.cosmos.cosmos_client as cosmos_client
import test_config

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class PartitionKeyTests(unittest.TestCase):
    """Tests to verify if non partitoned collections are properly accessed on migration with version 2018-12-31.
    """

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def tearDownClass(cls):
        cls.created_db.delete_container(container=cls.created_collection_id)

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, "Session", connection_policy=cls.connectionPolicy)
        cls.created_db = test_config._test_config.create_database_if_not_exist(cls.client)
        cls.created_collection = test_config._test_config.create_multi_partition_collection_with_custom_pk_if_not_exist(cls.client)

        # Create a non partitioned collection using the rest API and older version
        requests_client = requests.Session()
        base_url_split = cls.host.split(":");
        resource_url = base_url_split[0] + ":" + base_url_split[1] + ":" + base_url_split[2].split("/")[0] + "//dbs/" + cls.created_db.id + "/colls/"
        verb = "post"
        resource_id_or_fullname = "dbs/" + cls.created_db.id
        resource_type = "colls"
        data = '{"id":"mycoll"}'

        headers = {}
        headers["x-ms-version"] = "2018-09-17"
        headers["x-ms-date"] = (datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        headers['authorization'] = cls.get_authorization(cls.created_db.client_connection, verb, resource_id_or_fullname, resource_type, headers)
        response = requests_client.request(verb,
                                  resource_url,
                                  data=data,
                                  headers=headers,
                                  timeout=60,
                                  stream=False,
                                  verify=False)

        data = response.content
        if not six.PY2:
            # python 3 compatible: convert data from byte to unicode string
            data = data.decode('utf-8')
        data = json.loads(data)
        cls.created_collection_id = data['id']

        # Create a document in the non partitioned collection using the rest API and older version
        resource_url = base_url_split[0] + ":" + base_url_split[1] + ":" + base_url_split[2].split("/")[0]\
                       + "//dbs/" + cls.created_db.id + "/colls/" + cls.created_collection_id + "/docs/"
        resource_id_or_fullname = "dbs/" + cls.created_db.id + "/colls/" + cls.created_collection_id
        resource_type = "docs"
        data = '{"id":"doc1"}'

        headers['authorization'] = cls.get_authorization(cls.created_db.client_connection, verb,
                                                         resource_id_or_fullname, resource_type, headers)
        response = requests_client.request(verb,
                                  resource_url,
                                  data=data,
                                  headers=headers,
                                  timeout=60,
                                  stream=False,
                                  verify=False)

        data = response.content
        if not six.PY2:
            # python 3 compatible: convert data from byte to unicode string
            data = data.decode('utf-8')
        data = json.loads(data)
        cls.created_document = data

    @classmethod
    def get_authorization(cls, client, verb, resource_id_or_fullname, resource_type, headers):
        authorization = auth.GetAuthorizationHeader(
            cosmos_client_connection=client,
            verb=verb,
            path='',
            resource_id_or_fullname=resource_id_or_fullname,
            is_name_based=True,
            resource_type=resource_type,
            headers=headers)

        # urllib.quote throws when the input parameter is None
        if authorization:
            # -_.!~*'() are valid characters in url, and shouldn't be quoted.
            authorization = urllib_quote(authorization, '-_.!~*\'()')

        return authorization

    def test_non_partitioned_collection_operations(self):
        created_container = self.created_db.get_container_client(self.created_collection_id)

        # Pass partitionKey.Empty as partition key to access documents from a single partition collection with v 2018-12-31 SDK
        read_item = created_container.read_item(self.created_document['id'], partition_key=partition_key.NonePartitionKeyValue)
        self.assertEqual(read_item['id'], self.created_document['id'])

        document_definition = {'id': str(uuid.uuid4())}
        created_item = created_container.create_item(body=document_definition)
        self.assertEqual(created_item['id'], document_definition['id'])

        read_item = created_container.read_item(created_item['id'], partition_key=partition_key.NonePartitionKeyValue)
        self.assertEqual(read_item['id'], created_item['id'])

        document_definition_for_replace = {'id': str(uuid.uuid4())}
        replaced_item = created_container.replace_item(created_item['id'], body=document_definition_for_replace)
        self.assertEqual(replaced_item['id'], document_definition_for_replace['id'])

        upserted_item = created_container.upsert_item(body=document_definition)
        self.assertEqual(upserted_item['id'], document_definition['id'])

        # one document was created during setup, one with create (which was replaced) and one with upsert
        items = list(created_container.query_items("SELECT * from c", partition_key=partition_key.NonePartitionKeyValue))
        self.assertEqual(len(items), 3)

        document_created_by_sproc_id = 'testDoc'
        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                'function () {' +
                '   var client = getContext().getCollection();' +
                '   var doc = client.createDocument(client.getSelfLink(), { id: \'' + document_created_by_sproc_id + '\'}, {}, function(err, docCreated, options) { ' +
                '   if(err) throw new Error(\'Error while creating document: \' + err.message);' +
                '   else {' +
                '   getContext().getResponse().setBody(1);' +
                '        }' +
                '   });}')
        }

        created_sproc = created_container.scripts.create_stored_procedure(body=sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        result = created_container.scripts.execute_stored_procedure(sproc=created_sproc['id'], partition_key=partition_key.NonePartitionKeyValue)
        self.assertEqual(result, 1)

        # 3 previous items + 1 created from the sproc
        items = list(created_container.read_all_items())
        self.assertEqual(len(items), 4)

        created_container.delete_item(upserted_item['id'], partition_key=partition_key.NonePartitionKeyValue)
        created_container.delete_item(replaced_item['id'], partition_key=partition_key.NonePartitionKeyValue)
        created_container.delete_item(document_created_by_sproc_id, partition_key=partition_key.NonePartitionKeyValue)
        created_container.delete_item(self.created_document['id'], partition_key=partition_key.NonePartitionKeyValue)

        items = list(created_container.read_all_items())
        self.assertEqual(len(items), 0)

    def test_multi_partition_collection_read_document_with_no_pk(self):
        document_definition = {'id': str(uuid.uuid4())}
        self.created_collection.create_item(body=document_definition)
        read_item = self.created_collection.read_item(item=document_definition['id'], partition_key=partition_key.NonePartitionKeyValue)
        self.assertEqual(read_item['id'], document_definition['id'])
        self.created_collection.delete_item(item=document_definition['id'], partition_key=partition_key.NonePartitionKeyValue)

    def test_hash_v2_partition_key_definition(self):
        created_container = self.created_db.create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash")
        )
        created_container_properties = created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 2)
        self.created_db.delete_container(created_container)

        created_container = self.created_db.create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=2)
        )
        created_container_properties = created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 2)
        self.created_db.delete_container(created_container)

    def test_hash_v1_partition_key_definition(self):
        created_container = self.created_db.create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=1)
        )
        created_container_properties = created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 1)
        self.created_db.delete_container(created_container)
