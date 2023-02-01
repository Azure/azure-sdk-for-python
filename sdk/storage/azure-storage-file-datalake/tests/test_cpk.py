# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.filedatalake import CustomerProvidedEncryptionKey, DataLakeServiceClient

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import DataLakePreparer
from test_quick_query import DATALAKE_CSV_DATA

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
TEST_FILE_PREFIX = 'file'
TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(
    key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
    key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")
# ------------------------------------------------------------------------------


class TestDatalakeCpk(StorageRecordedTestCase):
    def _setup(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=account_key)
        self.file_system_name = self.get_resource_name('utfilesystem')

        if self.is_live:
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                file_system.create_file_system(timeout=5)
            except ResourceExistsError:
                pass

    def teardown(self):
        if self.is_live:
            try:
                self.dsc.delete_file_system(self.file_system_name)
            except ResourceNotFoundError:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    def _get_file_reference(self, prefix=TEST_FILE_PREFIX):
        file_name = self.get_resource_name(prefix)
        return file_name

    def _create_directory(self, name=None, cpk=None):
        directory_name = name if name else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        try:
            directory_client.create_directory(cpk=cpk)
        except ResourceExistsError:
            pass
        return directory_client

    def _create_file(self, directory_name=None, file_name=None, cpk=None):
        if directory_name:
            self._create_directory(directory_name, cpk)
        if not file_name:
            file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.file_system_name, directory_name + '/' + file_name)
        try:
            file_client.create_file(cpk=cpk)
        except ResourceExistsError:
            pass
        return file_client
    # ---------------------------------------------------------------------------

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, 'cpkdirectory')
        response = directory_client.create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert response is not None
        assert response['request_server_encrypted']
        assert TEST_ENCRYPTION_KEY.key_hash == response['encryption_key_sha256']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_sub_directory_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = self._create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Act
        sub_directory_client = directory_client.create_sub_directory('cpksubdirectory', cpk=TEST_ENCRYPTION_KEY)
        props = sub_directory_client.get_directory_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert props is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_file_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = self._create_directory(cpk=TEST_ENCRYPTION_KEY)
        file_client = directory_client.get_file_client('cpkfile')

        # Act
        response = file_client.create_file(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert response is not None
        assert response['request_server_encrypted']
        assert TEST_ENCRYPTION_KEY.key_hash == response['encryption_key_sha256']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_directory_properties_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = self._create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Act
        props = directory_client.get_directory_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert props is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_get_file_properties_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)

        # Act
        props = file_client.get_file_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert props is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_directory_exists_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = self._create_directory(cpk=TEST_ENCRYPTION_KEY)

        # Act
        exists = directory_client.exists()

        # Assert
        assert exists

    @DataLakePreparer()
    @recorded_by_proxy
    def test_file_exists_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)

        # Act
        exists = file_client.exists()

        # Assert
        assert exists is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_file_upload_data_file_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)
        data = self.get_random_bytes(1024)

        # Act
        response = file_client.upload_data(data, overwrite=True, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert response is not None
        assert response['request_server_encrypted']
        assert TEST_ENCRYPTION_KEY.key_hash == response['encryption_key_sha256']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_file_append_flush_data_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)
        data = self.get_random_bytes(1024)

        # Act
        file_client.append_data(data, offset=0, cpk=TEST_ENCRYPTION_KEY)
        response = file_client.flush_data(offset=0, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert response is not None
        assert response['request_server_encrypted']
        assert TEST_ENCRYPTION_KEY.key_hash == response['encryption_key_sha256']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_file_download_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_client = self._create_directory(cpk=TEST_ENCRYPTION_KEY)
        file_name = self._get_file_reference()
        file_client = directory_client.get_file_client(file_name)

        data = self.get_random_bytes(1024)
        file_client.upload_data(data, overwrite=True, cpk=TEST_ENCRYPTION_KEY)

        # Act
        file = file_client.download_file(cpk=TEST_ENCRYPTION_KEY).readall()

        # Assert
        assert file is not None
        assert data == file

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_metadata_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        file_client.set_metadata(metadata, cpk=TEST_ENCRYPTION_KEY)
        props = file_client.get_file_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        assert props is not None
        assert metadata == props.metadata

    @DataLakePreparer()
    @recorded_by_proxy
    def test_query_file_cpk(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()
        file_client = self._create_file(directory_name=directory_name, cpk=TEST_ENCRYPTION_KEY)
        file_client.upload_data(DATALAKE_CSV_DATA, overwrite=True, cpk=TEST_ENCRYPTION_KEY)

        errors = []

        def on_error(error):
            errors.append(error)

        # Act
        reader = file_client.query_file(
            "SELECT * from DataLakeStorage",
            on_error=on_error,
            cpk=TEST_ENCRYPTION_KEY)
        reader.readall()

        # Assert
        assert len(errors) == 0
        assert len(reader) == len(DATALAKE_CSV_DATA)
        assert len(reader) == reader._blob_query_reader._bytes_processed
