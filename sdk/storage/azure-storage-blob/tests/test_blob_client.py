# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform

from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import AzureError
from azure.storage.blob import (
    VERSION,
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from settings.testcase import BlobPreparer
from devtools_testutils.storage import StorageTestCase

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
        self.sas_token = self.generate_sas_token()
        self.token_credential = self.generate_oauth_token()

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type, name, storage_account_key):
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, name)
        self.assertEqual(service.credential.account_name, name)
        self.assertEqual(service.credential.account_key, storage_account_key)
        self.assertTrue('{}.{}.core.windows.net'.format(name, url_type) in service.url)
        self.assertTrue('{}-secondary.{}.core.windows.net'.format(name, url_type) in service.secondary_endpoint)

    # --Direct Parameters Test Cases --------------------------------------------
    @BlobPreparer()
    def test_create_service_with_key(self, storage_account_name, storage_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, url, storage_account_name, storage_account_key)

            self.assertEqual(service.scheme, 'https')

    @BlobPreparer()
    def test_create_blob_client_with_complete_blob_url(self, storage_account_name, storage_account_key):
        # Arrange
        blob_url = self.account_url(storage_account_name, "blob") + "/foourl/barurl"
        service = BlobClient(blob_url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
        self.assertEqual(service.scheme, 'https')
        self.assertEqual(service.container_name, 'foo')
        self.assertEqual(service.blob_name, 'bar')
        self.assertEqual(service.account_name, storage_account_name)

    @BlobPreparer()
    def test_create_service_with_connection_string(self, storage_account_name, storage_account_key):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(storage_account_name, storage_account_key), container_name="test", blob_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @BlobPreparer()
    def test_create_service_with_sas(self, storage_account_name, storage_account_key):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "blob"), credential=self.sas_token, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertTrue(service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    @BlobPreparer()
    def test_create_service_with_sas_credential(self, storage_account_name, storage_account_key):
        # Arrange
        sas_credential = AzureSasCredential(self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "blob"), credential=sas_credential, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertTrue(service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net'))
            self.assertFalse(service.url.endswith(self.sas_token))
            self.assertEqual(service.credential, sas_credential)

    @BlobPreparer()
    def test_create_service_with_sas_credential_url_raises_if_sas_is_in_uri(self, storage_account_name, storage_account_key):
        # Arrange
        sas_credential = AzureSasCredential(self.sas_token)

        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                service = service_type(
                    self.account_url(storage_account_name, "blob") + "?sig=foo", credential=sas_credential, container_name='foo', blob_name='bar')

    @BlobPreparer()
    def test_create_service_with_token(self, storage_account_name, storage_account_key):
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "blob"), credential=self.token_credential, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net'))
            self.assertEqual(service.credential, self.token_credential)
            self.assertEqual(service.account_name, storage_account_name)

    @BlobPreparer()
    def test_create_service_with_token_and_http(self, storage_account_name, storage_account_key):
        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                url = self.account_url(storage_account_name, "blob").replace('https', 'http')
                service_type(url, credential=self.token_credential, container_name='foo', blob_name='bar')

    @BlobPreparer()
    def test_create_service_china(self, storage_account_name, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account_name, "blob").replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertEqual(service.credential.account_name, storage_account_name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith(
                'https://{}.{}.core.chinacloudapi.cn'.format(storage_account_name, service_type[1])))
            self.assertTrue(service.secondary_endpoint.startswith(
                'https://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account_name, service_type[1])))

    @BlobPreparer()
    def test_create_service_protocol(self, storage_account_name, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account_name, "blob").replace('https', 'http')
            service = service_type[0](
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            self.assertEqual(service.scheme, 'http')

    @BlobPreparer()
    def test_create_blob_service_anonymous(self, storage_account_name, storage_account_key):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(self.account_url(storage_account_name, "blob"), container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertTrue(service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net'))
            self.assertIsNone(service.credential)

    @BlobPreparer()
    def test_create_blob_service_custom_domain(self, storage_account_name, storage_account_key):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(
                'www.mydomain.com',
                credential={'account_name': storage_account_name, 'account_key': storage_account_key},
                container_name='foo',
                blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertEqual(service.credential.account_name, storage_account_name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account_name + '-secondary.blob.core.windows.net'))

    @BlobPreparer()
    def test_create_service_with_socket_timeout(self, storage_account_name, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.account_url(storage_account_name, "blob"), credential=storage_account_key,
                container_name='foo', blob_name='bar')
            service = service_type[0](
                self.account_url(storage_account_name, "blob"), credential=storage_account_key,
                container_name='foo', blob_name='bar', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------

    @BlobPreparer()
    def test_create_service_with_connection_string_key(self, storage_account_name, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(storage_account_name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @BlobPreparer()
    def test_create_service_with_connection_string_sas(self, storage_account_name, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(storage_account_name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, storage_account_name)

    @BlobPreparer()
    def test_create_service_with_connection_string_endpoint_protocol(self, storage_account_name, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            storage_account_name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertEqual(service.credential.account_name, storage_account_name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(
                service.primary_endpoint.startswith(
                    'http://{}.{}.core.chinacloudapi.cn/'.format(storage_account_name, service_type[1])))
            self.assertTrue(
                service.secondary_endpoint.startswith(
                    'http://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account_name, service_type[1])))
            self.assertEqual(service.scheme, 'http')

    @BlobPreparer()
    def test_create_service_with_connection_string_emulated(self, storage_account_name, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(storage_account_name, storage_account_key)

            # Act
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @BlobPreparer()
    def test_create_service_with_cstr_anonymous(self, storage_account_name, storage_account_key):
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

    @BlobPreparer()
    def test_create_service_with_cstr_custom_domain(self, storage_account_name, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com;'.format(
                storage_account_name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertEqual(service.credential.account_name, storage_account_name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account_name + '-secondary.blob.core.windows.net'))

    @BlobPreparer()
    def test_create_service_with_cstr_cust_dmn_trailing_slash(self, storage_account_name, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account_name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertEqual(service.credential.account_name, storage_account_name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account_name + '-secondary.blob.core.windows.net'))

    @BlobPreparer()
    def test_create_service_with_cstr_custom_domain_sec_override(self, storage_account_name, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account_name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertEqual(service.credential.account_name, storage_account_name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    @BlobPreparer()
    def test_create_service_with_cstr_fails_if_sec_without_prim(self, storage_account_name, storage_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                storage_account_name, storage_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @BlobPreparer()
    def test_create_service_with_cstr_succeeds_if_sec_with_prim(self, storage_account_name, storage_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                storage_account_name,
                storage_account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account_name)
            self.assertEqual(service.credential.account_name, storage_account_name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))


    def test_create_service_with_custom_account_endpoint_path(self):
        account_name = "blobstorage"
        account_key = "blobkey"
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};BlobEndpoint={};'.format(
                account_name, account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertEqual(service.account_name, account_name)
            self.assertEqual(service.credential.account_name, account_name)
            self.assertEqual(service.credential.account_key, account_key)
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

    def test_create_blob_client_with_sub_directory_path_in_blob_name(self):
        blob_url = "https://testaccount.blob.core.windows.net/containername/dir1/sub000/2010_Unit150_Ivan097_img0003.jpg"
        blob_client = BlobClient.from_blob_url(blob_url)
        self.assertEqual(blob_client.container_name, "containername")
        self.assertEqual(blob_client.blob_name, "dir1/sub000/2010_Unit150_Ivan097_img0003.jpg")

        blob_emulator_url = 'http://127.0.0.1:1000/devstoreaccount1/containername/dir1/sub000/2010_Unit150_Ivan097_img0003.jpg'
        blob_client = BlobClient.from_blob_url(blob_emulator_url)
        self.assertEqual(blob_client.container_name, "containername")
        self.assertEqual(blob_client.blob_name, "dir1/sub000/2010_Unit150_Ivan097_img0003.jpg")
        self.assertEqual(blob_client.url, blob_emulator_url)

    def test_from_blob_url_too_short_url(self):
        """Test that a useful error message is obtained if user gives incorrect URL"""
        url = "https://testaccount.blob.core.windows.net/containername/"
        with pytest.raises(ValueError, match="Invalid URL"):
            _ = BlobClient.from_blob_url(url)

    def test_create_client_for_emulator(self):
        container_client = ContainerClient(
            account_url='http://127.0.0.1:1000/devstoreaccount1',
            container_name='newcontainer',
            credential='Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==')

        self.assertEqual(container_client.container_name, "newcontainer")
        self.assertEqual(container_client.account_name, "devstoreaccount1")

        ContainerClient.from_container_url('http://127.0.0.1:1000/devstoreaccount1/newcontainer')
        self.assertEqual(container_client.container_name, "newcontainer")
        self.assertEqual(container_client.account_name, "devstoreaccount1")


    @BlobPreparer()
    def test_request_callback_signed_header(self, storage_account_name, storage_account_key):
        # Arrange
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
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

    @BlobPreparer()
    def test_response_callback(self, storage_account_name, storage_account_key):
        # Arrange
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        name = self.get_resource_name('cont')
        container = service.get_container_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200
            response.http_response.headers.clear()

        # Assert
        exists = container.get_container_properties(raw_response_hook=callback)
        self.assertTrue(exists)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_client_request_id_echo(self, storage_account_name, storage_account_key):
        # client request id is different for every request, so it will never match the recorded one
        pytest.skip("Issue tracked here: https://github.com/Azure/azure-sdk-for-python/issues/8098")

        # Arrange
        request_id_header_name = 'x-ms-client-request-id'
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

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

    @BlobPreparer()
    def test_user_agent_default(self, storage_account_name, storage_account_key):
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert "azsdk-python-storage-blob/{}".format(VERSION) in response.http_request.headers['User-Agent']

        service.get_service_properties(raw_response_hook=callback)

    @BlobPreparer()
    def test_user_agent_custom(self, storage_account_name, storage_account_key):
        custom_app = "TestApp/v1.0"
        service = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), credential=storage_account_key, user_agent=custom_app)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("TestApp/v2.0 TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @BlobPreparer()
    def test_user_agent_append(self, storage_account_name, storage_account_key):
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("customer_user_agent azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        service.get_service_properties(raw_response_hook=callback, user_agent='customer_user_agent')

    def test_error_with_malformed_conn_str(self):
        # Arrange
        for conn_str in ["", "foobar", "foo;bar;baz", ";", "foobar=baz=foo" , "foo=;bar=;", "=", "=;=="]:
            for service_type in SERVICES.items():
                # Act
                with self.assertRaises(ValueError) as e:
                    service = service_type[0].from_connection_string(conn_str, blob_name="test", container_name="foo/bar")

                if conn_str in("", "foobar", "foo;bar;baz", ";"):
                    self.assertEqual(
                        str(e.exception), "Connection string is either blank or malformed.")
                elif conn_str in ("foobar=baz=foo" , "foo=;bar=;", "=", "=;=="):
                    self.assertEqual(
                        str(e.exception), "Connection string missing required connection details.")

    @BlobPreparer()
    def test_closing_pipeline_client(self, storage_account_name, storage_account_key):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            with service:
                assert hasattr(service, 'close')
                service.close()

    @BlobPreparer()
    def test_closing_pipeline_client_simple(self, storage_account_name, storage_account_key):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')
            service.close()

# ------------------------------------------------------------------------------
