
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
from devtools_testutils.cognitiveservices_testcase import CognitiveServiceTest
from azure.core.credentials import AccessToken


LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'


class AsyncFakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    async def get_token(self, *args):
        return self.token


class AsyncCognitiveServiceTestCase(CognitiveServiceTest):
    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

        return run

    def get_oauth_endpoint(self):
        return self.get_settings_value("TEXT_ANALYTICS_ACCOUNT_NAME")

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
