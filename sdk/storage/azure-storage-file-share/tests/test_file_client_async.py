# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import platform

import pytest
from azure.storage.fileshare import VERSION
from azure.storage.fileshare.aio import ShareClient, ShareDirectoryClient, ShareFileClient, ShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from devtools_testutils.storage.testcase import generate_sas_token
from settings.testcase import FileSharePreparer


# ------------------------------------------------------------------------------
SERVICES = {
    ShareServiceClient: 'file',
    ShareClient: 'file',
    ShareDirectoryClient: 'file',
    ShareFileClient: 'file',
}

_CONNECTION_ENDPOINTS = {'file': 'FileEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'file': 'FileSecondaryEndpoint'}


class TestStorageFileClientAsync(AsyncStorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        self.account_name = storage_account_name
        self.account_key = storage_account_key
        self.sas_token = generate_sas_token()
        self.token_credential = self.generate_oauth_token()

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass
    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, service_type, protocol='https'):
        assert service is not None
        assert service.account_name == self.account_name
        assert service.credential.account_name == self.account_name
        assert service.credential.account_key == self.account_key
        assert service.primary_endpoint.startswith('{}://{}.{}.core.windows.net/'.format(protocol, self.account_name, service_type)) is True
        assert service.secondary_endpoint.startswith('{}://{}-secondary.{}.core.windows.net/'.format(protocol, self.account_name, service_type)) is True

    # --Direct Parameters Test Cases --------------------------------------------
    @FileSharePreparer()
    async def test_create_service_with_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "file"), credential=self.account_key,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, url)
            assert service.scheme == 'https'

    @FileSharePreparer()
    async def test_create_service_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "file"), credential=self.sas_token,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            assert service is not None
            assert service.credential is None
            assert service.account_name == self.account_name
            assert service.url.endswith(self.sas_token)

    @FileSharePreparer()
    async def test_create_service_with_token(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        for service_type in SERVICES:
            # Act
            # token credential is available for FileService
            try:
                service_type(self.account_url(storage_account_name, "file"), credential=self.token_credential,
                             share_name='foo', directory_path='bar', file_path='baz')
            except ValueError:
                pass

    @FileSharePreparer()
    async def test_create_service_china(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        url = self.account_url(storage_account_name, "file").replace('core.windows.net', 'core.chinacloudapi.cn')
        for service_type in SERVICES.items():
            # Act
            service = service_type[0](
                url, credential=self.account_key,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            assert service is not None
            assert service.account_name == self.account_name
            assert service.credential.account_name == self.account_name
            assert service.credential.account_key == self.account_key
            assert service.primary_hostname == '{}.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])
            assert service.secondary_hostname == '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])

    @FileSharePreparer()
    async def test_create_service_protocol(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        url = self.account_url(storage_account_name, "file").replace('https', 'http')
        for service_type in SERVICES.items():
            # Act
            service = service_type[0](
                url, credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], protocol='http')
            assert service.scheme == 'http'

    @FileSharePreparer()
    async def test_create_service_empty_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        for service_type in SERVICES:
            # Act
            # Passing an empty key to create account should fail.
            with pytest.raises(ValueError) as e:
                service_type(
                    self.account_url(storage_account_name, "file"), share_name='foo', directory_path='bar', file_path='baz')

            assert str(e.value.args[0]) == 'You need to provide either an account shared key or SAS token when creating a storage service.'

    @FileSharePreparer()
    async def test_create_service_with_socket_timeout(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.account_url(storage_account_name, "file"), credential=self.account_key,
                share_name='foo', directory_path='bar', file_path='baz')
            service = service_type[0](
                self.account_url(storage_account_name, "file"), credential=self.account_key, connection_timeout=22,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------

    @FileSharePreparer()
    async def test_create_service_with_connection_string_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        conn_string = 'AccountName={};AccountKey={};'.format(self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            assert service.scheme == 'https'

    @FileSharePreparer()
    async def test_create_service_with_connection_string_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.account_name, self.sas_token)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            assert service is not None
            assert service.credential is None
            assert service.account_name == self.account_name
            assert service.url.endswith(self.sas_token)

    @FileSharePreparer()
    async def test_create_service_with_connection_string_endpoint_protocol(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            assert service is not None
            assert service.account_name == self.account_name
            assert service.credential.account_name == self.account_name
            assert service.credential.account_key == self.account_key
            assert service.primary_hostname == '{}.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])
            assert service.secondary_hostname == '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])
            assert service.scheme == 'http'

    @FileSharePreparer()
    async def test_create_service_with_connection_string_emulated(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'

            # Act
            with pytest.raises(ValueError):
                service_type[0].from_connection_string(conn_string, share_name='foo', directory_path='bar', file_path='baz')

    @FileSharePreparer()
    async def test_create_service_with_connection_string_fails_if_secondary_without_primary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        for service_type in SERVICES.items():
            self._setup(storage_account_name, storage_account_key)
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.account_name, self.account_key, _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with pytest.raises(ValueError):
                service_type[0].from_connection_string(
                    conn_string, share_name='foo', directory_path='bar', file_path='baz')

    @FileSharePreparer()
    async def test_create_service_with_connection_string_succeeds_if_secondary_with_primary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        for service_type in SERVICES.items():
            self._setup(storage_account_name, storage_account_key)
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                self.account_name, self.account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            assert service is not None
            assert service.account_name == self.account_name
            assert service.credential.account_name == self.account_name
            assert service.credential.account_key == self.account_key
            assert service.primary_hostname == 'www.mydomain.com'
            assert service.secondary_hostname == 'www-sec.mydomain.com'

    @FileSharePreparer()
    async def test_create_service_with_custom_account_endpoint_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};FileEndpoint={};'.format(
                self.account_name, self.account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name="foo", directory_path="bar", file_path="baz")

            # Assert
            assert service.account_name == self.account_name
            assert service.credential.account_name == self.account_name
            assert service.credential.account_key == self.account_key
            assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        
        service = ShareServiceClient(account_url=custom_account_url)
        assert service.account_name == None
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/?')

        service = ShareClient(account_url=custom_account_url, share_name="foo", snapshot="snap")
        assert service.account_name == None
        assert service.share_name == "foo"
        assert service.snapshot == "snap"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo?sharesnapshot=snap&')

        service = ShareDirectoryClient(account_url=custom_account_url, share_name='foo', directory_path="bar/baz", snapshot="snap")
        assert service.account_name == None
        assert service.share_name == "foo"
        assert service.directory_path == "bar/baz"
        assert service.snapshot == "snap"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo/bar%2Fbaz?sharesnapshot=snap&')

        service = ShareDirectoryClient(account_url=custom_account_url, share_name='foo', directory_path="")
        assert service.account_name == None
        assert service.share_name == "foo"
        assert service.directory_path == ""
        assert service.snapshot == None
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo?')

        service = ShareFileClient(account_url=custom_account_url, share_name="foo", file_path="bar/baz/file", snapshot="snap")
        assert service.account_name == None
        assert service.share_name == "foo"
        assert service.directory_path == "bar/baz"
        assert service.file_path, ["bar", "baz" == "file"]
        assert service.file_name == "file"
        assert service.snapshot == "snap"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo/bar/baz/file?sharesnapshot=snap&')

        service = ShareFileClient(account_url=custom_account_url, share_name="foo", file_path="file")
        assert service.account_name == None
        assert service.share_name == "foo"
        assert service.directory_path == ""
        assert service.file_path == ["file"]
        assert service.file_name == "file"
        assert service.snapshot == None
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo/file?')

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_user_agent_default(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        service = ShareServiceClient(self.account_url(storage_account_name, "file"), credential=self.account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "azsdk-python-storage-file-share/{}".format(VERSION) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_user_agent_custom(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        custom_app = "TestApp/v1.0"
        service = ShareServiceClient(
            self.account_url(storage_account_name, "file"), credential=self.account_key, user_agent=custom_app)

        def callback1(response):
            assert 'User-Agent' in response.http_request.headers
            assert ("TestApp/v1.0 azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback1)

        def callback2(response):
            assert 'User-Agent' in response.http_request.headers
            assert ("TestApp/v2.0 TestApp/v1.0 azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback2, user_agent="TestApp/v2.0")

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_user_agent_append(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        service = ShareServiceClient(self.account_url(storage_account_name, "file"), credential=self.account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert ("customer_user_agent azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent='customer_user_agent')

    @FileSharePreparer()
    async def test_closing_pipeline_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "file"), credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            async with service:
                assert hasattr(service, 'close')
                await service.close()

    @FileSharePreparer()
    async def test_closing_pipeline_client_simple(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "file"), credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')
            await service.close()


