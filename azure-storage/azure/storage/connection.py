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

from .constants import (
    BLOB_SERVICE_HOST_BASE,
    TABLE_SERVICE_HOST_BASE,
    QUEUE_SERVICE_HOST_BASE,
    FILE_SERVICE_HOST_BASE
)


class StorageConnectionParameters(object):
    '''
    Extract connection parameters from a connection string.
    
    This is based on http://azure.microsoft.com/en-us/documentation/articles/storage-configure-connection-string/ .
       
    NOTE "(Blob|Table|Queue|File)Endpoint" are not supported.
         "SharedAccessSignature" is not supported.
         dev_host, timeout, and sas_token cannot be specified with a connection string.
    '''
    def __init__(self, connection_string = ''):
        connection_params = dict(s.split('=',1) for s in connection_string.split(';'))

        self.account_name = connection_params.get('AccountName', None)
        self.account_key = connection_params.get('AccountKey', None)
        self.protocol = connection_params.get('DefaultEndpointsProtocol', 'https').lower()
        endpoint_suffix = connection_params.get('EndpointSuffix', None)
        self.host_base_blob = BLOB_SERVICE_HOST_BASE if endpoint_suffix is None \
                              else ".blob.{}".format(endpoint_suffix)
        self.host_base_table = TABLE_SERVICE_HOST_BASE if endpoint_suffix is None \
                               else ".table.{}".format(endpoint_suffix)
        self.host_base_queue = QUEUE_SERVICE_HOST_BASE if endpoint_suffix is None \
                               else ".queue.{}".format(endpoint_suffix)
        self.host_base_file = FILE_SERVICE_HOST_BASE if endpoint_suffix is None \
                               else ".file.{}".format(endpoint_suffix)
