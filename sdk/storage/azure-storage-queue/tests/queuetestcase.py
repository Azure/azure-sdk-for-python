﻿# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division
import pytest
from contextlib import contextmanager
import copy
import inspect
import os
import os.path

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
import time
from devtools_testutils import AzureMgmtTestCase
try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO

from azure.core.credentials import AccessToken


LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'

class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token

class QueueTestCase(AzureMgmtTestCase):
    def connection_string(self, account, key):
        return "DefaultEndpointsProtocol=https;AccountName=" + account.name + ";AccountKey=" + str(key) + ";EndpointSuffix=core.windows.net"
    
    def _account_url (self, name):
        return 'https://{}.queue.core.windows.net'.format(name)

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
        if not self.is_playback():
            time.sleep(seconds)

    def get_random_bytes(self, size):
        if self.is_live:
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

    def assert_named_item_in_container(self, container, item_name, msg=None):
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
        pytest.fail(self._formatMessage(msg, standardMsg))

    def assert_named_item_not_in_container(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = '{0} unexpectedly found in {1}'.format(
                    repr(item_name), repr(container))
            pytest.fail(self._formatMessage(msg, standardMsg))

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
            self.settings.ACTIVE_DIRECTORY_APPLICATION_ID,
            self.settings.ACTIVE_DIRECTORY_APPLICATION_SECRET,
            self.settings.ACTIVE_DIRECTORY_TENANT_ID
        )

    def generate_fake_token(self):
        return FakeTokenCredential()


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
        if self.first and response.status == self.status:
            response.status = self.new_status
            self.first = False
        self.count += 1

    def override_status(self, response):
        if response.status == self.status:
            response.status = self.new_status
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
        self.logger.level = logging.INFO
        self.logger.addHandler(self.handler)

        # the stream is returned to the user so that the capture logs can be retrieved
        return self.log_stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        # stop the handler, and close the stream to exit
        self.logger.removeHandler(self.handler)
        self.log_stream.close()

        # reset logging since we messed with the setting
        self.test_case.configure_logging()
