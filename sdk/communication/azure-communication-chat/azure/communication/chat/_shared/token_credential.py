# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class CommunicationTokenCredential(object):
    def __init__(self, token_credential):
        self.token_credential = token_credential
    
    def get_token(self, *scopes):
        return self.token_credential.get_token()