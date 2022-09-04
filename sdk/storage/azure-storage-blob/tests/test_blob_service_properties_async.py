# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError
from azure.storage.blob import (
    AccountSasPermissions,
    BlobAnalyticsLogging,
    CorsRule,
    generate_account_sas,
    Metrics,
    ResourceTypes,
    RetentionPolicy,
    StaticWebsite
)
from azure.storage.blob.aio import BlobServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer


# ------------------------------------------------------------------------------


class TestServicePropertiesTest(AsyncStorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_properties_default(self, prop):
        assert prop is not None

        self._assert_logging_equal(prop['analytics_logging'], BlobAnalyticsLogging())
        self._assert_metrics_equal(prop['hour_metrics'], Metrics())
        self._assert_metrics_equal(prop['minute_metrics'], Metrics())
        self._assert_cors_equal(prop['cors'], list())

    def _assert_logging_equal(self, log1, log2):
        if log1 is None or log2 is None:
            assert log1 == log2
            return

        assert log1.version == log2.version
        assert log1.read == log2.read
        assert log1.write == log2.write
        assert log1.delete == log2.delete
        self._assert_retention_equal(log1.retention_policy, log2.retention_policy)

    def _assert_delete_retention_policy_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 == policy2
            return

        assert policy1.enabled == policy2.enabled
        assert policy1.days == policy2.days

    def _assert_static_website_equal(self, prop1, prop2):
        if prop1 is None or prop2 is None:
            assert prop1 == prop2
            return

        assert prop1.enabled == prop2.enabled
        assert prop1.index_document == prop2.index_document
        assert prop1.error_document404_path == prop2.error_document404_path
        assert prop1.default_index_document_path == prop2.default_index_document_path

    def _assert_delete_retention_policy_not_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 != policy2
            return

        assert (policy1.enabled == policy2.enabled and policy1.days == policy2.days) is False

    def _assert_metrics_equal(self, metrics1, metrics2):
        if metrics1 is None or metrics2 is None:
            assert metrics1 == metrics2
            return

        assert metrics1.version == metrics2.version
        assert metrics1.enabled == metrics2.enabled
        assert metrics1.include_apis == metrics2.include_apis
        self._assert_retention_equal(metrics1.retention_policy, metrics2.retention_policy)

    def _assert_cors_equal(self, cors1, cors2):
        if cors1 is None or cors2 is None:
            assert cors1 == cors2
            return

        assert len(cors1) == len(cors2)

        for i in range(0, len(cors1)):
            rule1 = cors1[i]
            rule2 = cors2[i]
            assert len(rule1.allowed_origins) == len(rule2.allowed_origins)
            assert len(rule1.allowed_methods) == len(rule2.allowed_methods)
            assert rule1.max_age_in_seconds == rule2.max_age_in_seconds
            assert len(rule1.exposed_headers) == len(rule2.exposed_headers)
            assert len(rule1.allowed_headers) == len(rule2.allowed_headers)

    def _assert_retention_equal(self, ret1, ret2):
        assert ret1.enabled == ret2.enabled
        assert ret1.days == ret2.days

    # --Test cases per service ---------------------------------------
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_empty_set_service_properties_exception(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        with pytest.raises(ValueError):
            await bsc.set_service_properties()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_service_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        # Act
        resp = await bsc.set_service_properties(
            analytics_logging=BlobAnalyticsLogging(),
            hour_metrics=Metrics(),
            minute_metrics=Metrics(),
            cors=list(),
            target_version='2014-02-14'
        )

        # Assert
        assert resp is None
        props = await bsc.get_service_properties()
        self._assert_properties_default(props)
        assert '2014-02-14' == props['target_version']

    # --Test cases per feature ---------------------------------------
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_default_service_version(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        # Act
        await bsc.set_service_properties(target_version='2014-02-14')

        # Assert
        received_props = await bsc.get_service_properties()
        assert received_props['target_version'] == '2014-02-14'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_delete_retention_policy(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        delete_retention_policy = RetentionPolicy(enabled=True, days=2)

        # Act
        await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_delete_retention_policy_edge_cases(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Should work with minimum settings
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        delete_retention_policy = RetentionPolicy(enabled=True, days=1)
        await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

        # Should work with maximum settings
        delete_retention_policy = RetentionPolicy(enabled=True, days=365)
        await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

        # Should not work with 0 days
        delete_retention_policy = RetentionPolicy(enabled=True, days=0)

        with pytest.raises(HttpResponseError):
            await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_not_equal(received_props['delete_retention_policy'], delete_retention_policy)

        # Should not work with 366 days
        delete_retention_policy = RetentionPolicy(enabled=True, days=366)

        with pytest.raises(HttpResponseError):
            await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_not_equal(received_props['delete_retention_policy'], delete_retention_policy)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_disabled_delete_retention_policy(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        delete_retention_policy = RetentionPolicy(enabled=False)

        # Act
        await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_static_website_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        static_website = StaticWebsite(
            enabled=True,
            index_document="index.html",
            error_document404_path="errors/error/404error.html")

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_static_website_properties_with_default_index_document_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        static_website = StaticWebsite(
            enabled=True,
            error_document404_path="errors/error/404error.html",
            default_index_document_path="index.html")

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_static_web_props_missing_field(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Case1: Arrange both missing
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        static_website = StaticWebsite(enabled=True)

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)

        # Case2: Arrange index document missing
        static_website = StaticWebsite(enabled=True, error_document404_path="errors/error/404error.html")

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)

        # Case3: Arrange error document missing
        static_website = StaticWebsite(enabled=True, index_document="index.html")

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_disabled_static_website_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        static_website = StaticWebsite(enabled=False, index_document="index.html",
                                       error_document404_path="errors/error/404error.html")

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], StaticWebsite(enabled=False))

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_static_webprops_no_impact_other_props(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])

        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers)

        cors = [cors_rule1, cors_rule2]

        # Act
        await bsc.set_service_properties(cors=cors)

        # Assert cors is updated
        received_props = await bsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        static_website = StaticWebsite(enabled=True, index_document="index.html",
                                       error_document404_path="errors/error/404error.html")

        # Act to set static website
        await bsc.set_service_properties(static_website=static_website)

        # Assert static website was updated was cors was unchanged
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)
        self._assert_cors_equal(received_props['cors'], cors)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_logging(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        logging = BlobAnalyticsLogging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await bsc.set_service_properties(analytics_logging=logging)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_logging_equal(received_props['analytics_logging'], logging)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_hour_metrics(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await bsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_minute_metrics(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await bsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_cors(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])

        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers)

        cors = [cors_rule1, cors_rule2]

        # Act
        await bsc.set_service_properties(cors=cors)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_service_properties_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        sas_token = generate_account_sas(
            account_name=storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=3)
        )
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=sas_token)

        # Act
        props = await bsc.get_service_properties()

        # Assert
        assert props is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_retention_no_days(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Assert
        pytest.raises(ValueError,
                          RetentionPolicy,
                          True, None)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_too_many_cors_rules(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        with pytest.raises(HttpResponseError):
            await bsc.set_service_properties(None, None, None, cors)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_retention_too_long(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=366))

        # Assert
        with pytest.raises(HttpResponseError):
            await bsc.set_service_properties(None, None, minute_metrics)

# ------------------------------------------------------------------------------
