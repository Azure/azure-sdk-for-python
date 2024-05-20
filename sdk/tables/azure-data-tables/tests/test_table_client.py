# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import platform
import os
import time

from datetime import datetime, timedelta
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.data.tables import (
    TableServiceClient,
    TableClient,
    AccountSasPermissions,
    ResourceTypes,
    generate_account_sas,
    __version__ as VERSION,
)
from azure.data.tables._constants import DEFAULT_STORAGE_ENDPOINT_SUFFIX
from azure.data.tables._error import _validate_storage_tablename
from azure.data.tables._models import LocationMode
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError, ClientAuthenticationError
from azure.identity import DefaultAzureCredential

from _shared.testcase import TableTestCase
from preparers import tables_decorator

SERVICES = [TableServiceClient, TableClient]


class TestTableClient(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_user_agent_custom(self, tables_storage_account_name, tables_primary_storage_account_key):
        custom_app = "TestApp/v1.0"
        service = TableServiceClient(
            self.account_url(tables_storage_account_name, "table"),
            credential=tables_primary_storage_account_key,
            user_agent=custom_app,
        )

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                "TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION, platform.python_version(), platform.platform()
                )
                in response.http_request.headers["User-Agent"]
            )

        tables = list(service.list_tables(raw_response_hook=callback))
        assert isinstance(tables, list)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                "TestApp/v2.0 TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION, platform.python_version(), platform.platform()
                )
                in response.http_request.headers["User-Agent"]
            )

        tables = list(service.list_tables(raw_response_hook=callback, user_agent="TestApp/v2.0"))
        assert isinstance(tables, list)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

    @tables_decorator
    @recorded_by_proxy
    def test_user_agent_append(self, tables_storage_account_name, tables_primary_storage_account_key):
        service = TableServiceClient(
            self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key
        )

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert response.http_request.headers["User-Agent"] == "customer_user_agent"

        custom_headers = {"User-Agent": "customer_user_agent"}
        tables = service.list_tables(raw_response_hook=callback, headers=custom_headers)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

    @tables_decorator
    @recorded_by_proxy
    def test_user_agent_default(self, tables_storage_account_name, tables_primary_storage_account_key):
        service = TableServiceClient(
            self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key
        )

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                "azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION, platform.python_version(), platform.platform()
                )
                in response.http_request.headers["User-Agent"]
            )

        tables = list(service.list_tables(raw_response_hook=callback))
        assert isinstance(tables, list)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

    @pytest.mark.live_test_only
    @tables_decorator
    @recorded_by_proxy
    def test_table_name_errors(self, tables_storage_account_name, tables_primary_storage_account_key):
        endpoint = self.account_url(tables_storage_account_name, "table")

        # storage table names must be alphanumeric, cannot begin with a number, and must be between 3 and 63 chars long.
        invalid_table_names = ["1table", "a" * 2, "a" * 64, "a//", "my_table"]
        for invalid_name in invalid_table_names:
            client = TableClient(
                endpoint=endpoint, credential=tables_primary_storage_account_key, table_name=invalid_name
            )
            with pytest.raises(ValueError) as error:
                client.create_table()
            assert "Storage table names must be alphanumeric" in str(error.value)
            with pytest.raises(ValueError) as error:
                client.create_entity({"PartitionKey": "foo", "RowKey": "bar"})
            assert "Storage table names must be alphanumeric" in str(error.value)
            with pytest.raises(ValueError) as error:
                client.upsert_entity({"PartitionKey": "foo", "RowKey": "foo"})
            assert "Storage table names must be alphanumeric" in str(error.value)
            with pytest.raises(ValueError) as error:
                client.delete_entity("PK", "RK")
            assert "Storage table names must be alphanumeric" in str(error.value)
            with pytest.raises(ValueError) as error:
                client.get_table_access_policy()
            assert "Storage table names must be alphanumeric" in str(error.value)
            with pytest.raises(ValueError):
                batch = []
                batch.append(("upsert", {"PartitionKey": "A", "RowKey": "B"}))
                client.submit_transaction(batch)
            assert "Storage table names must be alphanumeric" in str(error.value)

    @tables_decorator
    @recorded_by_proxy
    def test_client_with_url_ends_with_table_name(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        invalid_url = url + "/" + table_name
        # test table client has the same table name as in url
        tc = TableClient(invalid_url, table_name, credential=tables_primary_storage_account_key)
        with pytest.raises(ResourceNotFoundError) as exc:
            tc.create_table()
        assert ("table specified does not exist") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        # test table client has a different table name as in url
        table_name2 = self.get_resource_name("mytable2")
        tc2 = TableClient(invalid_url, table_name2, credential=tables_primary_storage_account_key)
        with pytest.raises(ResourceNotFoundError) as exc:
            tc2.create_table()
        assert ("table specified does not exist") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)

        valid_tc = TableClient(url, table_name, credential=tables_primary_storage_account_key)
        valid_tc.create_table()
        # test creating a table when it already exists
        with pytest.raises(HttpResponseError) as exc:
            tc.create_table()
        assert ("values are not specified") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        # test deleting a table when it already exists
        with pytest.raises(HttpResponseError) as exc:
            tc.delete_table()
        assert ("URI does not match number of key properties for the resource") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        valid_tc.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_error_handling(self, tables_storage_account_name, tables_primary_storage_account_key):
        with TableServiceClient(
            self.account_url(tables_storage_account_name, "table"),
            credential=DefaultAzureCredential(
                exclude_shared_token_cache_credential=True,
                exclude_powershell_credential=True,
                exclude_cli_credential=True,
                exclude_environment_credential=True,
            ),
        ) as service_client:
            with pytest.raises(ClientAuthenticationError):
                service_client.create_table_if_not_exists(table_name="TestInsert")

    def check_request_auth(self, pipeline_request):
        assert self.sas_token not in pipeline_request.http_request.url
        assert pipeline_request.http_request.headers.get("Authorization") is not None

    @tables_decorator
    @recorded_by_proxy
    def test_table_client_location_mode(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, location_mode=LocationMode.SECONDARY
        ) as client:
            with pytest.raises(HttpResponseError) as ex:
                client.create_table()
            assert "Write operations are not allowed." in str(ex.value)

        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            if self.is_live:
                time.sleep(15)

        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, location_mode=LocationMode.SECONDARY
        ) as client:
            with pytest.raises(HttpResponseError) as ex:
                client.create_entity(entity)
            assert "Operation returned an invalid status 'Forbidden'" in str(ex.value)

            with pytest.raises(HttpResponseError) as ex:
                client.upsert_entity(entity)
            assert "Write operations are not allowed." in str(ex.value)

            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar")
            assert "The specified resource does not exist." in str(ex.value)

            entities = client.list_entities()
            for e in entities:
                pass

            with pytest.raises(HttpResponseError) as ex:
                client.delete_entity(entity)
            assert "Write operations are not allowed." in str(ex.value)

            with pytest.raises(HttpResponseError) as ex:
                client.delete_table()
            assert "Write operations are not allowed." in str(ex.value)

        # clean up
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_table_client_with_named_key_credential(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        self.sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with TableClient.from_table_url(
            f"{base_url}/{table_name}", credential=tables_primary_storage_account_key
        ) as client:
            table = client.create_table()
            assert table.name == table_name

        conn_str = f"AccountName={tables_storage_account_name};AccountKey={tables_primary_storage_account_key.named_key.key};EndpointSuffix=core.windows.net"
        with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass

        # AzureNamedKeyCredential is actually in use
        with TableClient(
            f"{base_url}/?{self.sas_token}", table_name, credential=tables_primary_storage_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            for e in entities:
                pass

        # AzureNamedKeyCredential is actually in use
        with TableClient.from_table_url(
            f"{base_url}/{table_name}?{self.sas_token}", credential=tables_primary_storage_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            for e in entities:
                pass
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_table_service_client_with_named_key_credential(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        self.sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        name_filter = "TableName eq '{}'".format(table_name)
        conn_str = f"AccountName={tables_storage_account_name};AccountKey={tables_primary_storage_account_key.named_key.key};EndpointSuffix=core.windows.net"

        with TableServiceClient.from_connection_string(conn_str) as client:
            client.create_table(table_name)
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1

        # AzureNamedKeyCredential is actually in use
        with TableServiceClient(
            f"{base_url}/?{self.sas_token}", credential=tables_primary_storage_account_key
        ) as client:
            entities = client.get_table_client(table_name).query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            for e in entities:
                pass
            client.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_table_client_with_sas_token_credential(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with TableClient(base_url, table_name, credential=AzureSasCredential(sas_token)) as client:
            table = client.create_table()
            assert table.name == table_name

        with TableClient.from_table_url(f"{base_url}/{table_name}", credential=AzureSasCredential(sas_token)) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass

        conn_str = (
            f"AccountName={tables_storage_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature}"
        )
        with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass
            client.delete_table()

        with pytest.raises(ValueError) as ex:
            TableClient(f"{base_url}/?{sas_token}", table_name, credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

        with pytest.raises(ValueError) as ex:
            TableClient.from_table_url(f"{base_url}/{table_name}?{sas_token}", credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

    @tables_decorator
    @recorded_by_proxy
    def test_table_service_client_with_sas_token_credential(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        name_filter = "TableName eq '{}'".format(table_name)

        with TableServiceClient(base_url, credential=AzureSasCredential(sas_token)) as client:
            client.create_table(table_name)
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1

        conn_str = (
            f"AccountName={tables_storage_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature}"
        )
        with TableServiceClient.from_connection_string(conn_str) as client:
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1
            client.delete_table(table_name)

        with pytest.raises(ValueError) as ex:
            TableServiceClient(f"{base_url}/?{sas_token}", credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

    @tables_decorator
    @recorded_by_proxy
    def test_table_client_with_token_credential(self, tables_storage_account_name, tables_primary_storage_account_key):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        default_azure_credential = self.get_token_credential()
        self.sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with TableClient(base_url, table_name, credential=default_azure_credential) as client:
            table = client.create_table()
            assert table.name == table_name

        with TableClient.from_table_url(f"{base_url}/{table_name}", credential=default_azure_credential) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass

        # DefaultAzureCredential is actually in use
        with TableClient(f"{base_url}/?{self.sas_token}", table_name, credential=default_azure_credential) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            for e in entities:
                pass

        # DefaultAzureCredential is actually in use
        with TableClient.from_table_url(
            f"{base_url}/{table_name}?{self.sas_token}", credential=default_azure_credential
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            for e in entities:
                pass
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_table_service_client_with_token_credential(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        default_azure_credential = self.get_token_credential()
        name_filter = "TableName eq '{}'".format(table_name)
        self.sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with TableServiceClient(base_url, credential=default_azure_credential) as client:
            client.create_table(table_name)
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1

        # DefaultAzureCredential is actually in use
        with TableServiceClient(f"{base_url}/?{self.sas_token}", credential=default_azure_credential) as client:
            entities = client.get_table_client(table_name).query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            for e in entities:
                pass
            client.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_table_client_without_credential(self, tables_storage_account_name, tables_primary_storage_account_key):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),  # full permission
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with pytest.raises(ValueError) as ex:
            client = TableClient(base_url, table_name)
        assert str(ex.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

        with pytest.raises(ValueError) as ex:
            client = TableClient.from_table_url(f"{base_url}/{table_name}")
        assert str(ex.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

        with TableClient(f"{base_url}/?{sas_token}", table_name) as client:
            table = client.create_table()
            assert table.name == table_name

        with pytest.raises(ValueError) as ex:
            client = TableClient.from_table_url(f"{base_url}/{table_name}")
        assert str(ex.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

        with TableClient.from_table_url(f"{base_url}/{table_name}?{sas_token}") as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_table_service_client_without_credential(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        base_url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        name_filter = "TableName eq '{}'".format(table_name)
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_storage_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with pytest.raises(ValueError) as ex:
            TableServiceClient(base_url)
        assert str(ex.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

        with TableServiceClient(f"{base_url}/?{sas_token}") as client:
            client.create_table(table_name)
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1
            client.delete_table(table_name)


# --Helpers-----------------------------------------------------------------
def validate_standard_account_endpoints(service, account_name, account_key):
    endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
    assert service is not None
    assert service.account_name == account_name
    assert service.credential.named_key.name == account_name
    assert service.credential.named_key.key == account_key
    assert "{}.table.{}".format(account_name, endpoint_suffix) in service.url


class TestTableClientUnitTests(TableTestCase):
    tables_storage_account_name = "fake_storage_account"
    tables_primary_storage_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"
    credential = AzureNamedKeyCredential(name=tables_storage_account_name, key=tables_primary_storage_account_key)

    # --Direct Parameters Test Cases --------------------------------------------
    def test_create_service_with_key(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_storage_account_name, self.tables_primary_storage_account_key
            )
            assert service.scheme == "https"

    def test_create_service_with_connection_string(self):
        conn_string = (
            f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};"
        )
        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name="test")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_storage_account_name, self.tables_primary_storage_account_key
            )
            assert service.scheme == "https"

    def test_create_service_with_sas(self):
        # Arrange
        sas_token = self.generate_sas_token()
        url = self.account_url(self.tables_storage_account_name, "table")
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=AzureSasCredential(sas_token), table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.url.startswith(f"https://{self.tables_storage_account_name}.table.core.windows.net")
            assert isinstance(service.credential, AzureSasCredential)

    def test_create_service_protocol(self):
        url = self.account_url(self.tables_storage_account_name, "table").replace("https", "http")
        for service_type in SERVICES:
            # Act

            service = service_type(url, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_storage_account_name, self.tables_primary_storage_account_key
            )
            assert service.scheme == "http"

    def test_create_service_empty_key(self):
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = service_type("testaccount", credential="", table_name="foo")

            # test non-string account URL
            with pytest.raises(ValueError):
                test_service = service_type(endpoint=123456, credential=self.credential, table_name="foo")

            assert str(e.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

    def test_create_service_with_socket_timeout(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        for service_type in SERVICES:
            # Act
            default_service = service_type(url, credential=self.credential, table_name="foo")
            service = service_type(url, credential=self.credential, table_name="foo", connection_timeout=22)

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_storage_account_name, self.tables_primary_storage_account_key
            )
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout == 300

        # Assert Parent transport is shared with child client
        service = TableServiceClient(
            self.account_url(self.tables_storage_account_name, "table"),
            credential=self.credential,
            connection_timeout=22,
        )
        assert service._client._client._pipeline._transport.connection_config.timeout == 22
        table = service.get_table_client("tablename")
        assert table._client._client._pipeline._transport._transport.connection_config.timeout == 22

    # --Connection String Test Cases --------------------------------------------
    def test_create_service_with_connection_string_key(self):
        # Arrange
        conn_string = (
            f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};"
        )

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_storage_account_name, self.tables_primary_storage_account_key
            )
            assert service.scheme == "https"

    def test_create_service_with_connection_string_sas(self):
        # Arrange
        sas_token = self.generate_sas_token()
        conn_string = (
            f"AccountName={self.tables_storage_account_name};SharedAccessSignature={AzureSasCredential(sas_token)}"
        )

        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.url.startswith(f"https://{self.tables_storage_account_name}.table.core.windows.net")
            assert isinstance(service.credential, AzureSasCredential)

    def test_create_service_with_connection_string_emulated(self):
        conn_string = "UseDevelopmentStorage=true;"
        # Arrange
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                service = service_type.from_connection_string(conn_string, table_name="foo")

    def test_create_service_with_connection_string_custom_domain(self):
        # Arrange
        conn_string = f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};TableEndpoint=www.mydomain.com;"
        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")

    def test_create_service_with_conn_str_custom_domain_trailing_slash(self):
        # Arrange
        conn_string = f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};TableEndpoint=www.mydomain.com/;"
        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")

    def test_create_service_with_conn_str_custom_domain_sec_override(self):
        # Arrange
        conn_string = f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};TableEndpoint=www.mydomain.com/;"
        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", table_name="foo"
            )

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")

    def test_create_service_with_conn_str_fails_if_sec_without_primary(self):
        # Arrange
        conn_string = f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};TableSecondaryEndpoint=www.mydomain.com;"
        for service_type in SERVICES:
            # Act
            # Fails if primary excluded
            with pytest.raises(ValueError) as ex:
                service = service_type.from_connection_string(conn_string, table_name="foo")
            assert str(ex.value) == "Connection string specifies only secondary endpoint."

    def test_create_service_with_conn_str_succeeds_if_sec_with_primary(self):
        # Arrange
        conn_string = f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};TableEndpoint=www.mydomain.com;TableSecondaryEndpoint=www-sec.mydomain.com;"
        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")

    def test_create_service_with_custom_account_endpoint_path(self):
        sas_token = self.generate_sas_token()
        custom_account_url = f"http://local-machine:11002/custom/account/path{AzureSasCredential(sas_token).signature}"
        conn_string = f"DefaultEndpointsProtocol=http;AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};TableEndpoint={custom_account_url};"
        for service_type in SERVICES:
            # Act
            service = service_type.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service.account_name == self.tables_storage_account_name
            assert service.credential.named_key.name == self.tables_storage_account_name
            assert service.credential.named_key.key == self.tables_primary_storage_account_key
            assert service._primary_hostname == "local-machine:11002/custom/account/path"
            assert service.scheme == "http"

        service = TableServiceClient(endpoint=custom_account_url)
        assert service.account_name == "custom"
        assert service.credential == None
        assert service._primary_hostname == "local-machine:11002/custom/account/path"
        assert service.url.startswith("http://local-machine:11002/custom/account/path")
        assert service.scheme == "http"

        service = TableClient(endpoint=custom_account_url, table_name="foo")
        assert service.account_name == "custom"
        assert service.table_name == "foo"
        assert service.credential == None
        assert service._primary_hostname == "local-machine:11002/custom/account/path"
        assert service.url.startswith("http://local-machine:11002/custom/account/path")
        assert service.scheme == "http"

        service = TableClient.from_table_url(
            f"http://local-machine:11002/custom/account/path/foo{AzureSasCredential(sas_token).signature}"
        )
        assert service.account_name == "custom"
        assert service.table_name == "foo"
        assert service.credential == None
        assert service._primary_hostname == "local-machine:11002/custom/account/path"
        assert service.url.startswith("http://local-machine:11002/custom/account/path")
        assert service.scheme == "http"

    def test_create_table_client_with_complete_table_url(self):
        # Arrange
        table_url = self.account_url(self.tables_storage_account_name, "table") + "/foo"
        service = TableClient(table_url, table_name="bar", credential=self.credential)

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_storage_account_name

    def test_create_table_client_with_complete_url(self):
        # Arrange
        table_url = "https://{}.table.{}:443/foo".format(
            self.tables_storage_account_name,
            os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX),
        )
        service = TableClient(endpoint=table_url, table_name="bar", credential=self.credential)

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_storage_account_name

    def test_error_with_malformed_conn_str(self):
        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for service_type in SERVICES:
                # Act
                with pytest.raises(ValueError) as e:
                    service = service_type.from_connection_string(conn_str, table_name="test")

                if conn_str in ("", "foobar", "foo;bar;baz", ";", "foo=;bar=;", "=", "=;=="):
                    assert str(e.value) == "Connection string is either blank or malformed."
                elif conn_str in ("foobar=baz=foo"):
                    assert str(e.value) == "Connection string missing required connection details."

    def test_closing_pipeline_client(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="table")

            # Assert
            with service:
                assert hasattr(service, "close")
                service.close()

    def test_closing_pipeline_client_simple(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="table")
            service.close()

    @pytest.mark.skip("HTTP prefix does not raise an error")
    def test_create_service_with_token_and_http(self):
        for service_type in SERVICES:
            with pytest.raises(ValueError):
                url = self.account_url(self.tables_storage_account_name, "table").replace("https", "http")
                service_type(url, credential=AzureSasCredential("fake_sas_credential"), table_name="foo")

    def test_create_service_with_token(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        token_credential = self.get_token_credential()

        for service_type in SERVICES:
            service = service_type(url, credential=token_credential, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.url.startswith(f"https://{self.tables_storage_account_name}.table.core.windows.net")
            assert service.credential == token_credential
            assert not hasattr(service.credential, "account_key")

    def test_create_client_with_api_version(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        client = TableServiceClient(url, credential=self.credential)
        assert client._client._config.version == "2019-02-02"
        table = client.get_table_client("tablename")
        assert table._client._config.version == "2019-02-02"

        client = TableServiceClient(url, credential=self.credential, api_version="2019-07-07")
        assert client._client._config.version == "2019-07-07"
        table = client.get_table_client("tablename")
        assert table._client._config.version == "2019-07-07"

        with pytest.raises(ValueError):
            TableServiceClient(url, credential=self.credential, api_version="foo")

    def test_create_client_for_azurite(self):
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

        client = TableServiceClient.from_connection_string(http_connstr)
        assert client.account_name == "devstoreaccount1"
        assert client.url == "http://127.0.0.1:10002/devstoreaccount1"
        assert client._location_mode == "primary"
        assert client._secondary_endpoint == "http://127.0.0.1:10002/devstoreaccount1-secondary"
        assert client.credential.named_key.key == self.tables_primary_storage_account_key
        assert client.credential.named_key.name == "devstoreaccount1"
        assert not client._cosmos_endpoint
        assert client.scheme == "http"

        client = TableServiceClient.from_connection_string(https_connstr)
        assert client.account_name == "devstoreaccount1"
        assert client.url == "https://127.0.0.1:10002/devstoreaccount1"
        assert client._location_mode == "primary"
        assert client._secondary_endpoint == "https://127.0.0.1:10002/devstoreaccount1-secondary"
        assert client.credential.named_key.key == self.tables_primary_storage_account_key
        assert client.credential.named_key.name == "devstoreaccount1"
        assert not client._cosmos_endpoint
        assert client.scheme == "https"

        table = TableClient(account_url, "tablename", credential=azurite_credential)
        assert table.account_name == "myaccount"
        assert table.table_name == "tablename"
        assert table.url == "https://127.0.0.1:10002/myaccount"
        assert table._location_mode == "primary"
        assert table._secondary_endpoint == "https://127.0.0.1:10002/myaccount-secondary"
        assert table.credential.named_key.key == azurite_credential.named_key.key
        assert table.credential.named_key.name == azurite_credential.named_key.name
        assert not table._cosmos_endpoint

        table = TableClient.from_connection_string(http_connstr, "tablename")
        assert table.account_name == "devstoreaccount1"
        assert table.table_name == "tablename"
        assert table.url == "http://127.0.0.1:10002/devstoreaccount1"
        assert table._location_mode == "primary"
        assert table._secondary_endpoint == "http://127.0.0.1:10002/devstoreaccount1-secondary"
        assert table.credential.named_key.key == self.tables_primary_storage_account_key
        assert table.credential.named_key.name == "devstoreaccount1"
        assert not table._cosmos_endpoint
        assert table.scheme == "http"

        table = TableClient.from_connection_string(https_connstr, "tablename")
        assert table.account_name == "devstoreaccount1"
        assert table.table_name == "tablename"
        assert table.url == "https://127.0.0.1:10002/devstoreaccount1"
        assert table._location_mode == "primary"
        assert table._secondary_endpoint == "https://127.0.0.1:10002/devstoreaccount1-secondary"
        assert table.credential.named_key.key == self.tables_primary_storage_account_key
        assert table.credential.named_key.name == "devstoreaccount1"
        assert not table._cosmos_endpoint
        assert table.scheme == "https"

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

    def test_validate_storage_tablename(self):
        with pytest.raises(ValueError):
            _validate_storage_tablename("a")
        with pytest.raises(ValueError):
            _validate_storage_tablename("aa")
        _validate_storage_tablename("aaa")
        _validate_storage_tablename("a" * 63)
        with pytest.raises(ValueError):
            _validate_storage_tablename("a" * 64)
        with pytest.raises(ValueError):
            _validate_storage_tablename("aaa-")
        with pytest.raises(ValueError):
            _validate_storage_tablename("aaa ")
        with pytest.raises(ValueError):
            _validate_storage_tablename("a aa")
        with pytest.raises(ValueError):
            _validate_storage_tablename("1aaa")

    def test_use_development_storage(self):
        tsc = TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
        assert tsc.account_name == "devstoreaccount1"
        assert tsc.scheme == "http"
        assert tsc.credential.named_key.name == "devstoreaccount1"
        assert (
            tsc.credential.named_key.key
            == "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
        )
        assert tsc.url == "http://127.0.0.1:10002/devstoreaccount1"
        assert tsc._primary_endpoint == "http://127.0.0.1:10002/devstoreaccount1"
        assert tsc._secondary_endpoint == "http://127.0.0.1:10002/devstoreaccount1-secondary"
        assert not tsc._cosmos_endpoint
