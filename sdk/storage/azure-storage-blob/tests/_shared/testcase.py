# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division
import os.path
import time
import logging
from devtools_testutils import (
    AzureMgmtTestCase,
    AzureMgmtPreparer,
    ResourceGroupPreparer,
    StorageAccountPreparer,
    FakeResource,
)
try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO

from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.core.credentials import AccessToken
from azure.mgmt.storage.models import StorageAccount, Endpoints
try:
    # Running locally - use configuration in settings_real.py
    from .settings_real import *
except ImportError:
    # Running on the pipeline - use fake values in order to create rg, etc.
    from .settings_fake import *

import pytest

from devtools_testutils.storage import StorageTestCase

LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
os.environ['AZURE_STORAGE_ACCOUNT_NAME'] = STORAGE_ACCOUNT_NAME
os.environ['AZURE_STORAGE_ACCOUNT_KEY'] = STORAGE_ACCOUNT_KEY
os.environ['AZURE_TEST_RUN_LIVE'] = os.environ.get('AZURE_TEST_RUN_LIVE', None) or RUN_IN_LIVE
os.environ['AZURE_SKIP_LIVE_RECORDING'] = os.environ.get('AZURE_SKIP_LIVE_RECORDING', None) or SKIP_LIVE_RECORDING


class GlobalStorageAccountPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalStorageAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        storage_account = StorageTestCase._STORAGE_ACCOUNT
        if self.is_live:
            self.test_class_instance.scrubber.register_name_pair(
                storage_account.name,
                "storagename"
            )
            self.test_class_instance.scrubber.register_name_pair(
                ":.{43}=\r",
                ":fake_shared_key=\r"
            )
        else:
            name = "storagename"
            storage_account.name = name
            storage_account.primary_endpoints.blob = 'https://{}.{}.core.windows.net'.format(name, 'blob')
            storage_account.primary_endpoints.queue = 'https://{}.{}.core.windows.net'.format(name, 'queue')
            storage_account.primary_endpoints.table = 'https://{}.{}.core.windows.net'.format(name, 'table')
            storage_account.primary_endpoints.file = 'https://{}.{}.core.windows.net'.format(name, 'file')

        return {
            'location': 'westus',
            'resource_group': StorageTestCase._RESOURCE_GROUP,
            'storage_account': storage_account,
            'storage_account_key': StorageTestCase._STORAGE_KEY,
            'storage_account_cs': StorageTestCase._STORAGE_CONNECTION_STRING,
        }


class GlobalResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalResourceGroupPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        rg = StorageTestCase._RESOURCE_GROUP
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


def not_for_emulator(test):
    def skip_test_if_targeting_emulator(self):
        test(self)
    return skip_test_if_targeting_emulator


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

    # Create
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
    location = os.environ.get("AZURE_LOCATION", "westus")

    existing_rg_name = os.environ.get("AZURE_RESOURCEGROUP_NAME")
    existing_storage_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    existing_storage_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    storage_connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

    i_need_to_create_rg = not (existing_rg_name or existing_storage_name or storage_connection_string)
    got_storage_info_from_env = existing_storage_name or storage_connection_string

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
        StorageTestCase._RESOURCE_GROUP = rg

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
                    storage_account.primary_endpoints = Endpoints()
                    storage_account.primary_endpoints.blob = '{}://{}.{}.{}'.format(PROTOCOL, storage_name, 'blob', ACCOUNT_URL_SUFFIX)
                    storage_account.primary_endpoints.queue = '{}://{}.{}.{}'.format(PROTOCOL, storage_name, 'queue', ACCOUNT_URL_SUFFIX)
                    storage_account.primary_endpoints.table = '{}://{}.{}.{}'.format(PROTOCOL, storage_name, 'table', ACCOUNT_URL_SUFFIX)
                    storage_account.primary_endpoints.file = '{}://{}.{}.{}'.format(PROTOCOL, storage_name, 'file', ACCOUNT_URL_SUFFIX)
                    storage_key = existing_storage_key

                if not storage_connection_string:
                    # It means I have received a storage name from env
                    storage_connection_string=";".join([
                        "DefaultEndpointsProtocol=https",
                        "AccountName={}".format(storage_name),
                        "AccountKey={}".format(storage_key),
                        "BlobEndpoint={}".format(storage_account.primary_endpoints.blob),
                        "TableEndpoint={}".format(storage_account.primary_endpoints.table),
                        "QueueEndpoint={}".format(storage_account.primary_endpoints.queue),
                        "FileEndpoint={}".format(storage_account.primary_endpoints.file),
                    ])

                if not storage_account:
                    # It means I have received a connection string
                    storage_name = storage_connection_string_parts["AccountName"]
                    storage_account = StorageAccount(
                        location=location,
                    )

                    def build_service_endpoint(service):
                        return "{}://{}.{}.{}".format(
                            storage_connection_string_parts.get("DefaultEndpointsProtocol", "https"),
                            storage_connection_string_parts["AccountName"],
                            service,
                            storage_connection_string_parts["EndpointSuffix"], # Let it fail if we don't even have that
                        )

                    storage_account.name = storage_name
                    storage_account.id = storage_name
                    storage_account.primary_endpoints=Endpoints()
                    storage_account.primary_endpoints.blob = storage_connection_string_parts.get("BlobEndpoint", build_service_endpoint("blob"))
                    storage_account.primary_endpoints.queue = storage_connection_string_parts.get("QueueEndpoint", build_service_endpoint("queue"))
                    storage_account.primary_endpoints.file = storage_connection_string_parts.get("FileEndpoint", build_service_endpoint("file"))
                    storage_account.secondary_endpoints=Endpoints()
                    storage_account.secondary_endpoints.blob = storage_connection_string_parts.get("BlobSecondaryEndpoint", build_service_endpoint("blob"))
                    storage_account.secondary_endpoints.queue = storage_connection_string_parts.get("QueueSecondaryEndpoint", build_service_endpoint("queue"))
                    storage_account.secondary_endpoints.file = storage_connection_string_parts.get("FileSecondaryEndpoint", build_service_endpoint("file"))
                    storage_key = storage_connection_string_parts["AccountKey"]

            else:
                for i in range(5):
                    try:
                        time.sleep(i) if i == 0 else time.sleep(2 ** i)
                        storage_name, storage_kwargs = storage_preparer._prepare_create_resource(
                            test_case, **rg_kwargs)
                        break
                        # Some tests may be running on the storage account and a conflict may occur. Backoff & Retry.
                    except HttpResponseError:
                        continue
                storage_account = storage_kwargs['storage_account']
                storage_key = storage_kwargs['storage_account_key']
                storage_connection_string = storage_kwargs['storage_account_cs']

            StorageTestCase._STORAGE_ACCOUNT = storage_account
            StorageTestCase._STORAGE_KEY = storage_key
            StorageTestCase._STORAGE_CONNECTION_STRING = storage_connection_string
            yield
        finally:
            if not got_storage_info_from_env:
                storage_preparer.remove_resource(
                    storage_name,
                    resource_group=rg
                )
    finally:
        if i_need_to_create_rg:
            try:
                rg_preparer.remove_resource(rg_name)
            # This covers the case where another test had already removed the resource group
            except ResourceNotFoundError:
                pass
        StorageTestCase._RESOURCE_GROUP = None
