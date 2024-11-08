# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import platform

from datetime import datetime, timedelta
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.data.tables import (
    TableServiceClient,
    TableClient,
    TableTransactionError,
    AccountSasPermissions,
    ResourceTypes,
    generate_account_sas,
    __version__ as VERSION,
)
from azure.data.tables._error import _validate_cosmos_tablename
from azure.data.tables._models import LocationMode

from _shared.testcase import TableTestCase
from preparers import cosmos_decorator

SERVICES = [TableServiceClient, TableClient]


class TestTableClientCosmos(AzureRecordedTestCase, TableTestCase):
    @cosmos_decorator
    @recorded_by_proxy
    def test_user_agent_default(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                f"azsdk-python-data-tables/{VERSION} Python/{platform.python_version()} ({platform.platform()})"
                in response.http_request.headers["User-Agent"]
            )

        tables = list(service.list_tables(raw_response_hook=callback))
        assert isinstance(tables, list)

        count = 0
        for table in tables:
            count += 1

    @cosmos_decorator
    @recorded_by_proxy
    def test_user_agent_custom(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        custom_app = "TestApp/v1.0"
        service = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"),
            credential=tables_primary_cosmos_account_key,
            user_agent=custom_app,
        )

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                f"TestApp/v1.0 azsdk-python-data-tables/{VERSION} Python/{platform.python_version()} ({platform.platform()})"
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
                f"TestApp/v2.0 TestApp/v1.0 azsdk-python-data-tables/{VERSION} Python/{platform.python_version()} ({platform.platform()})"
                in response.http_request.headers["User-Agent"]
            )

        tables = list(service.list_tables(raw_response_hook=callback, user_agent="TestApp/v2.0"))
        assert isinstance(tables, list)

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        for table in tables:
            count += 1

    @cosmos_decorator
    @recorded_by_proxy
    def test_user_agent_append(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
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

    @pytest.mark.live_test_only
    @cosmos_decorator
    @recorded_by_proxy
    def test_table_name_errors_bad_chars(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        endpoint = self.account_url(tables_cosmos_account_name, "cosmos")

        # cosmos table names must be a non-empty string without chars '\', '/', '#', '?', trailing space, and less than 255 chars.
        invalid_table_names = ["\\", "//", "#", "?", "- "]
        for invalid_name in invalid_table_names:
            client = TableClient(
                endpoint=endpoint, credential=tables_primary_cosmos_account_key, table_name=invalid_name
            )
            with pytest.raises(ValueError) as error:
                client.create_table()
            assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
            try:
                with pytest.raises(ValueError) as error:
                    client.delete_table()
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
            except HttpResponseError as error:
                # Delete table returns a MethodNotAllowed for tablename == "\"
                if error.error_code != "MethodNotAllowed":
                    raise
            with pytest.raises(ValueError) as error:
                client.create_entity({"PartitionKey": "foo", "RowKey": "foo"})
            assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
            with pytest.raises(ValueError) as error:
                client.upsert_entity({"PartitionKey": "foo", "RowKey": "foo"})
            assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
            with pytest.raises(ValueError) as error:
                client.delete_entity("PK", "RK")
            assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
            with pytest.raises(ValueError) as error:
                batch = []
                batch.append(("upsert", {"PartitionKey": "A", "RowKey": "B"}))
                client.submit_transaction(batch)
            assert "Cosmos table names must contain from 1-255 characters" in str(error.value)

    @pytest.mark.live_test_only
    @cosmos_decorator
    @recorded_by_proxy
    def test_table_name_errors_bad_length(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        endpoint = self.account_url(tables_cosmos_account_name, "cosmos")

        # cosmos table names must be a non-empty string without chars '\', '/', '#', '?', and less than 255 chars.
        client = TableClient(endpoint=endpoint, credential=tables_primary_cosmos_account_key, table_name="-" * 255)
        with pytest.raises(ValueError) as error:
            client.create_table()
        assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
        with pytest.raises(ResourceNotFoundError):
            client.create_entity({"PartitionKey": "foo", "RowKey": "foo"})
        with pytest.raises(ResourceNotFoundError):
            client.upsert_entity({"PartitionKey": "foo", "RowKey": "foo"})
        with pytest.raises(TableTransactionError) as error:
            batch = []
            batch.append(("upsert", {"PartitionKey": "A", "RowKey": "B"}))
            client.submit_transaction(batch)
        assert error.value.error_code == "ResourceNotFound"

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_client_location_mode(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        with TableClient(
            url, table_name, credential=tables_primary_cosmos_account_key, location_mode=LocationMode.SECONDARY
        ) as client:
            client.create_table()
            client.create_entity(entity)
            client.upsert_entity(entity)
            client.get_entity("foo", "bar")

            entities = client.list_entities()
            for e in entities:
                pass

            client.delete_entity(entity)
            client.delete_table()

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_client_with_named_key_credential(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with TableClient.from_table_url(
            f"{base_url}/{table_name}", credential=tables_primary_cosmos_account_key
        ) as client:
            table = client.create_table()
            assert table.name == table_name

        conn_str = f"AccountName={tables_cosmos_account_name};AccountKey={tables_primary_cosmos_account_key.named_key.key};EndpointSuffix=cosmos.azure.com"
        with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass

        with TableClient(
            f"{base_url}/?{sas_token}", table_name, credential=tables_primary_cosmos_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass

        with TableClient.from_table_url(
            f"{base_url}/{table_name}?{sas_token}", credential=tables_primary_cosmos_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass
            client.delete_table()

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_service_client_with_named_key_credential(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        name_filter = f"TableName eq '{table_name}'"
        conn_str = f"AccountName={tables_cosmos_account_name};AccountKey={tables_primary_cosmos_account_key.named_key.key};EndpointSuffix=cosmos.azure.com"

        with TableServiceClient.from_connection_string(conn_str) as client:
            client.create_table(table_name)
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1

        with TableServiceClient(f"{base_url}/?{sas_token}", credential=tables_primary_cosmos_account_key) as client:
            entities = client.get_table_client(table_name).query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass
            client.delete_table(table_name)

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_client_with_sas_token_credential(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
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

        conn_str = f"AccountName={tables_cosmos_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature};TableEndpoint={base_url}"
        with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            for e in entities:
                pass

        with TableClient.from_table_url(f"{base_url}/{table_name}", credential=AzureSasCredential(sas_token)) as client:
            client.delete_table()

        with pytest.raises(ValueError) as ex:
            TableClient(f"{base_url}/?{sas_token}", table_name, credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

        with pytest.raises(ValueError) as ex:
            client = TableClient.from_table_url(
                f"{base_url}/{table_name}?{sas_token}", credential=AzureSasCredential(sas_token)
            )
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_service_client_with_sas_token_credential(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        name_filter = f"TableName eq '{table_name}'"

        with TableServiceClient(base_url, credential=AzureSasCredential(sas_token)) as client:
            client.create_table(table_name)
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1

        conn_str = f"AccountName={tables_cosmos_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature};TableEndpoint={base_url}"
        with TableServiceClient.from_connection_string(conn_str) as client:
            result = client.query_tables(name_filter)
            for table in result:
                pass

        with TableServiceClient(base_url, credential=AzureSasCredential(sas_token)) as client:
            client.delete_table(table_name)

        with pytest.raises(ValueError) as ex:
            TableServiceClient(f"{base_url}/?{sas_token}", credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_client_with_token_credential(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        default_azure_credential = self.get_token_credential()
        self.sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
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

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_service_client_with_token_credential(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        default_azure_credential = self.get_token_credential()
        name_filter = "TableName eq '{}'".format(table_name)
        self.sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
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

    def check_request_auth(self, pipeline_request):
        assert self.sas_token not in pipeline_request.http_request.url
        assert pipeline_request.http_request.headers.get("Authorization") is not None

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_client_without_credential(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
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

    @cosmos_decorator
    @recorded_by_proxy
    def test_table_service_client_without_credential(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        base_url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        name_filter = f"TableName eq '{table_name}'"
        sas_token = self.generate_sas(
            generate_account_sas,
            tables_primary_cosmos_account_key,
            resource_types=ResourceTypes.from_string("sco"),
            permission=AccountSasPermissions.from_string("rwdlacu"),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with pytest.raises(ValueError) as ex:
            client = TableServiceClient(base_url)
        assert str(ex.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

        with TableServiceClient(f"{base_url}/?{sas_token}") as client:
            client.create_table(table_name)
            result = client.query_tables(name_filter)
            assert len(list(result)) == 1
            client.delete_table(table_name)


# --Helpers-----------------------------------------------------------------
def validate_standard_account_endpoints(service, account_name, account_key):
    assert service is not None
    assert service.account_name == account_name
    assert service.credential.named_key.name == account_name
    assert service.credential.named_key.key == account_key
    assert f"{account_name}.table.cosmos.azure.com" in service.url


class TestTableClientCosmosUnitTests(TableTestCase):
    tables_cosmos_account_name = "fake_cosmos_account"
    tables_primary_cosmos_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"
    credential = AzureNamedKeyCredential(name=tables_cosmos_account_name, key=tables_primary_cosmos_account_key)

    # --Direct Parameters Test Cases --------------------------------------------
    def test_create_service_with_key(self):
        # Arrange
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service.scheme == "https"

    def test_create_service_with_connection_string(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint={self.tables_cosmos_account_name}.table.cosmos.azure.com"
        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="test")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service.scheme == "https"

    def test_create_service_with_sas(self):
        # Arrange
        endpoint = self.account_url(self.tables_cosmos_account_name, "cosmos")
        sas_token = self.generate_sas_token()
        for client in SERVICES:
            # Act
            service = client(endpoint=endpoint, credential=AzureSasCredential(sas_token), table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.url.startswith(f"https://{self.tables_cosmos_account_name}.table.cosmos.azure.com")
            assert isinstance(service.credential, AzureSasCredential)

    def test_create_service_with_token(self):
        # Arrange
        endpoint = self.account_url(self.tables_cosmos_account_name, "cosmos")
        token_credential = self.get_token_credential()
        for client in SERVICES:
            # Act
            service = client(endpoint=endpoint, credential=token_credential, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.url.startswith(f"https://{self.tables_cosmos_account_name}.table.cosmos.azure.com")
            assert service.credential == token_credential
            assert not hasattr(service.credential, "account_key")

    @pytest.mark.skip("HTTP prefix does not raise an error")
    def test_create_service_with_token_and_http(self):
        # Arrange
        url = self.account_url(self.tables_cosmos_account_name, "cosmos").replace("https", "http")
        sas_token = self.generate_sas_token()
        for client in SERVICES:
            # Act
            with pytest.raises(ValueError):
                client = client(endpoint=url, credential=AzureSasCredential(sas_token), table_name="foo")

    def test_create_service_protocol(self):
        # Arrange
        endpoint = self.account_url(self.tables_cosmos_account_name, "cosmos").replace("https", "http")
        for client in SERVICES:
            # Act
            service = client(endpoint=endpoint, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service.scheme == "http"

    def test_create_service_empty_key(self):
        for client in SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = client("testaccount", credential="", table_name="foo")

            assert str(e.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

    def test_create_service_with_socket_timeout(self):
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        for client in SERVICES:
            # Act
            default_service = client(url, credential=self.credential, table_name="foo")
            service = client(url, credential=self.credential, table_name="foo", connection_timeout=22)

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service._client._client._pipeline._transport.connection_config.timeout == 22
            assert default_service._client._client._pipeline._transport.connection_config.timeout == 300

    # --Connection String Test Cases --------------------------------------------
    def test_create_service_with_connection_string_key(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint={self.tables_cosmos_account_name}.table.cosmos.azure.com"

        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service.scheme == "https"

    def test_create_service_with_connection_string_sas(self):
        # Arrange
        sas_token = self.generate_sas_token()
        conn_string = f"AccountName={self.tables_cosmos_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature};TableEndpoint=www.mydomain.com"

        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.url.startswith("https://www.mydomain.com")
            assert isinstance(service.credential, AzureSasCredential)

    def test_create_service_with_connection_string_cosmos(self):
        # Arrange
        conn_string = f"DefaultEndpointsProtocol=https;AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint=https://www.mydomain.com"

        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.url.startswith("https://www.mydomain.com")
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")
            assert service.scheme == "https"

    def test_create_service_with_connection_string_emulated(self):
        # Arrange
        conn_string = f"UseDevelopmentStorage=true;"
        for client in SERVICES:
            # Act
            with pytest.raises(ValueError):
                service = client.from_connection_string(conn_string, table_name="foo")

    def test_create_service_with_connection_string_custom_domain(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint=https://www.mydomain.com"
        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")
            assert service.scheme == "https"

    def test_create_service_with_conn_str_custom_domain_trailing_slash(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint=www.mydomain.com/;"
        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")

    def test_create_service_with_conn_str_custom_domain_sec_override(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint=www.mydomain.com/;"
        for client in SERVICES:
            # Act
            service = client.from_connection_string(
                conn_string, secondary_hostname="www-sec.mydomain.com", table_name="foo"
            )

            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")

    def test_create_service_with_conn_str_fails_if_sec_without_primary(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableSecondaryEndpoint=www.mydomain.com;"
        for client in SERVICES:
            # Act
            # Fails if primary excluded
            with pytest.raises(ValueError) as ex:
                service = client.from_connection_string(conn_string, table_name="foo")
            assert str(ex.value) == "Connection string specifies only secondary endpoint."

    def test_create_service_with_conn_str_succeeds_if_sec_with_primary(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint=www.mydomain.com;TableSecondaryEndpoint=www-sec.mydomain.com;"
        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")
            # Assert
            assert service is not None
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_endpoint.startswith("https://www.mydomain.com")

    def test_create_service_with_custom_account_endpoint_path(self):
        sas_token = self.generate_sas_token()
        custom_account_url = f"http://local-machine:11002/custom/account/path{AzureSasCredential(sas_token).signature}"
        conn_string = f"DefaultEndpointsProtocol=http;AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint={custom_account_url};"
        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")

            # Assert
            assert service.account_name == self.tables_cosmos_account_name
            assert service.credential.named_key.name == self.tables_cosmos_account_name
            assert service.credential.named_key.key == self.tables_primary_cosmos_account_key
            assert service._primary_hostname == "local-machine:11002/custom/account/path"
            assert service.scheme == "http"

        service = TableServiceClient(endpoint=custom_account_url)
        assert service.account_name == "custom"
        assert service.credential == None
        assert service._primary_hostname == "local-machine:11002/custom/account/path"
        # mine doesnt have a question mark at the end
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
        table_url = self.account_url(self.tables_cosmos_account_name, "cosmos") + "/foo"
        service = TableClient(endpoint=table_url, credential=self.credential, table_name="bar")

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_cosmos_account_name

    def test_create_table_client_with_complete_url(self):
        # Arrange
        table_url = f"https://{self.tables_cosmos_account_name}.table.cosmos.azure.com:443/foo"
        service = TableClient(endpoint=table_url, credential=self.credential, table_name="bar")

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_cosmos_account_name

    def test_error_with_malformed_conn_str(self):
        # Arrange

        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for client in SERVICES:
                # Act
                with pytest.raises(ValueError) as e:
                    service = client.from_connection_string(conn_str, table_name="test")

                if conn_str in ("", "foobar", "foo;bar;baz", ";", "foo=;bar=;", "=", "=;=="):
                    assert str(e.value) == "Connection string is either blank or malformed."
                elif conn_str in ("foobar=baz=foo"):
                    assert str(e.value) == "Connection string missing required connection details."

    def test_create_client_for_cosmos_emulator(self):
        emulator_credential = AzureNamedKeyCredential("localhost", self.tables_primary_cosmos_account_key)
        emulator_connstr = f"DefaultEndpointsProtocol=http;AccountName=localhost;AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint=http://localhost:8902/;"

        client = TableServiceClient.from_connection_string(emulator_connstr)
        assert client.url == "http://localhost:8902"
        assert client.account_name == "localhost"
        assert client.credential.named_key.name == "localhost"
        assert client.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert client._cosmos_endpoint
        assert client.scheme == "http"

        client = TableServiceClient("http://localhost:8902/", credential=emulator_credential)
        assert client.url == "http://localhost:8902"
        assert client.account_name == "localhost"
        assert client.credential.named_key.name == "localhost"
        assert client.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert client._cosmos_endpoint
        assert client.scheme == "http"

        table = TableClient.from_connection_string(emulator_connstr, "tablename")
        assert table.url == "http://localhost:8902"
        assert table.account_name == "localhost"
        assert table.table_name == "tablename"
        assert table.credential.named_key.name == "localhost"
        assert table.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert table._cosmos_endpoint
        assert table.scheme == "http"

        table = TableClient("http://localhost:8902/", "tablename", credential=emulator_credential)
        assert table.url == "http://localhost:8902"
        assert table.account_name == "localhost"
        assert table.table_name == "tablename"
        assert table.credential.named_key.name == "localhost"
        assert table.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert table._cosmos_endpoint
        assert table.scheme == "http"

        table = TableClient.from_table_url("http://localhost:8902/Tables('tablename')", credential=emulator_credential)
        assert table.url == "http://localhost:8902"
        assert table.account_name == "localhost"
        assert table.table_name == "tablename"
        assert table.credential.named_key.name == "localhost"
        assert table.credential.named_key.key == self.tables_primary_cosmos_account_key
        assert table._cosmos_endpoint
        assert table.scheme == "http"

    def test_closing_pipeline_client(self):
        # Arrange
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="table")

            # Assert
            with service:
                assert hasattr(service, "close")
                service.close()

    def test_closing_pipeline_client_simple(self):
        # Arrange
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="table")
            service.close()

    def test_validate_cosmos_tablename(self):
        _validate_cosmos_tablename("a")
        _validate_cosmos_tablename("1")
        _validate_cosmos_tablename("=-{}!@")
        _validate_cosmos_tablename("a" * 254)
        with pytest.raises(ValueError):
            _validate_cosmos_tablename("\\")
        with pytest.raises(ValueError):
            _validate_cosmos_tablename("/")
        with pytest.raises(ValueError):
            _validate_cosmos_tablename("#")
        with pytest.raises(ValueError):
            _validate_cosmos_tablename("?")
        with pytest.raises(ValueError):
            _validate_cosmos_tablename("a ")
        with pytest.raises(ValueError):
            _validate_cosmos_tablename("a" * 255)
