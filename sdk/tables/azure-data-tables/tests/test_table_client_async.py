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
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError, ClientAuthenticationError
from azure.identity.aio import DefaultAzureCredential
from azure.data.tables import AccountSasPermissions, ResourceTypes, generate_account_sas, __version__ as VERSION
from azure.data.tables.aio import TableServiceClient, TableClient
from azure.data.tables._models import LocationMode
from azure.data.tables._constants import DEFAULT_STORAGE_ENDPOINT_SUFFIX

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async
from test_table_client import validate_standard_account_endpoints

# ------------------------------------------------------------------------------
SERVICES = [TableServiceClient, TableClient]


class TestTableClientAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_default_async(self, tables_storage_account_name, tables_primary_storage_account_key):
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

        tables = service.list_tables(raw_response_hook=callback)
        assert tables is not None

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

        def callback(response):
            assert "User-Agent" in response.http_request.headers
            assert (
                "TestApp/v2.0 TestApp/v1.0 azsdk-python-data-tables/{} Python/{} ({})".format(
                    VERSION, platform.python_version(), platform.platform()
                )
                in response.http_request.headers["User-Agent"]
            )

        tables = service.list_tables(raw_response_hook=callback, user_agent="TestApp/v2.0")
        assert tables is not None

        # The count doesn't matter, going through the PagedItem calls `callback`
        count = 0
        async for table in tables:
            count += 1

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_agent_append(self, tables_storage_account_name, tables_primary_storage_account_key):
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
        async for table in tables:
            count += 1

    @pytest.mark.live_test_only
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_name_errors(self, tables_storage_account_name, tables_primary_storage_account_key):
        endpoint = self.account_url(tables_storage_account_name, "table")

        # storage table names must be alphanumeric, cannot begin with a number, and must be between 3 and 63 chars long.
        invalid_table_names = ["1table", "a" * 2, "a" * 64, "a//", "my_table"]
        for invalid_name in invalid_table_names:
            client = TableClient(
                endpoint=endpoint, credential=tables_primary_storage_account_key, table_name=invalid_name
            )
            async with client:
                with pytest.raises(ValueError) as error:
                    await client.create_table()
                assert "Storage table names must be alphanumeric" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.create_entity({"PartitionKey": "foo", "RowKey": "bar"})
                assert "Storage table names must be alphanumeric" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.upsert_entity({"PartitionKey": "foo", "RowKey": "foo"})
                assert "Storage table names must be alphanumeric" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.delete_entity("PK", "RK")
                assert "Storage table names must be alphanumeric" in str(error.value)
                with pytest.raises(ValueError) as error:
                    await client.get_table_access_policy()
                assert "Storage table names must be alphanumeric" in str(error.value)
                with pytest.raises(ValueError) as error:
                    batch = []
                    batch.append(("upsert", {"PartitionKey": "A", "RowKey": "B"}))
                    await client.submit_transaction(batch)
                assert "Storage table names must be alphanumeric" in str(error.value)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_client_with_url_ends_with_table_name(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        invalid_url = url + "/" + table_name
        # test table client has the same table name as in url
        tc = TableClient(invalid_url, table_name, credential=tables_primary_storage_account_key)
        with pytest.raises(ResourceNotFoundError) as exc:
            await tc.create_table()
        assert ("table specified does not exist") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        # test table client has a different table name as in url
        table_name2 = self.get_resource_name("mytable2")
        tc2 = TableClient(invalid_url, table_name2, credential=tables_primary_storage_account_key)
        with pytest.raises(ResourceNotFoundError) as exc:
            await tc2.create_table()
        assert ("table specified does not exist") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)

        valid_tc = TableClient(url, table_name, credential=tables_primary_storage_account_key)
        await valid_tc.create_table()
        # test creating a table when it already exists
        with pytest.raises(HttpResponseError) as exc:
            await tc.create_table()
        assert ("values are not specified") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        # test deleting a table when it already exists
        with pytest.raises(HttpResponseError) as exc:
            await tc.delete_table()
        assert ("URI does not match number of key properties for the resource") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        await valid_tc.delete_table()
        await valid_tc.close()
        await tc.close()
        await tc2.close()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_error_handling(self, tables_storage_account_name, tables_primary_storage_account_key):
        async with TableServiceClient(
            self.account_url(tables_storage_account_name, "table"),
            credential=DefaultAzureCredential(
                exclude_shared_token_cache_credential=True,
                exclude_powershell_credential=True,
                exclude_cli_credential=True,
                exclude_environment_credential=True,
            ),
        ) as service_client:
            with pytest.raises(ClientAuthenticationError):
                await service_client.create_table_if_not_exists(table_name="TestInsert")

    def check_request_auth(self, pipeline_request):
        assert self.sas_token not in pipeline_request.http_request.url
        assert pipeline_request.http_request.headers.get("Authorization") is not None

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_location_mode(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, location_mode=LocationMode.SECONDARY
        ) as client:
            with pytest.raises(HttpResponseError) as ex:
                await client.create_table()
            assert "Write operations are not allowed." in str(ex.value)

        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            await client.create_table()
            if self.is_live:
                time.sleep(15)

        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, location_mode=LocationMode.SECONDARY
        ) as client:
            with pytest.raises(HttpResponseError) as ex:
                await client.create_entity(entity)
            assert "Operation returned an invalid status 'Forbidden'" in str(ex.value)

            with pytest.raises(HttpResponseError) as ex:
                await client.upsert_entity(entity)
            assert "Write operations are not allowed." in str(ex.value)

            with pytest.raises(ResourceNotFoundError) as ex:
                await client.get_entity("foo", "bar")
            assert "The specified resource does not exist." in str(ex.value)

            entities = client.list_entities()
            async for e in entities:
                pass

            with pytest.raises(HttpResponseError) as ex:
                await client.delete_entity(entity)
            assert "Write operations are not allowed." in str(ex.value)

            with pytest.raises(HttpResponseError) as ex:
                await client.delete_table()
            assert "Write operations are not allowed." in str(ex.value)

        # clean up
        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_with_named_key_credential(
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

        async with TableClient.from_table_url(
            f"{base_url}/{table_name}", credential=tables_primary_storage_account_key
        ) as client:
            table = await client.create_table()
            assert table.name == table_name

        conn_str = f"AccountName={tables_storage_account_name};AccountKey={tables_primary_storage_account_key.named_key.key};EndpointSuffix=core.windows.net"
        async with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass

        # AzureNamedKeyCredential is actually in use
        async with TableClient(
            f"{base_url}/?{self.sas_token}", table_name, credential=tables_primary_storage_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            async for e in entities:
                pass

        # AzureNamedKeyCredential is actually in use
        async with TableClient.from_table_url(
            f"{base_url}/{table_name}?{self.sas_token}", credential=tables_primary_storage_account_key
        ) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            async for e in entities:
                pass
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_with_named_key_credential(
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

        async with TableServiceClient.from_connection_string(conn_str) as client:
            await client.create_table(table_name)
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1

        # AzureNamedKeyCredential is actually in use
        async with TableServiceClient(
            f"{base_url}/?{self.sas_token}", credential=tables_primary_storage_account_key
        ) as client:
            entities = client.get_table_client(table_name).query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
                raw_request_hook=self.check_request_auth,
            )
            async for e in entities:
                pass
            await client.delete_table(table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_with_sas_token_credential(
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

        conn_str = (
            f"AccountName={tables_storage_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature}"
        )
        async with TableClient.from_connection_string(conn_str, table_name) as client:
            entities = client.query_entities(
                query_filter="PartitionKey eq @pk",
                parameters={"pk": "dummy-pk"},
            )
            async for e in entities:
                pass
            await client.delete_table()

        sas_url = f"{base_url}/{table_name}?{sas_token}"

        with pytest.raises(ValueError) as ex:
            TableClient(sas_url, table_name, credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

        with pytest.raises(ValueError) as ex:
            client = TableClient.from_table_url(sas_url, credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_with_sas_token_credential(
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

        async with TableServiceClient(base_url, credential=AzureSasCredential(sas_token)) as client:
            await client.create_table(table_name)
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1

        conn_str = (
            f"AccountName={tables_storage_account_name};SharedAccessSignature={AzureSasCredential(sas_token).signature}"
        )
        async with TableServiceClient.from_connection_string(conn_str) as client:
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1
            await client.delete_table(table_name)

        with pytest.raises(ValueError) as ex:
            TableServiceClient(f"{base_url}/?{sas_token}", credential=AzureSasCredential(sas_token))
        ex_msg = "You cannot use AzureSasCredential when the resource URI also contains a Shared Access Signature."
        assert ex_msg == str(ex.value)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_with_token_credential(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
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

        # DefaultAzureCredential is actually in use
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

        # DefaultAzureCredential is actually in use
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_with_token_credential(
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

        async with TableServiceClient(base_url, credential=default_azure_credential) as client:
            await client.create_table(table_name)
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
            await client.delete_table(table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_client_without_credential(
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_client_without_credential(
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

        async with TableServiceClient(f"{base_url}/?{sas_token}") as client:
            await client.create_table(table_name)
            count = 0
            result = client.query_tables(name_filter)
            async for table in result:
                count += 1
            assert count == 1
            await client.delete_table(table_name)


class TestTableClientAsyncUnitTests(AsyncTableTestCase):
    tables_storage_account_name = "fake_storage_account"
    tables_primary_storage_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"
    credential = AzureNamedKeyCredential(name=tables_storage_account_name, key=tables_primary_storage_account_key)

    # --Direct Parameters Test Cases --------------------------------------------
    @pytest.mark.asyncio
    async def test_create_service_with_key_async(self):
        # Arrange
        url = self.account_url(self.tables_storage_account_name, "table")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_storage_account_name, self.tables_primary_storage_account_key
            )
            assert service.scheme == "https"

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_sas(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_token_async(self):
        url = self.account_url(self.tables_storage_account_name, "table")
        token_credential = self.get_token_credential()
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=token_credential, table_name="foo")

            # Assert
            assert service is not None
            assert service.account_name == self.tables_storage_account_name
            assert service.url.startswith(f"https://{self.tables_storage_account_name}.table.core.windows.net")
            assert service.credential == token_credential
            assert not hasattr(service.credential, "account_key")

    @pytest.mark.skip("HTTP prefix does not raise an error")
    @pytest.mark.asyncio
    async def test_create_service_with_token_and_http(self):
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                url = self.account_url(self.tables_storage_account_name, "table").replace("https", "http")
                service_type(url, credential=AzureSasCredential("fake_sas_credential"), table_name="foo")

    @pytest.mark.asyncio
    async def test_create_service_protocol_async(self):
        # Arrange
        url = self.account_url(self.tables_storage_account_name, "table").replace("https", "http")
        for service_type in SERVICES:
            # Act
            service = service_type(url, credential=self.credential, table_name="foo")

            # Assert
            validate_standard_account_endpoints(
                service, self.tables_storage_account_name, self.tables_primary_storage_account_key
            )
            assert service.scheme == "http"

    @pytest.mark.asyncio
    async def test_create_service_empty_key_async(self):
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError) as e:
                test_service = service_type("testaccount", credential="", table_name="foo")

            assert str(e.value) == "You need to provide either an AzureSasCredential or AzureNamedKeyCredential"

    @pytest.mark.asyncio
    async def test_create_service_with_socket_timeout_async(self):
        # Arrange
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
    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_key_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_sas_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_emulated_async(self):
        # Arrange
        conn_string = "UseDevelopmentStorage=true;"
        for service_type in SERVICES:
            # Act
            with pytest.raises(ValueError):
                service = service_type.from_connection_string(conn_string, table_name="foo")

    @pytest.mark.asyncio
    async def test_create_service_with_connection_string_custom_domain_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_trailing_slash_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_custom_domain_sec_override_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_fails_if_sec_without_primary_async(self):
        # Arrange
        conn_string = f"AccountName={self.tables_storage_account_name};AccountKey={self.tables_primary_storage_account_key};TableSecondaryEndpoint=www.mydomain.com;"
        for service_type in SERVICES:
            # Act
            # Fails if primary excluded
            with pytest.raises(ValueError) as ex:
                service = service_type.from_connection_string(conn_string, table_name="foo")
            assert str(ex.value) == "Connection string specifies only secondary endpoint."

    @pytest.mark.asyncio
    async def test_create_service_with_conn_str_succeeds_if_sec_with_primary_async(self):
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

    @pytest.mark.asyncio
    async def test_create_service_with_custom_account_endpoint_path_async(self):
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

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_table_url_async(self):
        # Arrange
        table_url = self.account_url(self.tables_storage_account_name, "table") + "/foo"
        service = TableClient(table_url, table_name="bar", credential=self.credential)

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_storage_account_name

    @pytest.mark.asyncio
    async def test_create_table_client_with_complete_url_async(self):
        # Arrange
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
        table_url = "https://{}.table.{}:443/foo".format(self.tables_storage_account_name, endpoint_suffix)
        service = TableClient(endpoint=table_url, table_name="bar", credential=self.credential)

        # Assert
        assert service.scheme == "https"
        assert service.table_name == "bar"
        assert service.account_name == self.tables_storage_account_name

    @pytest.mark.asyncio
    async def test_error_with_malformed_conn_str_async(self):
        for conn_str in ["", "foobar", "foobar=baz=foo", "foo;bar;baz", "foo=;bar=;", "=", ";", "=;=="]:
            for service_type in SERVICES:
                # Act
                with pytest.raises(ValueError) as e:
                    service = service_type.from_connection_string(conn_str, table_name="test")

                if conn_str in ("", "foobar", "foo;bar;baz", ";", "foo=;bar=;", "=", "=;=="):
                    assert str(e.value) == "Connection string is either blank or malformed."
                elif conn_str in ("foobar=baz=foo"):
                    assert str(e.value) == "Connection string missing required connection details."

    @pytest.mark.asyncio
    async def test_closing_pipeline_client_async(self):
        # Arrange
        url = self.account_url(self.tables_storage_account_name, "table")
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
        url = self.account_url(self.tables_storage_account_name, "table")
        for client in SERVICES:
            # Act
            service = client(url, credential=self.credential, table_name="table")
            await service.close()

    @pytest.mark.asyncio
    async def test_create_client_with_api_version(self):
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
        assert client.scheme == "https"

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
        assert table.scheme == "https"

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
        assert table.scheme == "https"

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
