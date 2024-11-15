# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.storage.fileshare import ShareServiceClient

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import FileSharePreparer


TEST_INTENT = 'backup'
TEST_FILE_PREFIX = 'file'
TEST_DIRECTORY_PREFIX = 'directory'


class TestStorageFileNFS(StorageRecordedTestCase):

    fsc: ShareServiceClient = None

    def _setup(self, storage_account_name):
        account_url = self.account_url(storage_account_name, "file")
        self.credential = self.get_credential(ShareServiceClient)
        self.fsc = ShareServiceClient(account_url=account_url, credential=self.credential, token_intent=TEST_INTENT)
        self.share_name = self.get_resource_name('utshare')
        if self.is_live:
            try:
                self.fsc.create_share(self.share_name, protocols='NFS')
            except:
                pass

    def teardown_method(self):
        if self.fsc:
            try:
                self.fsc.delete_share(self.share_name)
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_file_name(self, prefix=TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    def _get_directory_name(self, prefix=TEST_DIRECTORY_PREFIX):
        return self.get_resource_name(prefix)

    # --Test cases for NFS ----------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_hard_link(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')

        self._setup(storage_account_name)

        share_client = self.fsc.get_share_client(self.share_name)

        directory_name = self._get_directory_name()
        directory_client = share_client.create_directory(directory_name)
        source_file_name = self._get_file_name('file1')
        source_file_client = directory_client.get_file_client(source_file_name)
        source_file_client.create_file(size=1024)
        hard_link_file_name = self._get_file_name('file2')
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        resp = hard_link_file_client.create_hard_link(target_file=f"{directory_name}/{source_file_name}")

        assert resp is not None
        assert resp['file_file_type'] == 'Regular'
        assert resp['owner'] == '0'
        assert resp['group'] == '0'
        assert resp['mode'] == '0664'
        assert resp['link_count'] == 2

        assert resp['file_creation_time'] is not None
        assert resp['file_last_write_time'] is not None
        assert resp['file_change_time'] is not None
        assert resp['file_id'] is not None
        assert resp['file_parent_id'] is not None

        assert 'file_attributes' not in resp
        assert 'file_response_key' not in resp

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_hard_link_error(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')

        self._setup(storage_account_name)

        share_client = self.fsc.get_share_client(self.share_name)

        directory_name = self._get_directory_name()
        directory_client = share_client.create_directory(directory_name)
        source_file_name = self._get_file_name()
        source_file_client = directory_client.get_file_client(source_file_name)
        hard_link_file_name = self._get_file_name()
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        with pytest.raises(ResourceNotFoundError) as e:
            hard_link_file_client.create_hard_link(target_file=source_file_client.url)

        assert 'ParentNotFound' in e.value.args[0]
