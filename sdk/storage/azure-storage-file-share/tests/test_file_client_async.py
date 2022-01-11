# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import platform
import asyncio
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.storage.fileshare import VERSION
from azure.storage.fileshare.aio import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient)

from settings.testcase import FileSharePreparer
from devtools_testutils.storage.aio import AsyncStorageTestCase

# ------------------------------------------------------------------------------
SERVICES = {
    ShareServiceClient: 'file',
    ShareClient: 'file',
    ShareDirectoryClient: 'file',
    ShareFileClient: 'file',
}

_CONNECTION_ENDPOINTS = {'file': 'FileEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'file': 'FileSecondaryEndpoint'}


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageFileClientTest(AsyncStorageTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        self.account_name = storage_account_name
        self.account_key = storage_account_key
        self.sas_token = self.generate_sas_token()
        self.token_credential = self.generate_oauth_token()

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass
    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, service_type, protocol='https'):
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, self.account_name)
        self.assertEqual(service.credential.account_name, self.account_name)
        self.assertEqual(service.credential.account_key, self.account_key)
        self.assertTrue(service.primary_endpoint.startswith('{}://{}.{}.core.windows.net/'.format(
            protocol, self.account_name, service_type)))
        self.assertTrue(service.secondary_endpoint.startswith('{}://{}-secondary.{}.core.windows.net/'.format(
            protocol, self.account_name, service_type)))

    # --Direct Parameters Test Cases --------------------------------------------
    @FileSharePreparer()
    def test_create_service_with_key_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "file"), credential=self.account_key,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, url)
            self.assertEqual(service.scheme, 'https')

    @FileSharePreparer()
    def test_create_service_with_sas_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "file"), credential=self.sas_token,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, self.account_name)
            self.assertTrue(service.url.endswith(self.sas_token))

    @FileSharePreparer()
    def test_create_service_with_token_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        for service_type in SERVICES:
            # Act
            # token credential is not available for FileService
            with self.assertRaises(ValueError):
                service_type(self.account_url(storage_account_name, "file"), credential=self.token_credential,
                             share_name='foo', directory_path='bar', file_path='baz')

    @FileSharePreparer()
    def test_create_service_china_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        url = self.account_url(storage_account_name, "file").replace('core.windows.net', 'core.chinacloudapi.cn')
        for service_type in SERVICES.items():
            # Act
            service = service_type[0](
                url, credential=self.account_key,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, '{}.{}.core.chinacloudapi.cn'.format(
                self.account_name, service_type[1]))
            self.assertEqual(service.secondary_hostname,
                             '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))
    @FileSharePreparer()
    def test_create_service_protocol_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        url = self.account_url(storage_account_name, "file").replace('https', 'http')
        for service_type in SERVICES.items():
            # Act
            service = service_type[0](
                url, credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], protocol='http')
            self.assertEqual(service.scheme, 'http')

    @FileSharePreparer()
    def test_create_service_empty_key_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        for service_type in SERVICES:
            # Act
            # Passing an empty key to create account should fail.
            with self.assertRaises(ValueError) as e:
                service_type(
                    self.account_url(storage_account_name, "file"), share_name='foo', directory_path='bar', file_path='baz')

            self.assertEqual(
                str(e.exception),
                'You need to provide either an account shared key or SAS token when creating a storage service.')

    @FileSharePreparer()
    def test_create_service_with_socket_timeout_async(self, storage_account_name, storage_account_key):
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
    def test_create_service_with_connection_string_key_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        conn_string = 'AccountName={};AccountKey={};'.format(self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'https')

    @FileSharePreparer()
    def test_create_service_with_connection_string_sas_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.account_name, self.sas_token)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz', transport=AiohttpTestTransport())

            # Assert
            self.assertIsNotNone(service)
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, self.account_name)
            self.assertTrue(service.url.endswith(self.sas_token))

    @FileSharePreparer()
    def test_create_service_with_connection_string_endpoint_protocol_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz', transport=AiohttpTestTransport())

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, '{}.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))
            self.assertEqual(service.secondary_hostname,
                             '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))
            self.assertEqual(service.scheme, 'http')

    @FileSharePreparer()
    def test_create_service_with_connection_string_emulated_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'

            # Act
            with self.assertRaises(ValueError):
                service_type[0].from_connection_string(
                    conn_string, share_name='foo', directory_path='bar', file_path='baz', transport=AiohttpTestTransport())

    @FileSharePreparer()
    def test_create_service_with_connection_string_fails_if_secondary_without_primary_async(self, storage_account_name, storage_account_key):
        for service_type in SERVICES.items():
            self._setup(storage_account_name, storage_account_key)
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.account_name, self.account_key, _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service_type[0].from_connection_string(
                    conn_string, share_name='foo', directory_path='bar', file_path='baz')

    @FileSharePreparer()
    def test_create_service_with_connection_string_succeeds_if_secondary_with_primary_async(self, storage_account_name, storage_account_key):
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
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, 'www.mydomain.com')
            self.assertEqual(service.secondary_hostname, 'www-sec.mydomain.com')

    @FileSharePreparer()
    def test_create_service_with_custom_account_endpoint_path(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};FileEndpoint={};'.format(
                self.account_name, self.account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name="foo", directory_path="bar", file_path="baz")

            # Assert
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        
        service = ShareServiceClient(account_url=custom_account_url)
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/?'))

        service = ShareClient(account_url=custom_account_url, share_name="foo", snapshot="snap")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.share_name, "foo")
        self.assertEqual(service.snapshot, "snap")
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/foo?sharesnapshot=snap&'))

        service = ShareDirectoryClient(account_url=custom_account_url, share_name='foo', directory_path="bar/baz", snapshot="snap")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.share_name, "foo")
        self.assertEqual(service.directory_path, "bar/baz")
        self.assertEqual(service.snapshot, "snap")
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/foo/bar%2Fbaz?sharesnapshot=snap&'))

        service = ShareDirectoryClient(account_url=custom_account_url, share_name='foo', directory_path="")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.share_name, "foo")
        self.assertEqual(service.directory_path, "")
        self.assertEqual(service.snapshot, None)
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/foo?'))

        service = ShareFileClient(account_url=custom_account_url, share_name="foo", file_path="bar/baz/file", snapshot="snap")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.share_name, "foo")
        self.assertEqual(service.directory_path, "bar/baz")
        self.assertEqual(service.file_path, ["bar", "baz", "file"])
        self.assertEqual(service.file_name, "file")
        self.assertEqual(service.snapshot, "snap")
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/foo/bar/baz/file?sharesnapshot=snap&'))

        service = ShareFileClient(account_url=custom_account_url, share_name="foo", file_path="file")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.share_name, "foo")
        self.assertEqual(service.directory_path, "")
        self.assertEqual(service.file_path, ["file"])
        self.assertEqual(service.file_name, "file")
        self.assertEqual(service.snapshot, None)
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/foo/file?'))

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_user_agent_default_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        service = ShareServiceClient(self.account_url(storage_account_name, "file"), credential=self.account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert "azsdk-python-storage-file-share/{}".format(VERSION) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_user_agent_custom_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        custom_app = "TestApp/v1.0"
        service = ShareServiceClient(
            self.account_url(storage_account_name, "file"), credential=self.account_key, user_agent=custom_app, transport=AiohttpTestTransport())

        def callback1(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("TestApp/v1.0 azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback1)

        def callback2(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("TestApp/v2.0 TestApp/v1.0 azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback2, user_agent="TestApp/v2.0")

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_user_agent_append_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        service = ShareServiceClient(self.account_url(storage_account_name, "file"), credential=self.account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("customer_user_agent azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent='customer_user_agent')


    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_closing_pipeline_client_async(self, storage_account_name, storage_account_key):
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
    @AsyncStorageTestCase.await_prepared_test
    async def test_closing_pipeline_client_simple_async(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "file"), credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')
            await service.close()


