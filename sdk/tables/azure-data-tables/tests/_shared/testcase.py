# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division
from contextlib import contextmanager
import copy
import inspect
import os
import os.path
import time
from datetime import datetime, timedelta

try:
    import unittest.mock as mock
except ImportError:
    import mock

import zlib
import math
import sys
import string
import random
import re
import logging
from devtools_testutils import (
    AzureTestCase,
    AzureMgmtPreparer,
    ResourceGroupPreparer,
    StorageAccountPreparer,
    FakeResource,
)
from .cosmos_testcase import CosmosAccountPreparer, CachedCosmosAccountPreparer
from azure_devtools.scenario_tests import RecordingProcessor, AzureTestError, create_random_name
try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO

from azure.core.credentials import AccessToken
from azure.mgmt.storage.models import StorageAccount, Endpoints

from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.data.tables import generate_account_sas, AccountSasPermissions, ResourceTypes

try:
    from devtools_testutils import mgmt_settings_real as settings
except ImportError:
    from devtools_testutils import mgmt_settings_fake as settings

import pytest


LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'

RERUNS_DELAY = 60

SLEEP_DELAY = 30

class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class XMSRequestIDBody(RecordingProcessor):
    """This process is used for Storage batch call only, to avoid the echo policy.
    """
    def process_response(self, response):
        content_type = None
        for key, value in response.get('headers', {}).items():
            if key.lower() == 'content-type':
                content_type = (value[0] if isinstance(value, list) else value).lower()
                break

        if content_type and 'multipart/mixed' in content_type:
            response['body']['string'] = re.sub(b"x-ms-client-request-id: [a-f0-9-]+\r\n", b"", response['body']['string'])

        return response


class GlobalResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalResourceGroupPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        rg = TableTestCase._RESOURCE_GROUP
        if self.is_live:
            self.test_class_instance.scrubber.register_name_pair(
                rg.name,
                "rgname"
            )
        else:
            rg = FakeResource(
                name="rgname",
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname"
            )

        return {
            'location': 'westus',
            'resource_group': rg,
        }


class TableTestCase(AzureTestCase):

    def __init__(self, *args, **kwargs):
        super(TableTestCase, self).__init__(*args, **kwargs)
        self.replay_processors.append(XMSRequestIDBody())
        self._RESOURCE_GROUP = None,

    def connection_string(self, account, key):
        return "DefaultEndpointsProtocol=https;AccountName=" + account.name + ";AccountKey=" + str(key) + ";EndpointSuffix=core.windows.net"

    def account_url(self, account, endpoint_type):
        """Return an url of storage account.

        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "table", or "cosmos", etc.
        """
        try:
            if endpoint_type == "table":
                return account.primary_endpoints.table.rstrip("/")
            if endpoint_type == "cosmos":
                return "https://{}.table.cosmos.azure.com".format(account.name)
            else:
                raise ValueError("Unknown storage type {}".format(storage_type))
        except AttributeError: # Didn't find "primary_endpoints"
            return 'https://{}.{}.core.windows.net'.format(account, endpoint_type)

    def configure_logging(self):
        try:
            enable_logging = self.get_settings_value("ENABLE_LOGGING")
        except AzureTestError:
            enable_logging = True  # That's the default value in fake settings

        self.enable_logging() if enable_logging else self.disable_logging()

    def enable_logging(self):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.logger.handlers = [handler]
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = True
        self.logger.disabled = False

    def disable_logging(self):
        self.logger.propagate = False
        self.logger.disabled = True
        self.logger.handlers = []

    def sleep(self, seconds):
        if self.is_live:
            time.sleep(seconds)

    def get_random_bytes(self, size):
        # recordings don't like random stuff. making this more
        # deterministic.
        return b'a'*size

    def get_random_text_data(self, size):
        '''Returns random unicode text data exceeding the size threshold for
        chunking blob upload.'''
        checksum = zlib.adler32(self.qualified_test_name.encode()) & 0xffffffff
        rand = random.Random(checksum)
        text = u''
        words = [u'hello', u'world', u'python', u'啊齄丂狛狜']
        while (len(text) < size):
            index = int(rand.random()*(len(words) - 1))
            text = text + u' ' + words[index]

        return text

    @staticmethod
    def _set_test_proxy(service, settings):
        if settings.USE_PROXY:
            service.set_proxy(
                settings.PROXY_HOST,
                settings.PROXY_PORT,
                settings.PROXY_USER,
                settings.PROXY_PASSWORD,
            )

    def assertNamedItemInContainer(self, container, item_name, msg=None):
        def _is_string(obj):
            if sys.version_info >= (3,):
                return isinstance(obj, str)
            else:
                return isinstance(obj, basestring)
        for item in container:
            if _is_string(item):
                if item == item_name:
                    return
            elif item.name == item_name:
                return
            elif hasattr(item, 'snapshot') and item.snapshot == item_name:
                return


        standardMsg = '{0} not found in {1}'.format(
            repr(item_name), [str(c) for c in container])
        self.fail(self._formatMessage(msg, standardMsg))

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = '{0} unexpectedly found in {1}'.format(
                    repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential
            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_sas_token(self):
        fake_key = 'a'*30 + 'b'*30

        return '?' + generate_account_sas(
            account_name = 'test', # name of the storage account
            account_key = fake_key, # key for the storage account
            resource_types = ResourceTypes(object=True),
            permission = AccountSasPermissions(read=True,list=True),
            start = datetime.now() - timedelta(hours = 24),
            expiry = datetime.now() + timedelta(days = 8)
        )

    def generate_fake_token(self):
        return FakeTokenCredential()


def not_for_emulator(test):
    def skip_test_if_targeting_emulator(self):
        test(self)
    return skip_test_if_targeting_emulator


class RetryCounter(object):
    def __init__(self):
        self.count = 0

    def simple_count(self, retry_context):
        self.count += 1


class ResponseCallback(object):
    def __init__(self, status=None, new_status=None):
        self.status = status
        self.new_status = new_status
        self.first = True
        self.count = 0

    def override_first_status(self, response):
        if self.first and response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
            self.first = False
        self.count += 1

    def override_status(self, response):
        if response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
        self.count += 1


class LogCaptured(object):
    def __init__(self, test_case=None):
        # accept the test case so that we may reset logging after capturing logs
        self.test_case = test_case

    def __enter__(self):
        # enable logging
        # it is possible that the global logging flag is turned off
        self.test_case.enable_logging()

        # create a string stream to send the logs to
        self.log_stream = StringIO()

        # the handler needs to be stored so that we can remove it later
        self.handler = logging.StreamHandler(self.log_stream)
        self.handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

        # get and enable the logger to send the outputs to the string stream
        self.logger = logging.getLogger('azure.storage')
        self.logger.level = logging.DEBUG
        self.logger.addHandler(self.handler)

        # the stream is returned to the user so that the capture logs can be retrieved
        return self.log_stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        # stop the handler, and close the stream to exit
        self.logger.removeHandler(self.handler)
        self.log_stream.close()

        # reset logging since we messed with the setting
        self.test_case.configure_logging()

