# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import platform
import pytest

from azure.core.exceptions import AzureError
from azure.storage.fileshare import (
    VERSION,
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient)

from filetestcase import (
    FileTestCase,
    record,
    TestMode
)
#from azure.storage.common import TokenCredential

# ------------------------------------------------------------------------------
SERVICES = {
    ShareServiceClient: 'file',
    ShareClient: 'file',
    ShareDirectoryClient: 'file',
    ShareFileClient: 'file',
}

_CONNECTION_ENDPOINTS = {'file': 'FileEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'file': 'FileSecondaryEndpoint'}

class StorageFileClientTest(FileTestCase):
    def setUp(self):
        super(StorageFileClientTest, self).setUp()
        self.account_name = self.settings.STORAGE_ACCOUNT_NAME
        self.account_key = self.settings.STORAGE_ACCOUNT_KEY
        self.sas_token = self.generate_sas_token()
        self.token_credential = self.generate_oauth_token()

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
    def test_create_service_with_key(self):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.get_file_url(), credential=self.account_key,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, url)
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_sas(self):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.get_file_url(), credential=self.sas_token,
                share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, self.account_name)
            self.assertTrue(service.url.endswith(self.sas_token))

    def test_create_service_with_token(self):
        for service_type in SERVICES:
            # Act
            # token credential is not available for FileService
            with self.assertRaises(ValueError):
                service_type(self.get_file_url(), credential=self.token_credential,
                             share_name='foo', directory_path='bar', file_path='baz')

    def test_create_service_china(self):
        # Arrange
        url = self.get_file_url().replace('core.windows.net', 'core.chinacloudapi.cn')
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

    def test_create_service_protocol(self):
        # Arrange
        url = self.get_file_url().replace('https', 'http')
        for service_type in SERVICES.items():
            # Act
            service = service_type[0](
                url, credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')

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
                    self.get_file_url(), share_name='foo', directory_path='bar', file_path='baz')

            self.assertEqual(
                str(e.exception),
                'You need to provide either an account shared key or SAS token when creating a storage service.')

    def test_create_service_with_socket_timeout(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.get_file_url(), credential=self.account_key,
                share_name='foo', directory_path='bar', file_path='baz')
            service = service_type[0](
                self.get_file_url(), credential=self.account_key, connection_timeout=22,
                share_name='foo', directory_path='bar', file_path='baz')

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
                conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1])
            self.assertEqual(service.scheme, 'https')

    def test_create_service_with_connection_string_sas(self):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.account_name, self.sas_token)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, self.account_name)
            self.assertTrue(service.url.endswith(self.sas_token))

    def test_create_service_with_connection_string_endpoint_protocol(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.account_name, self.account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, self.account_name)
            self.assertEqual(service.credential.account_name, self.account_name)
            self.assertEqual(service.credential.account_key, self.account_key)
            self.assertEqual(service.primary_hostname, '{}.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))
            self.assertEqual(service.secondary_hostname,
                             '{}-secondary.{}.core.chinacloudapi.cn'.format(self.account_name, service_type[1]))
            self.assertEqual(service.scheme, 'http')

    def test_create_service_with_connection_string_emulated(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'

            # Act
            with self.assertRaises(ValueError):
                service_type[0].from_connection_string(
                    conn_string, share_name='foo', directory_path='bar', file_path='baz')

    def test_create_service_with_connection_string_fails_if_secondary_without_primary(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.account_name, self.account_key, _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service_type[0].from_connection_string(
                    conn_string, share_name='foo', directory_path='bar', file_path='baz')

    def test_create_service_with_connection_string_succeeds_if_secondary_with_primary(self):
        for service_type in SERVICES.items():
            # Arrange
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

    def test_create_service_with_custom_account_endpoint_path(self):
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

    def test_client_request_id_echo(self):
        # client request id is different for every request, so it will never match the recorded one
        pytest.skip("Issue tracked here: https://github.com/Azure/azure-sdk-for-python/issues/8098")
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        request_id_header_name = 'x-ms-client-request-id'
        service = ShareServiceClient(self.get_file_url(), credential=self.account_key)

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

    @record
    def test_user_agent_default(self):
        service = ShareServiceClient(self.get_file_url(), credential=self.account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback)

    @record
    def test_user_agent_custom(self):
        custom_app = "TestApp/v1.0"
        service = ShareServiceClient(
            self.get_file_url(), credential=self.account_key, user_agent=custom_app)

        def callback1(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v1.0 azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback1)

        def callback2(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "TestApp/v2.0 azsdk-python-storage-file-share/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        service.get_service_properties(raw_response_hook=callback2, user_agent="TestApp/v2.0")

    @record
    def test_user_agent_append(self):
        service = ShareServiceClient(self.get_file_url(), credential=self.account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-file-share/{} Python/{} ({}) customer_user_agent".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        custom_headers = {'User-Agent': 'customer_user_agent'}
        service.get_service_properties(raw_response_hook=callback, headers=custom_headers)

    def test_error_with_malformed_conn_str(self):
        # Arrange

        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for service_type in SERVICES.items():
                # Act
                with self.assertRaises(ValueError) as e:
                    service = service_type[0].from_connection_string(conn_str, share_name="test", directory_path="foo/bar", file_path="temp/dat")
                
                if conn_str in("", "foobar", "foo;bar;baz", ";"):
                    self.assertEqual(
                        str(e.exception), "Connection string is either blank or malformed.")
                elif conn_str in ("foobar=baz=foo" , "foo=;bar=;", "=", "=;=="):
                    self.assertEqual(
                        str(e.exception), "Connection string missing required connection details.")

    def test_closing_pipeline_client(self):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.get_file_url(), credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')

            # Assert
            with service:
                assert hasattr(service, 'close')
                service.close()

    def test_closing_pipeline_client_simple(self):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.get_file_url(), credential=self.account_key, share_name='foo', directory_path='bar', file_path='baz')
            service.close()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
