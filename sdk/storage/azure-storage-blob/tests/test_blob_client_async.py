# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform
import asyncio

from azure.storage.blob import VERSION
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from testcase import (
    StorageTestCase,
    record,
    TestMode
)
#from azure.storage.common import TokenCredential

# ------------------------------------------------------------------------------
SERVICES = {
    BlobServiceClient: 'blob',
    ContainerClient: 'blob',
    BlobClient: 'blob',
}

_CONNECTION_ENDPOINTS = {'blob': 'BlobEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'blob': 'BlobSecondaryEndpoint'}


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageClientTestAsync(StorageTestCase):
    def setUp(self):
        super(StorageClientTestAsync, self).setUp()
        self.account_name = self.settings.STORAGE_ACCOUNT_NAME
        self.account_key = self.settings.STORAGE_ACCOUNT_KEY
        self.sas_token = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'
        self.token_credential = self.generate_oauth_token()
        self.connection_string = self.settings.CONNECTION_STRING

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type):
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, self.account_name)
        self.assertEqual(service.credential.account_name, self.account_name)
        self.assertEqual(service.credential.account_key, self.account_key)
        self.assertTrue('{}.{}.core.windows.net'.format(self.account_name, url_type) in service.url)
        self.assertTrue('{}-secondary.{}.core.windows.net'.format(self.account_name, url_type) in service.secondary_endpoint)

    # --Direct Parameters Test Cases --------------------------------------------
    def test_create_service_with_key_async(self):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self._get_account_url(), credential=self.account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, url)
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_connection_string_async(self):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string, container_name="test", blob_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_sas_async(self):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self._get_account_url(), credential=self.sas_token, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    def test_create_service_with_token_async(self):
        for service_type in SERVICES:
            # Act
            service = service_type(
                self._get_account_url(), credential=self.token_credential, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertEqual(service.credential, self.token_credential)
            self.assertFalse(hasattr(service.credential, 'account_key'))
            self.assertTrue(hasattr(service.credential, 'get_token'))
            self.assertEqual(service.account_name, self.account_name)

    def test_create_service_with_token_and_http_async(self):
        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                url = self._get_account_url().replace('https', 'http')
                service_type(url, credential=self.token_credential, container_name='foo', blob_name='bar')

    def test_create_service_china_async(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self._get_account_url().replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=self.account_key, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith(
                'https://{}.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])))
            self.assertTrue(service.secondary_endpoint.startswith(
                'https://{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])))

    def test_create_service_protocol_async(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self._get_account_url().replace('https', 'http')
            service = service_type[0](
                url, credential=self.account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'http')

    def test_create_blob_service_anonymous_async(self):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(self._get_account_url(), container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, self.account_name)

    def test_create_blob_service_custom_domain_async(self):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(
                'www.mydomain.com',
                credential={'account_name': self.account_name, 'account_key':self.account_key},
                container_name='foo',
                blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + self.account_name + '-secondary.blob.core.windows.net'))

    def test_create_service_with_socket_timeout_async(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self._get_account_url(), credential=self.account_key,
                container_name='foo', blob_name='bar')
            service = service_type[0](
                self._get_account_url(), credential=self.account_key,
                container_name='foo', blob_name='bar', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------

    def test_create_service_with_connection_string_key_async(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_connection_string_sas_async(self):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.account_name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, self.account_name)

    def test_create_blob_client_with_complete_blob_url_async(self):
        # Arrange
        blob_url = self._get_account_url() + "/foourl/barurl"
        service = BlobClient(blob_url, credential=self.account_key, container_name='foo', blob_name='bar')

            # Assert
        self.assertEqual(service.scheme, 'https')
        self.assertEqual(service.container_name, 'foo')
        self.assertEqual(service.blob_name, 'bar')
        self.assertEqual(service.account_name, self.account_name)

    def test_create_service_with_connection_string_endpoint_protocol_async(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(
                service.primary_endpoint.startswith(
                    'http://{}.{}.core.chinacloudapi.cn/'.format(self.account_name, service_type[1])))
            self.assertTrue(
                service.secondary_endpoint.startswith(
                    'http://{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])))
            self.assertEqual(service.scheme, 'http')

    def test_create_service_with_connection_string_emulated_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(self.account_name, self.account_key)

            # Act
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    def test_create_service_with_connection_string_anonymous_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'BlobEndpoint=www.mydomain.com;'

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

        # Assert
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, None)
        self.assertIsNone(service.credential)
        self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
        with self.assertRaises(ValueError):
            service.secondary_endpoint

    def test_create_service_with_connection_string_custom_domain_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com;'.format(
                self.account_name, self.account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + self.account_name + '-secondary.blob.core.windows.net'))

    def test_create_service_with_connection_string_custom_domain_trailing_slash_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                self.account_name, self.account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + self.account_name + '-secondary.blob.core.windows.net'))

    def test_create_service_with_connection_string_custom_domain_secondary_override_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                self.account_name, self.account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    def test_create_service_with_connection_string_fails_if_secondary_without_primary_async(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.account_name, self.account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    def test_create_service_with_connection_string_succeeds_if_secondary_with_primary_async(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                self.account_name,
                self.account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    def test_create_service_with_custom_account_endpoint_path(self):
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};BlobEndpoint={};'.format(
                self.account_name, self.account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        
        service = BlobServiceClient(account_url=custom_account_url)
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/?'))

        service = ContainerClient(account_url=custom_account_url, container_name="foo")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.container_name, "foo")
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/foo?'))

        service = ContainerClient.from_container_url("http://local-machine:11002/custom/account/path/foo?query=value")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.container_name, "foo")
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertEqual(service.url, 'http://local-machine:11002/custom/account/path/foo')

        service = BlobClient(account_url=custom_account_url, container_name="foo", blob_name="bar", snapshot="baz")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.container_name, "foo")
        self.assertEqual(service.blob_name, "bar")
        self.assertEqual(service.snapshot, "baz")
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path/foo/bar?snapshot=baz&'))

        service = BlobClient.from_blob_url("http://local-machine:11002/custom/account/path/foo/bar?snapshot=baz&query=value")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.container_name, "foo")
        self.assertEqual(service.blob_name, "bar")
        self.assertEqual(service.snapshot, "baz")
        self.assertEqual(service.credential, None)
        self.assertEqual(service.primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertEqual(service.url, 'http://local-machine:11002/custom/account/path/foo/bar?snapshot=baz')

    async def _test_request_callback_signed_header_async(self):
        # Arrange
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key, transport=AiohttpTestTransport())
        name = self.get_resource_name('cont')

        # Act
        def callback(request):
            if request.http_request.method == 'PUT':
                request.http_request.headers['x-ms-meta-hello'] = 'world'

        # Assert
        try:
            container = await service.create_container(name, raw_request_hook=callback)
            metadata = (await container.get_container_properties()).metadata
            self.assertEqual(metadata, {'hello': 'world'})
        finally:
            await service.delete_container(name)

    @record
    def test_request_callback_signed_header_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_request_callback_signed_header_async())

    async def _test_response_callback_async(self):
        # Arrange
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key, transport=AiohttpTestTransport())
        name = self.get_resource_name('cont')
        container = service.get_container_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200
            response.http_response.headers = {}

        # Assert
        exists = await container.get_container_properties(raw_response_hook=callback)
        self.assertTrue(exists)

    @record
    def test_response_callback_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_response_callback_async())

    async def _test_user_agent_default_async(self):
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        await service.get_service_properties(raw_response_hook=callback)

    @record
    def test_user_agent_default_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_user_agent_default_async())

    async def _test_user_agent_custom_async(self):
        custom_app = "TestApp/v1.0"
        service = BlobServiceClient(
            self._get_account_url(), credential=self.account_key, user_agent=custom_app, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        await service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v2.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        await service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @record
    def test_user_agent_custom_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_user_agent_custom_async())

    async def _test_user_agent_append_async(self):
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-blob/{} Python/{} ({}) customer_user_agent".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        custom_headers = {'User-Agent': 'customer_user_agent'}
        await service.get_service_properties(raw_response_hook=callback, headers=custom_headers)

    @record
    def test_user_agent_append_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_user_agent_append_async())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
