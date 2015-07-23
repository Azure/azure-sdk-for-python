#-------------------------------------------------------------------------
# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
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
from .._common_error import (
    _validate_not_none
)
from .._common_serialization import (
    _update_request_uri_query_local_storage
)
from .._common_conversion import (
    _encode_base64,
    _int_or_none,
    _str,
    _str_or_none,
)
from .._http import HTTPRequest
from .models import (
    Share,
    ShareEnumResults
)
from ..auth import (
    StorageSASAuthentication,
    StorageSharedKeyAuthentication,
    StorageNoAuthentication,
)
from ..connection import (
    StorageConnectionParameters,
)
from ..constants import (
    FILES_SERVICE_HOST_BASE,
    DEFAULT_HTTP_TIMEOUT,
    DEV_FILES_HOST,
    X_MS_VERSION,
)
from ._serialization import (
    _parse_files_enum_results_list,
    _update_storage_files_header,
)
from ..sharedaccesssignature import (
    SharedAccessSignature,
    ResourceType,
)
from ..storageclient import _StorageClient

class FilesService(_StorageClient):

    '''
    This is the main class managing Files resources.
    '''

    def __init__(
        self, account_name=None, account_key=None, protocol='https',
        host_base=FILES_SERVICE_HOST_BASE, dev_host=DEV_FILES_HOST,
        timeout=DEFAULT_HTTP_TIMEOUT, sas_token=None, connection_string=None,
        request_session=None
    ):
        '''
        account_name:
            your storage account name, required for all operations.
        account_key:
            your storage account key, required for all operations.
        protocol:
            Optional. Protocol. Defaults to https.
        host_base:
            Optional. Live host base url. Defaults to Azure url. Override this
            for on-premise.
        dev_host:
            Optional. Dev host url. Defaults to localhost.
        timeout:
            Optional. Timeout for the http request, in seconds.
        sas_token:
            Optional. Token to use to authenticate with shared access signature.
        connection_string:
            Optional. If specified, the first four parameters
            (account_name, account_key, protocol, host_base) may be overridden
            by values specified in the connection_string. The next three
            parameters (dev_host, timeout, sas_token) cannot be specified
            with a connection_string. See http://azure.microsoft.com/ \
            en-us/documentation/articles/storage-configure-connection-string
            for the connection string format.
        request_session:
            Optional. Session object to use for http requests. If this is
            specified, it replaces the default use of httplib.
        '''
        if connection_string is not None:
            connection_params = StorageConnectionParameters(connection_string)
            account_name = connection_params.account_name
            account_key = connection_params.account_key
            protocol = connection_params.protocol.lower()
            host_base = connection_params.host_base_blob

        super(FilesService, self).__init__(
            account_name, account_key, protocol,
            host_base, dev_host, timeout, sas_token, request_session
        )

        if self.account_key:
            self.authentication = StorageSharedKeyAuthentication(
                self.account_name,
                self.account_key,
            )
        elif self.sas_token:
            self.authentication = StorageSASAuthentication(self.sas_token)
        else:
            self.authentication = StorageNoAuthentication()

    def list_shares(
        self, prefix=None, marker=None, maxresults=None, include=None
    ):
        '''
        The List Shares operation returns a list of the shares under the
        specified account.

        prefix:
            Optional. Filters the results to return only shares whose names
            begin with the specified prefix.
        marker:
            Optional. A string value that identifies the portion of the list to
            be returned with the next list operation.
        maxresults:
            Optional. Specifies the maximum number of shares to return.
        include:
            Optional. Include this parameter to specify that the share's
            metadata be returned as part of the response body. set this
            parameter to string 'metadata' to get shares's metadata.
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
        request.path, request.query = _update_request_uri_query_local_storage(
            request, self.use_local_storage
        )
        request.headers = _update_storage_files_header(
            request, self.authentication
        )
        response = self._perform_request(request)

        return _parse_files_enum_results_list(response)

    def create_share(self, share_name, x_ms_meta_name_values=None):
        '''
        The Create Share operation creates a new share under the specified
        account. If the share with the same name already exists, the operation
        fails. The share resource includes metadata and properties for that
        share. It does not include a list of the files contained by the share.

        share_name:
            Name of the share to create
        x_ms_meta_name_values:
            Optional. A dict with name_value pairs to associate with the
            share as metadata. Example:{'Category':'test'}
        '''
        _validate_not_none('share_name', share_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self._get_host()
        request.path = '/' + _str(share_name) + '?restype=share'
        request.headers = [
            ('x-ms-meta-name-values', x_ms_meta_name_values)
        ]
        request.path, request.query = _update_request_uri_query_local_storage(
            request, self.use_local_storage
        )
        request.headers = _update_storage_files_header(
            request, self.authentication
        )
        self._perform_request(request)
        return True

    def delete_share(self, share_name, x_ms_meta_name_values=None):
        '''
        The Delete Share operation marks the specified share for deletion.
        The share and any files contained within it are later deleted
        during garbage collection.

        share_name:
            Name of the share to create
        x_ms_meta_name_values:
            Optional. A dict with name_value pairs to associate with the
            share as metadata. Example:{'Category':'test'}
        '''
        _validate_not_none('share_name', share_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self._get_host()
        request.path = '/' + _str(share_name) + '?restype=share'
        request.headers = [
            ('x-ms-meta-name-values', x_ms_meta_name_values)
        ]
        request.path, request.query = _update_request_uri_query_local_storage(
            request, self.use_local_storage
        )
        request.headers = _update_storage_files_header(
            request, self.authentication
        )
        self._perform_request(request)
        return True
