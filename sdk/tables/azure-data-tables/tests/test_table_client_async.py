# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AzureNamedKeyCredential
import pytest
import platform

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.data.tables.aio import TableServiceClient, TableClient
from azure.data.tables import TableTransactionError
from azure.data.tables._version import VERSION

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async
from devtools_testutils import AzureTestCase
# ------------------------------------------------------------------------------
SERVICES = {
    TableServiceClient: 'table',
    TableClient: 'table',
}

_CONNECTION_ENDPOINTS = {'table': 'TableEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'table': 'TableSecondaryEndpoint'}


class TestTableClientAsync(AzureRecordedTestCase, AsyncTableTestCase):

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_default_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        service = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)

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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_custom_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        custom_app = "TestApp/v1.0"
        service = TableServiceClient(
            self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key, user_agent=custom_app)

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

        tables = service.list_tables(raw_response_hook=callback, user_agent="TestApp/v2.0")
        assert tables is not None

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_append(self, tables_storage_account_name, tables_primary_storage_account_key):
        service = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)

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
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_name_errors(self, tables_storage_account_name, tables_primary_storage_account_key):
        endpoint = self.account_url(tables_storage_account_name, "table")

        # storage table names must be alphanumeric, cannot begin with a number, and must be between 3 and 63 chars long.       
        invalid_table_names = ["1table", "a"*2, "a"*64, "a//", "my_table"]
        for invalid_name in invalid_table_names:
            client = TableClient(
                endpoint=endpoint, credential=tables_primary_storage_account_key, table_name=invalid_name)
            async with client:
                with pytest.raises(ValueError) as error:
                    await client.create_table()
                assert 'Storage table names must be alphanumeric' in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.create_entity({'PartitionKey': 'foo', 'RowKey': 'bar'})
                assert 'Storage table names must be alphanumeric' in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.upsert_entity({'PartitionKey': 'foo', 'RowKey': 'foo'})
                assert 'Storage table names must be alphanumeric' in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.delete_entity("PK", "RK")
                assert 'Storage table names must be alphanumeric' in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.get_table_access_policy()
                assert 'Storage table names must be alphanumeric' in str(error.value)
                with pytest.raises(ValueError) as error:
                    batch = []
                    batch.append(('upsert', {'PartitionKey': 'A', 'RowKey': 'B'}))
                    await client.submit_transaction(batch)
                assert 'Storage table names must be alphanumeric' in str(error.value)
    
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_client_with_url_ends_with_table_name(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        invalid_url = url+"/"+"tableName"
        # test table client has the same table name as in url
        tc = TableClient(invalid_url, "tableName", credential=tables_primary_storage_account_key)
        with pytest.raises(ValueError) as excinfo:
            await tc.create_table()
            assert ("table specified does not exist") in str(excinfo)
            assert ("Note: Try to remove the table name in the end of endpoint if it has.") in str(excinfo)
        # test table client has a different table name as in url
        tc2 = TableClient(invalid_url, "tableName2", credential=tables_primary_storage_account_key)
        with pytest.raises(ValueError) as excinfo:
            await tc2.create_table()
            assert ("table specified does not exist") in str(excinfo)
            assert ("Note: Try to remove the table name in the end of endpoint if it has.") in str(excinfo)

        valid_tc = TableClient(url, "tableName", credential=tables_primary_storage_account_key)
        valid_tc.create_table()
        # test creating a table when it already exists
        with pytest.raises(ValueError) as excinfo:
            await tc.create_table()
            assert ("values are not specified") in str(excinfo)
            assert ("Note: Try to remove the table name in the end of endpoint if it has.") in str(excinfo)
        # Note: delete_table() works well in async client.



class TestTableClientUnit(AsyncTableTestCase):
    tables_storage_account_name = "fake_storage_account"
    tables_primary_storage_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"
    credential = AzureNamedKeyCredential(name=tables_storage_account_name, key=tables_primary_storage_account_key)

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, account_name, account_key):
        assert service is not None
        assert service.account_name == account_name
        assert service.credential.named_key.name == account_name
        assert service.credential.named_key.key == account_key
        assert ('{}.{}'.format(account_name, 'table.core.windows.net') in service.url) or ('{}.{}'.format(account_name, 'table.cosmos.azure.com') in service.url)

    # --Direct Parameters Test Cases --------------------------------------------
    @pytest.mark.asyncio
    async def test_create_service_with_key_async(self):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(self.tables_storage_account_name, url), credential=self.credential, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_storage_account_name, self.tables_primary_storage_account_key)
            assert service.scheme == 'https'

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_async(self):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(self.tables_storage_account_name, self.tables_primary_storage_account_key), table_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_storage_account_name, self.tables_primary_storage_account_key)
            assert service.scheme == 'https'

    @pytest.mark.asyncio
    async def test_create_service_with_sas(self):
        # Arrange
        url = self.account_url(self.tables_storage_account_name, "table")
        suffix = '.table.core.windows.net'
        token = AzureSasCredential(self.generate_sas_token())
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(self.tables_storage_account_name, "table"), credential=token, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.url.startswith('https://' + self.tables_storage_account_name + suffix)
            assert isinstance(service.credential, AzureSasCredential)

    @pytest.mark.asyncio
    async def test_create_service_with_token_async(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        suffix = '.table.core.windows.net'
        self.token_credential = AzureSasCredential("fake_sas_credential")
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=self.token_credential, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.url.startswith('https://' + self.tables_storage_account_name + suffix)
            assert service.credential == self.token_credential
            assert not hasattr(service.credential, 'account_key')

    @pytest.mark.skip("HTTP prefix does not raise an error")
    @pytest.mark.asyncio
    async def test_create_service_with_token_and_http(self):
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                url = self.account_url(self.tables_storage_account_name, "table").replace('https', 'http')
                service_type(url, credential=AzureSasCredential("fake_sas_credential"), table_name='foo')

    @pytest.mark.asyncio
    async def test_create_service_china_async(self):
        # Arrange
        for service_type in SERVICES.items():
            # Act
            url = self.account_url(self.tables_storage_account_name, "table").replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=self.credential, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith('https://{}.{}.core.chinacloudapi.cn'.format(self.tables_storage_account_name, "table"))

    @pytest.mark.asyncio
    async def test_create_service_protocol_async(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(self.tables_storage_account_name, "table").replace('https', 'http')
            service = service_type[0](
                url, credential=self.credential, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_storage_account_name, self.tables_primary_storage_account_key)
            assert service.scheme == 'http'

    @pytest.mark.asyncio
    async def test_create_service_empty_key_async(self):
        # Arrange
        TABLE_SERVICES = [TableServiceClient, TableClient]

        for service_type in TABLE_SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = service_type('testaccount', credential='', table_name='foo')

            assert str(e.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

    @pytest.mark.asyncio
    async def test_create_service_with_socket_timeout_async(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.account_url(self.tables_storage_account_name, "table"), credential=self.credential, table_name='foo')
            service = service_type[0](
                self.account_url(self.tables_storage_account_name, "table"), credential=self.credential,
                table_name='foo', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_storage_account_name, self.tables_primary_storage_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout == 300

        # Assert Parent transport is shared with child client
        service = TableServiceClient(
            self.account_url(self.tables_storage_account_name, "table"),
            credential=self.credential,
            connection_timeout=22)
        assert service._client._client._pipeline._transport.connection_config.timeout == 22
        table = service.get_table_client('tablename')
        assert table._client._client._pipeline._transport._transport.connection_config.timeout == 22

    # --Connection String Test Cases --------------------------------------------
    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_key_async(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(self.tables_storage_account_name, self.tables_primary_storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_storage_account_name, self.tables_primary_storage_account_key)
            assert service.scheme == 'https'

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_sas_async(self):
        # Arrange
        token = AzureSasCredential(self.generate_sas_token())
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.tables_storage_account_name, token.signature)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.url.startswith('https://' + self.tables_storage_account_name + '.table.core.windows.net')
            assert isinstance(service.credential , AzureSasCredential)

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_cosmos_async(self):
        # Arrange
        conn_string = 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.cosmos.azure.com:443/;'.format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            assert service is not None
            assert service.url.startswith('https://' + self.tables_storage_account_name + '.table.cosmos.azure.com')
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith('https://' + self.tables_storage_account_name + '.table.cosmos.azure.com')
            assert service.scheme == 'https'

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_endpoint_protocol_async(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith('http://{}.{}.core.chinacloudapi.cn'.format(self.tables_storage_account_name, "table"))
            assert service.scheme == 'http'

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_emulated_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(self.tables_storage_account_name, self.tables_primary_storage_account_key)

            # Act
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_custom_domain_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com;'.format(
                self.tables_storage_account_name, self.tables_primary_storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_trailing_slash_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                self.tables_storage_account_name, self.tables_primary_storage_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_sec_override_async(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                self.tables_storage_account_name, self.tables_primary_storage_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_fails_if_sec_without_primary_async(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.tables_storage_account_name, self.tables_primary_storage_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Fails if primary excluded
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_succeeds_if_sec_with_primary_async(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                self.tables_storage_account_name,
                self.tables_primary_storage_account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    @pytest.mark.asyncio
    async def test_create_service_with_custom_account_endpoint_path_async(self):
        token = AzureSasCredential(self.generate_sas_token())
        custom_account_url = "http://local-machine:11002/custom/account/path/" + token.signature
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};TableEndpoint={};'.format(
                self.tables_storage_account_name, self.tables_primary_storage_account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service.account_name == self.tables_storage_account_name
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_hostname == 'local-machine:11002/custom/account/path'
            assert service.scheme == 'http'

        service = TableServiceClient(endpoint=custom_account_url)
        assert service.account_name == "custom"
        assert service.credential == None
        assert service._primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path')
        assert service.scheme == 'http'

        service = TableClient(endpoint=custom_account_url, table_name="foo")
        assert service.account_name == "custom"
        assert service.table_name == "foo"
        assert service.credential == None
        assert service._primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path')
        assert service.scheme == 'http'

        service = TableClient.from_table_url("http://local-machine:11002/custom/account/path/foo" + token.signature)
        assert service.account_name == "custom"
        assert service.table_name == "foo"
        assert service.credential == None
        assert service._primary_hostname == 'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path')
        assert service.scheme == 'http'

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_table_url_async(self):
        # Arrange
        table_url = self.account_url(self.tables_storage_account_name, "table") + "/foo"
        service = TableClient(table_url, table_name='bar', credential=self.credential)

        # Assert
        assert service.scheme == 'https'
        assert service.table_name == 'bar'
        assert service.account_name == self.tables_storage_account_name

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_url_async(self):
        # Arrange
        table_url = "https://{}.table.core.windows.net:443/foo".format(self.tables_storage_account_name)
        service = TableClient(endpoint=table_url, table_name='bar', credential=self.credential)

        # Assert
        assert service.scheme == 'https'
        assert service.table_name == 'bar'
        assert service.account_name == self.tables_storage_account_name

    @pytest.mark.asyncio
    async def test_error_with_malformed_conn_str_async(self):
        # Arrange

        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for service_type in SERVICES.items():
                # Act
                with pytest.raises(ValueError) as e:
                    service = service_type[0].from_connection_string(conn_str, table_name="test")

                if conn_str in("", "foobar", "foo;bar;baz", ";", "foo=;bar=;", "=", "=;=="):
                    assert str(e.value) == "Connection string is either blank or malformed."
                elif conn_str in ("foobar=baz=foo"):
                   assert str(e.value) == "Connection string missing required connection details."

    @pytest.mark.asyncio
    async def test_closing_pipeline_client_async(self):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(self.tables_storage_account_name, "table"), credential=self.credential, table_name='table')

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
                self.account_url(self.tables_storage_account_name, "table"), credential=self.credential, table_name='table')
            await service.close()

    @pytest.mark.asyncio
    async def test_create_client_with_api_version(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        client = TableServiceClient(url, credential=self.credential)
        assert client._client._config.version == "2019-02-02"
        table = client.get_table_client('tablename')
        assert table._client._config.version == "2019-02-02"

        client = TableServiceClient(url, credential=self.credential, api_version="2019-07-07")
        assert client._client._config.version == "2019-07-07"
        table = client.get_table_client('tablename')
        assert table._client._config.version == "2019-07-07"

        with pytest.raises(ValueError):
            TableServiceClient(url, credential=self.credential, api_version="foo")

    @pytest.mark.asyncio
    async def test_create_client_for_azurite(self):
        azurite_credential = AzureNamedKeyCredential("myaccount", self.tables_primary_storage_account_key)
        http_connstr = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey={};TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;".format(
            self.tables_primary_storage_account_key
        )
        https_connstr = "DefaultEndpointsProtocol=https;AccountName=devstoreaccount1;AccountKey={};TableEndpoint=https://127.0.0.1:10002/devstoreaccount1;".format(
            self.tables_primary_storage_account_key
        )
        account_url = "https://127.0.0.1:10002/myaccount"
        client = TableServiceClient(account_url, credential=azurite_credential)
        assert client.account_name == "myaccount"
        assert client.url == "https://127.0.0.1:10002/myaccount"
        assert client._location_mode == "primary"
        assert client._secondary_endpoint == "https://127.0.0.1:10002/myaccount-secondary"
        assert client.credential.named_key.key == azurite_credential.named_key.key
        assert client.credential.named_key.name == azurite_credential.named_key.name
        assert not client._cosmos_endpoint
        assert client.scheme == 'https'

        client = TableServiceClient.from_connection_string(http_connstr)
        assert client.account_name == "devstoreaccount1"
        assert client.url == "http://127.0.0.1:10002/devstoreaccount1"
        assert client._location_mode == "primary"
        assert client._secondary_endpoint == "http://127.0.0.1:10002/devstoreaccount1-secondary"
        assert client.credential.named_key.key == self.tables_primary_storage_account_key
        assert client.credential.named_key.name == "devstoreaccount1"
        assert not client._cosmos_endpoint
        assert client.scheme == 'http'

        client = TableServiceClient.from_connection_string(https_connstr)
        assert client.account_name == "devstoreaccount1"
        assert client.url == "https://127.0.0.1:10002/devstoreaccount1"
        assert client._location_mode == "primary"
        assert client._secondary_endpoint == "https://127.0.0.1:10002/devstoreaccount1-secondary"
        assert client.credential.named_key.key == self.tables_primary_storage_account_key
        assert client.credential.named_key.name == "devstoreaccount1"
        assert not client._cosmos_endpoint
        assert client.scheme == 'https'

        table = TableClient(account_url, "tablename", credential=azurite_credential)
        assert table.account_name == "myaccount"
        assert table.table_name == "tablename"
        assert table.url == "https://127.0.0.1:10002/myaccount"
        assert table._location_mode == "primary"
        assert table._secondary_endpoint == "https://127.0.0.1:10002/myaccount-secondary"
        assert table.credential.named_key.key == azurite_credential.named_key.key
        assert table.credential.named_key.name == azurite_credential.named_key.name
        assert not table._cosmos_endpoint
        assert table.scheme == 'https'

        table = TableClient.from_connection_string(http_connstr, "tablename")
        assert table.account_name == "devstoreaccount1"
        assert table.table_name == "tablename"
        assert table.url == "http://127.0.0.1:10002/devstoreaccount1"
        assert table._location_mode == "primary"
        assert table._secondary_endpoint == "http://127.0.0.1:10002/devstoreaccount1-secondary"
        assert table.credential.named_key.key == self.tables_primary_storage_account_key
        assert table.credential.named_key.name == "devstoreaccount1"
        assert not table._cosmos_endpoint
        assert table.scheme == 'http'

        table = TableClient.from_connection_string(https_connstr, "tablename")
        assert table.account_name == "devstoreaccount1"
        assert table.table_name == "tablename"
        assert table.url == "https://127.0.0.1:10002/devstoreaccount1"
        assert table._location_mode == "primary"
        assert table._secondary_endpoint == "https://127.0.0.1:10002/devstoreaccount1-secondary"
        assert table.credential.named_key.key == self.tables_primary_storage_account_key
        assert table.credential.named_key.name == "devstoreaccount1"
        assert not table._cosmos_endpoint
        assert table.scheme == 'https'

        table_url = "https://127.0.0.1:10002/myaccount/Tables('tablename')"
        table = TableClient.from_table_url(table_url, credential=azurite_credential)
        assert table.account_name == "myaccount"
        assert table.table_name == "tablename"
        assert table.url == "https://127.0.0.1:10002/myaccount"
        assert table._location_mode == "primary"
        assert table._secondary_endpoint == "https://127.0.0.1:10002/myaccount-secondary"
        assert table.credential.named_key.key == azurite_credential.named_key.key
        assert table.credential.named_key.name == azurite_credential.named_key.name
        assert not table._cosmos_endpoint
        assert table.scheme == 'https'
