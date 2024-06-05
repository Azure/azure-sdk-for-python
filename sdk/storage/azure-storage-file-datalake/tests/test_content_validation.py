# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.storage.filedatalake import (
    DataLakeServiceClient
)

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import GenericTestProxyParametrize1, StorageRecordedTestCase
from settings.testcase import DataLakePreparer


def assert_content_md5(request):
    if request.http_request.query.get('action') == 'append':
        assert request.http_request.headers.get('Content-MD5') is not None


def assert_content_crc64(request):
    if request.http_request.query.get('action') == 'append':
        assert request.http_request.headers.get('x-ms-content-crc64') is not None


class TestStorageContentValidation(StorageRecordedTestCase):
    def _setup(self, account_name, account_key):
        credential = {"account_name": account_name, "account_key": account_key}
        self.dsc = DataLakeServiceClient(self.account_url(account_name, "dfs"), credential=credential, logging_enable=True)
        self.file_system = self.dsc.get_file_system_client(self.get_resource_name('ufilesystem'))
        self.file_system.create_file_system()

    def teardown_method(self, _):
        if self.file_system:
            try:
                self.file_system.delete_file_system()
            except:
                pass

    def _get_file_reference(self):
        return self.get_resource_name('file')

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_upload_data(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        response = file.upload_data(data, overwrite=True, validate_content=a, raw_request_hook=assert_method)

        # Assert
        assert response

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_upload_data_chunks(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abcde' * 512
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        response = file.upload_data(
            data,
            overwrite=True,
            validate_content=a,
            chunk_size=1024,
            raw_request_hook=assert_method)

        # Assert
        assert response
