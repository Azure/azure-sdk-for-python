# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division

from datetime import datetime, timedelta
from io import StringIO
import logging
import math
import os
import random
import sys
import time
import zlib

import pytest

from devtools_testutils import AzureTestCase, AzureRecordedTestCase

from .processors import XMSRequestIDBody
from . import ApiVersionAssertPolicy, service_version_map
from .. import FakeTokenCredential

try:
    from cStringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO

try:
    from azure.storage.blob import (
        generate_account_sas,
        AccountSasPermissions,
        ResourceTypes,
    )
except:
    try:
        from azure.storage.queue import (
            generate_account_sas,
            AccountSasPermissions,
            ResourceTypes,
        )
    except:
        from azure.storage.fileshare import (
            generate_account_sas,
            AccountSasPermissions,
            ResourceTypes,
        )

LOGGING_FORMAT = "%(asctime)s %(name)-20s %(levelname)-5s %(message)s"

ENABLE_LOGGING = True


def generate_sas_token():
    fake_key = "a" * 30 + "b" * 30

    return "?" + generate_account_sas(
        account_name="test",  # name of the storage account
        account_key=fake_key,  # key for the storage account
        resource_types=ResourceTypes(object=True),
        permission=AccountSasPermissions(read=True, list=True),
        start=datetime.now() - timedelta(hours=24),
        expiry=datetime.now() + timedelta(days=8),
    )


class StorageTestCase(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(StorageTestCase, self).__init__(*args, **kwargs)
        self.replay_processors.append(XMSRequestIDBody())
        self.logger = logging.getLogger("azure.storage")
        self.configure_logging()

    def connection_string(self, account_name, key):
        return (
            "DefaultEndpointsProtocol=https;AcCounTName="
            + account_name
            + ";AccOuntKey="
            + str(key)
            + ";EndpoIntSuffix=core.windows.net"
        )

    def account_url(self, storage_account, storage_type):
        """Return an url of storage account.

        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "blob", or "queue", etc.
        """
        return "{}://{}.{}.{}".format(
            os.environ.get("PROTOCOL", "https"),
            storage_account,
            storage_type,
            os.environ.get("ACCOUNT_URL_SUFFIX", "core.windows.net"),
        )

    def configure_logging(self):
        enable_logging = ENABLE_LOGGING

        self.enable_logging() if enable_logging else self.disable_logging()

    def enable_logging(self):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.logger.handlers = [handler]
        self.logger.setLevel(logging.DEBUG)
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
        return b"a" * size

    def get_random_text_data(self, size):
        """Returns random unicode text data exceeding the size threshold for
        chunking blob upload."""
        checksum = zlib.adler32(self.qualified_test_name.encode()) & 0xFFFFFFFF
        rand = random.Random(checksum)
        text = ""
        words = ["hello", "world", "python", "啊齄丂狛狜"]
        while len(text) < size:
            index = int(rand.random() * (len(words) - 1))
            text = text + " " + words[index]

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
            elif isinstance(item, dict):
                if item_name == item["name"]:
                    return
            elif item.name == item_name:
                return
            elif hasattr(item, "snapshot") and item.snapshot == item_name:
                return

        standardMsg = "{0} not found in {1}".format(repr(item_name), [str(c) for c in container])
        self.fail(self._formatMessage(msg, standardMsg))

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = "{0} unexpectedly found in {1}".format(repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))

    def assert_upload_progress(self, size, max_chunk_size, progress, unknown_size=False):
        """Validates that the progress chunks align with our chunking procedure."""
        index = 0
        total = None if unknown_size else size
        small_chunk_size = size % max_chunk_size
        self.assertEqual(len(progress), math.ceil(size / max_chunk_size))
        for i in progress:
            self.assertTrue(i[0] % max_chunk_size == 0 or i[0] % max_chunk_size == small_chunk_size)
            self.assertEqual(i[1], total)

    def assert_download_progress(self, size, max_chunk_size, max_get_size, progress):
        """Validates that the progress chunks align with our chunking procedure."""
        if size <= max_get_size:
            self.assertEqual(len(progress), 1)
            self.assertTrue(progress[0][0], size)
            self.assertTrue(progress[0][1], size)
        else:
            small_chunk_size = (size - max_get_size) % max_chunk_size
            self.assertEqual(len(progress), 1 + math.ceil((size - max_get_size) / max_chunk_size))

            self.assertTrue(progress[0][0], max_get_size)
            self.assertTrue(progress[0][1], size)
            for i in progress[1:]:
                self.assertTrue(i[0] % max_chunk_size == 0 or i[0] % max_chunk_size == small_chunk_size)
                self.assertEqual(i[1], size)

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
        fake_key = "a" * 30 + "b" * 30

        return "?" + generate_account_sas(
            account_name="test",  # name of the storage account
            account_key=fake_key,  # key for the storage account
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True, list=True),
            start=datetime.now() - timedelta(hours=24),
            expiry=datetime.now() + timedelta(days=8),
        )

    def generate_fake_token(self):
        return FakeTokenCredential()

    def _get_service_version(self, **kwargs):
        env_version = service_version_map.get(os.environ.get("AZURE_LIVE_TEST_SERVICE_VERSION", "LATEST"))
        return kwargs.pop("service_version", env_version)

    def create_storage_client(self, client, *args, **kwargs):
        kwargs["api_version"] = self._get_service_version(**kwargs)
        kwargs["_additional_pipeline_policies"] = [ApiVersionAssertPolicy(kwargs["api_version"])]
        return client(*args, **kwargs)

    def create_storage_client_from_conn_str(self, client, *args, **kwargs):
        kwargs["api_version"] = self._get_service_version(**kwargs)
        kwargs["_additional_pipeline_policies"] = [ApiVersionAssertPolicy(kwargs["api_version"])]
        return client.from_connection_string(*args, **kwargs)


