# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import platform
from time import sleep

from azure.data.tables import TableServiceClient, TableClient
from azure.data.tables._version import VERSION
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import (
    TableTestCase,
    RERUNS_DELAY,
    SLEEP_DELAY
)
from azure.core.exceptions import HttpResponseError
from _shared.cosmos_testcase import CachedCosmosAccountPreparer

from devtools_testutils import CachedResourceGroupPreparer

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
        self.assertIsNotNone(service)
        self.assertEqual(service.account_name, account_name)
        self.assertEqual(service.credential.account_name, account_name)
        self.assertEqual(service.credential.account_key, account_key)
        self.assertTrue(
            ('{}.{}'.format(account_name, 'table.core.windows.net') in service.url) or
            ('{}.{}'.format(account_name, 'table.cosmos.azure.com') in service.url))

    # --Direct Parameters Test Cases --------------------------------------------
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_key(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange

        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(cosmos_account, url), credential=cosmos_account_key, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, cosmos_account.name, cosmos_account_key)
            self.assertEqual(service.scheme, 'https')

        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_connection_string(self, resource_group, location, cosmos_account, cosmos_account_key):

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(
                self.connection_string(cosmos_account, cosmos_account_key), table_name="test")

            # Assert
            self.validate_standard_account_endpoints(service, cosmos_account.name, cosmos_account_key)
            self.assertEqual(service.scheme, 'https')
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_sas(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        url = self.account_url(cosmos_account, "cosmos")
        suffix = '.table.core.windows.net'
        if 'cosmos' in url:
            suffix = '.table.cosmos.azure.com'
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(cosmos_account, "cosmos"), credential=self.sas_token, table_name='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertTrue(service.url.startswith('https://' + cosmos_account.name + suffix))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_token(self, resource_group, location, cosmos_account, cosmos_account_key):
        url = self.account_url(cosmos_account, "cosmos")
        suffix = '.table.core.windows.net'
        if 'cosmos' in url:
            suffix = '.table.cosmos.azure.com'
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=self.token_credential, table_name='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertTrue(service.url.startswith('https://' + cosmos_account.name + suffix))
            self.assertEqual(service.credential, self.token_credential)
            self.assertFalse(hasattr(service.credential, 'account_key'))
            self.assertTrue(hasattr(service.credential, 'get_token'))
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_token_and_http(self, resource_group, location, cosmos_account, cosmos_account_key):
        for service_type in SERVICES:
            # Act
            with self.assertRaises(ValueError):
                url = self.account_url(cosmos_account, "cosmos").replace('https', 'http')
                service_type(url, credential=self.token_credential, table_name='foo')
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_china(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        # TODO: Confirm regional cloud cosmos URLs
        for service_type in SERVICES.items():
            # Act
            url = self.account_url(cosmos_account, "cosmos").replace('core.windows.net', 'core.chinacloudapi.cn')
            if 'cosmos.azure' in url:
                pytest.skip("Confirm cosmos national cloud URLs")
            service = service_type[0](
                url, credential=cosmos_account_key, table_name='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertTrue(service._primary_endpoint.startswith(
                'https://{}.{}.core.chinacloudapi.cn'.format(cosmos_account.name, "cosmos")))
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_protocol(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            url = self.account_url(cosmos_account, "cosmos").replace('https', 'http')
            service = service_type[0](
                url, credential=cosmos_account_key, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, cosmos_account.name, cosmos_account_key)
            self.assertEqual(service.scheme, 'http')
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_empty_key(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        TABLE_SERVICES = [TableServiceClient, TableClient]

        for service_type in TABLE_SERVICES:
            # Act
            with self.assertRaises(ValueError) as e:
                test_service = service_type('testaccount', credential='', table_name='foo')

            self.assertEqual(
                str(e.exception), "You need to provide either a SAS token or an account shared key to authenticate.")
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_socket_timeout(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange

        for service_type in SERVICES.items():
            # Act
            default_service = service_type[0](
                self.account_url(cosmos_account, "cosmos"), credential=cosmos_account_key, table_name='foo')
            service = service_type[0](
                self.account_url(cosmos_account, "cosmos"), credential=cosmos_account_key,
                table_name='foo', connection_timeout=22)

            # Assert
            self.validate_standard_account_endpoints(service, cosmos_account.name, cosmos_account_key)
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout in [20, (20, 2000)]
        if self.is_live:
            sleep(SLEEP_DELAY)

    # --Connection String Test Cases --------------------------------------------
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_connection_string_key(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};'.format(cosmos_account.name, cosmos_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name='foo')

            # Assert
            self.validate_standard_account_endpoints(service, cosmos_account.name, cosmos_account_key)
            self.assertEqual(service.scheme, 'https')
        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos differential")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_connection_string_sas(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(cosmos_account.name, self.sas_token)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertTrue(service.url.startswith('https://' + cosmos_account.name + '.table.core.windows.net'))
            self.assertTrue(service.url.endswith(self.sas_token))
            self.assertIsNone(service.credential)
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_connection_string_cosmos(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        conn_string = 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.cosmos.azure.com:443/;'.format(
            cosmos_account.name, cosmos_account_key)

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name='foo')

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertTrue(service.url.startswith('https://' + cosmos_account.name + '.table.cosmos.azure.com'))
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertTrue(service._primary_endpoint.startswith('https://' + cosmos_account.name + '.table.cosmos.azure.com'))
            self.assertEqual(service.scheme, 'https')
        if self.is_live:
            sleep(SLEEP_DELAY)


    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_connection_string_endpoint_protocol(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            cosmos_account.name, cosmos_account_key)

        for service_type in SERVICES.items():
            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertTrue(
                service._primary_endpoint.startswith(
                    'http://{}.{}.core.chinacloudapi.cn'.format(cosmos_account.name, "cosmos")))
            self.assertEqual(service.scheme, 'http')
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_connection_string_emulated(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'UseDevelopmentStorage=true;'.format(cosmos_account.name, cosmos_account_key)

            # Act
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_connection_string_custom_domain(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com;'.format(
                cosmos_account.name, cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertTrue(service._primary_endpoint.startswith('https://www.mydomain.com'))
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_conn_str_custom_domain_trailing_slash(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                cosmos_account.name, cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertTrue(service._primary_endpoint.startswith('https://www.mydomain.com'))
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_conn_str_custom_domain_sec_override(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        for service_type in SERVICES.items():
            conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com/;'.format(
                cosmos_account.name, cosmos_account_key)

            # Act
            service = service_type[0].from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", table_name="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertTrue(service._primary_endpoint.startswith('https://www.mydomain.com'))
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_conn_str_fails_if_sec_without_primary(self, resource_group, location, cosmos_account, cosmos_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;'.format(
                cosmos_account.name, cosmos_account_key,
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act

            # Fails if primary excluded
            with self.assertRaises(ValueError):
                service = service_type[0].from_connection_string(conn_string, table_name="foo")
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_conn_str_succeeds_if_sec_with_primary(self, resource_group, location, cosmos_account, cosmos_account_key):
        for service_type in SERVICES.items():
            # Arrange
            conn_string = 'AccountName={};AccountKey={};{}=www.mydomain.com;{}=www-sec.mydomain.com;'.format(
                cosmos_account.name,
                cosmos_account_key,
                _CONNECTION_ENDPOINTS.get(service_type[1]),
                _CONNECTION_ENDPOINTS_SECONDARY.get(service_type[1]))

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            self.assertIsNotNone(service)
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertTrue(service._primary_endpoint.startswith('https://www.mydomain.com'))
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_service_with_custom_account_endpoint_path(self, resource_group, location, cosmos_account, cosmos_account_key):
        custom_account_url = "http://local-machine:11002/custom/account/path/" + self.sas_token
        for service_type in SERVICES.items():
            conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};TableEndpoint={};'.format(
                cosmos_account.name, cosmos_account_key, custom_account_url)

            # Act
            service = service_type[0].from_connection_string(conn_string, table_name="foo")

            # Assert
            self.assertEqual(service.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_name, cosmos_account.name)
            self.assertEqual(service.credential.account_key, cosmos_account_key)
            self.assertEqual(service._primary_hostname, 'local-machine:11002/custom/account/path')

        service = TableServiceClient(account_url=custom_account_url)
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.credential, None)
        self.assertEqual(service._primary_hostname, 'local-machine:11002/custom/account/path')
        # mine doesnt have a question mark at the end
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path'))

        service = TableClient(account_url=custom_account_url, table_name="foo")
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.table_name, "foo")
        self.assertEqual(service.credential, None)
        self.assertEqual(service._primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path'))

        service = TableClient.from_table_url("http://local-machine:11002/custom/account/path/foo" + self.sas_token)
        self.assertEqual(service.account_name, None)
        self.assertEqual(service.table_name, "foo")
        self.assertEqual(service.credential, None)
        self.assertEqual(service._primary_hostname, 'local-machine:11002/custom/account/path')
        self.assertTrue(service.url.startswith('http://local-machine:11002/custom/account/path'))

        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_user_agent_default(self, resource_group, location, cosmos_account, cosmos_account_key):
        service = TableServiceClient(self.account_url(cosmos_account, "cosmos"), credential=cosmos_account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-table/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()))

        tables = list(service.list_tables(raw_response_hook=callback))
        self.assertIsInstance(tables, list)

        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_user_agent_custom(self, resource_group, location, cosmos_account, cosmos_account_key):
        custom_app = "TestApp/v1.0"
        service = TableServiceClient(
            self.account_url(cosmos_account, "cosmos"), credential=cosmos_account_key, user_agent=custom_app)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertIn(
                "TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()),
                response.http_request.headers['User-Agent']
                )

        tables = list(service.list_tables(raw_response_hook=callback))
        self.assertIsInstance(tables, list)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertIn(
                "TestApp/v2.0 TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform()),
                response.http_request.headers['User-Agent']
                )

        tables = list(service.list_tables(raw_response_hook=callback, user_agent="TestApp/v2.0"))
        self.assertIsInstance(tables, list)

        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_user_agent_append(self, resource_group, location, cosmos_account, cosmos_account_key):
        service = TableServiceClient(self.account_url(cosmos_account, "cosmos"), credential=cosmos_account_key)

        def callback(response):
            self.assertTrue('User-Agent' in response.http_request.headers)
            self.assertEqual(
                response.http_request.headers['User-Agent'],
                "azsdk-python-storage-tables/{} Python/{} ({}) customer_user_agent".format(
                    VERSION,
                    platform.python_version(),
                    platform.platform())
            )

        custom_headers = {'User-Agent': 'customer_user_agent'}
        tables = service.list_tables(raw_response_hook=callback, headers=custom_headers)

        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("kierans theory")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_table_client_with_complete_table_url(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        table_url = self.account_url(cosmos_account, "cosmos") + "/foo"
        service = TableClient(table_url, table_name='bar', credential=cosmos_account_key)

        # Assert
        self.assertEqual(service.scheme, 'https')
        self.assertEqual(service.table_name, 'bar')
        self.assertEqual(service.account_name, cosmos_account.name)

    @pytest.mark.skip("cosmos differential")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_create_table_client_with_complete_url(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        table_url = "https://{}.table.cosmos.azure.com:443/foo".format(cosmos_account.name)
        service = TableClient(account_url=table_url, table_name='bar', credential=cosmos_account_key)

        # Assert
        self.assertEqual(service.scheme, 'https')
        self.assertEqual(service.table_name, 'bar')
        self.assertEqual(service.account_name, cosmos_account.name)

        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("kierans theory")
    def test_create_table_client_with_invalid_name(self):
        # Arrange
        table_url = "https://{}.table.cosmos.azure.com:443/foo".format("cosmos_account_name")
        invalid_table_name = "my_table"

        # Assert
        with pytest.raises(ValueError) as excinfo:
            service = TableClient(account_url=table_url, table_name=invalid_table_name, credential="cosmos_account_key")

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long." in str(excinfo)

        if self.is_live:
            sleep(SLEEP_DELAY)

    def test_error_with_malformed_conn_str(self):
        # Arrange

        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for service_type in SERVICES.items():
                # Act
                with self.assertRaises(ValueError) as e:
                    service = service_type[0].from_connection_string(conn_str, table_name="test")

                if conn_str in("", "foobar", "foo;bar;baz", ";"):
                    self.assertEqual(
                        str(e.exception), "Connection string is either blank or malformed.")
                elif conn_str in ("foobar=baz=foo" , "foo=;bar=;", "=", "=;=="):
                    self.assertEqual(
                        str(e.exception), "Connection string missing required connection details.")

        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_closing_pipeline_client(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(cosmos_account, "cosmos"), credential=cosmos_account_key, table_name='table')

            # Assert
            with service:
                assert hasattr(service, 'close')
                service.close()

        if self.is_live:
            sleep(SLEEP_DELAY)

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_closing_pipeline_client_simple(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        for client, url in SERVICES.items():
            # Act
            service = client(
                self.account_url(cosmos_account, "cosmos"), credential=cosmos_account_key, table_name='table')
            service.close()

        if self.is_live:
            sleep(SLEEP_DELAY)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
