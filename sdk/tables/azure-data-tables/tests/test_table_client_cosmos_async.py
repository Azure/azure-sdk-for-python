# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import platform
from time import sleep

from azure.data.tables.aio import TableServiceClient, TableClient
from azure.data.tables._version import VERSION

from _shared.testcase import (
    TableTestCase,
    SLEEP_DELAY
)
from preparers import CosmosPreparer
from devtools_testutils import AzureTestCase

# ------------------------------------------------------------------------------

SERVICES = {
    TableServiceClient: 'cosmos',
    TableClient: 'cosmos',
}

_CONNECTION_ENDPOINTS = {'table': 'TableEndpoint', 'cosmos': 'TableEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'table': 'TableSecondaryEndpoint', 'cosmos': 'TableSecondaryEndpoint'}

class StorageTableClientTest(TableTestCase):
    def setUp(self):
        super(StorageTableClientTest, self).setUp()
        self.sas_token = self.generate_sas_token()
        self.token_credential = self.generate_oauth_token()

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, account_name, account_key):
        assert service is not None
        assert service.account_name ==  account_name
        assert service.credential.account_name ==  account_name
        assert service.credential.account_key ==  account_key
        assert '{}.{}'.format(account_name, 'table.core.windows.net') in service.url or '{}.{}'.format(account_name, 'table.cosmos.azure.com') in service.url

    # --Direct Parameters Test Cases --------------------------------------------

    @CosmosPreparer()
    async def test_create_service_with_key_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(tables_cosmos_account_name, url), credential=tables_primary_cosmos_account_key, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, tables_cosmos_account_name, tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'
        if self.is_live:
            sleep(SLEEP_DELAY)


    @CosmosPreparer()
    async def test_create_service_with_connection_string_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(tables_cosmos_account_name, tables_primary_cosmos_account_key), table_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, tables_cosmos_account_name, tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'


    @CosmosPreparer()
    async def test_create_service_with_sas_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        suffix = '.table.cosmos.azure.com'
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(tables_cosmos_account_name, "cosmos"), credential=self.sas_token, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name == tables_cosmos_account_name
            assert service.url.startswith('https://' +tables_cosmos_account_name + suffix)
            assert service.url.endswith(self.sas_token)
            assert service.credential is None


    @CosmosPreparer()
    async def test_create_service_with_token_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        suffix = '.table.cosmos.azure.com'
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=self.token_credential, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.url.startswith('https://' + tables_cosmos_account_name + suffix)
            assert service.credential ==  self.token_credential
            assert not hasattr(service.credential, 'account_key')
            assert hasattr(service.credential, 'get_token')


    @CosmosPreparer()
    async def test_create_service_with_token_and_http_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                url = self.account_url(tables_cosmos_account_name, "cosmos").replace('https', 'http')
                service_type(url, credential=self.token_credential, table_name='foo')

    @pytest.mark.skip("Confirm cosmos national cloud URLs")

    @CosmosPreparer()
    async def test_create_service_china_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        # TODO: Confirm regional cloud cosmos URLs
        for service_type in SERVICES.items():
            # Act
            url = self.account_url(tables_cosmos_account_name, "cosmos").replace('core.windows.net', 'core.chinacloudapi.cn')
            service = service_type[0](
                url, credential=tables_primary_cosmos_account_key, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://{}.{}.core.chinacloudapi.cn'.format(tables_cosmos_account_name, "cosmos"))


    @CosmosPreparer()
    async def test_create_service_protocol_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(tables_cosmos_account_name, "cosmos").replace('https', 'http')
            service = service_type[0](
                url, credential=tables_primary_cosmos_account_key, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, tables_cosmos_account_name, tables_primary_cosmos_account_key)
            assert service.scheme ==  'http'


    @CosmosPreparer()
    async def test_create_service_empty_key_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        TABLE_SERVICES = [TableServiceClient, TableClient]

        for service_type in TABLE_SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = service_type('testaccount', credential='', table_name='foo')

            assert str(e.value) == "You need to provide either a SAS token or an account shared key to authenticate."


    @CosmosPreparer()
    async def test_create_service_with_socket_timeout_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key, table_name='foo')
            service = service_type[0](
                self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key,
                table_name='foo', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, tables_cosmos_account_name, tables_primary_cosmos_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]

    # --Connection String Test Cases --------------------------------------------

    @CosmosPreparer()
    async def test_create_service_with_connection_string_key_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(tables_cosmos_account_name, tables_primary_cosmos_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, tables_cosmos_account_name, tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'

    @pytest.mark.skip("Error with sas formation")

    @CosmosPreparer()
    async def test_create_service_with_connection_string_sas_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(tables_cosmos_account_name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.url.startswith('https://' + tables_cosmos_account_name + '.table.core.windows.net')
            assert service.url.endswith(self.sas_token)
            assert service.credential is None


    @CosmosPreparer()
    async def test_create_service_with_connection_string_cosmos_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        conn_string = 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.cosmos.azure.com:443/;'.format(
            tables_cosmos_account_name, tables_primary_cosmos_account_key)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.url.startswith('https://' + tables_cosmos_account_name + '.table.cosmos.azure.com')
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://' + tables_cosmos_account_name + '.table.cosmos.azure.com')
            assert service.scheme ==  'https'


    @CosmosPreparer()
    async def test_create_service_with_connection_string_endpoint_protocol_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            tables_cosmos_account_name, tables_primary_cosmos_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            print(service._primary_endpoint)
            assert service._primary_endpoint.startswith('http://{}.{}.core.chinacloudapi.cn'.format(tables_cosmos_account_name, "table"))
            assert service.scheme ==  'http'


    @CosmosPreparer()
    async def test_create_service_with_connection_string_emulated_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(tables_cosmos_account_name, tables_primary_cosmos_account_key)

            # Act
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")


    @CosmosPreparer()
    async def test_create_service_with_connection_string_custom_domain_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com;'.format(
                tables_cosmos_account_name, tables_primary_cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')


    @CosmosPreparer()
    async def test_create_service_with_conn_str_custom_domain_trailing_slash_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                tables_cosmos_account_name, tables_primary_cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')


    @CosmosPreparer()
    async def test_create_service_with_conn_str_custom_domain_sec_override_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                tables_cosmos_account_name, tables_primary_cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')


    @CosmosPreparer()
    async def test_create_service_with_conn_str_fails_if_sec_without_primary_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                tables_cosmos_account_name, tables_primary_cosmos_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Fails if primary excluded
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")


    @CosmosPreparer()
    async def test_create_service_with_conn_str_succeeds_if_sec_with_primary_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  tables_cosmos_account_name
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')


    @CosmosPreparer()
    async def test_create_service_with_custom_account_endpoint_path_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};TableEndpoint={};'.format(
                tables_cosmos_account_name, tables_primary_cosmos_account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service.account_name ==  tables_cosmos_account_name
            assert service.credential.account_name ==  tables_cosmos_account_name
            assert service.credential.account_key ==  tables_primary_cosmos_account_key
            assert service._primary_hostname ==  'local-machine:11002/custom/account/path'

        service = TableServiceClient(account_url=custom_account_url)
        assert service.account_name ==  None
        assert service.credential ==  None
        assert service._primary_hostname ==  'local-machine:11002/custom/account/path'
        # mine doesnt have a question mark at the end
        assert service.url.startswith('http://local-machine:11002/custom/account/path')

        service = TableClient(account_url=custom_account_url, table_name="foo")
        assert service.account_name ==  None
        assert service.table_name ==  "foo"
        assert service.credential ==  None
        assert service._primary_hostname ==  'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path')

        service = TableClient.from_table_url("http://local-machine:11002/custom/account/path/foo" + self.sas_token)
        assert service.account_name ==  None
        assert service.table_name ==  "foo"
        assert service.credential ==  None
        assert service._primary_hostname ==  'local-machine:11002/custom/account/path'
        assert service.url.startswith('http://local-machine:11002/custom/account/path')


    @CosmosPreparer()
    async def test_user_agent_default_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert response.http_request.headers['User-Agent'] == "azsdk-python-storage-table/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())

        tables = service.list_tables(raw_response_hook=callback)
        assert tables is not None


    @CosmosPreparer()
    async def test_user_agent_custom_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        custom_app = "TestApp/v1.0"
        service = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key, user_agent=custom_app)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "TestApp/v1.0 azsdk-python-storage-table/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        tables = service.list_tables(raw_response_hook=callback)
        assert tables is not None

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "TestApp/v2.0 TestApp/v1.0 azsdk-python-storage-table/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        tables = service.list_tables(raw_response_hook=callback, user_agent="TestApp/v2.0")
        assert tables is not None


    @CosmosPreparer()
    async def test_user_agent_append(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # TODO: fix this one
        service = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert response.http_request.headers['User-Agent'] == "azsdk-python-storage-tables/{} Python/{} ({}) customer_user_agent".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())

        custom_headers = {'User-Agent': 'customer_user_agent'}
        tables = service.list_tables(raw_response_hook=callback, headers=custom_headers)


    @CosmosPreparer()
    async def test_create_table_client_with_complete_table_url_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        table_url = self.account_url(tables_cosmos_account_name, "cosmos") + "/foo"
        service = TableClient(table_url, table_name='bar', credential=tables_primary_cosmos_account_key)

        # Assert
        assert service.scheme ==  'https'
        assert service.table_name ==  'bar'
        assert service.account_name ==  tables_cosmos_account_name

    @pytest.mark.skip("cosmos differential")

    @CosmosPreparer()
    async def test_create_table_client_with_complete_url_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        table_url = "https://{}.table.cosmos.azure.com:443/foo".format(tables_cosmos_account_name)
        service = TableClient(table_url, table_name='bar', credential=tables_primary_cosmos_account_key)

        # Assert
        assert service.scheme ==  'https'
        assert service.table_name ==  'bar'
        assert service.account_name ==  tables_cosmos_account_name

    @AzureTestCase.await_prepared_test
    async def test_create_table_client_with_invalid_name_async(self):
        # Arrange
        table_url = "https://{}.table.cosmos.azure.com:443/foo".format("cosmos_account_name")
        invalid_table_name = "my_table"

        # Assert
        with pytest.raises(ValueError) as excinfo:
            service = TableClient(account_url=table_url, table_name=invalid_table_name, credential="tables_primary_cosmos_account_key")

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(excinfo)

    @AzureTestCase.await_prepared_test
    async def test_error_with_malformed_conn_str_async(self):
        # Arrange

        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for service_type in SERVICES.items():
                # Act
                with pytest.raises(ValueError) as e:
                    service = service_type[0].from_connection_string(conn_str, table_name="test")

                if conn_str in("", "foobar", "foo;bar;baz", ";"):
                    assert str(e.value) == "Connection string is either blank or malformed."
                elif conn_str in ("foobar=baz=foo" , "foo=;bar=;", "=", "=;=="):
                    assert str(e.value) == "Connection string missing required connection details."


    @CosmosPreparer()
    async def test_closing_pipeline_client_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key, table_name='table')

            # Assert
            async with service:
                assert hasattr(service, 'close')
                await service.close()


    @CosmosPreparer()
    async def test_closing_pipeline_client_simple_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key, table_name='table')
            await service.close()
