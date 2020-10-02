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
    AzureMgmtTestCase,
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

SLEEP_DELAY = 15

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


class GlobalStorageAccountPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalStorageAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        storage_account = TableTestCase._STORAGE_ACCOUNT
        if self.is_live:
            self.test_class_instance.scrubber.register_name_pair(
                storage_account.name,
                "storagename"
            )
        else:
            name = "storagename"
            storage_account.name = name
            storage_account.primary_endpoints.table = 'https://{}.{}.core.windows.net'.format(name, 'table')

        return {
            'location': 'westus',
            'resource_group': TableTestCase._RESOURCE_GROUP,
            'storage_account': storage_account,
            'storage_account_key': TableTestCase._STORAGE_KEY,
            'storage_account_cs': TableTestCase._STORAGE_CONNECTION_STRING,
        }


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


class TableTestCase(AzureMgmtTestCase):

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


@pytest.fixture(scope="session")
def storage_account():
    test_case = AzureMgmtTestCase("__init__")
    rg_preparer = ResourceGroupPreparer(random_name_enabled=True, name_prefix='pystorage')
    storage_preparer = StorageAccountPreparer(random_name_enabled=True, name_prefix='pyacrstorage')
    cosmos_preparer = CosmosAccountPreparer(random_name_enabled=True, name_prefix='pycosmos')

    # Create
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
    location = os.environ.get("AZURE_LOCATION", "westus")

    existing_rg_name = os.environ.get("AZURE_RESOURCEGROUP_NAME")
    existing_storage_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    existing_storage_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    storage_connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    cosmos_connection_string = os.environ.get("AZURE_COSMOS_CONNECTION_STRING")
    existing_cosmos_name = os.environ.get("AZURE_COSMOS_ACCOUNT_URL")
    existing_cosmos_key = os.environ.get("AZURE_COSMOS_ACCOUNT_KEY")

    i_need_to_create_rg = not (existing_rg_name or existing_storage_name or storage_connection_string)
    got_storage_info_from_env = existing_storage_name or storage_connection_string
    got_cosmos_info_from_env = existing_cosmos_name or cosmos_connection_string

    storage_name = None
    rg_kwargs = {}

    try:
        if i_need_to_create_rg:
            rg_name, rg_kwargs = rg_preparer._prepare_create_resource(test_case)
            rg = rg_kwargs['resource_group']
        else:
            rg_name = existing_rg_name or "no_rg_needed"
            rg = FakeResource(
                name=rg_name,
                id="/subscriptions/{}/resourceGroups/{}".format(subscription_id, rg_name)
            )
        TableTestCase._RESOURCE_GROUP = rg

        try:
            if got_storage_info_from_env:

                if storage_connection_string:
                    storage_connection_string_parts = dict([
                        part.split('=', 1)
                        for part in storage_connection_string.split(";")
                    ])

                storage_account = None
                if existing_storage_name:
                    storage_name = existing_storage_name
                    storage_account = StorageAccount(
                        location=location,
                    )
                    storage_account.name = storage_name
                    storage_account.id = storage_name
                    storage_account.primary_endpoints=Endpoints()
                    storage_account.primary_endpoints.table = 'https://{}.{}.core.windows.net'.format(storage_name, 'table')
                    storage_key = existing_storage_key

                if not storage_connection_string:
                    # It means I have received a storage name from env
                    storage_connection_string=";".join([
                        "DefaultEndpointsProtocol=https",
                        "AccountName={}".format(storage_name),
                        "AccountKey={}".format(storage_key),
                        "TableEndpoint={}".format(storage_account.primary_endpoints.table),
                    ])

                if not storage_account:
                    # It means I have received a connection string
                    storage_name = storage_connection_string_parts["AccountName"]
                    storage_account = StorageAccount(
                        location=location,
                    )

                    def build_service_endpoint(service):
                        try:
                            suffix = storage_connection_string_parts["EndpointSuffix"]
                        except KeyError:
                            suffix = "cosmos.azure.com"
                        return "{}://{}.{}.{}".format(
                            storage_connection_string_parts.get("DefaultEndpointsProtocol", "https"),
                            storage_connection_string_parts["AccountName"],
                            service,
                            suffix
                        )

                    storage_account.name = storage_name
                    storage_account.id = storage_name
                    storage_account.primary_endpoints=Endpoints()
                    storage_account.primary_endpoints.table = storage_connection_string_parts.get("TableEndpoint", build_service_endpoint("table"))
                    storage_account.secondary_endpoints=Endpoints()
                    storage_account.secondary_endpoints.table = storage_connection_string_parts.get("TableSecondaryEndpoint", build_service_endpoint("table"))
                    storage_key = storage_connection_string_parts["AccountKey"]

            else:
                storage_name, storage_kwargs = storage_preparer._prepare_create_resource(test_case, **rg_kwargs)
                storage_account = storage_kwargs['storage_account']
                storage_key = storage_kwargs['storage_account_key']
                storage_connection_string = storage_kwargs['storage_account_cs']

            if cosmos_connection_string:
                cosmos_connection_string_parts = dict([
                    part.split('=', 1)
                    for part in cosmos_connection_string.split(';')
                ])

            if got_cosmos_info_from_env:

                if cosmos_connection_string:
                    cosmos_connection_string_parts = dict([
                        part.split('=', 1)
                        for part in storage_connection_string.split(";")
                    ])

                cosmos_account = None
                if existing_cosmos_name:
                    cosmos_name = existing_cosmos_name
                    cosmos_account.name = cosmos_name
                    cosmos_account.id = cosmos_name
                    cosmos_acount.primary_endpoints = Endpoints()
                    cosmos_account.primary_endpoints.table = "https://{}.table.cosmos.azure.com".format(cosmos_name)
                    cosmos_key = existing_cosmos_key

                if not cosmos_connection_string:
                    # I have received a cosmos name from env
                    cosmos_connection_string=";".join([
                        "DefaultEndpointsProtocol=https",
                        "AccountName={}".format(cosmos_name),
                        "AccountKey={}".format(cosmos_key),
                        "TableEndpoint={}".format(cosmos_account.primary_endpoints.table),
                    ])

                if not cosmos_account:
                    cosmos_name = cosmos_connection_string_parts["AccountName"]

                    def build_service_endpoint(service):
                        try:
                            suffix = cosmos_connection_string_parts["EndpointSuffix"]
                        except KeyError:
                            suffix = "cosmos.azure.com"
                        return "{}://{}.{}.{}".format(
                            cosmos_connection_string_parts.get("DefaultEndpointsProtocol", "https"),
                            cosmos_connection_string_parts["AccountName"],
                            service,
                            suffix
                        )

                    cosmos_account.name = cosmos_name
                    cosmos_account.id = cosmos_name
                    cosmos_account.primary_endpoints=Endpoints()
                    cosmos_account.primary_endpoints.table = cosmos_connection_string_parts.get("TableEndpoint", build_service_endpoint("table"))
                    cosmos_account.secondary_endpoints=Endpoints()
                    cosmos_account.secondary_endpoints.table = cosmos_connection_string_parts.get("TableSecondaryEndpoint", build_service_endpoint("table"))
                    cosmos_key = cosmos_connection_string_parts["AccountKey"]

            else:
                cosmos_name, cosmos_kwargs = cosmos_preparer._prepare_create_resource(test_case, **rg_kwargs)
                cosmos_account = cosmos_kwargs['cosmos_account']
                cosmos_key = cosmos_kwargs['cosmos_account_key']
                cosmos_connection_string = cosmos_kwargs['cosmos_account_cs']

            TableTestCase._STORAGE_ACCOUNT = storage_account
            TableTestCase._STORAGE_KEY = storage_key
            TableTestCase._STORAGE_CONNECTION_STRING = storage_connection_string
            TableTestCase._COSMOS_ACCOUNT = cosmos_account
            TableTestCase._COSMOS_KEY = cosmos_key
            TableTestCase._COSMOS_CONNECTION_STRING = cosmos_connection_string
            yield
        finally:
            if not got_storage_info_from_env:
                storage_preparer.remove_resource(
                    storage_name,
                    resource_group=rg
                )
                cosmos_preparer.remove_resource(
                    cosmos_name,
                    resource_group=rg
                )
    finally:
        if i_need_to_create_rg:
            rg_preparer.remove_resource(rg_name)
        TableTestCase._RESOURCE_GROUP = None
