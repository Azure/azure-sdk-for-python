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
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.storage.queue import VERSION
from azure.storage.queue.aio import (
    QueueServiceClient,
    QueueClient
)
from asyncqueuetestcase import (
    AsyncQueueTestCase,
)

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


class StorageQueueClientTestAsync(AsyncQueueTestCase):
    def setUp(self):
        super(StorageQueueClientTestAsync, self).setUp()
        self.sas_token = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'
        self.token_credential = self.generate_oauth_token()

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type, storage_account, storage_account_key):
        self.assertIsNotNone(service)
        self.assertEqual(service.credential.account_name, storage_account.name)
        self.assertEqual(service.credential.account_key, storage_account_key)
        self.assertTrue('{}.{}.core.windows.net'.format(storage_account.name, url_type) in service.url)
        self.assertTrue('{}-secondary.{}.core.windows.net'.format(storage_account.name, url_type) in service.secondary_endpoint)

    # --Direct Parameters Test Cases --------------------------------------------
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_key(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self._account_url(storage_account.name), credential=storage_account_key, queue='foo', transport=AiohttpTestTransport())

            # Assert
            self.validate_standard_account_endpoints(service, url, storage_account, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string(self, resource_group, location, storage_account, storage_account_key):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(storage_account, storage_account_key), queue="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_sas(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self._account_url(storage_account.name), credential=self.sas_token, queue='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.queue.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_token(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES:
            # Act
            service = service_type(
                self._account_url(storage_account.name), credential=self.token_credential, queue='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.queue.core.windows.net'))
            self.assertEqual(service.credential, self.token_credential)
            self.assertFalse(hasattr(service.credential, 'account_key'))
            self.assertTrue(hasattr(service.credential, 'get_token'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_token_and_http(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                url = self._account_url(storage_account.name).replace('https', 'http')
                service_type(url, credential=self.token_credential, queue='foo')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_china(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self._account_url(storage_account.name).replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=storage_account_key, queue='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith(
                'https://{}.{}.core.chinacloudapi.cn'.format(storage_account.name, service_type[1])))
            self.assertTrue(service.secondary_endpoint.startswith(
                'https://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account.name, service_type[1])))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_protocol(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self._account_url(storage_account.name).replace('https', 'http')
            service = service_type[0](
                url, credential=storage_account_key, queue='foo')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account, storage_account_key)
            self.assertEqual(service.scheme, 'http')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_empty_key(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        QUEUE_SERVICES = [QueueServiceClient, QueueClient]

        for service_type in QUEUE_SERVICES:
            # Act
            with self.assertRaises(ValueError) as e:
                test_service = service_type('testaccount', credential='', queue='foo')

            self.assertEqual(
                str(e.exception), "You need to provide either a SAS token or an account key to authenticate.")

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_missing_arguments(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                service = service_type(None)
                # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_socket_timeout(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self._account_url(storage_account.name), credential=storage_account_key, queue='foo')
            service = service_type[0](
                self._account_url(storage_account.name), credential=storage_account_key,
                queue='foo', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account, storage_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string_key(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(storage_account.name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, queue='foo')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string_sas(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(storage_account.name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, queue='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.queue.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_conn_str_endpoint_protocol(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            storage_account.name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, queue="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(
                service.primary_endpoint.startswith(
                    'http://{}.{}.core.chinacloudapi.cn/'.format(storage_account.name, service_type[1])))
            self.assertTrue(
                service.secondary_endpoint.startswith(
                    'http://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account.name, service_type[1])))
            self.assertEqual(service.scheme, 'http')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string_emulated(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(storage_account.name, storage_account_key)

            # Act
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, queue="foo")

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string_custom_domain(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};QueueEndpoint=www.mydomain.com;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, queue="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.queue.core.windows.net'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_serv_with_cs_custom_dmn_trlng_slash(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};QueueEndpoint=www.mydomain.com/;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, queue="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.queue.core.windows.net'))


    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cs_custom_dmn_sec_override(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};QueueEndpoint=www.mydomain.com/;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", queue="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cs_fails_if_sec_without_prim(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                storage_account.name, storage_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, queue="foo")

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cs_succeeds_if_sec_with_prim(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                storage_account.name,
                storage_account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, queue="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_request_callback_signed_header(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        service = QueueServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        name = self.get_resource_name('cont')

        # Act
        try:
            headers = {'x-ms-meta-hello': 'world'}
            queue = await service.create_queue(name, headers=headers)

            # Assert
            metadata_cr = await queue.get_queue_properties()
            metadata = metadata_cr.metadata
            self.assertEqual(metadata, {'hello': 'world'})
        finally:
            await service.delete_queue(name)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_response_callback(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        service = QueueServiceClient(self._account_url(storage_account.name), credential=storage_account_key, transport=AiohttpTestTransport())
        name = self.get_resource_name('cont')
        queue = service.get_queue_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200
            

        # Assert
        exists = await queue.get_queue_properties(raw_response_hook=callback)
        self.assertTrue(exists)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_user_agent_default(self, resource_group, location, storage_account, storage_account_key):
        service = QueueServiceClient(self._account_url(storage_account.name), credential=storage_account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-queue/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        await service.get_service_properties(raw_response_hook=callback)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_user_agent_custom(self, resource_group, location, storage_account, storage_account_key):
        custom_app = "TestApp/v1.0"
        service = QueueServiceClient(
            self._account_url(storage_account.name), credential=storage_account_key, user_agent=custom_app, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v1.0 azsdk-python-storage-queue/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        await service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v2.0 azsdk-python-storage-queue/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        await service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_user_agent_append(self, resource_group, location, storage_account, storage_account_key):
        service = QueueServiceClient(self._account_url(storage_account.name), credential=storage_account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-queue/{} Python/{} ({}) customer_user_agent".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        custom_headers = {'User-Agent': 'customer_user_agent'}
        await service.get_service_properties(raw_response_hook=callback, headers=custom_headers)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
