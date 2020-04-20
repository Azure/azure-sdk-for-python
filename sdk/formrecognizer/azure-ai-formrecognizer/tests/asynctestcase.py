
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.credentials import AccessToken
from testcase import FormRecognizerTest


class AsyncFakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    async def get_token(self, *args):
        return self.token


class AsyncFormRecognizerTest(FormRecognizerTest):

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity.aio import ClientSecretCredential
            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return AsyncFakeTokenCredential()
