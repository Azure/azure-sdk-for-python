# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import platform

from datetime import datetime, timedelta
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.data.tables import (
    TableTransactionError,
    AccountSasPermissions,
    ResourceTypes,
    generate_account_sas,
    __version__ as VERSION,
)
from azure.data.tables.aio import TableServiceClient, TableClient
from azure.data.tables._models import LocationMode

from test_table_client_cosmos import validate_standard_account_endpoints
from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import cosmos_decorator_async

SERVICES = [TableServiceClient, TableClient]


class TestTableClientCosmosAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_default_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        service = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                f"azsdk-python-data-tables/{VERSION} Python/{platform.python_version()} ({platform.platform()})"
                in response.http_request.headers["User-Agent"]
            )

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

        tables = service.list_tables(raw_response_hook=callback)
        assert tables is not None

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                f"TestApp/v2.0 TestApp/v1.0 azsdk-python-data-tables/{VERSION} Python/{platform.python_version()} ({platform.platform()})"
                in response.http_request.headers["User-Agent"]
            )

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_append(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
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
                endpoint=endpoint, credential=tables_primary_cosmos_account_key, table_name=invalid_name
            )
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
                    if error.error_code != "MethodNotAllowed":
                        raise
                with pytest.raises(ValueError) as error:
                    await client.create_entity({"PartitionKey": "foo", "RowKey": "foo"})
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.upsert_entity({"PartitionKey": "foo", "RowKey": "foo"})
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.delete_entity("PK", "RK")
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
                with pytest.raises(ValueError) as error:
                    batch = []
                    batch.append(("upsert", {"PartitionKey": "A", "RowKey": "B"}))
                    await client.submit_transaction(batch)
                assert "Cosmos table names must contain from 1-255 characters" in str(error.value)

    @pytest.mark.live_test_only
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_name_errors_bad_length(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        endpoint = self.account_url(tables_cosmos_account_name, "cosmos")

        # cosmos table names must be a non-empty string without chars '\', '/', '#', '?', and less than 255 chars.
        client = TableClient(endpoint=endpoint, credential=tables_primary_cosmos_account_key, table_name="-" * 255)
        async with client:
            with pytest.raises(ValueError) as error:
                await client.create_table()
            assert "Cosmos table names must contain from 1-255 characters" in str(error.value)
            with pytest.raises(ResourceNotFoundError):
                await client.create_entity({"PartitionKey": "foo", "RowKey": "foo"})
            with pytest.raises(ResourceNotFoundError):
                await client.upsert_entity({"PartitionKey": "foo", "RowKey": "foo"})
            with pytest.raises(TableTransactionError) as error:
                batch = []
                batch.append(("upsert", {"PartitionKey": "A", "RowKey": "B"}))
                await client.submit_transaction(batch)
            assert error.value.error_code == "ResourceNotFound"

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_location_mode(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        async with TableClient(
            url, table_name, credential=tables_primary_cosmos_account_key, location_mode=LocationMode.SECONDARY
        ) as client:
            await client.create_table()
            await client.create_entity(entity)
            await client.upsert_entity(entity)
            await client.get_entity("foo", "bar")

            entities = client.list_entities()
            async for e in entities:
                pass

            await client.delete_entity(entity)
            await client.delete_table()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_with_named_key_credential(
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

        async with TableClient.from_table_url(
            f"{base_url}/{table_name}", credential=tables_primary_cosmos_account_key
        ) as client:
            table = await client.create_table()
            assert table.name == table_name

        conn_str = f"AccountName={tables_cosmos_account_name};AccountKey={tables_primary_cosmos_account_key.named_key.key};EndpointSuffix=cosmos.azure.com"
        async with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass

        async with TableClient(
            f"{base_url}/?{sas_token}", table_name, credential=tables_primary_cosmos_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass

        async with TableClient.from_table_url(
            f"{base_url}/{table_name}?{sas_token}", credential=tables_primary_cosmos_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass
            await client.delete_table()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_with_named_key_credential(
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

        async with TableServiceClient.from_connection_string(conn_str) as client:
            await client.create_table(table_name)
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1

        async with TableServiceClient(
            f"{base_url}/?{sas_token}", credential=tables_primary_cosmos_account_key
        ) as client:
            entities = client.get_table_client(table_name).query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass
            await client.delete_table(table_name)

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_with_sas_token_credential(
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

        async with TableClient(base_url, table_name, credential=AzureSasCredential(sas_token)) as client:
            table = await client.create_table()
            assert table.name == table_name

        async with TableClient.from_table_url(
            f"{base_url}/{table_name}", credential=AzureSasCredential(sas_token)
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass

        conn_str = f"AccountName={tables_cosmos_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature};TableEndpoint={base_url}"
        async with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass

        async with TableClient.from_table_url(
            f"{base_url}/{table_name}", credential=AzureSasCredential(sas_token)
        ) as client:
            await client.delete_table()

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

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_with_sas_token_credential(
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

        async with TableServiceClient(base_url, credential=AzureSasCredential(sas_token)) as client:
            await client.create_table(table_name)
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1

        conn_str = f"AccountName={tables_cosmos_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature};TableEndpoint={base_url}"
        async with TableServiceClient.from_connection_string(conn_str) as client:
            result = client.query_tables(name_filter)
            async for table in result:
                pass

        async with TableServiceClient(base_url, credential=AzureSasCredential(sas_token)) as client:
            await client.delete_table(table_name)

        with pytest.raises(ValueError) as ex:
            TableServiceClient(f"{base_url}/?{sas_token}", credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_with_token_credential(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
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

        async with TableClient(base_url, table_name, credential=default_azure_credential) as client:
            table = await client.create_table()
            assert table.name == table_name

        async with TableClient.from_table_url(
            f"{base_url}/{table_name}", credential=default_azure_credential
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass

        async with TableClient(
            f"{base_url}/?{self.sas_token}", table_name, credential=default_azure_credential
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            async for e in entities:
                pass

        async with TableClient.from_table_url(
            f"{base_url}/{table_name}?{self.sas_token}", credential=default_azure_credential
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            async for e in entities:
                pass
            await client.delete_table()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_with_token_credential(
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

        async with TableServiceClient(base_url, credential=default_azure_credential) as client:
            await client.create_table(table_name)
            name_filter = "TableName eq '{}'".format(table_name)
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1

        # DefaultAzureCredential is actually in use
        async with TableServiceClient(f"{base_url}/?{self.sas_token}", credential=default_azure_credential) as client:
            entities = client.get_table_client(table_name).query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            async for e in entities:
                pass
            client.delete_table(table_name)

    def check_request_auth(self, pipeline_request):
        assert self.sas_token not in pipeline_request.http_request.url
        assert pipeline_request.http_request.headers.get("Authorization") is not None

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_without_credential(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
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

        async with TableClient(f"{base_url}/?{sas_token}", table_name) as client:
            table = await client.create_table()
            assert table.name == table_name

        with pytest.raises(ValueError) as ex:
            client = TableClient.from_table_url(f"{base_url}/{table_name}")
        assert str(ex.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

        async with TableClient.from_table_url(f"{base_url}/{table_name}?{sas_token}") as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass
            await client.delete_table()

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_without_credential(
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

        async with TableServiceClient(f"{base_url}/?{sas_token}") as client:
            await client.create_table(table_name)
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1
            await client.delete_table(table_name)


class TestTableClientCosmosAsyncUnitTests(AsyncTableTestCase):
    tables_cosmos_account_name = "fake_cosmos_account"
    tables_primary_cosmos_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"
    credential = AzureNamedKeyCredential(name=tables_cosmos_account_name, key=tables_primary_cosmos_account_key)

    # --Direct Parameters Test Cases --------------------------------------------
    @pytest.mark.asyncio
    async def test_create_service_with_key_async(self):
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service.scheme == "https"

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_async(self):
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint={self.tables_cosmos_account_name}.table.cosmos.azure.com"
        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="test")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service.scheme == "https"

    @pytest.mark.asyncio
    async def test_create_service_with_sas(self):
        # Arrange
        sas_token = self.generate_sas_token()
        for service_type in SERVICES:
            # Act
            service = service_type(
                self.account_url(self.tables_cosmos_account_name, "cosmos"),
                credential=AzureSasCredential(sas_token),
                table_name="foo",
            )

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.url.startswith(f"https://{self.tables_cosmos_account_name}.table.cosmos.azure.com")
            assert isinstance(service.credential, AzureSasCredential)

    @pytest.mark.asyncio
    async def test_create_service_with_token_async(self):
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        token_credential = self.get_token_credential()
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=token_credential, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_cosmos_account_name
            assert service.url.startswith(f"https://{self.tables_cosmos_account_name}.table.cosmos.azure.com")
            assert service.credential == token_credential
            assert not hasattr(service.credential, "account_key")

    @pytest.mark.skip("HTTP prefix does not raise an error")
    @pytest.mark.asyncio
    async def test_create_service_with_token_and_http(self):
        url = self.account_url(self.tables_cosmos_account_name, url).replace("https", "http")
        sas_token = self.generate_sas_token()
        for client in SERVICES:
            # Act
            with pytest.raises(ValueError):
                client(url, credential=AzureSasCredential(sas_token), table_name="foo")

    @pytest.mark.asyncio
    async def test_create_service_protocol_async(self):
        # Arrange
        endpoint = self.account_url(self.tables_cosmos_account_name, "cosmos").replace("https", "http")
        for client in SERVICES:
            # Act
            service = client(endpoint, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key
            )
            assert service.scheme == "http"

    @pytest.mark.asyncio
    async def test_create_service_empty_key_async(self):
        # Arrange
        for client in SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = client("testaccount", credential="", table_name="foo")

            assert str(e.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

    @pytest.mark.asyncio
    async def test_create_service_with_socket_timeout_async(self):
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
    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_key_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_sas_async(self):
        # Arrange
        sas_token = self.generate_sas_token()
        conn_string = f"AccountName={self.tables_cosmos_account_name};SharedAccessSignature={AzureSasCredential(sas_token)};TableEndpoint=www.mydomain.com"

        for client in SERVICES:
            # Act
            service = client.from_connection_string(conn_string, table_name="foo")
            # Assert
            assert service is not None
            assert service.url.startswith("https://www.mydomain.com")
            assert isinstance(service.credential, AzureSasCredential)

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_cosmos_async(self):
        # Arrange
        conn_string = f"DefaultEndpointsProtocol=https;AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableEndpoint=www.mydomain.com;"

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

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_emulated_async(self):
        # Arrange
        conn_string = f"UseDevelopmentStorage=true;"

        for client in SERVICES:
            # Act
            with pytest.raises(ValueError):
                service = client.from_connection_string(conn_string, table_name="foo")

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_custom_domain_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_trailing_slash_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_sec_override_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_fails_if_sec_without_primary_async(self):
        # Arrange
        conn_string = f"AccountName={self.tables_cosmos_account_name};AccountKey={self.tables_primary_cosmos_account_key};TableSecondaryEndpoint=www.mydomain.com;"
        for client in SERVICES:
            # Fails if primary excluded
            with pytest.raises(ValueError) as ex:
                service = client.from_connection_string(conn_string, table_name="foo")
            assert str(ex.value) == "Connection string specifies only secondary endpoint."

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_succeeds_if_sec_with_primary_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_custom_account_endpoint_path_async(self):
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

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_table_url_async(self):
        # Arrange
        table_url = self.account_url(self.tables_cosmos_account_name, "cosmos") + "/foo"
        service = TableClient(table_url, table_name="bar", credential=self.credential)

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_cosmos_account_name

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_url_async(self):
        # Arrange
        table_url = "https://{self.tables_cosmos_account_name}.table.cosmos.azure.com:443/foo"
        service = TableClient(table_url, table_name="bar", credential=self.credential)

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_cosmos_account_name

    @pytest.mark.asyncio
    async def test_error_with_malformed_conn_str_async(self):
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

    @pytest.mark.asyncio
    async def test_closing_pipeline_client_async(self):
        # Arrange
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="table")

            # Assert
            async with service:
                assert hasattr(service, "close")
                await service.close()

    @pytest.mark.asyncio
    async def test_closing_pipeline_client_simple_async(self):
        # Arrange
        url = self.account_url(self.tables_cosmos_account_name, "cosmos")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="table")
            await service.close()