class StorageRecordedTestCase(AzureRecordedTestCase):
    def setup_class(cls):
        cls.logger = logging.getLogger("azure.storage")
        cls.sas_token = generate_sas_token()

    def setup_method(self, _):
        self.configure_logging()

    def connection_string(self, account_name, key):
        return (
            "DefaultEndpointsProtocol=https;AcCounTName="
            + account_name
            + ";AccOuntKey="
            + str(key)
            + ";EndpoIntSuffix=core.windows.net"
        )

    def account_url(self, storage_account, storage_type):
        """Return an url of storage account.

        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "blob", or "queue", etc.
        """
        protocol = os.environ.get("PROTOCOL", "https")
        suffix = os.environ.get("ACCOUNT_URL_SUFFIX", "core.windows.net")
        return f"{protocol}://{storage_account}.{storage_type}.{suffix}"

    def configure_logging(self):
        enable_logging = ENABLE_LOGGING

        self.enable_logging() if enable_logging else self.disable_logging()

    def enable_logging(self):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.logger.handlers = [handler]
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = True
        self.logger.disabled = False

    def disable_logging(self):
        self.logger.propagate = False
        self.logger.disabled = True
        self.logger.handlers = []

    def get_random_bytes(self, size):
        # recordings don't like random stuff. making this more
        # deterministic.
        return b"a" * size

    def get_random_text_data(self, size):
        """Returns random unicode text data exceeding the size threshold for
        chunking blob upload."""
        checksum = zlib.adler32(self.qualified_test_name.encode()) & 0xFFFFFFFF
        rand = random.Random(checksum)
        text = ""
        words = ["hello", "world", "python", "啊齄丂狛狜"]
        while len(text) < size:
            index = int(rand.random() * (len(words) - 1))
            text = text + " " + words[index]

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
            return isinstance(obj, str)

        for item in container:
            if _is_string(item):
                if item == item_name:
                    return
            elif isinstance(item, dict):
                if item_name == item["name"]:
                    return
            elif item.name == item_name:
                return
            elif hasattr(item, "snapshot") and item.snapshot == item_name:
                return

        error_message = f"{repr(item_name)} not found in {[str(c) for c in container]}"
        pytest.fail(error_message)

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                error_message = f"{repr(item_name)} unexpectedly found in {repr(container)}"
                pytest.fail(error_message)

    def assert_upload_progress(self, size, max_chunk_size, progress, unknown_size=False):
        """Validates that the progress chunks align with our chunking procedure."""
        total = None if unknown_size else size
        small_chunk_size = size % max_chunk_size
        assert len(progress) == math.ceil(size / max_chunk_size)
        for i in progress:
            assert i[0] % max_chunk_size == 0 or i[0] % max_chunk_size == small_chunk_size
            assert i[1] == total

    def assert_download_progress(self, size, max_chunk_size, max_get_size, progress):
        """Validates that the progress chunks align with our chunking procedure."""
        if size <= max_get_size:
            assert len(progress) == 1
            assert progress[0][0], size
            assert progress[0][1], size
        else:
            small_chunk_size = (size - max_get_size) % max_chunk_size
            assert len(progress) == 1 + math.ceil((size - max_get_size) / max_chunk_size)

            assert progress[0][0], max_get_size
            assert progress[0][1], size
            for i in progress[1:]:
                assert i[0] % max_chunk_size == 0 or i[0] % max_chunk_size == small_chunk_size
                assert i[1] == size

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential

            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return FakeTokenCredential()

    def _get_service_version(self, **kwargs):
        env_version = service_version_map.get(os.environ.get("AZURE_LIVE_TEST_SERVICE_VERSION", "LATEST"))
        return kwargs.pop("service_version", env_version)

    def create_storage_client(self, client, *args, **kwargs):
        kwargs["api_version"] = self._get_service_version(**kwargs)
        kwargs["_additional_pipeline_policies"] = [ApiVersionAssertPolicy(kwargs["api_version"])]
        return client(*args, **kwargs)

    def create_storage_client_from_conn_str(self, client, *args, **kwargs):
        kwargs["api_version"] = self._get_service_version(**kwargs)
        kwargs["_additional_pipeline_policies"] = [ApiVersionAssertPolicy(kwargs["api_version"])]
        return client.from_connection_string(*args, **kwargs)


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
        self.logger = logging.getLogger("azure.storage")
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
