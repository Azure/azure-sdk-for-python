# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform
import asyncio

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.storage.queue import VERSION
from azure.storage.queue.aio import (
    QueueServiceClient,
    QueueClient
)
from devtools_testutils.storage.aio import AsyncStorageTestCase
from settings.testcase import QueuePreparer

# ------------------------------------------------------------------------------
SERVICES = {
    QueueServiceClient: 'queue',
    QueueClient: 'queue',
}
_CONNECTION_ENDPOINTS = {'queue': 'QueueEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'queue': 'QueueSecondaryEndpoint'}


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageQueueClientTestAsync(AsyncStorageTestCase):
    def setUp(self):
        super(StorageQueueClientTestAsync, self).setUp()
        self.sas_token = self.generate_sas_token()
        self.token_credential = self.generate_oauth_token()

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type, storage_account_name, storage_account_key):
        assert service is not None
        assert service.account_name == storage_account_name
        assert service.credential.account_name == storage_account_name
        assert service.credential.account_key == storage_account_key
        assert f'{storage_account_name}.{url_type}.core.windows.net' in service.url
        assert f'{storage_account_name}-secondary.{url_type}.core.windows.net' in service.secondary_endpoint

    # --Direct Parameters Test Cases --------------------------------------------
    @QueuePreparer()
    def test_create_service_with_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "queue"), credential=storage_account_key, queue_name='foo', transport=AiohttpTestTransport())

            # Assert
            self.validate_standard_account_endpoints(service, url, storage_account_name, storage_account_key)
            assert service.scheme == 'https'

    @QueuePreparer()
    def test_create_service_with_connection_string(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(storage_account_name, storage_account_key), queue_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service.scheme == 'https'

    @QueuePreparer()
    def test_create_service_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "queue"), credential=self.sas_token, queue_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.url.startswith('https://' + storage_account_name + '.queue.core.windows.net')
            assert service.url.endswith(self.sas_token)
            assert service.credential is None

    @QueuePreparer()
    def test_create_service_with_token(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "queue"), credential=self.token_credential, queue_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.url.startswith('https://' + storage_account_name + '.queue.core.windows.net')
            assert service.credential == self.token_credential
            assert not hasattr(service.credential, 'account_key')
            assert hasattr(service.credential, 'get_token')

    @QueuePreparer()
    def test_create_service_with_token_and_http(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                url = self.account_url(storage_account_name, "queue").replace('https', 'http')
                service_type(url, credential=self.token_credential, queue_name='foo')

    @QueuePreparer()
    def test_create_service_china(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account_name, "queue").replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=storage_account_key, queue_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            self.assertTrue(service.primary_endpoint.startswith(
                f'https://{storage_account_name}.{service_type[1]}.core.chinacloudapi.cn'))
            self.assertTrue(service.secondary_endpoint.startswith(
                f'https://{storage_account_name}-secondary.{service_type[1]}.core.chinacloudapi.cn'))

    @QueuePreparer()
    def test_create_service_protocol(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account_name, "queue").replace('https', 'http')
            service = service_type[0](
                url, credential=storage_account_key, queue_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service.scheme == 'http'

    @QueuePreparer()
    def test_create_service_empty_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        QUEUE_SERVICES = [QueueServiceClient, QueueClient]

        for service_type in QUEUE_SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = service_type('testaccount', credential='', queue_name='foo')

            self.assertEqual(
                str(e.exception), "You need to provide either a SAS token or an account shared key to authenticate.")

    @QueuePreparer()
    def test_create_service_with_socket_timeout(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.account_url(storage_account_name, "queue"), credential=storage_account_key, queue_name='foo')
            service = service_type[0](
                self.account_url(storage_account_name, "queue"), credential=storage_account_key,
                queue_name='foo', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------
    @QueuePreparer()
    def test_create_service_with_connection_string_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        conn_string = (
            f'AccountName={storage_account_name};'
            f'AccountKey={storage_account_key};'
            )
        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, queue_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service.scheme == 'https'

    @QueuePreparer()
    def test_create_service_with_connection_string_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        conn_string = (
            f'AccountName={storage_account_name};'
            f'SharedAccessSignature={self.sas_token};'
            )

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, queue_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.url.startswith('https://' + storage_account_name + '.queue.core.windows.net')
            assert service.url.endswith(self.sas_token)
            assert service.credential is None

    @QueuePreparer()
    def test_create_service_with_conn_str_endpoint_protocol(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        conn_string = (
            f'AccountName={storage_account_name};'
            f'AccountKey={storage_account_key};'
            'DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'
            )

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, queue_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            self.assertTrue(
                service.primary_endpoint.startswith(
                    f'http://{storage_account_name}.{service_type[1]}.core.chinacloudapi.cn/'))
            self.assertTrue(
                service.secondary_endpoint.startswith(
                    f'http://{storage_account_name}-secondary.{service_type[1]}.core.chinacloudapi.cn'))
            assert service.scheme == 'http'

    @QueuePreparer()
    def test_create_service_with_connection_string_emulated(self, *args):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'

            # Act
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, queue_name="foo")

    @QueuePreparer()
    def test_create_service_with_connection_string_custom_domain(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            conn_string = (
                f'AccountName={storage_account_name};'
                f'AccountKey={storage_account_key};'
                'QueueEndpoint=www.mydomain.com;')

            # Act
            service = service_type[0].from_connection_string(conn_string, queue_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith(f'https://{storage_account_name}-secondary.queue.core.windows.net')

    @QueuePreparer()
    def test_create_serv_with_cs_custom_dmn_trlng_slash(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            conn_string = (
                f'AccountName={storage_account_name};'
                f'AccountKey={storage_account_key};'
                'QueueEndpoint=www.mydomain.com/;')

            # Act
            service = service_type[0].from_connection_string(conn_string, queue_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith(f'https://{storage_account_name}-secondary.queue.core.windows.net')


    @QueuePreparer()
    def test_create_service_with_cs_custom_dmn_sec_override(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            conn_string = (
                f'AccountName={storage_account_name};'
                f'AccountKey={storage_account_key};'
                'QueueEndpoint=www.mydomain.com/;')

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", queue_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith('https://www-sec.mydomain.com/')

    @QueuePreparer()
    def test_create_service_with_cs_fails_if_sec_without_prim(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        for service_type in SERVICES.items():
            # Arrange
            conn_string = (
                f'AccountName={storage_account_name};'
                f'AccountKey={storage_account_key};'
                f'{_CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1])}=www.mydomain.com;')

            # Act

            # Fails if primary excluded
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, queue_name="foo")

    @QueuePreparer()
    def test_create_service_with_cs_succeeds_if_sec_with_prim(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        for service_type in SERVICES.items():
            # Arrange
            conn_string = (
                f'AccountName={storage_account_name};'
                f'AccountKey={storage_account_key};'
                f'{_CONNECTION_ENDPOINTS.get(service_type[1])}=www.mydomain.com;'
                f'{_CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1])}=www-sec.mydomain.com;')

            # Act
            service = service_type[0].from_connection_string(conn_string, queue_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith('https://www-sec.mydomain.com/')

    @QueuePreparer()
    def test_create_service_with_custom_account_endpoint_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = (
                f'DefaultEndpointsProtocol=http;AccountName={storage_account_name};'
                f'AccountKey={storage_account_key};'
                f'QueueEndpoint={custom_account_url};')

            # Act
            service = service_type[0].from_connection_string(conn_string, queue_name="foo")

            # Assert
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_hostname == 'local-machine:11002/custom/account/path'

        service = QueueServiceClient(account_url=custom_account_url)
        assert service.account_name == None
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/?')

        service = QueueClient(account_url=custom_account_url, queue_name="foo")
        assert service.account_name == None
        assert service.queue_name == "foo"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo?')

        service = QueueClient.from_queue_url("http://local-machine:11002/custom/account/path/foo" + self.sas_token)
        assert service.account_name == None
        assert service.queue_name == "foo"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo?')

    @QueuePreparer()
    async def test_request_callback_signed_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        service = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=storage_account_key)
        name = self.get_resource_name('cont')

        # Act
        try:
            headers = {'x-ms-meta-hello': 'world'}
            queue = await service.create_queue(name, headers=headers)

            # Assert
            metadata_cr = await queue.get_queue_properties()
            metadata = metadata_cr.metadata
            assert metadata == {'hello': 'world'}
        finally:
            await service.delete_queue(name)

    @QueuePreparer()
    async def test_response_callback(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        service = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=storage_account_key, transport=AiohttpTestTransport())
        name = self.get_resource_name('cont')
        queue = service.get_queue_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200


        # Assert
        exists = await queue.get_queue_properties(raw_response_hook=callback)
        assert exists

    @QueuePreparer()
    async def test_user_agent_default(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=storage_account_key, transport=AiohttpTestTransport())

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert f"azsdk-python-storage-queue/{VERSION}" in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

    @QueuePreparer()
    async def test_user_agent_custom(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        custom_app = "TestApp/v1.0"
        service = QueueServiceClient(
            self.account_url(storage_account_name, "queue"), credential=storage_account_key, user_agent=custom_app, transport=AiohttpTestTransport())

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert (
                f"TestApp/v1.0 azsdk-python-storage-queue/{VERSION} "
                f"Python/{platform.python_version()} "
                f"({platform.platform()})") in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert (
                f"TestApp/v2.0 TestApp/v1.0 azsdk-python-storage-queue/{VERSION} "
                f"Python/{platform.python_version()} ({platform.platform()})"
                ) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @QueuePreparer()
    async def test_user_agent_append(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=storage_account_key, transport=AiohttpTestTransport())

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert (f"customer_user_agent azsdk-python-storage-queue/{VERSION} "
                    f"Python/{platform.python_version()} ({platform.platform()})"
                ) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent='customer_user_agent')

    @QueuePreparer()
    async def test_closing_pipeline_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "queue"), credential=storage_account_key, queue_name='queue')

            # Assert
            async with service:
                assert hasattr(service, 'close')
                await service.close()

    @QueuePreparer()
    async def test_closing_pipeline_client_simple(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "queue"), credential=storage_account_key, queue_name='queue')
            await service.close()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
