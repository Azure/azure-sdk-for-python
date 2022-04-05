# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division

import functools
import os
import logging
from devtools_testutils import PowerShellPreparer
from devtools_testutils.fake_credentials import STORAGE_ACCOUNT_FAKE_KEY

try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO

try:
    # Running locally - use configuration in settings_real.py
    from .settings_real import *
except ImportError:
    # Running on the pipeline - use fake values in order to create rg, etc.
    from .settings_fake import *


LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
os.environ['STORAGE_ACCOUNT_NAME'] = os.environ.get('STORAGE_ACCOUNT_NAME', None) or STORAGE_ACCOUNT_NAME
os.environ['STORAGE_ACCOUNT_KEY'] = os.environ.get('STORAGE_ACCOUNT_KEY', None) or STORAGE_ACCOUNT_KEY
os.environ['SECONDARY_STORAGE_ACCOUNT_NAME'] = os.environ.get('SECONDARY_STORAGE_ACCOUNT_NAME', None) or SECONDARY_STORAGE_ACCOUNT_NAME
os.environ['SECONDARY_STORAGE_ACCOUNT_KEY'] = os.environ.get('SECONDARY_STORAGE_ACCOUNT_KEY', None) or SECONDARY_STORAGE_ACCOUNT_KEY
os.environ['BLOB_STORAGE_ACCOUNT_NAME'] = os.environ.get('BLOB_STORAGE_ACCOUNT_NAME', None) or BLOB_STORAGE_ACCOUNT_NAME
os.environ['BLOB_STORAGE_ACCOUNT_KEY'] = os.environ.get('BLOB_STORAGE_ACCOUNT_KEY', None) or BLOB_STORAGE_ACCOUNT_KEY
os.environ['VERSIONED_STORAGE_ACCOUNT_NAME'] = os.environ.get('VERSIONED_STORAGE_ACCOUNT_NAME', None) or VERSIONED_STORAGE_ACCOUNT_NAME
os.environ['VERSIONED_STORAGE_ACCOUNT_KEY'] = os.environ.get('VERSIONED_STORAGE_ACCOUNT_KEY', None) or VERSIONED_STORAGE_ACCOUNT_KEY
os.environ['PREMIUM_STORAGE_ACCOUNT_NAME'] = os.environ.get('PREMIUM_STORAGE_ACCOUNT_NAME', None) or PREMIUM_STORAGE_ACCOUNT_NAME
os.environ['PREMIUM_STORAGE_ACCOUNT_KEY'] = os.environ.get('PREMIUM_STORAGE_ACCOUNT_KEY', None) or PREMIUM_STORAGE_ACCOUNT_KEY
os.environ['STORAGE_RESOURCE_GROUP_NAME'] = os.environ.get('STORAGE_RESOURCE_GROUP_NAME', None) or STORAGE_RESOURCE_GROUP_NAME


os.environ['AZURE_TEST_RUN_LIVE'] = os.environ.get('AZURE_TEST_RUN_LIVE', None) or RUN_IN_LIVE
os.environ['AZURE_SKIP_LIVE_RECORDING'] = os.environ.get('AZURE_SKIP_LIVE_RECORDING', None) or SKIP_LIVE_RECORDING
os.environ['PROTOCOL'] = PROTOCOL
os.environ['ACCOUNT_URL_SUFFIX'] = ACCOUNT_URL_SUFFIX

os.environ['STORAGE_TENANT_ID'] = os.environ.get('STORAGE_TENANT_ID', None) or TENANT_ID
os.environ['STORAGE_CLIENT_ID'] = os.environ.get('STORAGE_CLIENT_ID', None) or CLIENT_ID
os.environ['STORAGE_CLIENT_SECRET'] = os.environ.get('STORAGE_CLIENT_SECRET', None) or CLIENT_SECRET

BlobPreparer = functools.partial(
    PowerShellPreparer, "storage",
    storage_account_name="storagename",
    storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    secondary_storage_account_name="pyrmtstoragestorname",
    secondary_storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    blob_storage_account_name="storagenamestorname",
    blob_storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    versioned_storage_account_name="storagenamestorname",
    versioned_storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    premium_storage_account_name='pyacrstoragestorname',
    premium_storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    storage_resource_group_name="rgname",

)


def not_for_emulator(test):
    def skip_test_if_targeting_emulator(self):
        test(self)
    return skip_test_if_targeting_emulator
