# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform

from azure.core.exceptions import AzureError
from azure.storage.blob import (
    VERSION,
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from testcase import (
    StorageTestCase,
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


class StorageClientTest(StorageTestCase):
    def setUp(self):
        super(StorageClientTest, self).setUp()
        self.sas_token = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'
        self.token_credential = self.generate_oauth_token()

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type, name, storage_account_key):
        self.assertIsNotNone(service)
        self.assertEqual(service.credential.account_name, name)
        self.assertEqual(service.credential.account_key, storage_account_key)
        self.assertTrue('{}.{}.core.windows.net'.format(name, url_type) in service.url)
        self.assertTrue('{}-secondary.{}.core.windows.net'.format(name, url_type) in service.secondary_endpoint)

    # --Direct Parameters Test Cases --------------------------------------------
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_key(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self._account_url(storage_account.name), credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, url, storage_account.name, storage_account_key)

            self.assertEqual(service.scheme, 'https')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_client_with_complete_blob_url(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        blob_url = self._account_url(storage_account.name) + "/foourl/barurl"
        service = BlobClient(blob_url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
        self.assertEqual(service.scheme, 'https')
        self.assertEqual(service.container_name, 'foo')
        self.assertEqual(service.blob_name, 'bar')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string(self, resource_group, location, storage_account, storage_account_key):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(storage_account, storage_account_key), container_name="test", blob_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_sas(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self._account_url(storage_account.name), credential=self.sas_token, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_token(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES:
            # Act
            service = service_type(
                self._account_url(storage_account.name), credential=self.token_credential, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
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
                service_type(url, credential=self.token_credential, container_name='foo', blob_name='bar')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_china(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self._account_url(storage_account.name).replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

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
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
            self.assertEqual(service.scheme, 'http')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_service_anonymous(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(self._account_url(storage_account.name), container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
            self.assertIsNone(service.credential)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_service_custom_domain(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(
                'www.mydomain.com',
                credential={'account_name': storage_account.name, 'account_key': storage_account_key},
                container_name='foo',
                blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.blob.core.windows.net'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_missing_arguments(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                if service_type == BlobServiceClient:
                    service = service_type(None)
                if service_type == ContainerClient:
                    service = service_type(None, None)
                if service_type == BlobClient:
                    service = service_type(None, None, None)

                # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_socket_timeout(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self._account_url(storage_account.name), credential=storage_account_key,
                container_name='foo', blob_name='bar')
            service = service_type[0](
                self._account_url(storage_account.name), credential=storage_account_key,
                container_name='foo', blob_name='bar', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
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
            service = service_type[0].from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string_sas(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(storage_account.name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_connection_string_endpoint_protocol(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            storage_account.name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

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
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cstr_anonymous(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'BlobEndpoint=www.mydomain.com;'

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

        # Assert
        self.assertIsNotNone(service)
        self.assertIsNone(service.credential)
        self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
        with self.assertRaises(ValueError):
            service.secondary_endpoint

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cstr_custom_domain(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.blob.core.windows.net'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cstr_cust_dmn_trailing_slash(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.blob.core.windows.net'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cstr_custom_domain_sec_override(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cstr_fails_if_sec_without_prim(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                storage_account.name, storage_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_service_with_cstr_succeeds_if_sec_with_prim(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                storage_account.name,
                storage_account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_request_callback_signed_header(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        service = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        name = self.get_resource_name('cont')

        # Act
        def callback(request):
            if request.http_request.method == 'PUT':
                request.http_request.headers['x-ms-meta-hello'] = 'world'

        # Assert
        try:
            container = service.create_container(name, raw_request_hook=callback)
            metadata = container.get_container_properties().metadata
            self.assertEqual(metadata, {'hello': 'world'})
        finally:
            service.delete_container(name)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_response_callback(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        service = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        name = self.get_resource_name('cont')
        container = service.get_container_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200
            response.http_response.headers.clear()

        # Assert
        exists = container.get_container_properties(raw_response_hook=callback)
        self.assertTrue(exists)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_client_request_id_echo(self, resource_group, location, storage_account, storage_account_key):
        # client request id is different for every request, so it will never match the recorded one
        if not self.is_live:
            return

        # Arrange
        request_id_header_name = 'x-ms-client-request-id'
        service = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key)

        # Act make the client request ID slightly different
        def callback(response):
            response.http_response.status_code = 200
            response.http_response.headers[request_id_header_name] += '1'

        # Assert the client request ID validation is working
        with self.assertRaises(AzureError):
            service.get_service_properties(raw_response_hook=callback)

        # Act remove the echoed client request ID
        def callback(response):
            response.status_code = 200
            del response.http_response.headers[request_id_header_name]

        # Assert the client request ID validation is not throwing when the ID is not echoed
        service.get_service_properties(raw_response_hook=callback)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_user_agent_default(self, resource_group, location, storage_account, storage_account_key):
        service = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_user_agent_custom(self, resource_group, location, storage_account, storage_account_key):
        custom_app = "TestApp/v1.0"
        service = BlobServiceClient(
            self._account_url(storage_account.name), credential=storage_account_key, user_agent=custom_app)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v2.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_user_agent_append(self, resource_group, location, storage_account, storage_account_key):
        service = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-blob/{} Python/{} ({}) customer_user_agent".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        custom_headers = {'User-Agent': 'customer_user_agent'}
        service.get_service_properties(raw_response_hook=callback, headers=custom_headers)


# ------------------------------------------------------------------------------
