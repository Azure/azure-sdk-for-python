# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
from dateutil.tz import tzutc
import pytest
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.metricsadvisor.models import (
    SqlServerDataFeedSource,
    AzureTableDataFeedSource,
    AzureBlobDataFeedSource,
    AzureCosmosDbDataFeedSource,
    DataFeedMetric,
    DataFeedDimension,
    DataFeedSchema,
    DataFeedIngestionSettings,
    DataFeedGranularity,
    DataFeedMissingDataPointFillSettings,
    DataFeedRollupSettings,
    AzureApplicationInsightsDataFeedSource,
    AzureDataExplorerDataFeedSource,
    InfluxDbDataFeedSource,
    AzureDataLakeStorageGen2DataFeedSource,
    MongoDbDataFeedSource,
    MySqlDataFeedSource,
    PostgreSqlDataFeedSource,
)
from base_testcase_aad import TestMetricsAdvisorAdministrationClientBase


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorAdministrationClientBase):

    def test_create_simple_data_feed(self):
        data_feed_name = self.create_random_name("testfeed")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=data_feed_name,
                source=SqlServerDataFeedSource(
                    connection_string=self.sql_server_connection_string,
                    query="select * from adsample2 where Timestamp = @StartTime"
                ),
                granularity="Daily",
                schema=["cost", "revenue"],
                ingestion_settings=datetime.datetime(2019, 10, 1)
            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "SqlServer"
            assert data_feed.source.query is not None
            assert data_feed.granularity.granularity_type ==  "Daily"
            assert data_feed.schema.metrics[0].name ==  "cost"
            assert data_feed.schema.metrics[1].name ==  "revenue"
            assert data_feed.ingestion_settings.ingestion_begin_time == datetime.datetime(2019, 10, 1,  tzinfo=tzutc())
        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_from_sql_server(self):

        data_feed_name = self.create_random_name("testfeed")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=data_feed_name,
                source=SqlServerDataFeedSource(
                    connection_string=self.sql_server_connection_string,
                    query=u"select * from adsample2 where Timestamp = @StartTime"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost", display_name="display cost", description="the cost"),
                        DataFeedMetric(name="revenue", display_name="display revenue", description="the revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category", display_name="display category"),
                        DataFeedDimension(name="city", display_name="display city")
                    ],
                    timestamp_column="Timestamp"
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 10, 1),
                    data_source_request_concurrency=0,
                    ingestion_retry_delay=-1,
                    ingestion_start_offset=-1,
                    stop_retry_after=-1,
                ),
                admins=["yournamehere@microsoft.com"],
                data_feed_description="my first data feed",
                missing_data_point_fill_settings=DataFeedMissingDataPointFillSettings(
                    fill_type="SmartFilling"
                ),
                rollup_settings=DataFeedRollupSettings(
                    rollup_type="NoRollup",
                    rollup_method="None",
                ),
                viewers=["viewers"],
                access_mode="Private",
                action_link_template="action link template"
            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "SqlServer"
            assert data_feed.source.query is not None
            assert data_feed.granularity.granularity_type ==  "Daily"
            assert data_feed.granularity.custom_granularity_value ==  None
            assert data_feed.schema.metrics[0].name ==  "cost"
            assert data_feed.schema.metrics[1].name ==  "revenue"
            assert data_feed.schema.metrics[0].display_name ==  "display cost"
            assert data_feed.schema.metrics[1].display_name ==  "display revenue"
            assert data_feed.schema.metrics[0].description ==  "the cost"
            assert data_feed.schema.metrics[1].description ==  "the revenue"
            assert data_feed.schema.dimensions[0].name ==  "category"
            assert data_feed.schema.dimensions[1].name ==  "city"
            assert data_feed.schema.dimensions[0].display_name ==  "display category"
            assert data_feed.schema.dimensions[1].display_name ==  "display city"
            assert data_feed.ingestion_settings.ingestion_begin_time == datetime.datetime(2019, 10, 1, tzinfo=tzutc())
            assert data_feed.ingestion_settings.data_source_request_concurrency ==  0
            assert data_feed.ingestion_settings.ingestion_retry_delay ==  -1
            assert data_feed.ingestion_settings.ingestion_start_offset ==  -1
            assert data_feed.ingestion_settings.stop_retry_after ==  -1
            assert "yournamehere@microsoft.com" in  data_feed.admins
            assert data_feed.data_feed_description ==  "my first data feed"
            assert data_feed.missing_data_point_fill_settings.fill_type ==  "SmartFilling"
            assert data_feed.rollup_settings.rollup_type ==  "NoRollup"
            assert data_feed.rollup_settings.rollup_method ==  "None"
            assert data_feed.viewers ==  ["viewers"]
            assert data_feed.access_mode ==  "Private"
            assert data_feed.action_link_template ==  "action link template"
            assert data_feed.status ==  "Active"
            assert data_feed.is_admin
            assert data_feed.metric_ids is not None

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

            with pytest.raises(ResourceNotFoundError):
                self.admin_client.get_data_feed(data_feed.id)

    @pytest.mark.skip("skip test")
    def test_create_data_feed_from_sql_server_with_custom_values(self):

        data_feed_name = self.create_random_name("testfeed")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=data_feed_name,
                source=SqlServerDataFeedSource(
                    connection_string=self.sql_server_connection_string,
                    query=u"select * from adsample2 where Timestamp = @StartTime"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Custom",
                    custom_granularity_value=400
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost", display_name="display cost", description="the cost"),
                        DataFeedMetric(name="revenue", display_name="display revenue", description="the revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category", display_name="display category"),
                        DataFeedDimension(name="city", display_name="display city")
                    ],
                    timestamp_column="Timestamp"
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 10, 1),
                    data_source_request_concurrency=0,
                    ingestion_retry_delay=-1,
                    ingestion_start_offset=-1,
                    stop_retry_after=-1,
                ),
                admins=["yournamehere@microsoft.com"],
                data_feed_description="my first data feed",
                missing_data_point_fill_settings=DataFeedMissingDataPointFillSettings(
                    fill_type="CustomValue",
                    custom_fill_value=10
                ),
                rollup_settings=DataFeedRollupSettings(
                    rollup_type="AlreadyRollup",
                    rollup_method="Sum",
                    rollup_identification_value="sumrollup"
                ),
                viewers=["viewers"],
                access_mode="Private",
                action_link_template="action link template"
            )
            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "SqlServer"
            assert data_feed.source.query is not None
            assert data_feed.granularity.granularity_type ==  "Custom"
            assert data_feed.granularity.custom_granularity_value ==  400
            assert data_feed.schema.metrics[0].name ==  "cost"
            assert data_feed.schema.metrics[1].name ==  "revenue"
            assert data_feed.schema.metrics[0].display_name ==  "display cost"
            assert data_feed.schema.metrics[1].display_name ==  "display revenue"
            assert data_feed.schema.metrics[0].description ==  "the cost"
            assert data_feed.schema.metrics[1].description ==  "the revenue"
            assert data_feed.schema.dimensions[0].name ==  "category"
            assert data_feed.schema.dimensions[1].name ==  "city"
            assert data_feed.schema.dimensions[0].display_name ==  "display category"
            assert data_feed.schema.dimensions[1].display_name ==  "display city"
            assert data_feed.ingestion_settings.ingestion_begin_time == datetime.datetime(2019, 10, 1, tzinfo=tzutc())
            assert data_feed.ingestion_settings.data_source_request_concurrency ==  0
            assert data_feed.ingestion_settings.ingestion_retry_delay ==  -1
            assert data_feed.ingestion_settings.ingestion_start_offset ==  -1
            assert data_feed.ingestion_settings.stop_retry_after ==  -1
            assert "yournamehere@microsoft.com" in  data_feed.admins
            assert data_feed.data_feed_description ==  "my first data feed"
            assert data_feed.missing_data_point_fill_settings.fill_type ==  "CustomValue"
            assert data_feed.missing_data_point_fill_settings.custom_fill_value ==  10
            assert data_feed.rollup_settings.rollup_type ==  "AlreadyRollup"
            assert data_feed.rollup_settings.rollup_method ==  "Sum"
            assert data_feed.rollup_settings.rollup_identification_value ==  "sumrollup"
            assert data_feed.viewers ==  ["viewers"]
            assert data_feed.access_mode ==  "Private"
            assert data_feed.action_link_template ==  "action link template"
            assert data_feed.status ==  "Active"
            assert data_feed.is_admin
            assert data_feed.metric_ids is not None

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

            with pytest.raises(ResourceNotFoundError):
                self.admin_client.get_data_feed(data_feed.id)

    def test_create_data_feed_with_azure_table(self):
        name = self.create_random_name("tablefeed")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=AzureTableDataFeedSource(
                    connection_string=self.azure_table_connection_string,
                    query="PartitionKey ge '@StartTime' and PartitionKey lt '@EndTime'",
                    table="adsample"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 10, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "AzureTable"
            assert data_feed.source.table ==  "adsample"
            assert data_feed.source.query ==  "PartitionKey ge '@StartTime' and PartitionKey lt '@EndTime'"
        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_azure_blob(self):
        name = self.create_random_name("blobfeed")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=AzureBlobDataFeedSource(
                    connection_string=self.azure_blob_connection_string,
                    container="adsample",
                    blob_template="%Y/%m/%d/%h/JsonFormatV2.json"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 10, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "AzureBlob"
            assert data_feed.source.container ==  "adsample"
            assert data_feed.source.blob_template ==  "%Y/%m/%d/%h/JsonFormatV2.json"
        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_azure_cosmos_db(self):
        name = self.create_random_name("cosmosfeed")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=AzureCosmosDbDataFeedSource(
                    connection_string=self.azure_cosmosdb_connection_string,
                    sql_query="'SELECT * FROM Items I where I.Timestamp >= @StartTime and I.Timestamp < @EndTime'",
                    database="adsample",
                    collection_id="adsample"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 10, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "AzureCosmosDB"
            assert data_feed.source.database ==  "adsample"
            assert data_feed.source.collection_id ==  "adsample"
            assert data_feed.source.sql_query ==  "'SELECT * FROM Items I where I.Timestamp >= @StartTime and I.Timestamp < @EndTime'"
        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_application_insights(self):
        name = self.create_random_name("applicationinsight")
        try:
            query = "let gran=60m; let starttime=datetime(@StartTime); let endtime=starttime + gran; requests | " \
                "where timestamp >= starttime and timestamp < endtime | summarize request_count = count(), " \
                "duration_avg_ms = avg(duration), duration_95th_ms = percentile(duration, 95), " \
                "duration_max_ms = max(duration) by resultCode"
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=AzureApplicationInsightsDataFeedSource(
                    azure_cloud="Azure",
                    application_id="3706fe8b-98f1-47c7-bf69-b73b6e53274d",
                    api_key=self.application_insights_api_key,
                    query=query
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2021, 7, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "AzureApplicationInsights"
            assert data_feed.source.application_id ==  "3706fe8b-98f1-47c7-bf69-b73b6e53274d"
            assert data_feed.source.query is not None

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_data_explorer(self):
        name = self.create_random_name("azuredataexplorer")
        try:
            query = "let StartDateTime = datetime(@StartTime); let EndDateTime = StartDateTime + 1d; " \
                    "adsample | where Timestamp >= StartDateTime and Timestamp < EndDateTime"
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=AzureDataExplorerDataFeedSource(
                    connection_string=self.azure_data_explorer_connection_string,
                    query=query
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 1, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "AzureDataExplorer"
            assert data_feed.source.query ==  query

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_influxdb(self):
        name = self.create_random_name("influxdb")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=InfluxDbDataFeedSource(
                    connection_string=self.influxdb_connection_string,
                    database="adsample",
                    user_name="adreadonly",
                    password=self.influxdb_password,
                    query="'select * from adsample2 where Timestamp = @StartTime'"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 1, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "InfluxDB"
            assert data_feed.source.query is not None
            assert data_feed.source.database ==  "adsample"
            assert data_feed.source.user_name ==  "adreadonly"

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_datalake(self):
        name = self.create_random_name("datalake")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=AzureDataLakeStorageGen2DataFeedSource(
                    account_name="adsampledatalakegen2",
                    account_key=self.azure_datalake_account_key,
                    file_system_name="adsample",
                    directory_template="%Y/%m/%d",
                    file_template="adsample.json"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost", display_name="Cost"),
                        DataFeedMetric(name="revenue", display_name="Revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category", display_name="Category"),
                        DataFeedDimension(name="city", display_name="City")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 1, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "AzureDataLakeStorageGen2"
            assert data_feed.source.account_name ==  "adsampledatalakegen2"
            assert data_feed.source.file_system_name ==  "adsample"
            assert data_feed.source.directory_template ==  "%Y/%m/%d"
            assert data_feed.source.file_template ==  "adsample.json"

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_mongodb(self):
        name = self.create_random_name("mongodb")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=MongoDbDataFeedSource(
                    connection_string=self.mongodb_connection_string,
                    database="adsample",
                    command='{"find": "adsample", "filter": { Timestamp: { $eq: @StartTime }} "batchSize": 2000,}'
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 1, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "MongoDB"
            assert data_feed.source.database ==  "adsample"
            assert data_feed.source.command, '{"find": "adsample", "filter": { Timestamp: { $eq: @StartTime }} "batchSize": 2000 == }'

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_mysql(self):
        name = self.create_random_name("mysql")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=MySqlDataFeedSource(
                    connection_string=self.mysql_connection_string,
                    query="'select * from adsample2 where Timestamp = @StartTime'"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 1, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "MySql"
            assert data_feed.source.query ==  "'select * from adsample2 where Timestamp = @StartTime'"

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_create_data_feed_with_postgresql(self):
        name = self.create_random_name("postgresql")
        try:
            data_feed = self.admin_client.create_data_feed(
                name=name,
                source=PostgreSqlDataFeedSource(
                    connection_string=self.postgresql_connection_string,
                    query="'select * from adsample2 where Timestamp = @StartTime'"
                ),
                granularity=DataFeedGranularity(
                    granularity_type="Daily",
                ),
                schema=DataFeedSchema(
                    metrics=[
                        DataFeedMetric(name="cost"),
                        DataFeedMetric(name="revenue")
                    ],
                    dimensions=[
                        DataFeedDimension(name="category"),
                        DataFeedDimension(name="city")
                    ],
                ),
                ingestion_settings=DataFeedIngestionSettings(
                    ingestion_begin_time=datetime.datetime(2019, 1, 1),
                ),

            )

            assert data_feed.id is not None
            assert data_feed.created_time is not None
            assert data_feed.name is not None
            assert data_feed.source.data_source_type ==  "PostgreSql"
            assert data_feed.source.query ==  "'select * from adsample2 where Timestamp = @StartTime'"

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    def test_list_data_feeds(self):
        feeds = self.admin_client.list_data_feeds()
        assert len(list(feeds)) > 0

    def test_list_data_feeds_with_data_feed_name(self):
        feeds = self.admin_client.list_data_feeds(data_feed_name="azureSqlDatafeed")
        feed_list = list(feeds)
        assert len(feed_list) == 1

    @pytest.mark.skip("skip test")
    def test_list_data_feeds_with_skip(self):
        all_feeds = self.admin_client.list_data_feeds()
        skipped_feeds = self.admin_client.list_data_feeds(skip=1)
        all_feeds_list = list(all_feeds)
        skipped_feeds_list = list(skipped_feeds)
        assert len(all_feeds_list) == len(skipped_feeds_list) + 1

    def test_list_data_feeds_with_status(self):
        feeds = self.admin_client.list_data_feeds(status="Paused")
        assert len(list(feeds)) == 0

    def test_list_data_feeds_with_source_type(self):
        feeds = self.admin_client.list_data_feeds(data_source_type="SqlServer")
        assert len(list(feeds)) > 0

    def test_list_data_feeds_with_granularity_type(self):
        feeds = self.admin_client.list_data_feeds(granularity_type="Daily")
        assert len(list(feeds)) > 0

    @pytest.mark.skip("skip test")
    def test_update_data_feed_with_model(self):
        data_feed = self._create_data_feed_for_update("update")
        try:
            data_feed.name = "update"
            data_feed.data_feed_description = "updated"
            data_feed.schema.timestamp_column = "time"
            data_feed.ingestion_settings.ingestion_begin_time = datetime.datetime(2021, 12, 10)
            data_feed.ingestion_settings.ingestion_start_offset = 1
            data_feed.ingestion_settings.data_source_request_concurrency = 1
            data_feed.ingestion_settings.ingestion_retry_delay = 1
            data_feed.ingestion_settings.stop_retry_after = 1
            data_feed.rollup_settings.rollup_type = "AlreadyRollup"
            data_feed.rollup_settings.rollup_method = "Sum"
            data_feed.rollup_settings.rollup_identification_value = "sumrollup"
            data_feed.rollup_settings.auto_rollup_group_by_column_names = []
            data_feed.missing_data_point_fill_settings.fill_type = "CustomValue"
            data_feed.missing_data_point_fill_settings.custom_fill_value = 2
            data_feed.access_mode = "Public"
            data_feed.viewers = ["updated"]
            data_feed.status = "Paused"
            data_feed.action_link_template = "updated"
            data_feed.source.connection_string = "updated"
            data_feed.source.query = "get data"

            self.admin_client.update_data_feed(data_feed)
            updated = self.admin_client.get_data_feed(data_feed.id)
            assert updated.name ==  "update"
            assert updated.data_feed_description ==  "updated"
            assert updated.schema.timestamp_column ==  "time"
            assert updated.ingestion_settings.ingestion_begin_time == datetime.datetime(2021, 12, 10, tzinfo=tzutc())
            assert updated.ingestion_settings.ingestion_start_offset ==  1
            assert updated.ingestion_settings.data_source_request_concurrency ==  1
            assert updated.ingestion_settings.ingestion_retry_delay ==  1
            assert updated.ingestion_settings.stop_retry_after ==  1
            assert updated.rollup_settings.rollup_type ==  "AlreadyRollup"
            assert updated.rollup_settings.rollup_method ==  "Sum"
            assert updated.rollup_settings.rollup_identification_value ==  "sumrollup"
            assert updated.missing_data_point_fill_settings.fill_type ==  "CustomValue"
            assert updated.missing_data_point_fill_settings.custom_fill_value ==  2
            assert updated.access_mode ==  "Public"
            assert updated.viewers ==  ["updated"]
            assert updated.status ==  "Paused"
            assert updated.action_link_template ==  "updated"
            assert updated.source.query ==  "get data"

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    @pytest.mark.skip("skip test")
    def test_update_data_feed_with_kwargs(self):

        data_feed = self._create_data_feed_for_update("update")
        try:
            self.admin_client.update_data_feed(
                data_feed.id,
                name="update",
                data_feed_description="updated",
                timestamp_column="time",
                ingestion_begin_time=datetime.datetime(2021, 12, 10),
                ingestion_start_offset=1,
                data_source_request_concurrency=1,
                ingestion_retry_delay=1,
                stop_retry_after=1,
                rollup_type="AlreadyRollup",
                rollup_method="Sum",
                rollup_identification_value="sumrollup",
                auto_rollup_group_by_column_names=[],
                fill_type="CustomValue",
                custom_fill_value=2,
                access_mode="Public",
                viewers=["updated"],
                status="Paused",
                action_link_template="updated",
                source=SqlServerDataFeedSource(
                    connection_string="updated",
                    query="get data"
                )
            )
            updated = self.admin_client.get_data_feed(data_feed.id)
            assert updated.name ==  "update"
            assert updated.data_feed_description ==  "updated"
            assert updated.schema.timestamp_column ==  "time"
            assert updated.ingestion_settings.ingestion_begin_time == datetime.datetime(2021, 12, 10, tzinfo=tzutc())
            assert updated.ingestion_settings.ingestion_start_offset ==  1
            assert updated.ingestion_settings.data_source_request_concurrency ==  1
            assert updated.ingestion_settings.ingestion_retry_delay ==  1
            assert updated.ingestion_settings.stop_retry_after ==  1
            assert updated.rollup_settings.rollup_type ==  "AlreadyRollup"
            assert updated.rollup_settings.rollup_method ==  "Sum"
            assert updated.rollup_settings.rollup_identification_value ==  "sumrollup"
            assert updated.missing_data_point_fill_settings.fill_type ==  "CustomValue"
            assert updated.missing_data_point_fill_settings.custom_fill_value ==  2
            assert updated.access_mode ==  "Public"
            assert updated.viewers ==  ["updated"]
            assert updated.status ==  "Paused"
            assert updated.action_link_template ==  "updated"
            assert updated.source.query ==  "get data"

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    @pytest.mark.skip("skip test")
    def test_update_data_feed_with_model_and_kwargs(self):

        data_feed = self._create_data_feed_for_update("update")
        try:
            data_feed.name = "updateMe"
            data_feed.data_feed_description = "updateMe"
            data_feed.schema.timestamp_column = "don't update me"
            data_feed.ingestion_settings.ingestion_begin_time = datetime.datetime(2021, 12, 22)
            data_feed.ingestion_settings.ingestion_start_offset = 2
            data_feed.ingestion_settings.data_source_request_concurrency = 2
            data_feed.ingestion_settings.ingestion_retry_delay = 2
            data_feed.ingestion_settings.stop_retry_after = 2
            data_feed.rollup_settings.rollup_type = "don't update me"
            data_feed.rollup_settings.rollup_method = "don't update me"
            data_feed.rollup_settings.rollup_identification_value = "don't update me"
            data_feed.rollup_settings.auto_rollup_group_by_column_names = []
            data_feed.missing_data_point_fill_settings.fill_type = "don't update me"
            data_feed.missing_data_point_fill_settings.custom_fill_value = 4
            data_feed.access_mode = "don't update me"
            data_feed.viewers = ["don't update me"]
            data_feed.status = "don't update me"
            data_feed.action_link_template = "don't update me"
            data_feed.source.connection_string = "don't update me"
            data_feed.source.query = "don't update me"

            self.admin_client.update_data_feed(
                data_feed,
                timestamp_column="time",
                ingestion_begin_time=datetime.datetime(2021, 12, 10),
                ingestion_start_offset=1,
                data_source_request_concurrency=1,
                ingestion_retry_delay=1,
                stop_retry_after=1,
                rollup_type="AlreadyRollup",
                rollup_method="Sum",
                rollup_identification_value="sumrollup",
                auto_rollup_group_by_column_names=[],
                fill_type="CustomValue",
                custom_fill_value=2,
                access_mode="Public",
                viewers=["updated"],
                status="Paused",
                action_link_template="updated",
                source=SqlServerDataFeedSource(
                    connection_string="updated",
                    query="get data"
                )
            )
            updated = self.admin_client.get_data_feed(data_feed.id)
            assert updated.name ==  "updateMe"
            assert updated.data_feed_description ==  "updateMe"
            assert updated.schema.timestamp_column ==  "time"
            assert updated.ingestion_settings.ingestion_begin_time == datetime.datetime(2021, 12, 10, tzinfo=tzutc())
            assert updated.ingestion_settings.ingestion_start_offset ==  1
            assert updated.ingestion_settings.data_source_request_concurrency ==  1
            assert updated.ingestion_settings.ingestion_retry_delay ==  1
            assert updated.ingestion_settings.stop_retry_after ==  1
            assert updated.rollup_settings.rollup_type ==  "AlreadyRollup"
            assert updated.rollup_settings.rollup_method ==  "Sum"
            assert updated.rollup_settings.rollup_identification_value ==  "sumrollup"
            assert updated.missing_data_point_fill_settings.fill_type ==  "CustomValue"
            assert updated.missing_data_point_fill_settings.custom_fill_value ==  2
            assert updated.access_mode ==  "Public"
            assert updated.viewers ==  ["updated"]
            assert updated.status ==  "Paused"
            assert updated.action_link_template ==  "updated"
            assert updated.source.query ==  "get data"

        finally:
            self.admin_client.delete_data_feed(data_feed.id)

    @pytest.mark.skip("skip test")
    def test_update_data_feed_by_reseting_properties(self):

        data_feed = self._create_data_feed_for_update("update")
        try:
            self.admin_client.update_data_feed(
                data_feed.id,
                name="update",
                data_feed_description=None,
                timestamp_column=None,
                ingestion_start_offset=None,
                data_source_request_concurrency=None,
                ingestion_retry_delay=None,
                stop_retry_after=None,
                rollup_type=None,
                rollup_method=None,
                rollup_identification_value=None,
                auto_rollup_group_by_column_names=None,
                fill_type=None,
                custom_fill_value=None,
                access_mode=None,
                viewers=None,
                status=None,
                action_link_template=None,
            )
            updated = self.admin_client.get_data_feed(data_feed.id)
            assert updated.name ==  "update"
            # assert updated.data_feed_description ==  ""  # doesn't currently clear
            # assert updated.schema.timestamp_column ==  ""  # doesn't currently clear
            assert updated.ingestion_settings.ingestion_begin_time == datetime.datetime(2019, 10, 1, tzinfo=tzutc())
            assert updated.ingestion_settings.ingestion_start_offset ==  -1
            assert updated.ingestion_settings.data_source_request_concurrency ==  0
            assert updated.ingestion_settings.ingestion_retry_delay ==  -1
            assert updated.ingestion_settings.stop_retry_after ==  -1
            assert updated.rollup_settings.rollup_type ==  "NoRollup"
            assert updated.rollup_settings.rollup_method ==  "None"
            assert updated.rollup_settings.rollup_identification_value ==  None
            assert updated.missing_data_point_fill_settings.fill_type ==  "SmartFilling"
            assert updated.missing_data_point_fill_settings.custom_fill_value ==  0
            assert updated.access_mode ==  "Private"
            # assert updated.viewers ==  ["viewers"] # doesn't currently clear
            assert updated.status ==  "Active"
            # assert updated.action_link_template ==  "updated"  # doesn't currently clear

        finally:
            self.admin_client.delete_data_feed(data_feed.id)
