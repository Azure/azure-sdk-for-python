#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. 
#
# This source code is subject to terms and conditions of the Apache License, 
# Version 2.0. A copy of the license can be found in the License.html file at 
# the root of this distribution. If you cannot locate the Apache License, 
# Version 2.0, please send an email to vspython@microsoft.com. By using this 
# source code in any fashion, you are agreeing to be bound by the terms of the 
# Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#------------------------------------------------------------------------------
import base64
import os
import urllib2

from windowsazure.storage import *
from windowsazure.storage.storageclient import _StorageClient
from windowsazure.storage import (_update_storage_table_header, 
                                convert_table_to_xml, convert_xml_to_table, 
                                convert_entity_to_xml, convert_xml_to_entity)
from windowsazure.http.batchclient import _BatchClient
from windowsazure import (validate_length, validate_values, validate_not_none, Feed, _Request, 
                                convert_xml_to_feeds, to_right_type, 
                                _get_request_body, _update_request_uri_query, get_host, 
                                _dont_fail_on_exist, _dont_fail_not_exist, HTTPError, 
                                WindowsAzureError, _parse_response, _Request, convert_class_to_xml, 
                                _parse_response_for_dict, _parse_response_for_dict_prefix, 
                                _parse_response_for_dict_filter, _parse_response_for_dict_special, 
                                BLOB_SERVICE, QUEUE_SERVICE, TABLE_SERVICE, SERVICE_BUS_SERVICE)

