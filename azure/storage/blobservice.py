#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import base64

from azure import (WindowsAzureError,
                   BLOB_SERVICE_HOST_BASE,
                   DEV_BLOB_HOST,
                   _convert_class_to_xml,
                   _dont_fail_not_exist,
                   _dont_fail_on_exist,
                   _get_request_body,
                   _int_or_none,
                   _parse_enum_results_list,
                   _parse_response,
                   _parse_response_for_dict,
                   _parse_response_for_dict_filter,
                   _parse_response_for_dict_prefix,
                   _parse_simple_list,
                   _str,
                   _str_or_none,
                   _update_request_uri_query_local_storage,
                   _validate_not_none,
                   xml_escape,
                   )
from azure.http import HTTPRequest
from azure.storage import (Container,
                           ContainerEnumResults,
                           PageList,
                           PageRange,
                           SignedIdentifiers,
                           StorageServiceProperties,
                           _convert_block_list_to_xml,
                           _convert_response_to_block_list,
                           _create_blob_result,
                           _parse_blob_enum_results_list,
                           _update_storage_blob_header,
                           )
from azure.storage.storageclient import _StorageClient

class BlobService(_StorageClient):
    '''
    This is the main class managing Blob resources.
    '''

    def __init__(self, account_name = None, account_key = None, protocol = 'https', host_base = BLOB_SERVICE_HOST_BASE, dev_host = DEV_BLOB_HOST):
        '''
        account_name: your storage account name, required for all operations.
        account_key: your storage account key, required for all operations.
        protocol: Optional. Protocol. Defaults to http.
        host_base: 
            Optional. Live host base url. Defaults to Azure url. Override this 
            for on-premise.
        dev_host: Optional. Dev host url. Defaults to localhost. 
        '''
        return super(BlobService, self).__init__(account_name, account_key, protocol, host_base, dev_host)

    def list_containers(self, prefix=None, marker=None, maxresults=None, include=None):
        '''
        The List Containers operation returns a list of the containers under 
        the specified account.
        
        prefix:
            Optional. Filters the results to return only containers whose names 
            begin with the specified prefix. 
        marker:
            Optional. A string value that identifies the portion of the list to 
            be returned with the next list operation.
        maxresults: 
            Optional. Specifies the maximum number of containers to return. 
        include:
            Optional. Include this parameter to specify that the container's 
            metadata be returned as part of the response body. set this 
            parameter to string 'metadata' to get container's metadata.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/?comp=list'
        request.query = [
            ('prefix', _str_or_none(prefix)),
            ('marker', _str_or_none(marker)),
            ('maxresults', _int_or_none(maxresults)),
            ('include', _str_or_none(include))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_enum_results_list(response, ContainerEnumResults, "Containers", Container)

    def create_container(self, container_name, x_ms_meta_name_values=None, x_ms_blob_public_access=None, fail_on_exist=False):
        '''
        Creates a new container under the specified account. If the container 
        with the same name already exists, the operation fails.
        
        container_name: Name of container to create.
        x_ms_meta_name_values:
            Optional. A dict with name_value pairs to associate with the 
            container as metadata. Example:{'Category':'test'}
        x_ms_blob_public_access: 
            Optional. Possible values include: container, blob
        fail_on_exist:
            specify whether to throw an exception when the container exists.
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container'
        request.headers = [
            ('x-ms-meta-name-values', x_ms_meta_name_values),
            ('x-ms-blob-public-access', _str_or_none(x_ms_blob_public_access))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
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
        Returns all user-defined metadata and system properties for the 
        specified container.

        container_name: Name of existing container.
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container'
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict(response)

    def get_container_metadata(self, container_name):
        '''
        Returns all user-defined metadata for the specified container. The 
        metadata will be in returned dictionary['x-ms-meta-(name)'].

        container_name: Name of existing container.
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container&comp=metadata'
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict_prefix(response, prefixes=['x-ms-meta'])

    def set_container_metadata(self, container_name, x_ms_meta_name_values=None):
        '''
        Sets one or more user-defined name-value pairs for the specified 
        container.
        
        container_name: Name of existing container.
        x_ms_meta_name_values:
            A dict containing name, value for metadata. Example: {'category':'test'}
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container&comp=metadata'
        request.headers = [('x-ms-meta-name-values', x_ms_meta_name_values)]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def get_container_acl(self, container_name):
        '''
        Gets the permissions for the specified container.

        container_name: Name of existing container.
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container&comp=acl'
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response(response, SignedIdentifiers)

    def set_container_acl(self, container_name, signed_identifiers=None, x_ms_blob_public_access=None):
        '''
        Sets the permissions for the specified container.
        
        container_name: Name of existing container.
        signed_identifiers: SignedIdentifers instance
        x_ms_blob_public_access:
            Optional. Possible values include: container, blob 
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container&comp=acl'
        request.headers = [('x-ms-blob-public-access', _str_or_none(x_ms_blob_public_access))]
        request.body = _get_request_body(_convert_class_to_xml(signed_identifiers))
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def delete_container(self, container_name, fail_not_exist=False):
        '''
        Marks the specified container for deletion.
        
        container_name: Name of container to delete.
        fail_not_exist: 
            Specify whether to throw an exception when the container doesn't exist.
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container'
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
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

    def list_blobs(self, container_name, prefix=None, marker=None, maxresults=None, include=None, delimiter=None):
        '''
        Returns the list of blobs under the specified container.

        container_name: Name of existing container.
        prefix:
            Optional. Filters the results to return only blobs whose names 
            begin with the specified prefix.
        marker: 
            Optional. A string value that identifies the portion of the list 
            to be returned with the next list operation. The operation returns 
            a marker value within the response body if the list returned was 
            not complete. The marker value may then be used in a subsequent 
            call to request the next set of list items. The marker value is 
            opaque to the client.
        maxresults:
            Optional. Specifies the maximum number of blobs to return, 
            including all BlobPrefix elements. If the request does not specify 
            maxresults or specifies a value greater than 5,000, the server will 
            return up to 5,000 items. Setting maxresults to a value less than 
            or equal to zero results in error response code 400 (Bad Request).
        include:
            Optional. Specifies one or more datasets to include in the 
            response. To specify more than one of these options on the URI,
            you must separate each option with a comma. Valid values are:
                snapshots:
                    Specifies that snapshots should be included in the 
                    enumeration. Snapshots are listed from oldest to newest in 
                    the response. 
                metadata: 
                    Specifies that blob metadata be returned in the response.
                uncommittedblobs: 
                    Specifies that blobs for which blocks have been uploaded, 
                    but which have not been committed using Put Block List 
                    (REST API), be included in the response.
                copy:
                    Version 2012-02-12 and newer. Specifies that metadata 
                    related to any current or previous Copy Blob operation 
                    should be included in the response. 
        delimiter:
            Optional. When the request includes this parameter, the operation 
            returns a BlobPrefix element in the response body that acts as a 
            placeholder for all blobs whose names begin with the same 
            substring up to the appearance of the delimiter character. The 
            delimiter may be a single character or a string.
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '?restype=container&comp=list'
        request.query = [
            ('prefix', _str_or_none(prefix)),
            ('delimiter', _str_or_none(delimiter)),
            ('marker', _str_or_none(marker)),
            ('maxresults', _int_or_none(maxresults)),
            ('include', _str_or_none(include))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_blob_enum_results_list(response)

    def set_blob_service_properties(self, storage_service_properties, timeout=None):
        '''
        Sets the properties of a storage account's Blob service, including 
        Windows Azure Storage Analytics. You can also use this operation to 
        set the default request version for all incoming requests that do not 
        have a version specified.
        
        storage_service_properties: a StorageServiceProperties object.
        timeout: Optional. The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('storage_service_properties', storage_service_properties)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/?restype=service&comp=properties'
        request.query = [('timeout', _int_or_none(timeout))]
        request.body = _get_request_body(_convert_class_to_xml(storage_service_properties))
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def get_blob_service_properties(self, timeout=None):
        '''
        Gets the properties of a storage account's Blob service, including 
        Windows Azure Storage Analytics.
        
        timeout: Optional. The timeout parameter is expressed in seconds.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/?restype=service&comp=properties'
        request.query = [('timeout', _int_or_none(timeout))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response(response, StorageServiceProperties)

    def get_blob_properties(self, container_name, blob_name, x_ms_lease_id=None):
        '''
        Returns all user-defined metadata, standard HTTP properties, and 
        system properties for the blob.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'HEAD'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + ''
        request.headers = [('x-ms-lease-id', _str_or_none(x_ms_lease_id))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict(response)

    def set_blob_properties(self, container_name, blob_name, x_ms_blob_cache_control=None, x_ms_blob_content_type=None, x_ms_blob_content_md5=None, x_ms_blob_content_encoding=None, x_ms_blob_content_language=None, x_ms_lease_id=None):
        '''
        Sets system properties on the blob.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        x_ms_blob_cache_control:
            Optional. Modifies the cache control string for the blob. 
        x_ms_blob_content_type: Optional. Sets the blob's content type. 
        x_ms_blob_content_md5: Optional. Sets the blob's MD5 hash.
        x_ms_blob_content_encoding: Optional. Sets the blob's content encoding.
        x_ms_blob_content_language: Optional. Sets the blob's content language.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=properties'
        request.headers = [
            ('x-ms-blob-cache-control', _str_or_none(x_ms_blob_cache_control)),
            ('x-ms-blob-content-type', _str_or_none(x_ms_blob_content_type)),
            ('x-ms-blob-content-md5', _str_or_none(x_ms_blob_content_md5)),
            ('x-ms-blob-content-encoding', _str_or_none(x_ms_blob_content_encoding)),
            ('x-ms-blob-content-language', _str_or_none(x_ms_blob_content_language)),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def put_blob(self, container_name, blob_name, blob, x_ms_blob_type, content_encoding=None, content_language=None, content_md5=None, cache_control=None, x_ms_blob_content_type=None, x_ms_blob_content_encoding=None, x_ms_blob_content_language=None, x_ms_blob_content_md5=None, x_ms_blob_cache_control=None, x_ms_meta_name_values=None, x_ms_lease_id=None, x_ms_blob_content_length=None, x_ms_blob_sequence_number=None):
        '''
        Creates a new block blob or page blob, or updates the content of an 
        existing block blob. 
        
        container_name: Name of existing container.
        blob_name: Name of blob to create or update.
        blob: the content of blob.
        x_ms_blob_type: Required. Could be BlockBlob or PageBlob
        content_encoding:
            Optional. Specifies which content encodings have been applied to 
            the blob. This value is returned to the client when the Get Blob 
            (REST API) operation is performed on the blob resource. The client 
            can use this value when returned to decode the blob content.
        content_language:
            Optional. Specifies the natural languages used by this resource.
        content_md5:
            Optional. An MD5 hash of the blob content. This hash is used to 
            verify the integrity of the blob during transport. When this header 
            is specified, the storage service checks the hash that has arrived 
            with the one that was sent. If the two hashes do not match, the 
            operation will fail with error code 400 (Bad Request). 
        cache_control:
            Optional. The Blob service stores this value but does not use or 
            modify it.
        x_ms_blob_content_type: Optional. Set the blob's content type. 
        x_ms_blob_content_encoding: Optional. Set the blob's content encoding.
        x_ms_blob_content_language: Optional. Set the blob's content language.
        x_ms_blob_content_md5: Optional. Set the blob's MD5 hash.
        x_ms_blob_cache_control: Optional. Sets the blob's cache control. 
        x_ms_meta_name_values: A dict containing name, value for metadata.
        x_ms_lease_id: Required if the blob has an active lease.
        x_ms_blob_content_length:
            Required for page blobs. This header specifies the maximum size 
            for the page blob, up to 1 TB. The page blob size must be aligned 
            to a 512-byte boundary.
        x_ms_blob_sequence_number:
            Optional. Set for page blobs only. The sequence number is a 
            user-controlled value that you can use to track requests. The 
            value of the sequence number must be between 0 and 2^63 - 1. The 
            default value is 0.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('blob', blob)
        _validate_not_none('x_ms_blob_type', x_ms_blob_type)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + ''
        request.headers = [
            ('x-ms-blob-type', _str_or_none(x_ms_blob_type)),
            ('Content-Encoding', _str_or_none(content_encoding)),
            ('Content-Language', _str_or_none(content_language)),
            ('Content-MD5', _str_or_none(content_md5)),
            ('Cache-Control', _str_or_none(cache_control)),
            ('x-ms-blob-content-type', _str_or_none(x_ms_blob_content_type)),
            ('x-ms-blob-content-encoding', _str_or_none(x_ms_blob_content_encoding)),
            ('x-ms-blob-content-language', _str_or_none(x_ms_blob_content_language)),
            ('x-ms-blob-content-md5', _str_or_none(x_ms_blob_content_md5)),
            ('x-ms-blob-cache-control', _str_or_none(x_ms_blob_cache_control)),
            ('x-ms-meta-name-values', x_ms_meta_name_values),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id)),
            ('x-ms-blob-content-length', _str_or_none(x_ms_blob_content_length)),
            ('x-ms-blob-sequence-number', _str_or_none(x_ms_blob_sequence_number))
            ]
        request.body = _get_request_body(blob)
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def get_blob(self, container_name, blob_name, snapshot=None, x_ms_range=None, x_ms_lease_id=None, x_ms_range_get_content_md5=None):
        '''
        Reads or downloads a blob from the system, including its metadata and 
        properties. 
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        snapshot:
            Optional. The snapshot parameter is an opaque DateTime value that, 
            when present, specifies the blob snapshot to retrieve. 
        x_ms_range:
            Optional. Return only the bytes of the blob in the specified range.
        x_ms_lease_id: Required if the blob has an active lease.
        x_ms_range_get_content_md5:
            Optional. When this header is set to true and specified together 
            with the Range header, the service returns the MD5 hash for the 
            range, as long as the range is less than or equal to 4 MB in size.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + ''
        request.headers = [
            ('x-ms-range', _str_or_none(x_ms_range)),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id)),
            ('x-ms-range-get-content-md5', _str_or_none(x_ms_range_get_content_md5))
            ]
        request.query = [('snapshot', _str_or_none(snapshot))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _create_blob_result(response)

    def get_blob_metadata(self, container_name, blob_name, snapshot=None, x_ms_lease_id=None):
        '''
        Returns all user-defined metadata for the specified blob or snapshot.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        snapshot:
            Optional. The snapshot parameter is an opaque DateTime value that, 
            when present, specifies the blob snapshot to retrieve. 
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=metadata'
        request.headers = [('x-ms-lease-id', _str_or_none(x_ms_lease_id))]
        request.query = [('snapshot', _str_or_none(snapshot))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict_prefix(response, prefixes=['x-ms-meta'])

    def set_blob_metadata(self, container_name, blob_name, x_ms_meta_name_values=None, x_ms_lease_id=None):
        '''
        Sets user-defined metadata for the specified blob as one or more 
        name-value pairs.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        x_ms_meta_name_values: Dict containing name and value pairs.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=metadata'
        request.headers = [
            ('x-ms-meta-name-values', x_ms_meta_name_values),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def lease_blob(self, container_name, blob_name, x_ms_lease_action, x_ms_lease_id=None):
        '''
        Establishes and manages a one-minute lock on a blob for write operations.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        x_ms_lease_action: Required. Possible values: acquire|renew|release|break
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('x_ms_lease_action', x_ms_lease_action)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=lease'
        request.headers = [
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id)),
            ('x-ms-lease-action', _str_or_none(x_ms_lease_action))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict_filter(response, filter=['x-ms-lease-id'])

    def snapshot_blob(self, container_name, blob_name, x_ms_meta_name_values=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, x_ms_lease_id=None):
        '''
        Creates a read-only snapshot of a blob.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        x_ms_meta_name_values: Optional. Dict containing name and value pairs.
        if_modified_since: Optional. Datetime string.
        if_unmodified_since: DateTime string.
        if_match:
            Optional. snapshot the blob only if its ETag value matches the 
            value specified. 
        if_none_match: Optional. An ETag value
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=snapshot'
        request.headers = [
            ('x-ms-meta-name-values', x_ms_meta_name_values),
            ('If-Modified-Since', _str_or_none(if_modified_since)),
            ('If-Unmodified-Since', _str_or_none(if_unmodified_since)),
            ('If-Match', _str_or_none(if_match)),
            ('If-None-Match', _str_or_none(if_none_match)),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_response_for_dict_filter(response, filter=['x-ms-snapshot', 'etag', 'last-modified'])

    def copy_blob(self, container_name, blob_name, x_ms_copy_source, x_ms_meta_name_values=None, x_ms_source_if_modified_since=None, x_ms_source_if_unmodified_since=None, x_ms_source_if_match=None, x_ms_source_if_none_match=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, x_ms_lease_id=None, x_ms_source_lease_id=None):
        '''
        Copies a blob to a destination within the storage account. 
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        x_ms_copy_source: the blob to be copied. Should be absolute path format.
        x_ms_meta_name_values: Optional. Dict containing name and value pairs.
        x_ms_source_if_modified_since:
            Optional. An ETag value. Specify this conditional header to copy 
            the source blob only if its ETag matches the value specified.
        x_ms_source_if_unmodified_since:
            Optional. An ETag value. Specify this conditional header to copy 
            the blob only if its ETag does not match the value specified.
        x_ms_source_if_match:
            Optional. A DateTime value. Specify this conditional header to 
            copy the blob only if the source blob has been modified since the 
            specified date/time.
        x_ms_source_if_none_match:
            Optional. An ETag value. Specify this conditional header to copy 
            the source blob only if its ETag matches the value specified.
        if_modified_since: Optional. Datetime string.
        if_unmodified_since: DateTime string.
        if_match:
            Optional. Snapshot the blob only if its ETag value matches the 
            value specified. 
        if_none_match: Optional. An ETag value
        x_ms_lease_id: Required if the blob has an active lease.
        x_ms_source_lease_id:
            Optional. Specify this to perform the Copy Blob operation only if 
            the lease ID given matches the active lease ID of the source blob.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('x_ms_copy_source', x_ms_copy_source)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + ''
        request.headers = [
            ('x-ms-copy-source', _str_or_none(x_ms_copy_source)),
            ('x-ms-meta-name-values', x_ms_meta_name_values),
            ('x-ms-source-if-modified-since', _str_or_none(x_ms_source_if_modified_since)),
            ('x-ms-source-if-unmodified-since', _str_or_none(x_ms_source_if_unmodified_since)),
            ('x-ms-source-if-match', _str_or_none(x_ms_source_if_match)),
            ('x-ms-source-if-none-match', _str_or_none(x_ms_source_if_none_match)),
            ('If-Modified-Since', _str_or_none(if_modified_since)),
            ('If-Unmodified-Since', _str_or_none(if_unmodified_since)),
            ('If-Match', _str_or_none(if_match)),
            ('If-None-Match', _str_or_none(if_none_match)),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id)),
            ('x-ms-source-lease-id', _str_or_none(x_ms_source_lease_id))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def delete_blob(self, container_name, blob_name, snapshot=None, x_ms_lease_id=None):
        '''
        Marks the specified blob or snapshot for deletion. The blob is later 
        deleted during garbage collection.
        
        To mark a specific snapshot for deletion provide the date/time of the 
        snapshot via the snapshot parameter.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        snapshot:
            Optional. The snapshot parameter is an opaque DateTime value that, 
            when present, specifies the blob snapshot to delete.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + ''
        request.headers = [('x-ms-lease-id', _str_or_none(x_ms_lease_id))]
        request.query = [('snapshot', _str_or_none(snapshot))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def put_block(self, container_name, blob_name, block, blockid, content_md5=None, x_ms_lease_id=None):
        '''
        Creates a new block to be committed as part of a blob.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        block: Content of the block.
        blockid:
            Required. A value that identifies the block. The string must be 
            less than or equal to 64 bytes in size.
        content_md5:
            Optional. An MD5 hash of the block content. This hash is used to 
            verify the integrity of the blob during transport. When this 
            header is specified, the storage service checks the hash that has 
            arrived with the one that was sent.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('block', block)
        _validate_not_none('blockid', blockid)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=block'
        request.headers = [
            ('Content-MD5', _str_or_none(content_md5)),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id))
            ]
        request.query = [('blockid', base64.b64encode(_str_or_none(blockid)))]
        request.body = _get_request_body(block)
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def put_block_list(self, container_name, blob_name, block_list, content_md5=None, x_ms_blob_cache_control=None, x_ms_blob_content_type=None, x_ms_blob_content_encoding=None, x_ms_blob_content_language=None, x_ms_blob_content_md5=None, x_ms_meta_name_values=None, x_ms_lease_id=None):
        '''
        Writes a blob by specifying the list of block IDs that make up the 
        blob. In order to be written as part of a blob, a block must have been 
        successfully written to the server in a prior Put Block (REST API) 
        operation.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        block_list: A str list containing the block ids.
        content_md5:
            Optional. An MD5 hash of the block content. This hash is used to 
            verify the integrity of the blob during transport. When this header 
            is specified, the storage service checks the hash that has arrived 
            with the one that was sent.
        x_ms_blob_cache_control:
            Optional. Sets the blob's cache control. If specified, this 
            property is stored with the blob and returned with a read request.
        x_ms_blob_content_type:
            Optional. Sets the blob's content type. If specified, this property 
            is stored with the blob and returned with a read request.
        x_ms_blob_content_encoding:
            Optional. Sets the blob's content encoding. If specified, this 
            property is stored with the blob and returned with a read request.
        x_ms_blob_content_language:
            Optional. Set the blob's content language. If specified, this 
            property is stored with the blob and returned with a read request. 
        x_ms_blob_content_md5:
            Optional. An MD5 hash of the blob content. Note that this hash is 
            not validated, as the hashes for the individual blocks were 
            validated when each was uploaded.
        x_ms_meta_name_values: Optional. Dict containing name and value pairs.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('block_list', block_list)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=blocklist'
        request.headers = [
            ('Content-MD5', _str_or_none(content_md5)),
            ('x-ms-blob-cache-control', _str_or_none(x_ms_blob_cache_control)),
            ('x-ms-blob-content-type', _str_or_none(x_ms_blob_content_type)),
            ('x-ms-blob-content-encoding', _str_or_none(x_ms_blob_content_encoding)),
            ('x-ms-blob-content-language', _str_or_none(x_ms_blob_content_language)),
            ('x-ms-blob-content-md5', _str_or_none(x_ms_blob_content_md5)),
            ('x-ms-meta-name-values', x_ms_meta_name_values),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id))
            ]
        request.body = _get_request_body(_convert_block_list_to_xml(block_list))
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def get_block_list(self, container_name, blob_name, snapshot=None, blocklisttype=None, x_ms_lease_id=None):
        '''
        Retrieves the list of blocks that have been uploaded as part of a 
        block blob.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        snapshot:
            Optional. Datetime to determine the time to retrieve the blocks.
        blocklisttype:
            Specifies whether to return the list of committed blocks, the list 
            of uncommitted blocks, or both lists together. Valid values are:
            committed, uncommitted, or all.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=blocklist'
        request.headers = [('x-ms-lease-id', _str_or_none(x_ms_lease_id))]
        request.query = [
            ('snapshot', _str_or_none(snapshot)),
            ('blocklisttype', _str_or_none(blocklisttype))
            ]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _convert_response_to_block_list(response)

    def put_page(self, container_name, blob_name, page, x_ms_range, x_ms_page_write, timeout=None, content_md5=None, x_ms_lease_id=None, x_ms_if_sequence_number_lte=None, x_ms_if_sequence_number_lt=None, x_ms_if_sequence_number_eq=None, if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None):
        '''
        Writes a range of pages to a page blob.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        page: Content of the page.
        x_ms_range:
            Required. Specifies the range of bytes to be written as a page. 
            Both the start and end of the range must be specified. Must be in 
            format: bytes=startByte-endByte. Given that pages must be aligned 
            with 512-byte boundaries, the start offset must be a modulus of 
            512 and the end offset must be a modulus of 512-1. Examples of 
            valid byte ranges are 0-511, 512-1023, etc.
        x_ms_page_write:
            Required. You may specify one of the following options: 
                update (lower case):
                    Writes the bytes specified by the request body into the 
                    specified range. The Range and Content-Length headers must 
                    match to perform the update.
                clear (lower case):
                    Clears the specified range and releases the space used in 
                    storage for that range. To clear a range, set the 
                    Content-Length header to zero, and the Range header to a 
                    value that indicates the range to clear, up to maximum 
                    blob size.
        timeout: the timeout parameter is expressed in seconds.
        content_md5:
            Optional. An MD5 hash of the page content. This hash is used to 
            verify the integrity of the page during transport. When this header 
            is specified, the storage service compares the hash of the content 
            that has arrived with the header value that was sent. If the two 
            hashes do not match, the operation will fail with error code 400 
            (Bad Request).
        x_ms_lease_id: Required if the blob has an active lease.
        x_ms_if_sequence_number_lte:
            Optional. If the blob's sequence number is less than or equal to 
            the specified value, the request proceeds; otherwise it fails.
        x_ms_if_sequence_number_lt:
            Optional. If the blob's sequence number is less than the specified 
            value, the request proceeds; otherwise it fails.
        x_ms_if_sequence_number_eq:
            Optional. If the blob's sequence number is equal to the specified 
            value, the request proceeds; otherwise it fails.
        if_modified_since:
            Optional. A DateTime value. Specify this conditional header to 
            write the page only if the blob has been modified since the 
            specified date/time. If the blob has not been modified, the Blob 
            service fails.
        if_unmodified_since:
            Optional. A DateTime value. Specify this conditional header to 
            write the page only if the blob has not been modified since the 
            specified date/time. If the blob has been modified, the Blob 
            service fails.
        if_match:
            Optional. An ETag value. Specify an ETag value for this conditional 
            header to write the page only if the blob's ETag value matches the 
            value specified. If the values do not match, the Blob service fails.
        if_none_match:
            Optional. An ETag value. Specify an ETag value for this conditional 
            header to write the page only if the blob's ETag value does not 
            match the value specified. If the values are identical, the Blob 
            service fails.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('page', page)
        _validate_not_none('x_ms_range', x_ms_range)
        _validate_not_none('x_ms_page_write', x_ms_page_write)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=page'
        request.headers = [
            ('x-ms-range', _str_or_none(x_ms_range)),
            ('Content-MD5', _str_or_none(content_md5)),
            ('x-ms-page-write', _str_or_none(x_ms_page_write)),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id)),
            ('x-ms-if-sequence-number-lte', _str_or_none(x_ms_if_sequence_number_lte)),
            ('x-ms-if-sequence-number-lt', _str_or_none(x_ms_if_sequence_number_lt)),
            ('x-ms-if-sequence-number-eq', _str_or_none(x_ms_if_sequence_number_eq)),
            ('If-Modified-Since', _str_or_none(if_modified_since)),
            ('If-Unmodified-Since', _str_or_none(if_unmodified_since)),
            ('If-Match', _str_or_none(if_match)),
            ('If-None-Match', _str_or_none(if_none_match))
            ]
        request.query = [('timeout', _int_or_none(timeout))]
        request.body = _get_request_body(page)
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

    def get_page_ranges(self, container_name, blob_name, snapshot=None, range=None, x_ms_range=None, x_ms_lease_id=None):
        '''
        Retrieves the page ranges for a blob.
        
        container_name: Name of existing container.
        blob_name: Name of existing blob.
        snapshot:
            Optional. The snapshot parameter is an opaque DateTime value that, 
            when present, specifies the blob snapshot to retrieve information 
            from.
        range:
            Optional. Specifies the range of bytes over which to list ranges, 
            inclusively. If omitted, then all ranges for the blob are returned.
        x_ms_range:
            Optional. Specifies the range of bytes to be written as a page. 
            Both the start and end of the range must be specified. Must be in 
            format: bytes=startByte-endByte. Given that pages must be aligned 
            with 512-byte boundaries, the start offset must be a modulus of 
            512 and the end offset must be a modulus of 512-1. Examples of 
            valid byte ranges are 0-511, 512-1023, etc.
        x_ms_lease_id: Required if the blob has an active lease.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self._get_host()
        request.path = '/' + _str(container_name) + '/' + _str(blob_name) + '?comp=pagelist'
        request.headers = [
            ('Range', _str_or_none(range)),
            ('x-ms-range', _str_or_none(x_ms_range)),
            ('x-ms-lease-id', _str_or_none(x_ms_lease_id))
            ]
        request.query = [('snapshot', _str_or_none(snapshot))]
        request.path, request.query = _update_request_uri_query_local_storage(request, self.use_local_storage)
        request.headers = _update_storage_blob_header(request, self.account_name, self.account_key)
        response = self._perform_request(request)

        return _parse_simple_list(response, PageList, PageRange, "page_ranges")
