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
import urllib2

from windowsazure.storage import *
from windowsazure.storage.storageclient import _StorageClient
from windowsazure.storage import (_update_storage_blob_header,
                                convert_block_list_to_xml, convert_xml_to_block_list) 
from windowsazure import (validate_length, validate_values, validate_not_none, Feed, _Request, 
                                convert_xml_to_feeds, to_right_type, 
                                _get_request_body, _update_request_uri_query, get_host, 
                                _dont_fail_on_exist, _dont_fail_not_exist, HTTPError, 
                                WindowsAzureError, _parse_response, _Request, convert_class_to_xml, 
                                _parse_response_for_dict, _parse_response_for_dict_prefix, 
                                _parse_response_for_dict_filter, _parse_response_for_dict_special, 
                                BLOB_SERVICE, QUEUE_SERVICE, TABLE_SERVICE, SERVICE_BUS_SERVICE)

class CloudBlobClient(_StorageClient):
    '''
    This is the main class managing Blob resources.
    account_name: your storage account name, required for all operations.
    account_key: your storage account key, required for all operations.
    '''

    def list_containers(self, prefix=None, marker=None, maxresults=None, include=None):
        '''
        The List Containers operation returns a list of the containers under the specified account.
        
        prefix: Optional. A string value that identifies the portion of the list to be returned 
                with the next list operation. 
        marker: Optional. A string value that identifies the portion of the list to be returned 
                with the next list operation.
        maxresults: Optional. Specifies the maximum number of containers to return. 
        include: Optional. Include this parameter to specify that the container's metadata be 
                returned as part of the response body.
        '''
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?comp=list'
        request.query = [
            ('prefix', to_right_type(prefix)),
            ('marker', to_right_type(marker)),
            ('maxresults', to_right_type(maxresults)),
            ('include', to_right_type(include))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, ContainerEnumResults)

    def create_container(self, container_name, x_ms_meta_name_values=None, x_ms_blob_public_access=None, fail_on_exist=False):
        '''
        Creates a new container under the specified account. If the container with the same name 
        already exists, the operation fails.
        
        x_ms_meta_name_values: Optional. A dict with name_value pairs to associate with the 
                container as metadata. Example:{'Category':'test'}
        x_ms_blob_public_access: Optional. Possible values include: container, blob.
        fail_on_exist: specify whether throw exception when container exists.
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container'
        request.header = [
            ('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values)),
            ('x-ms-blob-public-access', to_right_type(x_ms_blob_public_access))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
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

    def get_container_properties(self, container_name):
        '''
        Returns all user-defined metadata and system properties for the specified container.
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return _parse_response_for_dict(self)

    def get_container_metadata(self, container_name):
        '''
        Returns all user-defined metadata for the specified container. The metadata will be 
        in 'x_ms_meta_(name)' property of return object. Example: x_ms_meta_category.
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container&comp=metadata'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return _parse_response_for_dict(self)

    def set_container_metadata(self, container_name, x_ms_meta_name_values=None):
        '''
        Sets one or more user-defined name-value pairs for the specified container.
        
        x_ms_meta_name_values: A dict containing name, value for metadata. Example: {'category':'test'}
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container&comp=metadata'
        request.header = [('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def get_container_acl(self, container_name):
        '''
        Gets the permissions for the specified container.
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container&comp=acl'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, SignedIdentifiers)

    def set_container_acl(self, container_name, signed_identifiers=None, x_ms_blob_public_access=None):
        '''
        Sets the permissions for the specified container.
        
        x_ms_blob_public_access: Optional. Possible values include 'container' and 'blob'. 
        signed_identifiers: SignedIdentifers instance
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container&comp=acl'
        request.header = [('x-ms-blob-public-access', to_right_type(x_ms_blob_public_access))]
        request.body = _get_request_body(convert_class_to_xml(signed_identifiers))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def delete_container(self, container_name, fail_not_exist=False):
        '''
        Marks the specified container for deletion.
        
        fail_not_exist: specify whether throw exception when container doesn't exist.
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'DELETE'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
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

    def list_blobs(self, container_name):
        '''
        Returns the list of blobs under the specified container.
        '''
        validate_not_none('container-name', container_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '?restype=container&comp=list'
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, BlobEnumResults)

    def set_blob_properties(self, storage_service_properties=None, x_ms_blob_cache_control=None, x_ms_blob_content_type=None, x_ms_blob_content_md5=None, x_ms_blob_content_encoding=None, x_ms_blob_content_language=None, x_ms_lease_id=None):
        '''
        Sets system properties on the blob.
        
        storage_service_properties: a StorageServiceProperties object.
        x_ms_blob_cache_control: Optional. Modifies the cache control string for the blob. 
        x_ms_blob_content_type: Optional. Sets the blob's content type. 
        x_ms_blob_content_md5: Optional. Sets the blob's MD5 hash.
        x_ms_blob_content_encoding: Optional. Sets the blob's content encoding.
        x_ms_blob_content_language: Optional. Sets the blob's content language.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?restype=service&comp=properties'
        request.header = [
            ('x-ms-blob-cache-control', to_right_type(x_ms_blob_cache_control)),
            ('x-ms-blob-content-type', to_right_type(x_ms_blob_content_type)),
            ('x-ms-blob-content-md5', to_right_type(x_ms_blob_content_md5)),
            ('x-ms-blob-content-encoding', to_right_type(x_ms_blob_content_encoding)),
            ('x-ms-blob-content-language', to_right_type(x_ms_blob_content_language)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id))
            ]
        request.body = _get_request_body(convert_class_to_xml(storage_service_properties))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def get_blob_properties(self, x_ms_lease_id=None):
        '''
        Returns all user-defined metadata, standard HTTP properties, and system properties for the blob.
        
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/?restype=service&comp=properties'
        request.header = [('x-ms-lease-id', to_right_type(x_ms_lease_id))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, StorageServiceProperties)

    def put_blob(self, container_name, blob_name, blob, x_ms_blob_type, content_encoding=None, content_language=None, content_m_d5=None, cache_control=None, x_ms_blob_content_type=None, x_ms_blob_content_encoding=None, x_ms_blob_content_language=None, x_ms_blob_content_md5=None, x_ms_blob_cache_control=None, x_ms_meta_name_values=None, x_ms_lease_id=None, x_ms_blob_content_length=None, x_ms_blob_sequence_number=None):
        '''
        Creates a new block blob or page blob, or updates the content of an existing block blob. 
        
        container_name: the name of container to put the blob
        blob_name: the name of blob
        x_ms_blob_type: Required. Could be BlockBlob or PageBlob
        x_ms_meta_name_values: A dict containing name, value for metadata.
        x_ms_lease_id: Required if the blob has an active lease.
        blob: the content of blob.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        validate_not_none('binary:blob', blob)
        validate_not_none('x-ms-blob-type', x_ms_blob_type)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + ''
        request.header = [
            ('x-ms-blob-type', to_right_type(x_ms_blob_type)),
            ('Content-Encoding', to_right_type(content_encoding)),
            ('Content-Language', to_right_type(content_language)),
            ('Content-MD5', to_right_type(content_m_d5)),
            ('Cache-Control', to_right_type(cache_control)),
            ('x-ms-blob-content-type', to_right_type(x_ms_blob_content_type)),
            ('x-ms-blob-content-encoding', to_right_type(x_ms_blob_content_encoding)),
            ('x-ms-blob-content-language', to_right_type(x_ms_blob_content_language)),
            ('x-ms-blob-content-md5', to_right_type(x_ms_blob_content_md5)),
            ('x-ms-blob-cache-control', to_right_type(x_ms_blob_cache_control)),
            ('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id)),
            ('x-ms-blob-content-length', to_right_type(x_ms_blob_content_length)),
            ('x-ms-blob-sequence-number', to_right_type(x_ms_blob_sequence_number))
            ]
        request.body = _get_request_body(blob)
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def get_blob(self, container_name, blob_name, snapshot=None, x_ms_range=None, x_ms_lease_id=None, x_ms_range_get_content_md5=None):
        '''
        Reads or downloads a blob from the system, including its metadata and properties. 
        
        container_name: the name of container to get the blob
        blob_name: the name of blob
        x_ms_range: Optional. Return only the bytes of the blob in the specified range.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + ''
        request.header = [
            ('x-ms-range', to_right_type(x_ms_range)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id)),
            ('x-ms-range-get-content-md5', to_right_type(x_ms_range_get_content_md5))
            ]
        request.query = [('snapshot', to_right_type(snapshot))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return respbody

    def get_blob_metadata(self, container_name, blob_name, snapshot=None, x_ms_lease_id=None):
        '''
        Returns all user-defined metadata for the specified blob or snapshot.
        
        container_name: the name of container containing the blob.
        blob_name: the name of blob to get metadata.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=metadata'
        request.header = [('x-ms-lease-id', to_right_type(x_ms_lease_id))]
        request.query = [('snapshot', to_right_type(snapshot))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return _parse_response_for_dict(self)

    def set_blob_metadata(self, container_name, blob_name, x_ms_meta_name_values=None, x_ms_lease_id=None):
        '''
        Sets user-defined metadata for the specified blob as one or more name-value pairs.
        
        container_name: the name of container containing the blob
        blob_name: the name of blob
        x_ms_meta_name_values: Dict containing name and value pairs.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=metadata'
        request.header = [
            ('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def lease_blob(self, container_name, blob_name, x_ms_lease_action, x_ms_lease_id=None):
        '''
        Establishes and manages a one-minute lock on a blob for write operations.
        
        container_name: the name of container.
        blob_name: the name of blob
        x_ms_lease_id: Any GUID format string
        x_ms_lease_action: Required. Possible values: acquire|renew|release|break
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        validate_not_none('x-ms-lease-action', x_ms_lease_action)
        validate_values('x-ms-lease-action', to_right_type(x_ms_lease_action), 'acquire|renew|release|break')
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=lease'
        request.header = [
            ('x-ms-lease-id', to_right_type(x_ms_lease_id)),
            ('x-ms-lease-action', to_right_type(x_ms_lease_action))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return _parse_response_for_dict_filter(self, filter=['x-ms-lease-id'])

    def snapshot_blob(self, container_name, blob_name, x_ms_meta_name_values=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, x_ms_lease_id=None):
        '''
        Creates a read-only snapshot of a blob.
        
        container_name: the name of container.
        blob_name: the name of blob
        x_ms_meta_name_values: Optional. Dict containing name and value pairs.
        if_modified_since: Optional. Datetime string.
        if_unmodified_since: DateTime string.
        if_match: Optional. snapshot the blob only if its ETag value matches the value specified. 
        if_none_match: Optional. An ETag value
        x_ms_lease_id: Optional. If this header is specified, the operation will be performed 
                  only if both of the following conditions are met. 
        			1. The blob's lease is currently active
        			2. The lease ID specified in the request matches that of the blob.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=snapshot'
        request.header = [
            ('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values)),
            ('If-Modified-Since', to_right_type(if_modified_since)),
            ('If-Unmodified-Since', to_right_type(if_unmodified_since)),
            ('If-Match', to_right_type(if_match)),
            ('If-None-Match', to_right_type(if_none_match)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def copy_blob(self, container_name, blob_name, x_ms_copy_source, x_ms_meta_name_values=None, x_ms_source_if_modified_since=None, x_ms_source_if_unmodified_since=None, x_ms_source_if_match=None, x_ms_source_if_none_match=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, x_ms_lease_id=None, x_ms_source_lease_id=None):
        '''
        Copies a blob to a destination within the storage account. 
        
        container_name: the name of container.
        blob_name: the name of blob
        x_ms_copy_source: the blob to be copied. Should be absolute path format.
        x_ms_meta_name_values: Optional. Dict containing name and value pairs.
        x_ms_source_if_modified_since: Optional. An ETag value. Specify this conditional 
        		header to copy the source blob only if its ETag matches the value specified.
        x_ms_source_if_unmodified_since: Optional. An ETag value. Specify this conditional 
        		header to copy the blob only if its ETag does not match the value specified.
        x_ms_source_if_match: Optional. A DateTime value. Specify this conditional header to copy
        		the blob only if the source blob has been modified since the specified date/time.
        x_ms_source_if_none_match: Optional. An ETag value. Specify this conditional header to 
        		copy the source blob only if its ETag matches the value specified.
        if_modified_since: Optional. Datetime string.
        if_unmodified_since: DateTime string.
        if_match: Optional. snapshot the blob only if its ETag value matches the value specified. 
        if_none_match: Optional. An ETag value
        x_ms_lease_id: Optional. If this header is specified, the operation will be performed 
        		only if both of the following conditions are met. 
        		1. The blob's lease is currently active
        		2. The lease ID specified in the request matches that of the blob.
        x-ms-meta-name-values:  a dict containing name, value for metadata.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        validate_not_none('x-ms-copy-source', x_ms_copy_source)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + ''
        request.header = [
            ('x-ms-copy-source', to_right_type(x_ms_copy_source)),
            ('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values)),
            ('x-ms-source-if-modified-since', to_right_type(x_ms_source_if_modified_since)),
            ('x-ms-source-if-unmodified-since', to_right_type(x_ms_source_if_unmodified_since)),
            ('x-ms-source-if-match', to_right_type(x_ms_source_if_match)),
            ('x-ms-source-if-none-match', to_right_type(x_ms_source_if_none_match)),
            ('If-Modified-Since', to_right_type(if_modified_since)),
            ('If-Unmodified-Since', to_right_type(if_unmodified_since)),
            ('If-Match', to_right_type(if_match)),
            ('If-None-Match', to_right_type(if_none_match)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id)),
            ('x-ms-source-lease-id', to_right_type(x_ms_source_lease_id))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def delete_blob(self, container_name, blob_name, snapshot=None, x_ms_copy_source=None, x_ms_meta_name_values=None, x_ms_source_if_modified_since=None, x_ms_source_if_unmodified_since=None, x_ms_source_if_match=None, x_ms_source_if_none_match=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, x_ms_lease_id=None, x_ms_source_lease_id=None):
        '''
        Marks the specified blob or snapshot for deletion. The blob is later deleted 
        during garbage collection.
        
        container_name: the name of container.
        blob_name: the name of blob
        x_ms_copy_source: the blob to be copied. Should be absolute path format.
        x_ms_meta_name_values: Optional. Dict containing name and value pairs.
        x_ms_source_if_modified_since: Optional. An ETag value. Specify this conditional 
        		header to copy the source blob only if its ETag matches the value specified.
        x_ms_source_if_unmodified_since: Optional. An ETag value. Specify this conditional 
        		header to copy the blob only if its ETag does not match the value specified.
        x_ms_source_if_match: Optional. A DateTime value. Specify this conditional header to copy
        		the blob only if the source blob has been modified since the specified date/time.
        x_ms_source_if_none_match: Optional. An ETag value. Specify this conditional header to 
        		copy the source blob only if its ETag matches the value specified.
        if_modified_since: Optional. Datetime string.
        if_unmodified_since: DateTime string.
        if_match: Optional. snapshot the blob only if its ETag value matches the value specified. 
        if_none_match: Optional. An ETag value
        x_ms_lease_id: Optional. If this header is specified, the operation will be performed 
        		only if both of the following conditions are met. 
        		1. The blob's lease is currently active
        		2. The lease ID specified in the request matches that of the blob.
        x-ms-meta-name-values:  a dict containing name, value for metadata.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        request = _Request()
        request.method = 'DELETE'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + ''
        request.header = [
            ('x-ms-copy-source', to_right_type(x_ms_copy_source)),
            ('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values)),
            ('x-ms-source-if-modified-since', to_right_type(x_ms_source_if_modified_since)),
            ('x-ms-source-if-unmodified-since', to_right_type(x_ms_source_if_unmodified_since)),
            ('x-ms-source-if-match', to_right_type(x_ms_source_if_match)),
            ('x-ms-source-if-none-match', to_right_type(x_ms_source_if_none_match)),
            ('If-Modified-Since', to_right_type(if_modified_since)),
            ('If-Unmodified-Since', to_right_type(if_unmodified_since)),
            ('If-Match', to_right_type(if_match)),
            ('If-None-Match', to_right_type(if_none_match)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id)),
            ('x-ms-source-lease-id', to_right_type(x_ms_source_lease_id))
            ]
        request.query = [('snapshot', to_right_type(snapshot))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def put_block(self, container_name, blob_name, block, blockid, content_m_d5=None, x_ms_lease_id=None):
        '''
        Creates a new block to be committed as part of a blob.
        
        container_name: the name of container.
        blob_name: the name of blob
        content_md5: Optional. An MD5 hash of the block content. This hash is used to verify
        		the integrity of the blob during transport. When this header is specified, 
        		the storage service checks the hash that has arrived with the one that was sent.
        x_ms_lease_id: Required if the blob has an active lease. To perform this operation on
        		a blob with an active lease, specify the valid lease ID for this header.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        validate_not_none('binary:block', block)
        validate_not_none('blockid', blockid)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=block'
        request.header = [
            ('Content-MD5', to_right_type(content_m_d5)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id))
            ]
        request.query = [('blockid', base64.b64encode(to_right_type(blockid)))]
        request.body = _get_request_body(block)
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def put_block_list(self, container_name, blob_name, block_list, content_m_d5=None, x_ms_blob_cache_control=None, x_ms_blob_content_type=None, x_ms_blob_content_encoding=None, x_ms_blob_content_language=None, x_ms_blob_content_md5=None, x_ms_meta_name_values=None, x_ms_lease_id=None):
        '''
        Writes a blob by specifying the list of block IDs that make up the blob. In order to 
        be written as part of a blob, a block must have been successfully written to the server
        in a prior Put Block (REST API) operation.
        
        container_name: the name of container.
        blob_name: the name of blob
        x_ms_meta_name_values: Optional. Dict containing name and value pairs.
        x_ms_blob_cache_control: Optional. Sets the blob's cache control. If specified, this 
        		property is stored with the blob and returned with a read request.
        x_ms_blob_content_type: Optional. Sets the blob's content type. If specified, this 
        		property is stored with the blob and returned with a read request.
        x_ms_blob_content_encoding: Optional. Sets the blob's content encoding. If specified,
        		this property is stored with the blob and returned with a read request.
        x_ms_blob_content_language: Optional. Set the blob's content language. If specified, 
        		this property is stored with the blob and returned with a read request. 
        x_ms_blob_content_md5: Optional. An MD5 hash of the blob content. Note that this hash
        		is not validated, as the hashes for the individual blocks were validated when
        		each was uploaded.
        content_md5: Optional. An MD5 hash of the block content. This hash is used to verify
        		the integrity of the blob during transport. When this header is specified, 
        		the storage service checks the hash that has arrived with the one that was sent.
        x_ms_lease_id: Required if the blob has an active lease. To perform this operation on
        		a blob with an active lease, specify the valid lease ID for this header.
        x-ms-meta-name-values:  a dict containing name, value for metadata.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        validate_not_none('class:block_list', block_list)
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=blocklist'
        request.header = [
            ('Content-MD5', to_right_type(content_m_d5)),
            ('x-ms-blob-cache-control', to_right_type(x_ms_blob_cache_control)),
            ('x-ms-blob-content-type', to_right_type(x_ms_blob_content_type)),
            ('x-ms-blob-content-encoding', to_right_type(x_ms_blob_content_encoding)),
            ('x-ms-blob-content-language', to_right_type(x_ms_blob_content_language)),
            ('x-ms-blob-content-md5', to_right_type(x_ms_blob_content_md5)),
            ('x-ms-meta-name-values', to_right_type(x_ms_meta_name_values)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id))
            ]
        request.body = _get_request_body(convert_block_list_to_xml(block_list))
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def get_block_list(self, container_name, blob_name, snapshot=None, blocklisttype=None, x_ms_lease_id=None):
        '''
        Retrieves the list of blocks that have been uploaded as part of a block blob.
        
        container_name: the name of container.
        blob_name: the name of blob
        snapshot: Optional. Datetime to determine the time to retrieve the blocks.
        blocklisttype: Specifies whether to return the list of committed blocks, the 
        		list of uncommitted blocks, or both lists together. Valid values are 
        		committed, uncommitted, or all.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=blocklist'
        request.header = [('x-ms-lease-id', to_right_type(x_ms_lease_id))]
        request.query = [
            ('snapshot', to_right_type(snapshot)),
            ('blocklisttype', to_right_type(blocklisttype))
            ]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return convert_xml_to_block_list(respbody)

    def put_page(self, container_name, blob_name, page, x_ms_range, x_ms_page_write, content_m_d5=None, x_ms_lease_id=None, x_ms_if_sequence_number_lte=None, x_ms_if_sequence_number_lt=None, x_ms_if_sequence_number_eq=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None):
        '''
        Writes a range of pages to a page blob.
        
        container_name: the name of container.
        blob_name: the name of blob
        x_ms_range: Required. Specifies the range of bytes to be written as a page. Both the start
        		and end of the range must be specified. Must be in format: bytes=startByte-endByte.
        		Given that pages must be aligned with 512-byte boundaries, the start offset must be
        		a modulus of 512 and the end offset must be a modulus of 512-1. Examples of valid
        		byte ranges are 0-511, 512-1023, etc.
        x_ms_page_write: Required. You may specify one of the following options: 
        		1. Update: Writes the bytes specified by the request body into the specified range. 
        		   The Range and Content-Length headers must match to perform the update.
        		2. Clear: Clears the specified range and releases the space used in storage for 
        		   that range. To clear a range, set the Content-Length header to zero, and the Range
        		   header to a value that indicates the range to clear, up to maximum blob size.
        x_ms_lease_id: Required if the blob has an active lease. To perform this operation on a blob
        		 with an active lease, specify the valid lease ID for this header.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        validate_not_none('binary:page', page)
        validate_not_none('x-ms-range', x_ms_range)
        validate_not_none('x-ms-page-write', x_ms_page_write)
        validate_values('x-ms-page-write', to_right_type(x_ms_page_write), 'update|clear')
        request = _Request()
        request.method = 'PUT'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=page'
        request.header = [
            ('x-ms-range', to_right_type(x_ms_range)),
            ('Content-MD5', to_right_type(content_m_d5)),
            ('x-ms-page-write', to_right_type(x_ms_page_write)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id)),
            ('x-ms-if-sequence-number-lte', to_right_type(x_ms_if_sequence_number_lte)),
            ('x-ms-if-sequence-number-lt', to_right_type(x_ms_if_sequence_number_lt)),
            ('x-ms-if-sequence-number-eq', to_right_type(x_ms_if_sequence_number_eq)),
            ('If-Modified-Since', to_right_type(if_modified_since)),
            ('If-Unmodified-Since', to_right_type(if_unmodified_since)),
            ('If-Match', to_right_type(if_match)),
            ('If-None-Match', to_right_type(if_none_match))
            ]
        request.body = _get_request_body(page)
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

    def get_page_ranges(self, container_name, blob_name, snapshot=None, range=None, x_ms_range=None, x_ms_lease_id=None):
        '''
        Retrieves the page ranges for a blob.
        
        container_name: the name of container.
        blob_name: the name of blob
        _ms_range: Optional. Specifies the range of bytes to be written as a page. Both the start
        		and end of the range must be specified. Must be in format: bytes=startByte-endByte.
        		Given that pages must be aligned with 512-byte boundaries, the start offset must be
        		a modulus of 512 and the end offset must be a modulus of 512-1. Examples of valid
        		byte ranges are 0-511, 512-1023, etc.
        x_ms_lease_id: Required if the blob has an active lease. To perform this operation on a blob
        		 with an active lease, specify the valid lease ID for this header.
        '''
        validate_not_none('container-name', container_name)
        validate_not_none('blob-name', blob_name)
        request = _Request()
        request.method = 'GET'
        request.host = get_host(BLOB_SERVICE, self.account_name, self.use_local_storage)
        request.uri = '/' + to_right_type(container_name) + '/' + to_right_type(blob_name) + '?comp=pagelist'
        request.header = [
            ('Range', to_right_type(range)),
            ('x-ms-range', to_right_type(x_ms_range)),
            ('x-ms-lease-id', to_right_type(x_ms_lease_id))
            ]
        request.query = [('snapshot', to_right_type(snapshot))]
        request.uri, request.query = _update_request_uri_query(request, self.use_local_storage)
        request.header = _update_storage_blob_header(request, self.account_name, self.account_key)
        respbody = self._perform_request(request)

        return self._parse_response(respbody, PageList)


