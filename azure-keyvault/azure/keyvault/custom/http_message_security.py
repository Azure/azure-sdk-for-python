#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------


class HttpMessageSecurity(object):
    def __init__(self, client_security_token=None,
                 client_signature_key=None,
                 client_encryption_key=None,
                 server_signature_key=None,
                 server_encryption_key=None):
        self.client_security_token = client_security_token
        self.client_signature_key = client_signature_key
        self.client_encryption_key = client_encryption_key
        self.server_signature_key = server_signature_key
        self.server_encryption_key = server_encryption_key

    def protect_request(self, request):

        # get the original body
        return request

    def unprotect_response(self, response):
        return response
