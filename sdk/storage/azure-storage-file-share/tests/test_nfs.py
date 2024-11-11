# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import tempfile
from datetime import datetime, timedelta, timezone

import pytest
import requests
from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.fileshare import (
    AccessPolicy,
    AccountSasPermissions,
    ContentSettings,
    FileSasPermissions,
    generate_account_sas,
    generate_file_sas,
    generate_share_sas,
    NTFSAttributes,
    ResourceTypes,
    ShareFileClient,
    ShareSasPermissions,
    ShareServiceClient,
    StorageErrorCode
)

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import FileSharePreparer
from test_helpers import ProgressTracker


class TestStorageFileNFS(StorageRecordedTestCase):

    fsc: ShareServiceClient = None

    def _setup(self, storage_account_name):
        account_url = self.account_url(storage_account_name, "file")
        credential = DefaultAzureCredential()
        self.fsc = ShareServiceClient(account_url=account_url, credential=credential, token_intent='backup')

    def teardown_method(self):
        if self.fsc:
            try:
                self.fsc.delete_share()
            except:
                pass

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_file_and_set_file_properties(self, **kwargs):
        self._setup(kwargs.pop('storage_account_name'))

        props = self.fsc.get_service_properties()
        assert props is not None
