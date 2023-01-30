# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
import pytest
import platform
import os

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.data.tables.aio import TableServiceClient, TableClient
from azure.data.tables import __version__ as VERSION, TableTransactionError
from azure.data.tables._constants import DEFAULT_COSMOS_ENDPOINT_SUFFIX
from test_table_client_cosmos import validate_standard_account_endpoints

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import cosmos_decorator_async

SERVICES = {
    TableServiceClient: 'cosmos',
    TableClient: 'cosmos',
}

_CONNECTION_ENDPOINTS = {'table': 'TableEndpoint', 'cosmos': 'TableEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'table': 'TableSecondaryEndpoint', 'cosmos': 'TableSecondaryEndpoint'}


class TestTableClientCosmosAsync(AzureRecordedTestCase, AsyncTableTestCase):

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_default_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        tables = service.list_tables(raw_response_hook=callback)
        assert tables is not None

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_custom_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        custom_app = "TestApp/v1.0"
        service = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key, user_agent=custom_app)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        tables = service.list_tables(raw_response_hook=callback)
        assert tables is not None

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "TestApp/v2.0 TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_append(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert response.http_request.headers['User-Agent'] == 'customer_user_agent'

        custom_headers = {'User-Agent': 'customer_user_agent'}
        tables = service.list_tables(raw_response_hook=callback, headers=custom_headers)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1
            
    @pytest.mark.live_test_only
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_name_errors_bad_chars(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        endpoint = self.account_url(tables_cosmos_account_name, "cosmos")
        
        # cosmos table names must be a non-empty string without chars '\', '/', '#', '?', trailing space, and less than 255 chars.
        invalid_table_names = ["\\", "//", "#", "?", "- "]
        for invalid_name in invalid_table_names:
            client = TableClient(
                endpoint=endpoint, credential=tables_primary_cosmos_account_key, table_name=invalid_name)
            async with client:
                with pytest.raises(ValueError) as error:
                    await client.create_table()
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                try:
                    with pytest.raises(ValueError) as error:
                        await client.delete_table()
                    assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                except HttpResponseError as error:
                    # Delete table returns a MethodNotAllowed for tablename == "\"
                    if error.error_code != 'MethodNotAllowed':
                        raise
                with pytest.raises(ValueError) as error:
                    await client.create_entity({'PartitionKey': 'foo', 'RowKey': 'foo'})
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.upsert_entity({'PartitionKey': 'foo', 'RowKey': 'foo'})
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.delete_entity("PK", "RK")
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                with pytest.raises(ValueError) as error:
                    batch = []
                    batch.append(('upsert', {'PartitionKey': 'A', 'RowKey': 'B'}))
                    await client.submit_transaction(batch)
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
        
    @pytest.mark.live_test_only
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_name_errors_bad_length(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        endpoint = self.account_url(tables_cosmos_account_name, "cosmos")
        
        # cosmos table names must be a non-empty string without chars '\', '/', '#', '?', and less than 255 chars.
        client = TableClient(endpoint=endpoint, credential=tables_primary_cosmos_account_key, table_name="-"*255)
        async with client:
            with pytest.raises(ValueError) as error:
                await client.create_table()
            assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
            with pytest.raises(ResourceNotFoundError):
                await client.create_entity({'PartitionKey': 'foo', 'RowKey': 'foo'})
            with pytest.raises(ResourceNotFoundError):
                await client.upsert_entity({'PartitionKey': 'foo', 'RowKey': 'foo'})
            with pytest.raises(TableTransactionError) as error:
                batch = []
                batch.append(('upsert', {'PartitionKey': 'A', 'RowKey': 'B'}))
                await client.submit_transaction(batch)
            assert error.value.error_code == 'ResourceNotFound'


class TestTableClientCosmosAsyncUnitTests(AsyncTableTestCase):
    tables_cosmos_account_name = "fake_cosmos_account"
    tables_primary_cosmos_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"
    credential = AzureNamedKeyCredential(name=tables_cosmos_account_name, key=tables_primary_cosmos_account_key)

    # --Direct Parameters Test Cases --------------------------------------------
    @pytest.mark.asyncio
    async def test_create_service_with_key_async(self):
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(self.tables_cosmos_account_name, url), credential=self.credential, table_name='foo')

            # Assert
            validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_async(self):
        for client, url in SERVICES.items():
            # Act
            service = client.from_connection_string(
                self.cosmos_connection_string(
                    self.tables_cosmos_account_name,
                    self.tables_primary_cosmos_account_key),
                    table_name="test",
                    endpoint_type=url
                )

            # Assert
            validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'

    @pytest.mark.asyncio
    async def test_create_service_with_sas(self):
        # Arrange
        endpoint_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
        self.sas_token = self.generate_sas_token()
        self.sas_token = AzureSasCredential(self.sas_token)
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(self.tables_cosmos_account_name, "cosmos"), credential=self.sas_token, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + '.table.' + endpoint_suffix)
            assert isinstance(service.credential, AzureSasCredential)

    @pytest.mark.asyncio
    async def test_create_service_with_token_async(self):
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        endpoint_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
        self.token_credential = AzureSasCredential("fake_sas_credential")
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=self.token_credential, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + '.table.' + endpoint_suffix)
            assert service.credential ==  self.token_credential
            assert not hasattr(service.credential, 'account_key')

    @pytest.mark.skip("HTTP prefix does not raise an error")
    @pytest.mark.asyncio
    async def test_create_service_with_token_and_http(self):
        self.token_credential = self.generate_fake_token()
        for client, url in SERVICES:
            # Act
            with pytest.raises(ValueError):
                url = self.account_url(self.tables_cosmos_account_name, url).replace('https', 'http')
                client(url, credential=AzureSasCredential("fake_sas_credential"), table_name='foo', endpoint_type=url)

    @pytest.mark.asyncio
    async def test_create_service_protocol_async(self):
        for client, url in SERVICES.items():
            # Act
            url = self.account_url(self.tables_cosmos_account_name, url).replace('https', 'http')
            service = client(url, credential=self.credential, table_name='foo', endpoint_type=url)

            # Assert
            validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme ==  'http'

    @pytest.mark.asyncio
    async def test_create_service_empty_key_async(self):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            with pytest.raises(ValueError) as e:
                test_service = client('testaccount', credential='', table_name='foo', endpoint_type=url)

            assert str(e.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

    @pytest.mark.asyncio
    async def test_create_service_with_socket_timeout_async(self):
        for client, url in SERVICES.items():
            # Act
            default_service = client(
                self.account_url(self.tables_cosmos_account_name, url),
                credential=self.credential,
                table_name='foo',
                endpoint_type=url
            )
            service = client(
                self.account_url(self.tables_cosmos_account_name, url),
                credential=self.credential,
                table_name='foo',
                connection_timeout=22,
                endpoint_type=url
            )

            # Assert
            validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout == 300

    # --Connection String Test Cases --------------------------------------------
    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_key_async(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

        for client, url in SERVICES.items():
            # Act
            service = client.from_connection_string(conn_string, table_name='foo', endpoint_type=url)

            # Assert
            validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_sas_async(self):
        self.sas_token = self.generate_sas_token()
        self.sas_token = AzureSasCredential(self.sas_token)
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.tables_cosmos_account_name, self.sas_token)

        for client, url in SERVICES.items():
            # Act
            service = client.from_connection_string(conn_string, table_name='foo', endpoint_type=url)
            endpoint_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + '.table.' + endpoint_suffix)
            assert isinstance(service.credential , AzureSasCredential)

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_cosmos_async(self):
        # Arrange
        endpoint_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
        conn_string = 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.{2}:443/;'.format(
            self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key, endpoint_suffix)

        for client, url in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name='foo', endpoint_type=url)

            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + '.table.' + endpoint_suffix)
            assert service.credential.named_key.name ==  self.tables_cosmos_account_name
            assert service.credential.named_key.key ==  self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://' + self.tables_cosmos_account_name + '.table.' + endpoint_suffix)
            assert service.scheme ==  'https'

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_emulated_async(self):
        # Arrange
        for client, url in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            with pytest.raises(ValueError):
                service = client.from_connection_string(conn_string, table_name="foo", endpoint_type=url)

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_custom_domain_async(self):
        # Arrange
        for client, url in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            service = client.from_connection_string(conn_string, table_name="foo", endpoint_type=url)

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_trailing_slash_async(self):
        # Arrange
        for client, url in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            service = client.from_connection_string(conn_string, table_name="foo", endpoint_type=url)

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_sec_override_async(self):
        # Arrange
        for client, url in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            service = client.from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", table_name="foo", endpoint_type=url
            )

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_fails_if_sec_without_primary_async(self):
        for client, url in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(url)
            )

            # Fails if primary excluded
            with pytest.raises(ValueError):
                service = client.from_connection_string(conn_string, table_name="foo", endpoint_type=url)

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_succeeds_if_sec_with_primary_async(self):
        for client, url in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                self.tables_cosmos_account_name,
                self.tables_primary_cosmos_account_key,
                _CONNECTION_ENDPOINTS.get(url),
                _CONNECTION_ENDPOINTS_SECONDARY.get(url))

            # Act
            service = client.from_connection_string(conn_string, table_name="foo", endpoint_type=url)

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_custom_account_endpoint_path_async(self):
        self.sas_token = self.generate_sas_token()
        self.sas_token = AzureSasCredential(self.sas_token)
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token.signature
        for client, url  in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};TableEndpoint={};'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key, custom_account_url)

            # Act
            service = client.from_connection_string(conn_string, table_name="foo", endpoint_type=url)

            # Assert
            assert service.account_name == self.tables_cosmos_account_name
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_hostname == 'local-machine:11002/custom/account/path'
            assert service.scheme ==  'http'

        service = TableServiceClient(endpoint=custom_account_url)
        assert service.account_name == "custom"
        assert service.credential == None
        assert service._primary_hostname == 'local-machine:11002/custom/account/path'
        # mine doesnt have a question mark at the end
        assert service.url.startswith('http://local-machine:11002/custom/account/path')
        assert service.scheme ==  'http'

        service = TableClient(endpoint=custom_account_url, table_name="foo")
        assert service.account_name == "custom"
        assert service.table_name == "foo"
        assert service.credential == None
        assert service._primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path')
        assert service.scheme ==  'http'

        service = TableClient.from_table_url("http://local-machine:11002/custom/account/path/foo" + self.sas_token.signature)
        assert service.account_name == "custom"
        assert service.table_name == "foo"
        assert service.credential == None
        assert service._primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path')
        assert service.scheme ==  'http'

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_table_url_async(self):
        # Arrange
        table_url = self.account_url(self.tables_cosmos_account_name, "cosmos") + "/foo"
        service = TableClient(table_url, table_name='bar', credential=self.credential)

        # Assert
        assert service.scheme ==  'https'
        assert service.table_name ==  'bar'
        assert service.account_name ==  self.tables_cosmos_account_name

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_url_async(self):
        # Arrange
        table_url = "https://{}.table.cosmos.azure.com:443/foo".format(self.tables_cosmos_account_name)
        service = TableClient(table_url, table_name='bar', credential=self.credential)

        # Assert
        assert service.scheme ==  'https'
        assert service.table_name ==  'bar'
        assert service.account_name ==  self.tables_cosmos_account_name

    @pytest.mark.asyncio
    async def test_error_with_malformed_conn_str_async(self):
        # Arrange

        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for client, url  in SERVICES.items():
                # Act
                with pytest.raises(ValueError) as e:
                    service = client.from_connection_string(conn_str, table_name="test", endpoint_type=url)

                if conn_str in("", "foobar", "foo;bar;baz", ";", "foo=;bar=;", "=", "=;=="):
                    assert str(e.value) == "Connection string is either blank or malformed."
                elif conn_str in ("foobar=baz=foo"):
                   assert str(e.value) == "Connection string missing required connection details."

    def test_create_client_for_cosmos_emulator(self):
        emulator_credential = AzureNamedKeyCredential('localhost', self.tables_primary_cosmos_account_key)
        emulator_connstr = "DefaultEndpointsProtocol=http;AccountName=localhost;AccountKey={};TableEndpoint=http://localhost:8902/;".format(
            self.tables_primary_cosmos_account_key
        )

        client = TableServiceClient.from_connection_string(emulator_connstr, endpoint_type='cosmos')
        assert client.url == "http://localhost:8902"
        assert client.account_name == 'localhost'
        assert client.credential.named_key.name == 'localhost'
        assert client.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert client._cosmos_endpoint
        assert client.scheme ==  'http'

        client = TableServiceClient("http://localhost:8902/", credential=emulator_credential)
        assert client.url == "http://localhost:8902"
        assert client.account_name == 'localhost'
        assert client.credential.named_key.name == 'localhost'
        assert client.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert client._cosmos_endpoint
        assert client.scheme ==  'http'

        table = TableClient.from_connection_string(emulator_connstr, 'tablename', endpoint_type='cosmos')
        assert table.url == "http://localhost:8902"
        assert table.account_name == 'localhost'
        assert table.table_name == 'tablename'
        assert table.credential.named_key.name == 'localhost'
        assert table.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert table._cosmos_endpoint
        assert table.scheme ==  'http'

        table = TableClient("http://localhost:8902/", "tablename", credential=emulator_credential)
        assert table.url == "http://localhost:8902"
        assert table.account_name == 'localhost'
        assert table.table_name == 'tablename'
        assert table.credential.named_key.name == 'localhost'
        assert table.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert table._cosmos_endpoint
        assert table.scheme ==  'http'

        table = TableClient.from_table_url("http://localhost:8902/Tables('tablename')", credential=emulator_credential)
        assert table.url == "http://localhost:8902"
        assert table.account_name == 'localhost'
        assert table.table_name == 'tablename'
        assert table.credential.named_key.name == 'localhost'
        assert table.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert table._cosmos_endpoint
        assert table.scheme ==  'http'

    @pytest.mark.asyncio
    async def test_closing_pipeline_client_async(self):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(self.tables_cosmos_account_name, url), credential=self.credential, table_name=url)

            # Assert
            async with service:
                assert hasattr(service, 'close')
                await service.close()

    @pytest.mark.asyncio
    async def test_closing_pipeline_client_simple_async(self):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(self.tables_cosmos_account_name, url), credential=self.credential, table_name=url)
            await service.close()

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_cosmos_async(self):
        # Arrange
        endpoint_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
        conn_string = 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.{2}:443/;'.format(
            self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key, endpoint_suffix)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo', endpoint_type='cosmos')

            # Assert
            assert service is not None
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + '.table.' + endpoint_suffix)
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://' + self.tables_cosmos_account_name + '.table.' + endpoint_suffix)
            assert service.scheme == 'https'
