# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division

import functools
import os.path

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
LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'
os.environ['DATALAKE_STORAGE_ACCOUNT_NAME'] = os.environ.get('DATALAKE_STORAGE_ACCOUNT_NAME', None) or DATALAKE_STORAGE_ACCOUNT_NAME
os.environ['DATALAKE_STORAGE_ACCOUNT_KEY'] = os.environ.get('DATALAKE_STORAGE_ACCOUNT_KEY', None) or DATALAKE_STORAGE_ACCOUNT_KEY

os.environ['STORAGE_DATA_LAKE_SOFT_DELETE_ACCOUNT_NAME'] = os.environ.get('STORAGE_DATA_LAKE_SOFT_DELETE_ACCOUNT_NAME', None) or STORAGE_DATA_LAKE_SOFT_DELETE_ACCOUNT_NAME
os.environ['STORAGE_DATA_LAKE_SOFT_DELETE_ACCOUNT_KEY'] = os.environ.get('STORAGE_DATA_LAKE_SOFT_DELETE_ACCOUNT_KEY', None) or STORAGE_DATA_LAKE_SOFT_DELETE_ACCOUNT_KEY

os.environ['AZURE_TEST_RUN_LIVE'] = os.environ.get('AZURE_TEST_RUN_LIVE', None) or RUN_IN_LIVE
os.environ['AZURE_SKIP_LIVE_RECORDING'] = os.environ.get('AZURE_SKIP_LIVE_RECORDING', None) or SKIP_LIVE_RECORDING
os.environ['PROTOCOL'] = PROTOCOL
os.environ['ACCOUNT_URL_SUFFIX'] = ACCOUNT_URL_SUFFIX

DataLakePreparer = functools.partial(
    PowerShellPreparer, "storage",
    datalake_storage_account_name="storagename",
    datalake_storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    storage_data_lake_soft_delete_account_name="storagesoftdelname",
    storage_data_lake_soft_delete_account_key=STORAGE_ACCOUNT_FAKE_KEY,
)
