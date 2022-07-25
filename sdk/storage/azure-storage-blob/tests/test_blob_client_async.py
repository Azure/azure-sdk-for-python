# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import platform
from datetime import datetime, timedelta

import pytest
from azure.core.credentials import AzureSasCredential
from azure.storage.blob import (
    AccountSasPermissions,
    generate_account_sas,
    ResourceTypes,
    VERSION,
)
from azure.storage.blob.aio import (
    BlobClient,
    ContainerClient,
    BlobServiceClient
)

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer

SERVICES = {
    BlobServiceClient: 'blob',
    ContainerClient: 'blob',
    BlobClient: 'blob',
}
_CONNECTION_ENDPOINTS = {'blob': 'BlobEndpoint'}
_CONNECTION_ENDPOINTS_SECONDARY = {'blob': 'BlobSecondaryEndpoint'}


class TestStorageClientAsync(AsyncStorageRecordedTestCase):

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, url_type, account_name, account_key):
        assert service is not None
        assert service.account_name == account_name
        assert service.credential.account_name == account_name
        assert service.credential.account_key == account_key
        assert '{}.{}.core.windows.net'.format(account_name, url_type) in service.url
        assert '{}-secondary.{}.core.windows.net'.format(account_name, url_type) in service.secondary_endpoint

    def generate_fake_sas_token(self):
        fake_key = "a" * 30 + "b" * 30

        return "?" + generate_account_sas(
            account_name="test",  # name of the storage account
            account_key=fake_key,  # key for the storage account
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True, list=True),
            start=datetime.now() - timedelta(hours=24),
            expiry=datetime.now() + timedelta(days=8),
        )

    # --Direct Parameters Test Cases --------------------------------------------
    @BlobPreparer()
    def test_create_service_with_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, url, storage_account_name, storage_account_key)
            assert service.scheme == 'https'

    @BlobPreparer()
    def test_create_service_with_connection_string(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(storage_account_name, storage_account_key), container_name="test", blob_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service.scheme == 'https'

    @BlobPreparer()
    def test_create_service_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        sas_token = self.generate_fake_sas_token()
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "blob"), credential=sas_token, container_name='foo', blob_name='bar')

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net')
            assert service.url.endswith(sas_token)
            assert service.credential is None

    @BlobPreparer()
    def test_create_service_with_sas_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        sas_token = self.generate_fake_sas_token()
        sas_credential = AzureSasCredential(sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "blob"), credential=sas_credential, container_name='foo', blob_name='bar')

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net')
            assert not service.url.endswith(sas_token)
            assert service.credential == sas_credential

    @BlobPreparer()
    def test_create_service_with_sas_credential_url_raises_if_sas_is_in_uri(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        sas_token = self.generate_fake_sas_token()
        sas_credential = AzureSasCredential(sas_token)

        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                service = service_type(
                    self.account_url(storage_account_name, "blob") + "?sig=foo", credential=sas_credential, container_name='foo', blob_name='bar')

    @BlobPreparer()
    def test_create_service_with_token(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        token_credential = self.generate_oauth_token()
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(storage_account_name, "blob"), credential=token_credential, container_name='foo', blob_name='bar')

            # Assert
            assert service is not None
            assert service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net')
            assert service.credential == token_credential
            assert service.account_name == storage_account_name

    @BlobPreparer()
    def test_create_service_with_token_and_http(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        token_credential = self.generate_oauth_token()
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                url = self.account_url(storage_account_name, "blob").replace('https', 'http')
                service_type(url, credential=token_credential, container_name='foo', blob_name='bar')

    @BlobPreparer()
    def test_create_service_china(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account_name, "blob").replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith(
                'https://{}.{}.core.chinacloudapi.cn'.format(storage_account_name, service_type[1]))
            assert service.secondary_endpoint.startswith(
                'https://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account_name, service_type[1]))

    @BlobPreparer()
    def test_create_service_protocol(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            # Act
            url = self.account_url(storage_account_name, "blob").replace('https', 'http')
            service = service_type[0](
                url, credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service.scheme == 'http'

    @BlobPreparer()
    def test_create_blob_service_anonymous(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        BLOB_SERVICES = [BlobServiceClient, ContainerClient, BlobClient]

        for service_type in BLOB_SERVICES:
            # Act
            service = service_type(self.account_url(storage_account_name, "blob"), container_name='foo', blob_name='bar')

            # Assert
            assert service is not None
            assert service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net')
            assert service.credential is None
            assert service.account_name == storage_account_name

    @BlobPreparer()
    def test_create_blob_service_custom_domain(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith('https://' + storage_account_name + '-secondary.blob.core.windows.net')

    @BlobPreparer()
    def test_create_service_with_socket_timeout(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
    def test_create_service_with_connection_string_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(storage_account_name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            self.validate_standard_account_endpoints(service, service_type[1], storage_account_name, storage_account_key)
            assert service.scheme == 'https'

    @BlobPreparer()
    def test_create_service_with_connection_string_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        sas_token = self.generate_fake_sas_token()
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(storage_account_name, sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(
                conn_string, container_name='foo', blob_name='bar')

            # Assert
            assert service is not None
            assert service.url.startswith('https://' + storage_account_name + '.blob.core.windows.net')
            assert service.url.endswith(sas_token)
            assert service.credential is None
            assert service.account_name == storage_account_name

    @BlobPreparer()
    def test_create_blob_client_with_complete_blob_url(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        blob_url = self.account_url(storage_account_name, "blob") + "/foourl/barurl"
        service = BlobClient(blob_url, credential=storage_account_key, container_name='foo', blob_name='bar')

        # Assert
        assert service.scheme == 'https'
        assert service.container_name == 'foo'
        assert service.blob_name == 'bar'
        assert service.account_name == storage_account_name

    @BlobPreparer()
    def test_creat_serv_w_connstr_endpoint_protocol(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            storage_account_name, storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith(
                    'http://{}.{}.core.chinacloudapi.cn/'.format(storage_account_name, service_type[1]))
            assert service.secondary_endpoint.startswith(
                    'http://{}-secondary.{}.core.chinacloudapi.cn'.format(storage_account_name, service_type[1]))
            assert service.scheme == 'http'

    @BlobPreparer()
    def test_create_service_with_connection_string_emulated(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(storage_account_name, storage_account_key)

            # Act
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @BlobPreparer()
    def test_create_service_with_connection_string_anonymous(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'BlobEndpoint=www.mydomain.com;'

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

        # Assert
        assert service is not None
        assert service.account_name == None
        assert service.credential is None
        assert service.primary_endpoint.startswith('https://www.mydomain.com/')
        with pytest.raises(ValueError):
            service.secondary_endpoint

    @BlobPreparer()
    def test_creat_serv_w_connstr_custm_domain(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com;'.format(
                storage_account_name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith('https://' + storage_account_name + '-secondary.blob.core.windows.net')

    @BlobPreparer()
    def test_creat_serv_w_connstr_custm_dom_trailing_slash(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account_name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith('https://' + storage_account_name + '-secondary.blob.core.windows.net')

    @BlobPreparer()
    def test_creat_serv_w_connstr_custm_dom_2ndry_override(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};BlobEndpoint=www.mydomain.com/;'.format(
                storage_account_name, storage_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", container_name="foo", blob_name="bar")

            # Assert
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith('https://www-sec.mydomain.com/')

    @BlobPreparer()
    def test_creat_serv_w_connstr_fail_if_2ndry_wo_primary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                storage_account_name, storage_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, container_name="foo", blob_name="bar")

    @BlobPreparer()
    def test_creat_serv_w_connstr_pass_if_2ndry_w_primary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
            assert service is not None
            assert service.account_name == storage_account_name
            assert service.credential.account_name == storage_account_name
            assert service.credential.account_key == storage_account_key
            assert service.primary_endpoint.startswith('https://www.mydomain.com/')
            assert service.secondary_endpoint.startswith('https://www-sec.mydomain.com/')

    def test_create_service_with_custom_account_endpoint_path(self):
        account_name = "blobstorage"
        account_key = "blobkey"
        sas_token = self.generate_fake_sas_token()
        custom_account_url = "http://local-machine:11002/custom/account/path/" + sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};BlobEndpoint={};'.format(
                account_name, account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, container_name="foo", blob_name="bar")

            # Assert
            assert service.account_name == account_name
            assert service.credential.account_name == account_name
            assert service.credential.account_key == account_key
            assert service.primary_hostname == 'local-machine:11002/custom/account/path'

        service = BlobServiceClient(account_url=custom_account_url)
        assert service.account_name == None
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/?')

        service = ContainerClient(account_url=custom_account_url, container_name="foo")
        assert service.account_name == None
        assert service.container_name == "foo"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo?')

        service = ContainerClient.from_container_url("http://local-machine:11002/custom/account/path/foo?query=value")
        assert service.account_name == None
        assert service.container_name == "foo"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url == 'http://local-machine:11002/custom/account/path/foo'

        service = BlobClient(account_url=custom_account_url, container_name="foo", blob_name="bar", snapshot="baz")
        assert service.account_name == None
        assert service.container_name == "foo"
        assert service.blob_name == "bar"
        assert service.snapshot == "baz"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path/foo/bar?snapshot=baz&')

        service = BlobClient.from_blob_url("http://local-machine:11002/custom/account/path/foo/bar?snapshot=baz&query=value")
        assert service.account_name == None
        assert service.container_name == "foo"
        assert service.blob_name == "bar"
        assert service.snapshot == "baz"
        assert service.credential == None
        assert service.primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url == 'http://local-machine:11002/custom/account/path/foo/bar?snapshot=baz'

    def test_create_blob_client_with_sub_directory_path_in_blob_name(self):
        blob_url = "https://testaccount.blob.core.windows.net/containername/dir1/sub000/2010_Unit150_Ivan097_img0003.jpg"
        blob_client = BlobClient.from_blob_url(blob_url)
        assert blob_client.container_name == "containername"
        assert blob_client.blob_name == "dir1/sub000/2010_Unit150_Ivan097_img0003.jpg"

        blob_emulator_url = 'http://127.0.0.1:1000/devstoreaccount1/containername/dir1/sub000/2010_Unit150_Ivan097_img0003.jpg'
        blob_client = BlobClient.from_blob_url(blob_emulator_url)
        assert blob_client.container_name == "containername"
        assert blob_client.blob_name == "dir1/sub000/2010_Unit150_Ivan097_img0003.jpg"
        assert blob_client.url == blob_emulator_url

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_request_callback_signed_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        name = self.get_resource_name('cont')

        # Act
        def callback(request):
            if request.http_request.method == 'PUT':
                request.http_request.headers['x-ms-meta-hello'] = 'world'

        # Assert
        try:
            container = await service.create_container(name, raw_request_hook=callback)
            metadata = (await container.get_container_properties()).metadata
            assert metadata == {'hello': 'world'}
        finally:
            await service.delete_container(name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_response_callback(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        name = self.get_resource_name('cont')
        container = service.get_container_client(name)

        # Act
        def callback(response):
            response.http_response.status_code = 200
            response.http_response.headers = {}

        # Assert
        exists = await container.get_container_properties(raw_response_hook=callback)
        assert exists

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_user_agent_default(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "azsdk-python-storage-blob/{}".format(VERSION) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_user_agent_custom(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        custom_app = "TestApp/v1.0"
        service = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), credential=storage_account_key, user_agent=custom_app)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert ("TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert ("TestApp/v2.0 TestApp/v1.0 azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent="TestApp/v2.0")

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_user_agent_append(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert ("customer_user_agent azsdk-python-storage-blob/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())) in response.http_request.headers['User-Agent']

        await service.get_service_properties(raw_response_hook=callback, user_agent='customer_user_agent')

    @BlobPreparer()
    async def test_closing_pipeline_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')

            # Assert
            async with service:
                assert hasattr(service, 'close')
                await service.close()

    @BlobPreparer()
    async def test_closing_pipeline_client_simple(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name='foo', blob_name='bar')
            await service.close()

# ------------------------------------------------------------------------------
