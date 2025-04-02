# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""
import json
import os.path
import time
import unittest
import urllib.parse as urllib
import uuid

import pytest
import requests
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError
from azure.core.pipeline.transport import AsyncioRequestsTransport, AsyncioRequestsTransportResponse

import azure.cosmos._base as base
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.aio import CosmosClient, _retry_utility_async, DatabaseProxy
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey


class TimeoutTransport(AsyncioRequestsTransport):

    def __init__(self, response):
        self._response = response
        super(TimeoutTransport, self).__init__()

    async def send(self, *args, **kwargs):
        if kwargs.pop("passthrough", False):
            return super(TimeoutTransport, self).send(*args, **kwargs)

        time.sleep(5)
        if isinstance(self._response, Exception):
            raise self._response
        current_response = await self._response
        output = requests.Response()
        output.status_code = current_response
        response = AsyncioRequestsTransportResponse(None, output)
        return response


@pytest.mark.cosmosLong
class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
    """
    client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    database_for_test: DatabaseProxy = None

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            await func(*args, **kwargs)
            self.fail('function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.database_for_test = self.client.get_database_client(self.configs.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_partitioned_collection_execute_stored_procedure_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        document_id = str(uuid.uuid4())

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '   var client = getContext().getCollection();' +
                    '   client.createDocument(client.getSelfLink(), { id: "' + document_id + '", pk : 2}, ' +
                    '   {}, function(err, docCreated, options) { ' +
                    '   if(err) throw new Error(\'Error while creating document: \' + err.message);' +
                    '   else {' +
                    '   getContext().getResponse().setBody(1);' +
                    '        }' +
                    '   });}')
        }

        created_sproc = await created_collection.scripts.create_stored_procedure(body=sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        result = await created_collection.scripts.execute_stored_procedure(sproc=created_sproc['id'], partition_key=2)
        assert result == 1

        # Partiton Key value different than what is specified in the stored procedure body will cause a bad request(400) error
        await self.__assert_http_failure_with_status(
            StatusCodes.BAD_REQUEST,
            created_collection.scripts.execute_stored_procedure,
            created_sproc['id'])

    async def test_partitioned_collection_partition_key_value_types_async(self):

        created_db = self.database_for_test

        created_collection = created_db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': None,
                               'spam': 'eggs'}

        # create document with partitionKey set as None here
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'spam': 'eggs'}

        # create document with partitionKey set as Undefined here
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': True,
                               'spam': 'eggs'}

        # create document with bool partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 'value',
                               'spam': 'eggs'}

        # create document with string partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 100,
                               'spam': 'eggs'}

        # create document with int partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 10.50,
                               'spam': 'eggs'}

        # create document with float partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'value'}

        # Should throw an error because automatic id generation is disabled always.
        await self.__assert_http_failure_with_status(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition
        )

    async def test_partitioned_collection_conflict_crud_and_query_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        conflict_definition = {'id': 'new conflict',
                               'resourceId': 'doc1',
                               'operationType': 'create',
                               'resourceType': 'document'
                               }

        # read conflict here will return resource not found(404) since there is no conflict here
        await self.__assert_http_failure_with_status(
            StatusCodes.NOT_FOUND,
            created_collection.get_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        # Read conflict feed doesn't require partitionKey to be specified as it's a cross partition thing
        conflict_list = [conflict async for conflict in created_collection.list_conflicts()]
        assert len(conflict_list) == 0

        # delete conflict here will return resource not found(404) since there is no conflict here
        await self.__assert_http_failure_with_status(
            StatusCodes.NOT_FOUND,
            created_collection.delete_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        conflict_list = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'')]

        assert len(conflict_list) == 0

        # query conflicts by providing the partitionKey value
        options = {'partitionKey': conflict_definition.get('id')}
        conflict_list = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'',
            # nosec
            partition_key=conflict_definition['id']
        )]

        assert len(conflict_list) == 0

    async def test_document_crud_async(self):

        # create collection
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # read documents
        document_list = [document async for document in created_collection.read_all_items()]
        # create a document
        before_create_documents_count = len(document_list)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        created_document = await created_collection.create_item(body=document_definition,
                                                                enable_automatic_id_generation=True)
        assert created_document.get('name') == document_definition['name']

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = await created_collection.create_item(body=document_definition)
        assert created_document.get('name') == document_definition['name']
        assert created_document.get('id') == document_definition['id']

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        await self.__assert_http_failure_with_status(StatusCodes.CONFLICT,
                                                     created_collection.create_item,
                                                     duplicated_definition_with_id)
        # read documents after creation
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 2
        # query documents
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[{'name': '@name', 'value': document_definition['name']}]
        )]
        assert document_list is not None
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[
                {'name': '@name', 'value': document_definition['name']}
            ],
            enable_scan_in_query=True
        )]
        assert document_list is not None
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document
        )
        assert replaced_document['name'] == 'replaced document'
        assert replaced_document['spam'] == 'not eggs'
        assert created_document['id'] == replaced_document['id']

        # replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        await self.__assert_http_failure_with_status(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        try:
            await created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only etag specified")
        except ValueError:
            pass

        # should fail if only match condition specified
        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        # should fail if invalid match condition specified
        try:
            await created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if invalid match condition specified")
        except TypeError:
            pass

        # should pass for most recent etag
        replaced_document_conditional = await created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document
        )
        assert replaced_document_conditional['name'] == 'replaced document based on condition'
        assert replaced_document_conditional['spam'] == 'new spam field'
        assert replaced_document_conditional['id'] == replaced_document['id']

        # read document
        one_document_from_read = await created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk']
        )
        assert replaced_document['id'] == one_document_from_read['id']
        # delete document
        await created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['pk']
        )
        # read documents after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     created_collection.read_item,
                                                     replaced_document['id'],
                                                     replaced_document['id'])

    async def test_document_upsert_async(self):

        # create collection
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read documents and check count
        document_list = [document async for document in created_collection.read_all_items()]
        before_create_documents_count = len(document_list)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        # create document using Upsert API
        created_document = await created_collection.upsert_item(body=document_definition)

        # verify id property
        assert created_document['id'] == document_definition['id']

        # test error for non-string id
        with self.assertRaises(TypeError):
            document_definition['id'] = 7
            await created_collection.upsert_item(body=document_definition)

        # read documents after creation and verify updated count
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 1

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'

        # should replace document since it already exists
        upserted_document = await created_collection.upsert_item(body=created_document)

        # verify the changed properties
        assert upserted_document['name'] == created_document['name']
        assert upserted_document['spam'] == created_document['spam']

        # verify id property
        assert upserted_document['id'] == created_document['id']

        # read documents after upsert and verify count doesn't increases again
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 1

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        new_document = await created_collection.upsert_item(body=created_document)

        # Test modified access conditions
        created_document['spam'] = 'more eggs'
        await created_collection.upsert_item(body=created_document)
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            await created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])

        # verify id property
        assert created_document['id'] == new_document['id']

        # read documents after upsert and verify count increases
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 2

        # delete documents
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document['pk'])
        await created_collection.delete_item(item=new_document, partition_key=new_document['pk'])

        # read documents after delete and verify count is same as original
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count

    async def test_geospatial_index_async(self):
        db = self.database_for_test
        # partial policy specified
        collection = await db.create_container(
            id='collection with spatial index ' + str(uuid.uuid4()),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/"Location"/?',
                        'indexes': [
                            {
                                'kind': 'Spatial',
                                'dataType': 'Point'
                            }
                        ]
                    },
                    {
                        'path': '/'
                    }
                ]
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        await collection.create_item(
            body={
                'id': 'loc1',
                'Location': {
                    'type': 'Point',
                    'coordinates': [20.0, 20.0]
                }
            }
        )
        await collection.create_item(
            body={
                'id': 'loc2',
                'Location': {
                    'type': 'Point',
                    'coordinates': [100.0, 100.0]
                }
            }
        )
        results = [result async for result in collection.query_items(
            query="SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000)")]
        assert len(results) == 1
        assert 'loc1' == results[0]['id']

    # CRUD test for User resource

    async def test_user_crud_async(self):

        # Should do User CRUD operations successfully.
        # create database
        db = self.database_for_test
        # list users
        users = [user async for user in db.list_users()]
        before_create_count = len(users)
        # create user
        user_id = 'new user' + str(uuid.uuid4())
        user = await db.create_user(body={'id': user_id})
        assert user.id == user_id
        # list users after creation
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 1
        # query users
        results = [user async for user in db.query_users(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': user_id}
            ]
        )]
        assert results is not None

        # replace user
        replaced_user_id = 'replaced user' + str(uuid.uuid4())
        user_properties = await user.read()
        user_properties['id'] = replaced_user_id
        replaced_user = await db.replace_user(user_id, user_properties)
        assert replaced_user.id == replaced_user_id
        assert user_properties['id'] == replaced_user.id

        # read user
        user = db.get_user_client(replaced_user.id)
        assert replaced_user.id == user.id

        # delete user
        await db.delete_user(user.id)

        # read user after deletion
        deleted_user = db.get_user_client(user.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     deleted_user.read)

    async def test_user_upsert_async(self):

        # create database
        db = self.database_for_test

        # read users and check count
        users = [user async for user in db.list_users()]
        before_create_count = len(users)

        # create user using Upsert API
        user_id = 'user' + str(uuid.uuid4())
        user = await db.upsert_user(body={'id': user_id})

        # verify id property
        assert user.id == user_id

        # read users after creation and verify updated count
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 1

        # Should replace the user since it already exists, there is no public property to change here
        user_properties = await user.read()
        upserted_user = await db.upsert_user(user_properties)

        # verify id property
        assert upserted_user.id == user.id

        # read users after upsert and verify count doesn't increase again
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 1

        user_properties = await user.read()
        user_properties['id'] = 'new user' + str(uuid.uuid4())
        user.id = user_properties['id']

        # Upsert should create new user since id is different
        new_user = await db.upsert_user(user_properties)

        # verify id property
        assert new_user.id == user.id

        # read users after upsert and verify count increases
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count + 2

        # delete users
        await db.delete_user(upserted_user.id)
        await db.delete_user(new_user.id)

        # read users after delete and verify count remains the same
        users = [user async for user in db.list_users()]
        assert len(users) == before_create_count

    async def test_permission_crud_async(self):

        # create database
        db = self.database_for_test
        # create user
        user = await db.create_user(body={'id': 'new user' + str(uuid.uuid4())})
        # list permissions
        permissions = [permission async for permission in user.list_permissions()]
        before_create_count = len(permissions)
        permission = {
            'id': 'new permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }
        # create permission
        permission = await user.create_permission(permission)
        assert permission.id == 'new permission'
        # list permissions after creation
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 1
        # query permissions
        results = [permission async for permission in user.query_permissions(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': permission.id}
            ]
        )]
        assert results is not None

        # replace permission
        change_permission = permission.properties.copy()
        permission.properties['id'] = 'replaced permission'
        permission.id = permission.properties['id']
        replaced_permission = await user.replace_permission(change_permission['id'], permission.properties)
        assert replaced_permission.id == 'replaced permission'
        assert permission.id == replaced_permission.id
        # read permission
        permission = await user.get_permission(replaced_permission.id)
        assert replaced_permission.id == permission.id
        # delete permission
        await user.delete_permission(replaced_permission.id)
        # read permission after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     user.get_permission,
                                                     permission.id)

    async def test_permission_upsert_async(self):

        # create database
        db = self.database_for_test

        # create user
        user = await db.create_user(body={'id': 'new user' + str(uuid.uuid4())})

        # read permissions and check count
        permissions = [permission async for permission in user.list_permissions()]
        before_create_count = len(permissions)

        permission_definition = {
            'id': 'permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }

        # create permission using Upsert API
        created_permission = await user.upsert_permission(permission_definition)

        # verify id property
        assert created_permission.id == permission_definition['id']

        # read permissions after creation and verify updated count
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 1

        # update permission mode
        permission_definition['permissionMode'] = documents.PermissionMode.All

        # should repace the permission since it already exists
        upserted_permission = await user.upsert_permission(permission_definition)
        # verify id property
        assert upserted_permission.id == created_permission.id

        # verify changed property
        assert upserted_permission.permission_mode == permission_definition['permissionMode']

        # read permissions and verify count doesn't increase again
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 1

        # update permission id
        created_permission.properties['id'] = 'new permission'
        created_permission.id = created_permission.properties['id']
        # resource needs to be changed along with the id in order to create a new permission
        created_permission.properties['resource'] = 'dbs/N9EdAA==/colls/N9EdAIugXgA='
        created_permission.resource_link = created_permission.properties['resource']

        # should create new permission since id has changed
        new_permission = await user.upsert_permission(created_permission.properties)

        # verify id and resource property
        assert new_permission.id == created_permission.id

        assert new_permission.resource_link == created_permission.resource_link

        # read permissions and verify count increases
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count + 2

        # delete permissions
        await user.delete_permission(upserted_permission.id)
        await user.delete_permission(new_permission.id)

        # read permissions and verify count remains the same
        permissions = [permission async for permission in user.list_permissions()]
        assert len(permissions) == before_create_count

    async def test_authorization_async(self):

        async def __setup_entities():
            """
            Sets up entities for this test.

            :Parameters:
                - `client`: cosmos_client_connection.CosmosClientConnection

            :Returns:
                dict

            """
            # create database
            db = self.database_for_test
            # create collection
            collection = await db.create_container(
                id='test_authorization' + str(uuid.uuid4()),
                partition_key=PartitionKey(path='/id', kind='Hash')
            )
            # create document1
            document = await collection.create_item(
                body={'id': 'doc1',
                      'spam': 'eggs',
                      'key': 'value'},
            )

            # create user
            user = await db.create_user(body={'id': 'user' + str(uuid.uuid4())})

            # create permission for collection
            permission = {
                'id': 'permission On Coll',
                'permissionMode': documents.PermissionMode.Read,
                'resource': "dbs/" + db.id + "/colls/" + collection.id
            }
            permission_on_coll = await user.create_permission(body=permission)
            assert permission_on_coll.properties['_token'] is not None

            # create permission for document
            permission = {
                'id': 'permission On Doc',
                'permissionMode': documents.PermissionMode.All,
                'resource': "dbs/" + db.id + "/colls/" + collection.id + "/docs/" + document["id"]
            }
            permission_on_doc = await user.create_permission(body=permission)
            assert permission_on_doc.properties['_token'] is not None

            entities = {
                'db': db,
                'coll': collection,
                'doc': document,
                'user': user,
                'permissionOnColl': permission_on_coll,
                'permissionOnDoc': permission_on_doc,
            }
            return entities

        # Client without any authorization will fail.
        try:
            async with CosmosClient(TestCRUDOperationsAsync.host, {}) as client:
                [db async for db in client.list_databases()]
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.UNAUTHORIZED

        # Client with master key.
        async with CosmosClient(TestCRUDOperationsAsync.host,
                                TestCRUDOperationsAsync.masterKey) as client:
            # setup entities
            entities = await __setup_entities()
            resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id:
                                   entities['permissionOnColl'].properties['_token']}

        async with CosmosClient(
                TestCRUDOperationsAsync.host, resource_tokens) as col_client:
            db = entities['db']

            old_client_connection = db.client_connection
            db.client_connection = col_client.client_connection
            # 1. Success-- Use Col Permission to Read
            success_coll = db.get_container_client(container=entities['coll'])
            # 2. Failure-- Use Col Permission to delete
            await self.__assert_http_failure_with_status(StatusCodes.FORBIDDEN,
                                                         db.delete_container,
                                                         success_coll)
            # 3. Success-- Use Col Permission to Read All Docs
            success_documents = [document async for document in success_coll.read_all_items()]
            assert success_documents is not None
            assert len(success_documents) == 1
            # 4. Success-- Use Col Permission to Read Doc

            doc_id = entities['doc']['id']
            success_doc = await success_coll.read_item(
                item=doc_id,
                partition_key=doc_id
            )
            assert success_doc is not None
            assert success_doc['id'] == entities['doc']['id']

            # 5. Failure-- Use Col Permission to Delete Doc
            await self.__assert_http_failure_with_status(StatusCodes.FORBIDDEN,
                                                         success_coll.delete_item,
                                                         doc_id, doc_id)

            resource_tokens = {"dbs/" + entities['db'].id + "/colls/" + entities['coll'].id + "/docs/" + doc_id:
                                   entities['permissionOnDoc'].properties['_token']}

        async with CosmosClient(
                TestCRUDOperationsAsync.host, resource_tokens) as doc_client:

            # 6. Success-- Use Doc permission to read doc
            read_doc = await doc_client.get_database_client(db.id).get_container_client(success_coll.id).read_item(
                doc_id, doc_id)
            assert read_doc["id"] == doc_id

            # 6. Success-- Use Doc permission to delete doc
            await doc_client.get_database_client(db.id).get_container_client(success_coll.id).delete_item(doc_id,
                                                                                                          doc_id)
            assert read_doc["id"] == doc_id

            db.client_connection = old_client_connection
            await db.delete_container(entities['coll'])

    async def test_script_logging_execute_stored_procedure_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '   var mytext = \'x\';' +
                    '   var myval = 1;' +
                    '   try {' +
                    '       console.log(\'The value of %s is %s.\', mytext, myval);' +
                    '       getContext().getResponse().setBody(\'Success!\');' +
                    '   }' +
                    '   catch (err) {' +
                    '       getContext().getResponse().setBody(\'inline err: [\' + err.number + \'] \' + err);' +
                    '   }'
                    '}')
        }

        created_sproc = await created_collection.scripts.create_stored_procedure(body=sproc)

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            partition_key=1
        )

        assert result == 'Success!'
        assert HttpHeaders.ScriptLogResults not in created_collection.scripts.client_connection.last_response_headers

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=True,
            partition_key=1
        )

        assert result == 'Success!'
        assert urllib.quote('The value of x is 1.') == created_collection.scripts.client_connection. \
            last_response_headers.get(HttpHeaders.ScriptLogResults)

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=False,
            partition_key=1
        )

        assert result == 'Success!'
        assert HttpHeaders.ScriptLogResults not in created_collection.scripts.client_connection.last_response_headers

    async def test_client_request_timeout_async(self):
        # Test is flaky on Emulator
        if not ('localhost' in self.host or '127.0.0.1' in self.host):
            connection_policy = documents.ConnectionPolicy()
            # making timeout 0 ms to make sure it will throw
            connection_policy.RequestTimeout = 0.000000000001
            # client does a getDatabaseAccount on initialization, which will not time out because
            # there is a forced timeout for those calls
            async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as client:
                with self.assertRaises(Exception):
                    databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
                    container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
                    item = {'id': str(uuid.uuid4()), 'name': 'sample'}
                    await container.create_item(body=item)
                    await container.read_item(item=item['id'], partition_key=item['id'])
                    print('Async initialization')

    async def test_read_timeout_async(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 0 ms to make sure it will throw
        connection_policy.DBAReadTimeout = 0.000000000001
        with self.assertRaises(ServiceResponseError):
            # this will make a get database account call
            async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy):
                print('Async initialization')

    async def test_client_request_timeout_when_connection_retry_configuration_specified_async(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 0 ms to make sure it will throw
        connection_policy.RequestTimeout = 0.000000000001
        async with CosmosClient(TestCRUDOperationsAsync.host, TestCRUDOperationsAsync.masterKey,
                                connection_policy=connection_policy,
                                retry_total=3, retry_connect=3, retry_read=3, retry_backoff_max=0.3,
                                retry_on_status_codes=[500, 502, 504]) as client:
            with self.assertRaises(AzureError):
                databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
                container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
                item = {'id': str(uuid.uuid4()), 'name': 'sample'}
                await container.create_item(body=item)
                await container.read_item(item=item['id'], partition_key=item['id'])
                print('Async Initialization')

    # TODO: Skipping this test to debug later
    @unittest.skip
    async def test_client_connection_retry_configuration_async(self):
        total_time_for_two_retries = await self.initialize_client_with_connection_urllib_retry_config(2)
        total_time_for_four_retries = await self.initialize_client_with_connection_urllib_retry_config(4)
        assert total_time_for_four_retries > total_time_for_two_retries

    async def initialize_client_with_connection_urllib_retry_config(self, retries):
        async with CosmosClient(TestCRUDOperationsAsync.host, TestCRUDOperationsAsync.masterKey,
                                retry_total=retries, retry_connect=retries, retry_read=retries,
                                retry_backoff_max=0.3,
                                connection_timeout=.000000001) as client:
            databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
            container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
            start_time = time.time()
            # client does a getDatabaseAccount on initialization, which will not time out because
            # there is a forced timeout for those calls

            try:
                item = {'id': str(uuid.uuid4()), 'name': 'sample'}
                await container.create_item(body=item)
                print('Async initialization')
                self.fail()
            except AzureError as e:
                self.assertIsInstance(e, ServiceResponseError)
                end_time = time.time()
                return end_time - start_time

    # TODO: Skipping this test to debug later
    @unittest.skip
    async def test_absolute_client_timeout_async(self):
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            async with CosmosClient(
                    "https://localhost:9999",
                    TestCRUDOperationsAsync.masterKey,
                    retry_total=3,
                    timeout=1) as client:
                print('Async initialization')

        error_response = ServiceResponseError("Read timeout")
        timeout_transport = TimeoutTransport(error_response)
        async with CosmosClient(
                self.host, self.masterKey, transport=timeout_transport,
                passthrough=True) as client:
            print('Async initialization')

            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                await client.create_database_if_not_exists("test", timeout=2)

        status_response = 500  # Users connection level retry
        timeout_transport = TimeoutTransport(status_response)
        async with CosmosClient(
                self.host, self.masterKey, transport=timeout_transport,
                passthrough=True) as client:
            print('Async initialization')
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                await client.create_database("test", timeout=2)

            databases = client.list_databases(timeout=2)
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                databases = [database async for database in databases]

        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response)
        async with CosmosClient(
                self.host, self.masterKey, transport=timeout_transport,
                passthrough=True) as client:
            print('Async initialization')
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                await client.create_database_if_not_exists("test", timeout=2)

            databases = client.list_databases(timeout=2)
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                databases = [database async for database in databases]

    async def test_query_iterable_functionality_async(self):

        collection = await self.database_for_test.create_container("query-iterable-container-async",
                                                                   PartitionKey(path="/pk"))
        doc1 = await collection.upsert_item(body={'id': 'doc1', 'prop1': 'value1'})
        doc2 = await collection.upsert_item(body={'id': 'doc2', 'prop1': 'value2'})
        doc3 = await collection.upsert_item(body={'id': 'doc3', 'prop1': 'value3'})
        resources = {
            'coll': collection,
            'doc1': doc1,
            'doc2': doc2,
            'doc3': doc3
        }
        # Validate QueryIterable by converting it to a list.
        results = resources['coll'].read_all_items(max_item_count=2)
        docs = [doc async for doc in results]
        assert 3 == len(docs)
        assert resources['doc1']['id'] == docs[0]['id']
        assert resources['doc2']['id'] == docs[1]['id']
        assert resources['doc3']['id'] == docs[2]['id']

        # Validate QueryIterable iterator with 'for'.
        results = resources['coll'].read_all_items(max_item_count=2)
        counter = 0
        # test QueryIterable with 'for'.
        async for doc in results:
            counter += 1
            if counter == 1:
                assert resources['doc1']['id'] == doc['id']
            elif counter == 2:
                assert resources['doc2']['id'] == doc['id']
            elif counter == 3:
                assert resources['doc3']['id'] == doc['id']
        assert counter == 3

        # Get query results page by page.
        results = resources['coll'].read_all_items(max_item_count=2)

        page_iter = results.by_page()
        first_block = [page async for page in await page_iter.__anext__()]
        assert 2 == len(first_block)
        assert resources['doc1']['id'] == first_block[0]['id']
        assert resources['doc2']['id'] == first_block[1]['id']
        assert 1 == len([page async for page in await page_iter.__anext__()])
        with self.assertRaises(StopAsyncIteration):
            await page_iter.__anext__()

        await self.database_for_test.delete_container(collection.id)

    async def test_stored_procedure_functionality_async(self):

        # create collection
        collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        sproc1 = {
            'id': 'storedProcedure1' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '  for (var i = 0; i < 1000; i++) {' +
                    '    var item = getContext().getResponse().getBody();' +
                    '    if (i > 0 && item != i - 1) throw \'body mismatch\';' +
                    '    getContext().getResponse().setBody(i);' +
                    '  }' +
                    '}')
        }

        retrieved_sproc = await collection.scripts.create_stored_procedure(body=sproc1)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc['id'],
            partition_key=1
        )
        assert result == 999
        sproc2 = {
            'id': 'storedProcedure2' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '  for (var i = 0; i < 10; i++) {' +
                    '    getContext().getResponse().appendValue(\'Body\', i);' +
                    '  }' +
                    '}')
        }
        retrieved_sproc2 = await collection.scripts.create_stored_procedure(body=sproc2)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc2['id'],
            partition_key=1
        )
        assert int(result) == 123456789
        sproc3 = {
            'id': 'storedProcedure3' + str(uuid.uuid4()),
            'body': (
                    'function (input) {' +
                    '  getContext().getResponse().setBody(' +
                    '      \'a\' + input.temp);' +
                    '}')
        }
        retrieved_sproc3 = await collection.scripts.create_stored_procedure(body=sproc3)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc3['id'],
            parameters={'temp': 'so'},
            partition_key=1
        )
        assert result == 'aso'

    async def test_get_resource_with_dictionary_and_object_async(self):

        created_db = self.database_for_test

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        assert read_db.id == created_db.id

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        assert read_db.id == created_db.id

        # read database with properties
        read_db = self.client.get_database_client(await created_db.read())
        assert read_db.id == created_db.id

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        assert read_container.id == created_container.id

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        assert read_container.id == created_container.id

        # read container with properties
        created_properties = await created_container.read()
        read_container = created_db.get_container_client(created_properties)
        assert read_container.id == created_container.id

        created_item = await created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})

        # read item with id
        read_item = await created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']

        # read item with properties
        read_item = await created_container.read_item(item=created_item, partition_key=created_item['pk'])
        assert read_item['id'], created_item['id']

        created_sproc = await created_container.scripts.create_stored_procedure({
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': 'function () { }'
        })

        # read sproc with id
        read_sproc = await created_container.scripts.get_stored_procedure(created_sproc['id'])
        assert read_sproc['id'] == created_sproc['id']

        # read sproc with properties
        read_sproc = await created_container.scripts.get_stored_procedure(created_sproc)
        assert read_sproc['id'] == created_sproc['id']

        created_trigger = await created_container.scripts.create_trigger({
            'id': 'sample trigger' + str(uuid.uuid4()),
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        })

        # read trigger with id
        read_trigger = await created_container.scripts.get_trigger(created_trigger['id'])
        assert read_trigger['id'] == created_trigger['id']

        # read trigger with properties
        read_trigger = await created_container.scripts.get_trigger(created_trigger)
        assert read_trigger['id'] == created_trigger['id']

        created_udf = await created_container.scripts.create_user_defined_function({
            'id': 'sample udf' + str(uuid.uuid4()),
            'body': 'function() {var x = 10;}'
        })

        # read udf with id
        read_udf = await created_container.scripts.get_user_defined_function(created_udf['id'])
        assert created_udf['id'] == read_udf['id']

        # read udf with properties
        read_udf = await created_container.scripts.get_user_defined_function(created_udf)
        assert created_udf['id'] == read_udf['id']

        created_user = await created_db.create_user({
            'id': 'user' + str(uuid.uuid4())})

        # read user with id
        read_user = created_db.get_user_client(created_user.id)
        assert read_user.id == created_user.id

        # read user with instance
        read_user = created_db.get_user_client(created_user)
        assert read_user.id == created_user.id

        # read user with properties
        created_user_properties = await created_user.read()
        read_user = created_db.get_user_client(created_user_properties)
        assert read_user.id == created_user.id

        created_permission = await created_user.create_permission({
            'id': 'all permission' + str(uuid.uuid4()),
            'permissionMode': documents.PermissionMode.All,
            'resource': created_container.container_link,
            'resourcePartitionKey': [1]
        })

        # read permission with id
        read_permission = await created_user.get_permission(created_permission.id)
        assert read_permission.id == created_permission.id

        # read permission with instance
        read_permission = await created_user.get_permission(created_permission)
        assert read_permission.id == created_permission.id

        # read permission with properties
        read_permission = await created_user.get_permission(created_permission.properties)
        assert read_permission.id == created_permission.id


    async def test_delete_all_items_by_partition_key_async(self):
        # enable the test only for the emulator
        if "localhost" not in self.host and "127.0.0.1" not in self.host:
            return
        # create database
        created_db = self.database_for_test

        # create container
        created_collection = await created_db.create_container(
            id='test_delete_all_items_by_partition_key ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )
        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            await created_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1)
            )

        # add items for partition key 2
        pk2_item = await created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))

        # delete all items for partition key 1
        await created_collection.delete_all_items_by_partition_key(partition_key1)

        # check that only items from partition key 1 have been deleted
        items = [item async for item in created_collection.read_all_items()]

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        # attempting to delete a non-existent partition key or passing none should not delete
        # anything and leave things unchanged
        await created_collection.delete_all_items_by_partition_key(None)

        # check that no changes were made by checking if the only item is still there
        items = [item async for item in created_collection.read_all_items()]

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        await created_db.delete_container(created_collection)

    async def test_patch_operations_async(self):

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # Create item to patch
        item_id = "patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations)
        # Verify results from patch operations
        assert patched_item.get("color") is None
        assert patched_item.get("prop") is None
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

        # Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST

    async def test_conditional_patching_async(self):

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Create item to patch
        item_id = "conditional_patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)

        # Define patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]

        # Run patch operations with wrong filter
        num_false = item.get("number") + 1
        filter_predicate = "from root where root.number = " + str(num_false)
        try:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations, filter_predicate=filter_predicate)
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.PRECONDITION_FAILED

        # Run patch operations with correct filter
        filter_predicate = "from root where root.number = " + str(item.get("number"))
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations,
                                                          filter_predicate=filter_predicate)
        # Verify results from patch operations
        assert patched_item.get("color") is None
        assert patched_item.get("prop") is None
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

    # Temporarily commenting analytical storage tests until emulator support comes.
    #
    # async def test_create_container_with_analytical_store_off(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.database_for_test
    #     collection_id = 'test_create_container_with_analytical_store_off_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container(id=collection_id,
    #                                                      indexing_policy=collection_indexing_policy,
    #                                                      partition_key=PartitionKey(path="/pk", kind="Hash"), 
    #                                                      response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key not in properties or properties[ttl_key] == None)

    # def test_create_container_with_analytical_store_on(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.database_for_test
    #     collection_id = 'test_create_container_with_analytical_store_on_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container(id=collection_id,
    #                                                      analytical_storage_ttl=-1,
    #                                                      indexing_policy=collection_indexing_policy,
    #                                                      partition_key=PartitionKey(path="/pk", kind="Hash"), 
    #                                                      response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    # def test_create_container_if_not_exists_with_analytical_store_on(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     # first, try when we know the container doesn't exist.
    #     created_db = self.database_for_test
    #     collection_id = 'test_create_container_if_not_exists_with_analytical_store_on_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container_if_not_exists(id=collection_id,
    #                                                                    analytical_storage_ttl=-1,
    #                                                                    indexing_policy=collection_indexing_policy,
    #                                                                    partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                                    response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    #     # next, try when we know the container DOES exist. This way both code paths are tested.
    #     created_collection = created_db.create_container_if_not_exists(id=collection_id,
    #                                                                    analytical_storage_ttl=-1,
    #                                                                    indexing_policy=collection_indexing_policy,
    #                                                                    partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                                    response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    async def test_priority_level_async(self):
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        priority_headers = []

        # mock execute function to check if priority level set in headers

        async def priority_mock_execute_function(function, *args, **kwargs):
            if args:
                priority_headers.append(args[4].headers[HttpHeaders.PriorityLevel]
                                              if HttpHeaders.PriorityLevel in args[4].headers else '')
            return await self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility_async.ExecuteFunctionAsync = priority_mock_execute_function
        # upsert item with high priority
        await created_container.upsert_item(body=item1, priority="High")
        # check if the priority level was passed
        assert priority_headers[-1] == "High"
        # upsert item with low priority
        await created_container.upsert_item(body=item2, priority="Low")
        # check that headers passed low priority
        assert priority_headers[-1] == "Low"
        # Repeat for read operations
        item1_read = await created_container.read_item("item1", "pk1", priority="High")
        assert priority_headers[-1] == "High"
        item2_read = await created_container.read_item("item2", "pk2", priority="Low")
        assert priority_headers[-1] == "Low"
        # repeat for query
        query = [doc async for doc in created_container.query_items("Select * from c",
                                                                    partition_key="pk1", priority="High")]

        assert priority_headers[-1] == "High"

        # Negative Test: Verify that if we send a value other than High or Low that it will not set the header value
        # and result in bad request
        try:
            item2_read = await created_container.read_item("item2", "pk2", priority="Medium")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction

    async def _mock_execute_function(self, function, *args, **kwargs):
        if HttpHeaders.PartitionKey in args[4].headers:
            self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey])
        return await self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    unittest.main()
