# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import platform
from time import sleep
import sys

from devtools_testutils import AzureTestCase

from azure.data.tables import TableServiceClient, TableClient
from azure.data.tables import __version__ as  VERSION

from _shared.testcase import (
    TableTestCase,
    SLEEP_DELAY
)
from preparers import CosmosPreparer

# ------------------------------------------------------------------------------
SERVICES = {
    TableServiceClient: 'cosmos',
    TableClient: 'cosmos',
}

_CONNECTION_ENDPOINTS = {'table': 'TableEndpoint', 'cosmos': 'TableEndpoint'}

_CONNECTION_ENDPOINTS_SECONDARY = {'table': 'TableSecondaryEndpoint', 'cosmos': 'TableSecondaryEndpoint'}

class TestTableClient(AzureTestCase, TableTestCase):

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="Malformed string")
    @CosmosPreparer()
    def test_user_agent_default(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        tables = list(service.list_tables(raw_response_hook=callback))
        assert isinstance(tables,  list)

        count = 0
        for table in tables:
            count += 1

        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_user_agent_custom(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        custom_app = "TestApp/v1.0"
        service = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key, user_agent=custom_app)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        tables = list(service.list_tables(raw_response_hook=callback))
        assert isinstance(tables,  list)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert "TestApp/v2.0 TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()) in response.http_request.headers['User-Agent']

        tables = list(service.list_tables(raw_response_hook=callback, user_agent="TestApp/v2.0"))
        assert isinstance(tables,  list)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_user_agent_append(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = self.create_client_from_credential(
            TableServiceClient,
            account_url=self.account_url(tables_cosmos_account_name, "cosmos"),
            credential=tables_primary_cosmos_account_key)

        def callback(response):
            assert 'User-Agent' in response.http_request.headers
            assert response.http_request.headers['User-Agent'] == 'customer_user_agent'

        custom_headers = {'User-Agent': 'customer_user_agent'}
        tables = service.list_tables(raw_response_hook=callback, headers=custom_headers)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

        if self.is_live:
            sleep(SLEEP_DELAY)


class TestTableClientUnit(TableTestCase):
    tables_cosmos_account_name = "fake_storage_account"
    tables_primary_cosmos_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"

    # --Helpers-----------------------------------------------------------------
    def validate_standard_account_endpoints(self, service, account_name, account_key):
        assert service is not None
        assert service.account_name ==  account_name
        assert service.credential.account_name ==  account_name
        assert service.credential.account_key ==  account_key
        assert ('{}.{}'.format(account_name, 'table.core.windows.net') in service.url) or ('{}.{}'.format(account_name, 'table.cosmos.azure.com') in service.url)

    def _account_url(self, account_name):
        return "https://{}.table.cosmos.azure.com".format(account_name)

    # --Direct Parameters Test Cases --------------------------------------------

    def test_create_service_with_key(self):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.tables_primary_cosmos_account_key,
                table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'


    def test_create_service_with_connection_string(self):

        for client, url in SERVICES.items():
            # Act
            service = client(
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.tables_primary_cosmos_account_key,
                table_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme ==  'https'

    def test_create_service_with_sas(self):
        # Arrange
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        suffix = '.table.cosmos.azure.com'
        self.sas_token = self.generate_sas_token()
        for service_type in SERVICES:
            # Act
            service = service_type(
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.sas_token,
                table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + suffix)
            assert service.url.endswith(self.sas_token)
            assert service.credential is None

    def test_create_service_with_token(self):
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        suffix = '.table.cosmos.azure.com'
        for service_type in SERVICES:
            # Act
            service = service_type(
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.tables_primary_cosmos_account_key,
                table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + suffix)
            assert not hasattr(service, 'account_key')


    def test_create_service_with_token_and_http(self):
        self.token_credential = self.generate_fake_token()
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                url = self.account_url(self.tables_cosmos_account_name, "cosmos").replace('https', 'http')
                service = service_type(
                    account_url=url,
                    credential=self.token_credential,
                    table_name="foo")

    @pytest.mark.skip("Testing against a different cloud than the one created in powershell script")

    def test_create_service_china(self):
        # Arrange
        # TODO: Confirm regional cloud cosmos URLs
        for service_type in SERVICES.items():
            # Act
            url = self.account_url(self.tables_cosmos_account_name, "cosmos").replace('core.windows.net', 'core.chinacloudapi.cn')
            if 'cosmos.azure' in url:
                pytest.skip("Confirm cosmos national cloud URLs")
            service = service_type[0](
                url, credential=self.tables_primary_cosmos_account_key, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.credential.account_name ==  self.tables_cosmos_account_name
            assert service.credential.account_key ==  self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://{}.{}.core.chinacloudapi.cn'.format(self.tables_cosmos_account_name, "table"))

    def test_create_service_protocol(self):
        # Arrange
        url = self._account_url(self.tables_cosmos_account_name).replace('https', 'http')
        suffix = '.table.cosmos.azure.com'
        for service_type in SERVICES:
            # Act
            service = service_type(
                account_url=url,
                credential=self.tables_primary_cosmos_account_key,
                table_name="foo")

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme ==  'http'

    def test_create_service_empty_key(self):
        # Arrange
        TABLE_SERVICES = [TableServiceClient, TableClient]

        for service_type in TABLE_SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = service_type('testaccount', credential='', table_name='foo')

            assert str(e.value) == "You need to provide either a SAS token or an account shared key to authenticate."

    def test_create_service_with_socket_timeout(self):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.tables_primary_cosmos_account_key,
                table_name="foo")
            service = service_type[0](
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.tables_primary_cosmos_account_key,
                table_name="foo", connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]


    # --Connection String Test Cases --------------------------------------------
    def test_create_service_with_connection_string_key(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)
            assert service.scheme == 'https'


    def test_create_service_with_connection_string_sas(self):
        # Arrange
        self.sas_token = self.generate_sas_token()
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.tables_cosmos_account_name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            assert service is not None
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + '.table.core.windows.net')
            assert service.url.endswith(self.sas_token)
            assert service.credential is None


    def test_create_service_with_connection_string_cosmos(self):
        # Arrange
        conn_string = 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.cosmos.azure.com:443/;'.format(
            self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.url.startswith('https://' + self.tables_cosmos_account_name + '.table.cosmos.azure.com')
            assert service.credential.account_name ==  self.tables_cosmos_account_name
            assert service.credential.account_key ==  self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://' + self.tables_cosmos_account_name + '.table.cosmos.azure.com')
            assert service.scheme ==  'https'

    @pytest.mark.skip("Tests fail with non-standard clouds")

    def test_create_service_with_connection_string_endpoint_protocol(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name ==  self.tables_cosmos_account_name
            assert service.credential.account_name ==  self.tables_cosmos_account_name
            assert service.credential.account_key ==  self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('http://{}.{}.core.chinacloudapi.cn'.format(self.tables_cosmos_account_name, "table"))
            assert service.scheme ==  'http'


    def test_create_service_with_connection_string_emulated(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")


    def test_create_service_with_connection_string_custom_domain(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.credential.account_name == self.tables_cosmos_account_name
            assert service.credential.account_key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')


    def test_create_service_with_conn_str_custom_domain_trailing_slash(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.credential.account_name == self.tables_cosmos_account_name
            assert service.credential.account_key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    def test_create_service_with_conn_str_custom_domain_sec_override(self):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.credential.account_name == self.tables_cosmos_account_name
            assert service.credential.account_key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    def test_create_service_with_conn_str_fails_if_sec_without_primary(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with pytest.raises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")


    def test_create_service_with_conn_str_succeeds_if_sec_with_primary(self):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                self.tables_cosmos_account_name,
                self.tables_primary_cosmos_account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.credential.account_name == self.tables_cosmos_account_name
            assert service.credential.account_key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith('https://www.mydomain.com')

    def test_create_service_with_custom_account_endpoint_path(self):
        self.sas_token = self.generate_sas_token()
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};TableEndpoint={};'.format(
                self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service.account_name == self.tables_cosmos_account_name
            assert service.credential.account_name == self.tables_cosmos_account_name
            assert service.credential.account_key == self.tables_primary_cosmos_account_key
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

    def test_create_table_client_with_complete_table_url(self):
        # Arrange
        table_url = self._account_url(self.tables_cosmos_account_name) + "/foo"
        service = TableClient(
            account_url=table_url,
            credential=self.tables_primary_cosmos_account_key,
            table_name="bar")

        # Assert
        assert service.scheme ==  'https'
        assert service.table_name ==  'bar'
        assert service.account_name ==  self.tables_cosmos_account_name


    def test_create_table_client_with_complete_url(self):
        # Arrange
        table_url = "https://{}.table.cosmos.azure.com:443/foo".format(self.tables_cosmos_account_name)
        service = TableClient(
            account_url=table_url,
            credential=self.tables_primary_cosmos_account_key,
            table_name="bar")

        # Assert
        assert service.scheme ==  'https'
        assert service.table_name ==  'bar'
        assert service.account_name ==  self.tables_cosmos_account_name

    def test_create_table_client_with_invalid_name(self):
        # Arrange
        table_url = "https://{}.table.cosmos.azure.com:443/foo".format("cosmos_account_name")
        invalid_table_name = "my_table"

        # Assert
        with pytest.raises(ValueError) as excinfo:
            service = TableClient(account_url=table_url, table_name=invalid_table_name, credential="self.tables_primary_cosmos_account_key")

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long." in str(excinfo)

    def test_error_with_malformed_conn_str(self):
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

    def test_closing_pipeline_client(self):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.tables_primary_cosmos_account_key,
                table_name='table')

            # Assert
            with service:
                assert hasattr(service, 'close')
                service.close()


    def test_closing_pipeline_client_simple(self):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                account_url=self._account_url(self.tables_cosmos_account_name),
                credential=self.tables_primary_cosmos_account_key,
                table_name='table')

            service.close()
