# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import os.path

try:
    import unittest.mock as mock
except ImportError:
    import mock

from devtools_testutils import PowerShellPreparer
from devtools_testutils.fake_credentials import STORAGE_ACCOUNT_FAKE_KEY

try:
    # Running locally - use configuration in settings_real.py
    from .settings_real import *
except ImportError:
    # Running on the pipeline - use fake values in order to create rg, etc.
    from .settings_fake import *


LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
os.environ['STORAGE_ACCOUNT_NAME'] = os.environ.get('STORAGE_ACCOUNT_NAME', None) or STORAGE_ACCOUNT_NAME
os.environ['STORAGE_ACCOUNT_KEY'] = os.environ.get('STORAGE_ACCOUNT_KEY', None) or STORAGE_ACCOUNT_KEY

os.environ['AZURE_TEST_RUN_LIVE'] = os.environ.get('AZURE_TEST_RUN_LIVE', None) or RUN_IN_LIVE
os.environ['AZURE_SKIP_LIVE_RECORDING'] = os.environ.get('AZURE_SKIP_LIVE_RECORDING', None) or SKIP_LIVE_RECORDING
os.environ['PROTOCOL'] = PROTOCOL
os.environ['ACCOUNT_URL_SUFFIX'] = ACCOUNT_URL_SUFFIX

# This has no effect currently in Storage as we use a different mechanism (generate_oauth_token) to get these credential types. This is set to suppress the warning for having
# no authentication type set or client secret authentication values set.
os.environ['AZURE_TEST_USE_CLI_AUTH'] = "true"

QueuePreparer = functools.partial(
    PowerShellPreparer, "storage",
    storage_account_name="storagename",
    storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
)

def not_for_emulator(test):
    def skip_test_if_targeting_emulator(self):
        test(self)
    return skip_test_if_targeting_emulator
