# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ..common.sharedaccesssignature import (
    SharedAccessSignature,
    _SharedAccessHelper,
    _QueryStringConstants,
    _sign_string,
)
from ._constants import X_MS_VERSION
from ..common._serialization import (
    url_quote,
)


class BlobSharedAccessSignature(SharedAccessSignature):
    '''
    Provides a factory for creating blob and container access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    '''

    def __init__(self, account_name, account_key=None, user_delegation_key=None):
        '''
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param str account_key:
            The access key to generate the shares access signatures.
        :param ~azure.storage.blob.models.UserDelegationKey user_delegation_key:
            Instead of an account key, the user could pass in a user delegation key.
            A user delegation key can be obtained from the service by authenticating with an AAD identity;
            this can be accomplished by calling get_user_delegation_key on any Blob service object.
        '''
        super(BlobSharedAccessSignature, self).__init__(account_name, account_key, x_ms_version=X_MS_VERSION)
        self.user_delegation_key = user_delegation_key

    def generate_blob(self, container_name, blob_name, snapshot=None, permission=None,
                      expiry=None, start=None, id=None, ip=None, protocol=None,
                      cache_control=None, content_disposition=None,
                      content_encoding=None, content_language=None,
                      content_type=None):
        '''
        Generates a shared access signature for the blob or one of its snapshots.
        Use the returned signature with the sas_token parameter of any BlobService.

        :param str container_name:
            Name of container.
        :param str blob_name:
            Name of blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to grant permission.
        :param BlobPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_blob_service_properties.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        '''
        resource_path = container_name + '/' + blob_name

        sas = _BlobSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(id)
        sas.add_resource('b' if snapshot is None else 'bs')
        sas.add_timestamp(snapshot)
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_resource_signature(self.account_name, self.account_key, resource_path,
                                   user_delegation_key=self.user_delegation_key)

        return sas.get_token()

    def generate_container(self, container_name, permission=None, expiry=None,
                           start=None, id=None, ip=None, protocol=None,
                           cache_control=None, content_disposition=None,
                           content_encoding=None, content_language=None,
                           content_type=None):
        '''
        Generates a shared access signature for the container.
        Use the returned signature with the sas_token parameter of any BlobService.

        :param str container_name:
            Name of container.
        :param ContainerPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_blob_service_properties.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        '''
        sas = _BlobSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(id)
        sas.add_resource('c')
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_resource_signature(self.account_name, self.account_key, container_name,
                                   user_delegation_key=self.user_delegation_key)
        return sas.get_token()


class _BlobQueryStringConstants(_QueryStringConstants):
    SIGNED_TIMESTAMP = 'snapshot'
    SIGNED_OID = 'skoid'
    SIGNED_TID = 'sktid'
    SIGNED_KEY_START = 'skt'
    SIGNED_KEY_EXPIRY = 'ske'
    SIGNED_KEY_SERVICE = 'sks'
    SIGNED_KEY_VERSION = 'skv'


class _BlobSharedAccessHelper(_SharedAccessHelper):
    def __init__(self):
        super(_BlobSharedAccessHelper, self).__init__()

    def add_timestamp(self, timestamp):
        self._add_query(_BlobQueryStringConstants.SIGNED_TIMESTAMP, timestamp)

    def get_value_to_append(self, query):
        return_value = self.query_dict.get(query) or ''
        return return_value + '\n'

    def add_resource_signature(self, account_name, account_key, path, user_delegation_key=None):
        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/blob/' + account_name + path + '\n'

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        string_to_sign = \
            (self.get_value_to_append(_BlobQueryStringConstants.SIGNED_PERMISSION) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_START) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_EXPIRY) +
             canonicalized_resource)

        if user_delegation_key is not None:
            self._add_query(_BlobQueryStringConstants.SIGNED_OID, user_delegation_key.signed_oid)
            self._add_query(_BlobQueryStringConstants.SIGNED_TID, user_delegation_key.signed_tid)
            self._add_query(_BlobQueryStringConstants.SIGNED_KEY_START, user_delegation_key.signed_start)
            self._add_query(_BlobQueryStringConstants.SIGNED_KEY_EXPIRY, user_delegation_key.signed_expiry)
            self._add_query(_BlobQueryStringConstants.SIGNED_KEY_SERVICE, user_delegation_key.signed_service)
            self._add_query(_BlobQueryStringConstants.SIGNED_KEY_VERSION, user_delegation_key.signed_version)

            string_to_sign += \
                (self.get_value_to_append(_BlobQueryStringConstants.SIGNED_OID) +
                 self.get_value_to_append(_BlobQueryStringConstants.SIGNED_TID) +
                 self.get_value_to_append(_BlobQueryStringConstants.SIGNED_KEY_START) +
                 self.get_value_to_append(_BlobQueryStringConstants.SIGNED_KEY_EXPIRY) +
                 self.get_value_to_append(_BlobQueryStringConstants.SIGNED_KEY_SERVICE) +
                 self.get_value_to_append(_BlobQueryStringConstants.SIGNED_KEY_VERSION))
        else:
            string_to_sign += self.get_value_to_append(_BlobQueryStringConstants.SIGNED_IDENTIFIER)

        string_to_sign += \
            (self.get_value_to_append(_BlobQueryStringConstants.SIGNED_IP) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_PROTOCOL) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_VERSION) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_RESOURCE) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_TIMESTAMP) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_CACHE_CONTROL) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_CONTENT_DISPOSITION) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_CONTENT_ENCODING) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_CONTENT_LANGUAGE) +
             self.get_value_to_append(_BlobQueryStringConstants.SIGNED_CONTENT_TYPE))

        # remove the trailing newline
        if string_to_sign[-1] == '\n':
            string_to_sign = string_to_sign[:-1]

        self._add_query(_BlobQueryStringConstants.SIGNED_SIGNATURE,
                        _sign_string(account_key if user_delegation_key is None else user_delegation_key.value,
                                     string_to_sign))

    def get_token(self):
        # a conscious decision was made to exclude the timestamp in the generated token
        # this is to avoid having two snapshot ids in the query parameters when the user appends the snapshot timestamp
        exclude = [_BlobQueryStringConstants.SIGNED_TIMESTAMP]
        return '&'.join(['{0}={1}'.format(n, url_quote(v))
                         for n, v in self.query_dict.items() if v is not None and n not in exclude])
