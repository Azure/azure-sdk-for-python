# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from azure.core.credentials import AccessToken
from testcase import ConversationTest


class AsyncFakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    async def get_token(self, *args):
        return self.token


class AsyncConversationTest(ConversationTest):

    def generate_fake_token(self):
        return AsyncFakeTokenCredential()
