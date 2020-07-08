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
import re
import time
from unittest import SkipTest

import adal
import vcr
import zlib
import math
import uuid
import unittest
import sys
import random
import logging

try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO

from azure.core.credentials import AccessToken

import data_lake_settings_fake as fake_settings
try:
    import settings_real as settings
except ImportError:
    settings = None


LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'


class TestMode(object):
    none = 'None'.lower() # this will be for unit test, no need for any recordings
    playback = 'Playback'.lower() # run against stored recordings
    record = 'Record'.lower() # run tests against live storage and update recordings
    run_live_no_record = 'RunLiveNoRecord'.lower() # run tests against live storage without altering recordings

    @staticmethod
    def is_playback(mode):
        return mode == TestMode.playback

    @staticmethod
    def need_recording_file(mode):
        return mode == TestMode.playback or mode == TestMode.record

    @staticmethod
    def need_real_credentials(mode):
        return mode == TestMode.run_live_no_record or mode == TestMode.record


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class StorageTestCase(unittest.TestCase):

    def setUp(self):
        self.working_folder = os.path.dirname(__file__)

        self.settings = settings
        self.fake_settings = fake_settings

        if settings is None:
            self.test_mode = os.getenv('TEST_MODE') or TestMode.playback
        else:
            self.test_mode = self.settings.TEST_MODE.lower() or TestMode.playback

        if self.test_mode == TestMode.playback or (self.settings is None and self.test_mode.lower() == TestMode.run_live_no_record):
            self.settings = self.fake_settings

        # example of qualified test name:
        # test_mgmt_network.test_public_ip_addresses
        _, filename = os.path.split(inspect.getsourcefile(type(self)))
        name, _ = os.path.splitext(filename)
        self.qualified_test_name = '{0}.{1}'.format(
            name,
            self._testMethodName,
        )

        self.logger = logging.getLogger('azure.storage')
        # enable logging if desired
        self.configure_logging()

    def configure_logging(self):
        self.enable_logging() if self.settings.ENABLE_LOGGING else self.disable_logging()

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
        if not self.is_playback():
            time.sleep(seconds)

    def is_playback(self):
        return self.test_mode == TestMode.playback

    def get_resource_name(self, prefix=''):
        # Append a suffix to the name, based on the fully qualified test name
        # We use a checksum of the test name so that each test gets different
        # resource names, but each test will get the same name on repeat runs,
        # which is needed for playback.
        # Most resource names have a length limit, so we use a crc32
        if self.test_mode.lower() == TestMode.run_live_no_record.lower():
            return prefix + str(uuid.uuid4()).replace('-', '')
        else:
            checksum = zlib.adler32(self.qualified_test_name.encode()) & 0xffffffff
            name = '{}{}'.format(prefix, hex(checksum)[2:])
            if name.endswith('L'):
                name = name[:-1]
            return name

    def get_random_bytes(self, size):
        if self.test_mode.lower() == TestMode.run_live_no_record.lower():
            rand = random.Random()
        else:
            checksum = zlib.adler32(self.qualified_test_name.encode()) & 0xffffffff
            rand = random.Random(checksum)
        result = bytearray(size)
        for i in range(size):
            result[i] = int(rand.random()*255)  # random() is consistent between python 2 and 3
        return bytes(result)

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

    def _get_shared_key_credential(self):
        return {
            "account_name": self.settings.STORAGE_DATA_LAKE_ACCOUNT_NAME,
            "account_key": self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY
        }

    def _get_account_url(self):
        return "{}://{}.dfs.core.windows.net".format(
            self.settings.PROTOCOL,
            self.settings.STORAGE_DATA_LAKE_ACCOUNT_NAME
        )

    def _get_oauth_account_url(self):
        return "{}://{}.blob.core.windows.net".format(
            self.settings.PROTOCOL,
            self.settings.STORAGE_DATA_LAKE_ACCOUNT_NAME
        )

    def _create_storage_service(self, service_class, settings, **kwargs):
        if settings.CONNECTION_STRING:
            service = service_class.from_connection_string(settings.CONNECTION_STRING, **kwargs)
        else:
            url = self._get_account_url()
            credential = self._get_shared_key_credential()
            service = service_class(url, credential=credential, **kwargs)
        return service

    # for blob storage account
    def _create_storage_service_for_blob_storage_account(self, service_class, settings):
        if hasattr(settings, 'BLOB_CONNECTION_STRING') and settings.BLOB_CONNECTION_STRING != "":
            service = service_class(connection_string=settings.BLOB_CONNECTION_STRING)
        elif hasattr(settings, 'BLOB_STORAGE_ACCOUNT_NAME') and settings.BLOB_STORAGE_ACCOUNT_NAME != "":
            service = service_class(
                settings.BLOB_STORAGE_ACCOUNT_NAME,
                settings.BLOB_STORAGE_ACCOUNT_KEY,
                protocol=settings.PROTOCOL,
            )
        else:
            raise SkipTest('BLOB_CONNECTION_STRING or BLOB_STORAGE_ACCOUNT_NAME must be populated to run this test')

    def _create_premium_storage_service(self, service_class, settings):
        if hasattr(settings, 'PREMIUM_CONNECTION_STRING') and settings.PREMIUM_CONNECTION_STRING != "":
            service = service_class(connection_string=settings.PREMIUM_CONNECTION_STRING)
        elif hasattr(settings, 'PREMIUM_STORAGE_ACCOUNT_NAME') and settings.PREMIUM_STORAGE_ACCOUNT_NAME != "":
            service = service_class(
                settings.PREMIUM_STORAGE_ACCOUNT_NAME,
                settings.PREMIUM_STORAGE_ACCOUNT_KEY,
                protocol=settings.PROTOCOL,
            )
        else:
            raise SkipTest('PREMIUM_CONNECTION_STRING or PREMIUM_STORAGE_ACCOUNT_NAME must be populated to run this test')

        self._set_test_proxy(service, settings)
        return service

    def _create_remote_storage_service(self, service_class, settings):
        if settings.REMOTE_STORAGE_ACCOUNT_NAME and settings.REMOTE_STORAGE_ACCOUNT_KEY:
            service = service_class(
                settings.REMOTE_STORAGE_ACCOUNT_NAME,
                settings.REMOTE_STORAGE_ACCOUNT_KEY,
                protocol=settings.PROTOCOL,
            )
        else:
            print("REMOTE_STORAGE_ACCOUNT_NAME and REMOTE_STORAGE_ACCOUNT_KEY not set in test settings file.")
        self._set_test_proxy(service, settings)
        return service

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

    def recording(self):
        if TestMode.need_recording_file(self.test_mode):
            cassette_name = '{0}.yaml'.format(self.qualified_test_name)

            my_vcr = vcr.VCR(
                before_record_request = self._scrub_sensitive_request_info,
                before_record_response = self._scrub_sensitive_response_info,
                record_mode = 'none' if TestMode.is_playback(self.test_mode) else 'all'
            )

            self.assertIsNotNone(self.working_folder)
            return my_vcr.use_cassette(
                os.path.join(self.working_folder, 'recordings', cassette_name),
                filter_headers=['authorization'],
            )
        else:
            @contextmanager
            def _nop_context_manager():
                yield
            return _nop_context_manager()

    def _scrub_sensitive_request_info(self, request):
        if not TestMode.is_playback(self.test_mode):
            request.uri = self._scrub(request.uri)
            if request.body is not None:
                request.body = self._scrub(request.body)
        return request

    def _scrub_sensitive_response_info(self, response):
        if not TestMode.is_playback(self.test_mode):
            # We need to make a copy because vcr doesn't make one for us.
            # Without this, changing the contents of the dicts would change
            # the contents returned to the caller - not just the contents
            # getting saved to disk. That would be a problem with headers
            # such as 'location', often used in the request uri of a
            # subsequent service call.
            response = copy.deepcopy(response)
            headers = response.get('headers')
            if headers:
                headers.pop('x-ms-client-request-id', None)

                def internal_scrub(key, val):
                    if key.lower() == 'retry-after':
                        return '0'
                    return self._scrub(val)

                for name, val in headers.items():
                    if isinstance(val, list):
                        for i, e in enumerate(val):
                            val[i] = internal_scrub(name, e)
                    else:
                        headers[name] = internal_scrub(name, val)

            body = response.get('body')
            if body:
                body_str = body.get('string')
                if body_str:
                    response['body']['string'] = self._scrub(body_str)

                    content_type = response.get('headers', {}).get('Content-Type', '')
                    if content_type:
                        content_type = (content_type[0] if isinstance(content_type, list) else content_type).lower()
                        if 'multipart/mixed' in content_type:
                            response['body']['string'] = re.sub("x-ms-client-request-id: [a-f0-9-]+\r\n", "", body_str.decode()).encode()

        return response

    def _scrub(self, val):
        old_to_new_dict = {
            self.settings.STORAGE_DATA_LAKE_ACCOUNT_NAME: self.fake_settings.STORAGE_DATA_LAKE_ACCOUNT_NAME,
            self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY: self.fake_settings.STORAGE_DATA_LAKE_ACCOUNT_KEY,
            self.settings.ACTIVE_DIRECTORY_APPLICATION_ID: self.fake_settings.ACTIVE_DIRECTORY_APPLICATION_ID,
            self.settings.ACTIVE_DIRECTORY_APPLICATION_SECRET: self.fake_settings.ACTIVE_DIRECTORY_APPLICATION_SECRET,
            self.settings.ACTIVE_DIRECTORY_TENANT_ID: self.fake_settings.ACTIVE_DIRECTORY_TENANT_ID,
        }
        replacements = list(old_to_new_dict.keys())

        # if we have 'val1' and 'val10', we want 'val10' to be replaced first
        replacements.sort(reverse=True)

        for old_value in replacements:
            if old_value:
                new_value = old_to_new_dict[old_value]
                if old_value != new_value:
                    if isinstance(val, bytes):
                        val = val.replace(old_value.encode(), new_value.encode())
                    elif isinstance(val, dict):
                        val2 = str(val).replace(old_value, new_value)
                        val = eval(val2)    # nosec
                    else:
                        val = val.replace(old_value, new_value)
        return val

    def assert_upload_progress(self, size, max_chunk_size, progress, unknown_size=False):
        '''Validates that the progress chunks align with our chunking procedure.'''
        index = 0
        total = None if unknown_size else size
        small_chunk_size = size % max_chunk_size
        self.assertEqual(len(progress), math.ceil(size / max_chunk_size))
        for i in progress:
            self.assertTrue(i[0] % max_chunk_size == 0 or i[0] % max_chunk_size == small_chunk_size)
            self.assertEqual(i[1], total)

    def assert_download_progress(self, size, max_chunk_size, max_get_size, progress):
        '''Validates that the progress chunks align with our chunking procedure.'''
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

    def is_file_encryption_enabled(self):
        return self.settings.IS_SERVER_SIDE_FILE_ENCRYPTION_ENABLED

    def generate_oauth_token(self):
        from azure.identity import ClientSecretCredential

        return ClientSecretCredential(
            self.settings.ACTIVE_DIRECTORY_TENANT_ID,
            self.settings.ACTIVE_DIRECTORY_APPLICATION_ID,
            self.settings.ACTIVE_DIRECTORY_APPLICATION_SECRET,
        )

    def generate_fake_token(self):
        return FakeTokenCredential()

    def generate_async_oauth_token(self):
        from azure.identity.aio import ClientSecretCredential
        return ClientSecretCredential(
            self.settings.ACTIVE_DIRECTORY_TENANT_ID,
            self.settings.ACTIVE_DIRECTORY_APPLICATION_ID,
            self.settings.ACTIVE_DIRECTORY_APPLICATION_SECRET,
        )

def record(test):
    def recording_test(self):
        with self.recording():
            test(self)
    recording_test.__name__ = test.__name__
    return recording_test


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
        self.logger = logging.getLogger('azure.storage.blob')
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