class CloudTableClient(_StorageClient):
    '''
    This is the main class managing Table resources.
    account_name: your storage account name, required for all operations.
    account_key: your storage account key, required for all operations.
    '''

    def begin_batch(self):
        if self._batchclient is None:
            self._batchclient = _BatchClient(service_instance=self, account_key=self.account_key, account_name=self.account_name)
        return self._batchclient.begin_batch()

    def commit_batch(self):
        try:
            ret = self._batchclient.commit_batch()
        finally:
            self._batchclient = None
        return ret

    def cancel_batch(self):
        self._batchclient = None
    def get_table_service_properties(self):
        '''
        Gets the properties of a storage account's Table service, including Windows Azure
        Storage Analytics.
        '''
        request = _Request()
        request.method = 'GET'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?restype=service&comp=properties'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, StorageServiceProperties)

    def set_table_service_properties(self, storage_service_properties):
        '''
        Sets the properties of a storage account's Table Service, including Windows Azure Storage Analytics.
        
        storage_service_properties: a StorageServiceProperties object.
        '''
        validate_not_none('class:storage_service_properties', storage_service_properties)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?restype=service&comp=properties'
        request.body = _get_request_body(convert_class_to_xml(storage_service_properties))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return _parse_response_for_dict(self)

    def query_tables(self):
        '''
        Returns a list of tables under the specified account.
        '''
        request = _Request()
        request.method = 'GET'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/Tables'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return convert_xml_to_feeds(respbody, convert_xml_to_table)

    def create_table(self, table, fail_on_exist=False):
        '''
        Creates a new table in the storage account.
        
        table: name of the table to create.
        fail_on_exist: specify whether throw exception when table exists.
        '''
        validate_not_none('feed:table', table)
        request = _Request()
        request.method = 'POST'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/Tables'
        request.body = _get_request_body(convert_table_to_xml(table))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        if not fail_on_exist:
            try:
                self._perform_request(request)
                return True
            except WindowsAzureError as e:
                _dont_fail_on_exist(e)
                return False
        else:
            self._perform_request(request)
            return True

    def delete_table(self, table_name, fail_not_exist=False):
        '''
        table_name: name of the table to delete. 
        
        fail_not_exist: specify whether throw exception when table doesn't exist.
        '''
        validate_not_none('table-name', table_name)
        request = _Request()
        request.method = 'DELETE'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/Tables(\'' + to_right_type(table_name) + '\')'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        if not fail_not_exist:
            try:
                self._perform_request(request)
                return True
            except WindowsAzureError as e:
                _dont_fail_not_exist(e)
                return False
        else:
            self._perform_request(request)
            return True

    def get_entity(self, table_name, partition_key, row_key, comma_separated_property_names=''):
        '''
        Get an entity in a table and includes the $select options. 
        
        partition_key: PartitionKey of the entity.
        row_key: RowKey of the entity.
        comma_separated_property_names: the property names to select.
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('partition-key', partition_key)
        validate_not_none('row-key', row_key)
        validate_not_none('comma-separated-property-names', comma_separated_property_names)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + '(PartitionKey=\'' + to_right_type(partition_key) + '\',RowKey=\'' + to_right_type(row_key) + '\')?$select=' + to_right_type(comma_separated_property_names) + ''
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return convert_xml_to_entity(respbody)

    def query_entities(self, table_name, query_expression='', comma_separated_property_names=''):
        '''
        Get entities in a table and includes the $filter and $select options. 
        
        query_expression: the query to get entities.
        comma_separated_property_names: the property names to select.
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('query-expression', query_expression)
        validate_not_none('comma-separated-property-names', comma_separated_property_names)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + '()?$filter=' + to_right_type(query_expression) + '&$select=' + to_right_type(comma_separated_property_names) + ''
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return convert_xml_to_feeds(respbody, convert_xml_to_entity)

    def insert_entity(self, table_name, entity, content_type='application/atom+xml'):
        '''
        Inserts a new entity into a table.
        
        entity: Required. The entity object to insert. Could be a dict format or entity object.
        Content-Type: this is required and has to be set to application/atom+xml
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('feed:entity', entity)
        validate_not_none('Content-Type', content_type)
        validate_values('Content-Type', to_right_type(content_type), 'application/atom+xml|')
        request = _Request()
        request.method = 'POST'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + ''
        request.header = [('Content-Type', to_right_type(content_type))]
        request.body = _get_request_body(convert_entity_to_xml(entity))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def update_entity(self, table_name, partition_key, row_key, entity, content_type='application/atom+xml', if_match='*'):
        '''
        Updates an existing entity in a table. The Update Entity operation replaces the entire 
        entity and can be used to remove properties.
        
        entity: Required. The entity object to insert. Could be a dict format or entity object.
        partition_key: PartitionKey of the entity.
        row_key: RowKey of the entity.
        Content-Type: this is required and has to be set to application/atom+xml
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('partition-key', partition_key)
        validate_not_none('row-key', row_key)
        validate_not_none('feed:entity', entity)
        validate_not_none('Content-Type', content_type)
        validate_values('Content-Type', to_right_type(content_type), 'application/atom+xml|')
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + '(PartitionKey=\'' + to_right_type(partition_key) + '\',RowKey=\'' + to_right_type(row_key) + '\')'
        request.header = [
            ('Content-Type', to_right_type(content_type)),
            ('If-Match', to_right_type(if_match))
            ]
        request.body = _get_request_body(convert_entity_to_xml(entity))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def merge_entity(self, table_name, partition_key, row_key, entity, content_type='application/atom+xml', if_match='*'):
        '''
        Updates an existing entity by updating the entity's properties. This operation does 
        not replace the existing entity, as the Update Entity operation does.
        
        entity: Required. The entity object to insert. Could be a dict format or entity object.
        partition_key: PartitionKey of the entity.
        row_key: RowKey of the entity.
        Content-Type: this is required and has to be set to application/atom+xml
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('partition-key', partition_key)
        validate_not_none('row-key', row_key)
        validate_not_none('feed:entity', entity)
        validate_not_none('Content-Type', content_type)
        validate_values('Content-Type', to_right_type(content_type), 'application/atom+xml|')
        request = _Request()
        request.method = 'MERGE'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + '(PartitionKey=\'' + to_right_type(partition_key) + '\',RowKey=\'' + to_right_type(row_key) + '\')'
        request.header = [
            ('Content-Type', to_right_type(content_type)),
            ('If-Match', to_right_type(if_match))
            ]
        request.body = _get_request_body(convert_entity_to_xml(entity))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def delete_entity(self, table_name, partition_key, row_key, content_type='application/atom+xml', if_match='*'):
        '''
        Deletes an existing entity in a table.
        
        partition_key: PartitionKey of the entity.
        row_key: RowKey of the entity.
        if_match: Required. Specifies the condition for which the delete should be performed.
        		To force an unconditional delete, set If-Match to the wildcard character (*). 
        Content-Type: this is required and has to be set to application/atom+xml
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('partition-key', partition_key)
        validate_not_none('row-key', row_key)
        validate_not_none('Content-Type', content_type)
        validate_values('Content-Type', to_right_type(content_type), 'application/atom+xml|')
        validate_not_none('If-Match', if_match)
        request = _Request()
        request.method = 'DELETE'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + '(PartitionKey=\'' + to_right_type(partition_key) + '\',RowKey=\'' + to_right_type(row_key) + '\')'
        request.header = [
            ('Content-Type', to_right_type(content_type)),
            ('If-Match', to_right_type(if_match))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def insert_or_replace_entity(self, table_name, partition_key, row_key, entity, content_type='application/atom+xml', if_match='*'):
        '''
        Replaces an existing entity or inserts a new entity if it does not exist in the table. 
        Because this operation can insert or update an entity, it is also known as an "upsert"
        operation.
        
        entity: Required. The entity object to insert. Could be a dict format or entity object.
        partition_key: PartitionKey of the entity.
        row_key: RowKey of the entity.
        Content-Type: this is required and has to be set to application/atom+xml
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('partition-key', partition_key)
        validate_not_none('row-key', row_key)
        validate_not_none('feed:entity', entity)
        validate_not_none('Content-Type', content_type)
        validate_values('Content-Type', to_right_type(content_type), 'application/atom+xml|')
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + '(PartitionKey=\'' + to_right_type(partition_key) + '\',RowKey=\'' + to_right_type(row_key) + '\')'
        request.header = [
            ('Content-Type', to_right_type(content_type)),
            ('If-Match', to_right_type(if_match))
            ]
        request.body = _get_request_body(convert_entity_to_xml(entity))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def insert_or_merge_entity(self, table_name, partition_key, row_key, entity, content_type='application/atom+xml', if_match='*'):
        '''
        Merges an existing entity or inserts a new entity if it does not exist in the table. 
        Because this operation can insert or update an entity, it is also known as an "upsert"
        operation..
        
        entity: Required. The entity object to insert. Could be a dict format or entity object.
        partition_key: PartitionKey of the entity.
        row_key: RowKey of the entity.
        Content-Type: this is required and has to be set to application/atom+xml
        '''
        validate_not_none('table-name', table_name)
        validate_not_none('partition-key', partition_key)
        validate_not_none('row-key', row_key)
        validate_not_none('feed:entity', entity)
        validate_not_none('Content-Type', content_type)
        validate_values('Content-Type', to_right_type(content_type), 'application/atom+xml|')
        request = _Request()
        request.method = 'MERGE'
        request.host = get_host(TABLE_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(table_name) + '(PartitionKey=\'' + to_right_type(partition_key) + '\',RowKey=\'' + to_right_type(row_key) + '\')'
        request.header = [
            ('Content-Type', to_right_type(content_type)),
            ('If-Match', to_right_type(if_match))
            ]
        request.body = _get_request_body(convert_entity_to_xml(entity))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_table_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)


