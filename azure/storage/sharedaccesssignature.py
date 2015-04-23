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
from azure import _sign_string, url_quote
from azure.storage import X_MS_VERSION


class ResourceType(object):
    RESOURCE_BLOB = 'b'
    RESOURCE_CONTAINER = 'c'


class QueryStringConstants(object):
    SIGNED_VERSION = 'sv'
    SIGNED_START = 'st'
    SIGNED_EXPIRY = 'se'
    SIGNED_RESOURCE = 'sr'
    SIGNED_PERMISSION = 'sp'
    SIGNED_IDENTIFIER = 'si'
    SIGNED_SIGNATURE = 'sig'
    SIGNED_CACHE_CONTROL = 'rscc'
    SIGNED_CONTENT_DISPOSITION = 'rscd'
    SIGNED_CONTENT_ENCODING = 'rsce'
    SIGNED_CONTENT_LANGUAGE = 'rscl'
    SIGNED_CONTENT_TYPE = 'rsct'
    TABLE_NAME = 'tn'
    START_PK = 'spk'
    START_RK = 'srk'
    END_PK = 'epk'
    END_RK = 'erk'


class SharedAccessPolicy(object):

    ''' SharedAccessPolicy class. '''

    def __init__(self, access_policy=None, signed_identifier=None):
        self.id = signed_identifier
        self.access_policy = access_policy


class SharedAccessSignature(object):

    '''
    The main class used to do the signing and generating the signature.

    account_name:
        the storage account name used to generate shared access signature
    account_key:
        the access key to genenerate share access signature
    '''

    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key

    def generate_signed_query_string(self, path, resource_type,
                                     shared_access_policy,
                                     version=X_MS_VERSION,
                                     cache_control=None, content_disposition=None,
                                     content_encoding=None, content_language=None,
                                     content_type=None, table_name=None):
        '''
        Generates the query string for path, resource type and shared access
        policy.

        path:
            the resource
        resource_type:
            'b' for blob, 'c' for container, None for queue/table
        shared_access_policy:
            shared access policy
        version:
            x-ms-version for storage service, or None to get a signed query
            string compatible with pre 2012-02-12 clients, where the version
            is not included in the query string.
        cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        table_name:
            Name of table.
        '''
        query_dict = self._generate_signed_query_dict(
            path,
            resource_type,
            shared_access_policy,
            version,
            cache_control,
            content_disposition,
            content_encoding,
            content_language,
            content_type,
            table_name,
        )
        return '&'.join(['{0}={1}'.format(n, url_quote(v, '/()$=\',')) for n, v in query_dict.items() if v is not None])

    def _generate_signed_query_dict(self, path, resource_type,
                                   shared_access_policy,
                                   version=X_MS_VERSION,
                                   cache_control=None, content_disposition=None,
                                   content_encoding=None, content_language=None,
                                   content_type=None, table_name=None):
        query_dict = {}

        def add_query(name, val):
            if val:
                query_dict[name] = val

        if shared_access_policy is not None:
            if shared_access_policy.access_policy is not None:
                ap = shared_access_policy.access_policy

                add_query(QueryStringConstants.SIGNED_START, ap.start)
                add_query(QueryStringConstants.SIGNED_EXPIRY, ap.expiry)
                add_query(QueryStringConstants.SIGNED_PERMISSION, ap.permission)
                add_query(QueryStringConstants.START_PK, ap.start_pk)
                add_query(QueryStringConstants.START_RK, ap.start_rk)
                add_query(QueryStringConstants.END_PK, ap.end_pk)
                add_query(QueryStringConstants.END_RK, ap.end_rk)

            add_query(QueryStringConstants.SIGNED_IDENTIFIER, shared_access_policy.id)

        add_query(QueryStringConstants.SIGNED_VERSION, version)
        add_query(QueryStringConstants.SIGNED_RESOURCE, resource_type)
        add_query(QueryStringConstants.SIGNED_CACHE_CONTROL, cache_control)
        add_query(QueryStringConstants.SIGNED_CONTENT_DISPOSITION, content_disposition)
        add_query(QueryStringConstants.SIGNED_CONTENT_ENCODING, content_encoding)
        add_query(QueryStringConstants.SIGNED_CONTENT_LANGUAGE, content_language)
        add_query(QueryStringConstants.SIGNED_CONTENT_TYPE, content_type)
        add_query(QueryStringConstants.TABLE_NAME, table_name)

        query_dict[QueryStringConstants.SIGNED_SIGNATURE] = self._generate_signature(
            path, resource_type, shared_access_policy, version, cache_control,
            content_disposition, content_encoding, content_language,
            content_type, table_name)

        return query_dict

    def _generate_signature(self, path, resource_type, shared_access_policy,
                            version=X_MS_VERSION,
                            cache_control=None, content_disposition=None,
                            content_encoding=None, content_language=None,
                            content_type=None, table_name=None):
        ''' Generates signature for a given path and shared access policy. '''

        def get_value_to_append(value):
            return_value = value or ''
            return return_value + '\n'

        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/' + self.account_name + path

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        ap = shared_access_policy.access_policy

        string_to_sign = \
            (get_value_to_append(ap.permission if ap else '') +
             get_value_to_append(ap.start if ap else '') +
             get_value_to_append(ap.expiry if ap else '') +
             get_value_to_append(canonicalized_resource) +
             get_value_to_append(shared_access_policy.id) +
             get_value_to_append(version))

        if resource_type:
            string_to_sign += \
                (get_value_to_append(cache_control) +
                get_value_to_append(content_disposition) +
                get_value_to_append(content_encoding) +
                get_value_to_append(content_language) +
                get_value_to_append(content_type))

        if table_name:
            string_to_sign += \
                (get_value_to_append(ap.start_pk if ap else '') +
                get_value_to_append(ap.start_rk if ap else '') +
                get_value_to_append(ap.end_pk if ap else '') +
                get_value_to_append(ap.end_rk if ap else ''))

        if string_to_sign[-1] == '\n':
            string_to_sign = string_to_sign[:-1]

        return _sign_string(self.account_key, string_to_sign)
