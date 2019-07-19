# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from testcase import (
    StorageTestCase,
    record,
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
        self.account_name = self.settings.STORAGE_ACCOUNT_NAME
        self.account_key = self.settings.STORAGE_ACCOUNT_KEY
        self.sas_token = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'
        self.token_credential = self.generate_oauth_token()
        self.connection_string = self.settings.CONNECTION_STRING

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type):
        self.assertIsNotNone(service)
        self.assertEqual(service.credential.account_name, self.account_name)
        self.assertEqual(service.credential.account_key, self.account_key)
        self.assertTrue('{}.{}.core.windows.net'.format(self.account_name, url_type) in service.url)
        self.assertTrue('{}-secondary.{}.core.windows.net'.format(self.account_name, url_type) in service.secondary_endpoint)

    # --Direct Parameters Test Cases --------------------------------------------
    def test_create_service_with_key(self):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self._get_account_url(), credential=self.account_key, container='foo', blob='bar')

            # Assert
            self.validate_standard_account_endpoints(service, url)
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_connection_string(self):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string, container="test", blob="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_sas(self):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self._get_account_url(), credential=self.sas_token, container='foo', blob='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    def test_create_service_with_token(self):
        for service_type in SERVICES:
            # Act
            service = service_type(
                self._get_account_url(), credential=self.token_credential, container='foo', blob='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertEqual(service.credential, self.token_credential)
            self.assertFalse(hasattr(service.credential, 'account_key'))
            self.assertTrue(hasattr(service.credential, 'get_token'))

    def test_create_service_with_token_and_http(self):
        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                url = self._get_account_url().replace('https', 'http')
                service_type(url, credential=self.token_credential, container='foo', blob='bar')

    def test_create_service_china(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self._get_account_url().replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=self.account_key, container='foo', blob='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith(
                'https://{}.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])))
            self.assertTrue(service.secondary_endpoint.startswith(
                'https://{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])))

    def test_create_service_protocol(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self._get_account_url().replace('https', 'http')
            service = service_type[0](
                url, credential=self.account_key, container='foo', blob='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'http')

    def test_create_blob_service_anonymous(self):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(self._get_account_url(), container='foo', blob='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertIsNone(service.credential)

    def test_create_blob_service_custom_domain(self):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(
                'www.mydomain.com',
                credential={'account_name': self.account_name, 'account_key':self.account_key},
                container='foo',
                blob='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + self.account_name + '-secondary.blob.core.windows.net'))

    def test_create_service_missing_arguments(self):
        # Arrange

        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                service = service_type(None)

                # Assert

    def test_create_service_with_socket_timeout(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self._get_account_url(), credential=self.account_key,
                container='foo', blob='bar')
            service = service_type[0](
                self._get_account_url(), credential=self.account_key,
                container='foo', blob='bar', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------

    def test_create_service_with_connection_string_key(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, container='foo', blob='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_connection_string_sas(self):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.account_name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(
                conn_string, container='foo', blob='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + self.account_name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    def test_create_service_with_connection_string_endpoint_protocol(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, container="foo", blob="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(
                service.primary_endpoint.startswith(
                    'http://{}.{}.core.chinacloudapi.cn/'.format(self.account_name, service_type[1])))
            self.assertTrue(
                service.secondary_endpoint.startswith(
                    'http://{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1])))
            self.assertEqual(service.scheme, 'http')

    def test_create_service_with_connection_string_emulated(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(self.account_name, self.account_key)

            # Act
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container="foo", blob="bar")

    def test_create_service_with_connection_string_anonymous(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'BlobEndpoint=www.mydomain.com;'

            # Act
            service = service_type[0].from_connection_string(conn_string, container="foo", blob="bar")

        # Assert
        self.assertIsNotNone(service)
        self.assertIsNone(service.credential)
        self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
        with self.assertRaises(ValueError):
            service.secondary_endpoint

    def test_create_service_with_connection_string_custom_domain(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com;'.format(
                self.account_name, self.account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container="foo", blob="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + self.account_name + '-secondary.blob.core.windows.net'))

    def test_create_service_with_connection_string_custom_domain_trailing_slash(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                self.account_name, self.account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container="foo", blob="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + self.account_name + '-secondary.blob.core.windows.net'))


    def test_create_service_with_connection_string_custom_domain_secondary_override(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                self.account_name, self.account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", container="foo", blob="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))


    def test_create_service_with_connection_string_fails_if_secondary_without_primary(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.account_name, self.account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container="foo", blob="bar")

    def test_create_service_with_connection_string_succeeds_if_secondary_with_primary(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                self.account_name,
                self.account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, container="foo", blob="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    @record
    def test_request_callback_signed_header(self):
        # Arrange
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key)
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

    @record
    def test_response_callback(self):
        # Arrange
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key)
        name = self.get_resource_name('cont')
        container = service.get_container_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200
            response.http_response.headers.clear()

        # Assert
        exists = container.get_container_properties(raw_response_hook=callback)
        self.assertTrue(exists)

    @record
    def test_user_agent_default(self):
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-blob/12.0.0b1 Python/{} ({})".format(
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback)

    @record
    def test_user_agent_custom(self):
        custom_app = "TestApp/v1.0"
        service = BlobServiceClient(
            self._get_account_url(), credential=self.account_key, user_agent=custom_app)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v1.0 azsdk-python-storage-blob/12.0.0b1 Python/{} ({})".format(
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v2.0 azsdk-python-storage-blob/12.0.0b1 Python/{} ({})".format(
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @record
    def test_user_agent_append(self):
        service = BlobServiceClient(self._get_account_url(), credential=self.account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-blob/12.0.0b1 Python/{} ({}) customer_user_agent".format(
                    platform.python_version(),
                    platform.platform()))

        custom_headers = {'User-Agent': 'customer_user_agent'}
        service.get_service_properties(raw_response_hook=callback, headers=custom_headers)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
