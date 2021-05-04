# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform
import asyncio

from azure.core.credentials import AzureSasCredential
from azure.storage.blob import VERSION
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from _shared.testcase import GlobalStorageAccountPreparer
from _shared.asynctestcase import AsyncStorageTestCase

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


class StorageClientTestAsync(AsyncStorageTestCase):
    def setUp(self):
        super(StorageClientTestAsync, self).setUp()
        self.sas_token = self.generate_sas_token()
        self.token_credential = self.generate_oauth_token()

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type, account_name, account_key):
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, account_name)
        self.assertEqual(service.credential.account_name, account_name)
        self.assertEqual(service.credential.account_key, account_key)
        self.assertTrue('{}.{}.core.windows.net'.format(account_name, url_type) in service.url)
        self.assertTrue('{}-secondary.{}.core.windows.net'.format(account_name, url_type) in service.secondary_endpoint)

    # --Direct Parameters Test Cases --------------------------------------------
    @GlobalStorageAccountPreparer()
    def test_create_service_with_key_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, url, storage_account.name, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @GlobalStorageAccountPreparer()
    def test_create_service_with_connection_string_async(self, resource_group, location, storage_account, storage_account_key):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(storage_account, storage_account_key), container_name="test", blob_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @GlobalStorageAccountPreparer()
    def test_create_service_with_sas_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account, "blob"), credential=self.sas_token, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account.name)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)

    @GlobalStorageAccountPreparer()
    def test_create_service_with_sas_credential_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        sas_credential = AzureSasCredential(self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account, "blob"), credential=sas_credential, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account.name)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
            self.assertFalse(service.url.endswith(self.sas_token))
            self.assertEqual(service.credential, sas_credential)

    @GlobalStorageAccountPreparer()
    def test_create_service_with_sas_credential_url_raises_if_sas_is_in_uri_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        sas_credential = AzureSasCredential(self.sas_token)

        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                service = service_type(
                    self.account_url(storage_account, "blob") + "?sig=foo", credential=sas_credential, container_name='foo', blob_name='bar')

    @GlobalStorageAccountPreparer()
    def test_create_service_with_token_async(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account, "blob"), credential=self.token_credential, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
            self.assertEqual(service.credential, self.token_credential)
            self.assertEqual(service.account_name, storage_account.name)

    @GlobalStorageAccountPreparer()
    def test_create_service_with_token_and_http_async(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                url = self.account_url(storage_account, "blob").replace('https', 'http')
                service_type(url, credential=self.token_credential, container_name='foo', blob_name='bar')

    @GlobalStorageAccountPreparer()
    def test_create_service_china_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account, "blob").replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account.name)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith(
                'https://{}.{}.core.chinacloudapi.cn'.format(storage_account.name, service_type[1])))
            self.assertTrue(service.secondary_endpoint.startswith(
                'https://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account.name, service_type[1])))

    @GlobalStorageAccountPreparer()
    def test_create_service_protocol_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account, "blob").replace('https', 'http')
            service = service_type[0](
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
            self.assertEqual(service.scheme, 'http')

    @GlobalStorageAccountPreparer()
    def test_create_blob_service_anonymous_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(self.account_url(storage_account, "blob"), container_name='foo', blob_name='bar')

            # Assert
            self.assertIsNotNone(service)
            self.assertTrue(service.url.startswith('https://' + storage_account.name + '.blob.core.windows.net'))
            self.assertIsNone(service.credential)
            self.assertEqual(service.account_name, storage_account.name)

    @GlobalStorageAccountPreparer()
    def test_create_blob_service_custom_domain_async(self, resource_group, location, storage_account, storage_account_key):
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
            self.assertEqual(service.account_name, storage_account.name)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.blob.core.windows.net'))

    @GlobalStorageAccountPreparer()
    def test_create_service_with_socket_timeout_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.account_url(storage_account, "blob"), credential=storage_account_key,
                container_name='foo', blob_name='bar')
            service = service_type[0](
                self.account_url(storage_account, "blob"), credential=storage_account_key,
                container_name='foo', blob_name='bar', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------
    @GlobalStorageAccountPreparer()
    def test_create_service_with_connection_string_key_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(storage_account.name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account.name, storage_account_key)
            self.assertEqual(service.scheme, 'https')

    @GlobalStorageAccountPreparer()
    def test_create_service_with_connection_string_sas_async(self, resource_group, location, storage_account, storage_account_key):
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
            self.assertEqual(service.account_name, storage_account.name)

    @GlobalStorageAccountPreparer()
    def test_create_blob_client_with_complete_blob_url_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        blob_url = self.account_url(storage_account, "blob") + "/foourl/barurl"
        service = BlobClient(blob_url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
        self.assertEqual(service.scheme, 'https')
        self.assertEqual(service.container_name, 'foo')
        self.assertEqual(service.blob_name, 'bar')
        self.assertEqual(service.account_name, storage_account.name)

    @GlobalStorageAccountPreparer()
    def test_creat_serv_w_connstr_endpoint_protocol_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            storage_account.name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account.name)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(
                service.primary_endpoint.startswith(
                    'http://{}.{}.core.chinacloudapi.cn/'.format(storage_account.name, service_type[1])))
            self.assertTrue(
                service.secondary_endpoint.startswith(
                    'http://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account.name, service_type[1])))
            self.assertEqual(service.scheme, 'http')

    @GlobalStorageAccountPreparer()
    def test_create_service_with_connection_string_emulated_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(storage_account.name, storage_account_key)

            # Act
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @GlobalStorageAccountPreparer()
    def test_create_service_with_connection_string_anonymous_async(self, resource_group, location, storage_account, storage_account_key):
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

    @GlobalStorageAccountPreparer()
    def test_creat_serv_w_connstr_custm_domain_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account.name)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.blob.core.windows.net'))

    @GlobalStorageAccountPreparer()
    def test_creat_serv_w_connstr_custm_dom_trailing_slash_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account.name)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://' + storage_account.name + '-secondary.blob.core.windows.net'))

    @GlobalStorageAccountPreparer()
    def test_creat_serv_w_connstr_custm_dom_2ndry_override_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account.name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", container_name="foo", blob_name="bar")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, storage_account.name)
            self.assertEqual(service.credential.account_name, storage_account.name)
            self.assertEqual(service.credential.account_key, storage_account_key)
            self.assertTrue(service.primary_endpoint.startswith('https://www.mydomain.com/'))
            self.assertTrue(service.secondary_endpoint.startswith('https://www-sec.mydomain.com/'))

    @GlobalStorageAccountPreparer()
    def test_creat_serv_w_connstr_fail_if_2ndry_wo_primary_async(self, resource_group, location, storage_account, storage_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                storage_account.name, storage_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @GlobalStorageAccountPreparer()
    def test_creat_serv_w_connstr_pass_if_2ndry_w_primary_async(self, resource_group, location, storage_account, storage_account_key):
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
            self.assertEqual(service.account_name, storage_account.name)
            self.assertEqual(service.credential.account_name, storage_account.name)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_request_callback_signed_header_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_response_callback_async(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        name = self.get_resource_name('cont')
        container = service.get_container_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200
            response.http_response.headers = {}

        # Assert
        exists = await container.get_container_properties(raw_response_hook=callback)
        self.assertTrue(exists)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_user_agent_default_async(self, resource_group, location, storage_account, storage_account_key):
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert "azsdk-python-storage-blob/{}".format(VERSION) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_user_agent_custom_async(self, resource_group, location, storage_account, storage_account_key):
        custom_app = "TestApp/v1.0"
        service = BlobServiceClient(
            self.account_url(storage_account, "blob"), credential=storage_account_key, user_agent=custom_app, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("TestApp/v2.0 TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_user_agent_append_async(self, resource_group, location, storage_account, storage_account_key):
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            assert ("customer_user_agent azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent='customer_user_agent')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_closing_pipeline_client(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            async with service:
                assert hasattr(service, 'close')
                await service.close()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_closing_pipeline_client_simple(self, resource_group, location, storage_account, storage_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')
            await service.close()
                
# ------------------------------------------------------------------------------
