# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division

import functools
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
    PowerShellPreparer)
from azure_devtools.scenario_tests import RecordingProcessor, AzureTestError, create_random_name
try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO

from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.core.credentials import AccessToken
from azure.storage.queue import generate_account_sas, AccountSasPermissions, ResourceTypes
from azure.mgmt.storage.models import StorageAccount, Endpoints
try:
    # Running locally - use configuration in settings_real.py
    from .settings_real import *
except ImportError:
    # Running on the pipeline - use fake values in order to create rg, etc.
    from .settings_fake import *

try:
    from devtools_testutils import mgmt_settings_real as settings
except ImportError:
    from devtools_testutils import mgmt_settings_fake as settings

import pytest

from .service_versions import service_version_map


LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
os.environ['STORAGE_ACCOUNT_NAME'] = os.environ.get('STORAGE_ACCOUNT_NAME', None) or STORAGE_ACCOUNT_NAME
os.environ['STORAGE_ACCOUNT_KEY'] = os.environ.get('STORAGE_ACCOUNT_KEY', None) or STORAGE_ACCOUNT_KEY

os.environ['AZURE_TEST_RUN_LIVE'] = os.environ.get('AZURE_TEST_RUN_LIVE', None) or RUN_IN_LIVE
os.environ['AZURE_SKIP_LIVE_RECORDING'] = os.environ.get('AZURE_SKIP_LIVE_RECORDING', None) or SKIP_LIVE_RECORDING
os.environ['PROTOCOL'] = PROTOCOL


QueuePreparer = functools.partial(
    PowerShellPreparer, "storage",
    storage_account_name="storagename",
    storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
)

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
