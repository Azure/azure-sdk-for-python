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
import hmac
import hashlib
import os

from windowsazure.storage import _storage_error_handler, X_MS_VERSION
from windowsazure.http.httpclient import _HTTPClient
from windowsazure import (_parse_response, HTTPError, WindowsAzureError,
                          DEV_ACCOUNT_NAME, DEV_ACCOUNT_KEY)

class _StorageClient:
    '''
    This is the base class for BlobManager, TableManager and QueueManager.
    '''

    def __init__(self, account_name, account_key, use_local_storage=None, protocol='http'):
        self.account_name = account_name
        self.account_key = account_key
        self.status = None
        self.message = None
        self.respheader = None
        self.requestid = None
        self.protocol = protocol
        self.use_local_storage = use_local_storage
        if use_local_storage is None:
            if os.environ.has_key('EMULATED'):
                self.use_local_storage = True
            else:
                self.use_local_storage = False
        else:
            self.use_local_storage = use_local_storage
        if self.use_local_storage:
            self.account_name = DEV_ACCOUNT_NAME
            self.account_key = DEV_ACCOUNT_KEY
        else:
            self.account_name = account_name
            self.account_key = account_key
        self.x_ms_version = X_MS_VERSION
        self._httpclient = _HTTPClient(service_instance=self, account_key=account_key, account_name=account_name, x_ms_version=self.x_ms_version, protocol=protocol)
        self._batchclient = None

    def _perform_request(self, request):
        try:
            if self._batchclient is not None:
                return self._batchclient.insert_request_to_batch(request)
            else:
                resp = self._httpclient.perform_request(request)
            self.status = self._httpclient.status
            self.message = self._httpclient.message
            self.respheader = self._httpclient.respheader
        except HTTPError as e:
            self.status = self._httpclient.status
            self.message = self._httpclient.message
            self.respheader = self._httpclient.respheader
            _storage_error_handler(e)

        if not resp:
            return None
        return resp

    def _parse_response(self, response, return_type=None):
        return _parse_response(response, return_type)

    def generate_share_access_string(self, container_name, blob_name, share_access_policy):
        resource = ''
        if container_name:
            resource += container_name + '/'
        if blob_name:
            resource += blob_name
        signed_identifier = ''
        access_policy = None
        string_to_sign = ''
        if isinstance(share_access_policy, SignedIdentifier):
            access_policy += share_access_policy.access_policy
            signed_identifier = share_access_policy.id
        elif isinstance(share_access_policy, AccessPolicy):
            access_policy = share_access_policy
        else:
            raise ValueError('Access Policy Error', 'share_access_policy must be either SignedIdentifier or AccessPolicy instance')

        string_to_sign += access_policy.permission + '\n'
        string_to_sign += access_policy.start + '\n'
        string_to_sign += access_policy.expiry + '\n'
        string_to_sign += '/' + self.account_name + urllib2.quote(resource) + '\n'
        string_to_sign += signed_identifier

        #sign the request
        decode_account_key = base64.b64decode(self.account_key)
        signed_hmac_sha256 = hmac.HMAC(decode_account_key, string_to_sign, hashlib.sha256)

        share_access_string = 'st=' + access_policy.start + '&'
        share_access_string += 'se=' + access_policy.expiry + '&'
        share_access_string += 'sp=' + access_policy.permission + '&'
        if not blob_name:
            share_access_string += 'sr=c&'
            share_access_string += signed_identifier + '&'
        else:
            share_access_string += 'sr=b&'
        share_access_string += base64.b64encode(signed_hmac_sha256.digest())

        return share_access_string





