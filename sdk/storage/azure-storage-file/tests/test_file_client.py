# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import platform

from azure.storage.file import (
    FileServiceClient,
    ShareClient,
    DirectoryClient,
    FileClient)

from filetestcase import (
    FileTestCase,
    record,
)
#from azure.storage.common import TokenCredential

# ------------------------------------------------------------------------------
SERVICES = {
    FileServiceClient: 'file',
    ShareClient: 'file',
    DirectoryClient: 'file',
    FileClient: 'file',
}

_CONNECTION_ENDPOINTS = {'file': 'FileEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'file': 'FileSecondaryEndpoint'}

class StorageFileClientTest(FileTestCase):
    def setUp(self):
        super(StorageFileClientTest, self).setUp()
        self.account_name = self.settings.STORAGE_ACCOUNT_NAME
        self.account_key = self.settings.STORAGE_ACCOUNT_KEY
        self.sas_token = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'
        self.token_credential = self.generate_oauth_token()

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, service_type, protocol='https'):
        self.assertIsNotNone(service)
        self.assertEqual(service.credential.account_name, self.account_name)
        self.assertEqual(service.credential.account_key, self.account_key)
        self.assertTrue(service.primary_endpoint.startswith('{}://{}.{}.core.windows.net/'.format(
            protocol, self.account_name, service_type)))
        self.assertTrue(service.secondary_endpoint.startswith('{}://{}-secondary.{}.core.windows.net/'.format(
            protocol, self.account_name, service_type)))

    # --Direct Parameters Test Cases --------------------------------------------
    def test_create_service_with_key(self):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.get_file_url(), credential=self.account_key,
                share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, url)
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_sas(self):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.get_file_url(), credential=self.sas_token,
                share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertIsNone(service.credential)
            self.assertTrue(service.url.endswith(self.sas_token))

    def test_create_service_with_token(self):
        for service_type in SERVICES:
            # Act
            # token credential is not available for FileService
            with self.assertRaises(ValueError):
                service_type(self.get_file_url(), credential=self.token_credential,
                             share='foo', directory_path='bar', file_path='baz')

    def test_create_service_china(self):
        # Arrange
        url = self.get_file_url().replace('core.windows.net', 'core.chinacloudapi.cn')
        for service_type in SERVICES.items():
            # Act
            service = service_type[0](
                url, credential=self.account_key,
                share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, '{}.{}.core.chinacloudapi.cn'.format(
                self.account_name, service_type[1]))
            self.assertEqual(service.secondary_hostname,
                             '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))

    def test_create_service_protocol(self):
        # Arrange
        url = self.get_file_url().replace('https', 'http')
        for service_type in SERVICES.items():
            # Act
            service = service_type[0](
                url, credential=self.account_key, share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], protocol='http')
            self.assertEqual(service.scheme, 'http')


    def test_create_service_empty_key(self):
        # Arrange
        for service_type in SERVICES:
            # Act
            # Passing an empty key to create account should fail.
            with self.assertRaises(ValueError) as e:
                service_type(
                    self.get_file_url(), share='foo', directory_path='bar', file_path='baz')

            self.assertEqual(
                str(e.exception),
                'You need to provide either an account key or SAS token when creating a storage service.')

    def test_create_service_missing_arguments(self):
        # Arrange

        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                service = service_type(None)

    def test_create_service_with_socket_timeout(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.get_file_url(), credential=self.account_key,
                share='foo', directory_path='bar', file_path='baz')
            service = service_type[0](
                self.get_file_url(), credential=self.account_key, connection_timeout=22,
                share='foo', directory_path='bar', file_path='baz')

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
                conn_string, share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_connection_string_sas(self):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.account_name, self.sas_token)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertIsNone(service.credential)
            self.assertTrue(service.url.endswith(self.sas_token))

    def test_create_service_with_connection_string_endpoint_protocol(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, '{}.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))
            self.assertEqual(service.secondary_hostname,
                             '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))
            self.assertEqual(service.scheme, 'http')

    def test_create_service_with_connection_string_emulated(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(self.account_name, self.account_key)

            # Act
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(
                    conn_string, share='foo', directory_path='bar', file_path='baz')

    def test_create_service_with_connection_string_fails_if_secondary_without_primary(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.account_name, self.account_key, _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(
                    conn_string, share='foo', directory_path='bar', file_path='baz')

    def test_create_service_with_connection_string_succeeds_if_secondary_with_primary(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                self.account_name, self.account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(
                conn_string, share='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, 'www.mydomain.com')
            self.assertEqual(service.secondary_hostname, 'www-sec.mydomain.com')

    @record
    def test_user_agent_default(self):
        service = FileServiceClient(self.get_file_url(), credential=self.account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-file/12.0.0b1 Python/{} ({})".format(
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback)

    @record
    def test_user_agent_custom(self):
        custom_app = "TestApp/v1.0"
        service = FileServiceClient(
            self.get_file_url(), credential=self.account_key, user_agent=custom_app)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v1.0 azsdk-python-storage-file/12.0.0b1 Python/{} ({})".format(
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v2.0 azsdk-python-storage-file/12.0.0b1 Python/{} ({})".format(
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @record
    def test_user_agent_append(self):
        service = FileServiceClient(self.get_file_url(), credential=self.account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-file/12.0.0b1 Python/{} ({}) customer_user_agent".format(
                    platform.python_version(),
                    platform.platform()))

        custom_headers = {'User-Agent': 'customer_user_agent'}
        service.get_service_properties(raw_response_hook=callback, headers=custom_headers)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
