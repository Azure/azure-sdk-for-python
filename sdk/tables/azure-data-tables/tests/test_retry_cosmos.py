# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import time

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.core.exceptions import ResourceNotFoundError, ServiceRequestError, ServiceResponseError, HttpResponseError
from azure.data.tables import TableClient
from azure.data.tables._models import LocationMode

from test_retry import FailoverRetryTransport, SecondpageFailoverRetryTransport
from preparers import cosmos_decorator
from _shared.testcase import TableTestCase


class TestStorageRetry(AzureRecordedTestCase, TableTestCase):
    @cosmos_decorator
    @recorded_by_proxy
    def test_failover_and_retry_on_secondary(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        # secondary endpoint only works on READ operations: get, list, query.
        # retry request type in frozenset({'PUT', 'HEAD', 'TRACE', 'OPTIONS', 'DELETE', 'GET'})
        with TableClient(
            url,
            table_name,
            credential=tables_primary_cosmos_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            with pytest.raises(ServiceRequestError) as ex:
                client.create_table(failover=ServiceRequestError("Attempting to force failover"))  # POST, not retry
            assert "Attempting to force failover" in str(ex.value)

        # prepare a table
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_table()
        time.sleep(10)

        # test get_entity() without the entity
        with TableClient(
            url,
            table_name,
            credential=tables_primary_cosmos_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceRequestError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceResponseError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=http_response_err)
            assert "The specified resource does not exist." in str(ex.value)

        # prepare an entity
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_entity(entity)
        time.sleep(10)

        # test get_entity() when the entity is ready
        with TableClient(
            url,
            table_name,
            credential=tables_primary_cosmos_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            client.get_entity(
                "foo", "bar", failover=ServiceRequestError("Attempting to force failover")
            )  # GET, succeed when retry
            client.get_entity(
                "foo", "bar", failover=ServiceResponseError("Attempting to force failover")
            )  # GET, succeed when retry
            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            client.get_entity("foo", "bar", failover=http_response_err)  # GET, succeed when retry

            with pytest.raises(ServiceRequestError) as ex:
                client.upsert_entity(
                    entity, failover=ServiceRequestError("Attempting to force failover")
                )  # PATCH, not retry
            assert "Attempting to force failover" in str(ex.value)

        with TableClient(
            url,
            table_name,
            credential=tables_primary_cosmos_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            entities = client.list_entities(
                failover=ServiceRequestError("Attempting to force failover")
            )  # GET, succeed when retry
            for e in entities:
                pass

        with TableClient(
            url,
            table_name,
            credential=tables_primary_cosmos_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            client.delete_entity(
                entity, failover=ServiceRequestError("Attempting to force failover")
            )  # DELETE, succeed when retry

            # clean up
            client.delete_table(failover=ServiceRequestError("Attempting to force failover"))

    @cosmos_decorator
    @recorded_by_proxy
    def test_failover_and_retry_on_primary(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        # prepare a table
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_table()
        time.sleep(10)

        # test get_entity() without the entity
        with TableClient(
            url,
            table_name,
            credential=tables_primary_cosmos_account_key,
            retry_total=5,
            location_mode=LocationMode.SECONDARY,
            transport=FailoverRetryTransport(location_mode=LocationMode.SECONDARY),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceRequestError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceResponseError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=http_response_err)
            assert "The specified resource does not exist." in str(ex.value)

        # prepare an entity
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_entity(entity)
        time.sleep(10)

        # test get_entity() when the entity is ready
        with TableClient(
            url,
            table_name,
            credential=tables_primary_cosmos_account_key,
            retry_total=5,
            location_mode=LocationMode.SECONDARY,
            transport=FailoverRetryTransport(location_mode=LocationMode.SECONDARY),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            client.get_entity(
                "foo", "bar", failover=ServiceRequestError("Attempting to force failover")
            )  # GET, retried on secondary endpoint
            client.get_entity(
                "foo", "bar", failover=ServiceResponseError("Attempting to force failover")
            )  # GET, succeed when retry
            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            client.get_entity("foo", "bar", failover=http_response_err)  # GET, succeed when retry

            entities = client.list_entities(
                failover=ServiceRequestError("Attempting to force failover")
            )  # GET, retried on secondary endpoint
            for e in entities:
                pass

        # clean up
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.delete_table()

    @cosmos_decorator
    @recorded_by_proxy
    def test_failover_and_retry_in_second_page_while_listing(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        entity1 = {"PartitionKey": "k1", "RowKey": "r1"}
        entity2 = {"PartitionKey": "k2", "RowKey": "r2"}

        # prepare entities so that can list in more than one page
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_table()
            client.create_entity(entity1)
            client.create_entity(entity2)

        with TableClient(
            url, table_name, credential=tables_primary_cosmos_account_key, transport=SecondpageFailoverRetryTransport()
        ) as client:
            entities = client.list_entities(
                results_per_page=1, failover=ServiceRequestError("Attempting to force failover")
            )
            next(entities)
            with pytest.raises(AssertionError):
                next(entities)

        # clean up
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.delete_table()
