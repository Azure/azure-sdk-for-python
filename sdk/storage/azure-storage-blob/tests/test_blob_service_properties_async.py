# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import asyncio

from msrest.exceptions import ValidationError  # TODO This should be an azure-core error.
from azure.core.exceptions import HttpResponseError
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob import (
    BlobAnalyticsLogging,
    Metrics,
    CorsRule,
    RetentionPolicy,
    StaticWebsite,
)
from _shared.testcase import GlobalStorageAccountPreparer
from _shared.asynctestcase import AsyncStorageTestCase


# ------------------------------------------------------------------------------
class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response

class ServicePropertiesTestAsync(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_properties_default(self, prop):
        self.assertIsNotNone(prop)

        self._assert_logging_equal(prop['analytics_logging'], BlobAnalyticsLogging())
        self._assert_metrics_equal(prop['hour_metrics'], Metrics())
        self._assert_metrics_equal(prop['minute_metrics'], Metrics())
        self._assert_cors_equal(prop['cors'], list())

    def _assert_logging_equal(self, log1, log2):
        if log1 is None or log2 is None:
            self.assertEqual(log1, log2)
            return

        self.assertEqual(log1.version, log2.version)
        self.assertEqual(log1.read, log2.read)
        self.assertEqual(log1.write, log2.write)
        self.assertEqual(log1.delete, log2.delete)
        self._assert_retention_equal(log1.retention_policy, log2.retention_policy)

    def _assert_delete_retention_policy_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            self.assertEqual(policy1, policy2)
            return

        self.assertEqual(policy1.enabled, policy2.enabled)
        self.assertEqual(policy1.days, policy2.days)

    def _assert_static_website_equal(self, prop1, prop2):
        if prop1 is None or prop2 is None:
            self.assertEqual(prop1, prop2)
            return

        self.assertEqual(prop1.enabled, prop2.enabled)
        self.assertEqual(prop1.index_document, prop2.index_document)
        self.assertEqual(prop1.error_document404_path, prop2.error_document404_path)

    def _assert_delete_retention_policy_not_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            self.assertNotEqual(policy1, policy2)
            return

        self.assertFalse(policy1.enabled == policy2.enabled
                         and policy1.days == policy2.days)

    def _assert_metrics_equal(self, metrics1, metrics2):
        if metrics1 is None or metrics2 is None:
            self.assertEqual(metrics1, metrics2)
            return

        self.assertEqual(metrics1.version, metrics2.version)
        self.assertEqual(metrics1.enabled, metrics2.enabled)
        self.assertEqual(metrics1.include_apis, metrics2.include_apis)
        self._assert_retention_equal(metrics1.retention_policy, metrics2.retention_policy)

    def _assert_cors_equal(self, cors1, cors2):
        if cors1 is None or cors2 is None:
            self.assertEqual(cors1, cors2)
            return

        self.assertEqual(len(cors1), len(cors2))

        for i in range(0, len(cors1)):
            rule1 = cors1[i]
            rule2 = cors2[i]
            self.assertEqual(len(rule1.allowed_origins), len(rule2.allowed_origins))
            self.assertEqual(len(rule1.allowed_methods), len(rule2.allowed_methods))
            self.assertEqual(rule1.max_age_in_seconds, rule2.max_age_in_seconds)
            self.assertEqual(len(rule1.exposed_headers), len(rule2.exposed_headers))
            self.assertEqual(len(rule1.allowed_headers), len(rule2.allowed_headers))

    def _assert_retention_equal(self, ret1, ret2):
        self.assertEqual(ret1.enabled, ret2.enabled)
        self.assertEqual(ret1.days, ret2.days)

    # --Test cases per service ---------------------------------------
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_service_properties(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())

        # Act
        resp = await bsc.set_service_properties(
            analytics_logging=BlobAnalyticsLogging(),
            hour_metrics=Metrics(),
            minute_metrics=Metrics(),
            cors=list(),
            target_version='2014-02-14'
        )

        # Assert
        self.assertIsNone(resp)
        props = await bsc.get_service_properties()
        self._assert_properties_default(props)
        self.assertEqual('2014-02-14', props['target_version'])

    # --Test cases per feature ---------------------------------------
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_default_service_version(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())

        # Act
        await bsc.set_service_properties(target_version='2014-02-14')

        # Assert
        received_props = await bsc.get_service_properties()
        self.assertEqual(received_props['target_version'], '2014-02-14')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_delete_retention_policy(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        delete_retention_policy = RetentionPolicy(enabled=True, days=2)

        # Act
        await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_delete_retention_policy_edge_cases(self, resource_group, location, storage_account, storage_account_key):
        # Should work with minimum settings
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())

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

        with self.assertRaises(ValidationError):
            await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_not_equal(received_props['delete_retention_policy'], delete_retention_policy)

        # Should not work with 366 days
        delete_retention_policy = RetentionPolicy(enabled=True, days=366)

        with self.assertRaises(HttpResponseError):
            await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_not_equal(received_props['delete_retention_policy'], delete_retention_policy)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_disabled_delete_retention_policy(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        delete_retention_policy = RetentionPolicy(enabled=False)

        # Act
        await bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_static_website_properties(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        static_website = StaticWebsite(
            enabled=True,
            index_document="index.html",
            error_document404_path="errors/error/404error.html")

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_static_web_props_missing_field(self, resource_group, location, storage_account, storage_account_key):
        # Case1: Arrange both missing
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())

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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_disabled_static_website_properties(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        static_website = StaticWebsite(enabled=False, index_document="index.html",
                                       error_document404_path="errors/error/404error.html")

        # Act
        await bsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], StaticWebsite(enabled=False))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_static_webprops_no_impact_other_props(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
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

        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        static_website = StaticWebsite(enabled=True, index_document="index.html",
                                       error_document404_path="errors/error/404error.html")

        # Act to set static website
        await bsc.set_service_properties(static_website=static_website)

        # Assert static website was updated was cors was unchanged
        received_props = await bsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)
        self._assert_cors_equal(received_props['cors'], cors)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_logging(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        logging = BlobAnalyticsLogging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await bsc.set_service_properties(analytics_logging=logging)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_logging_equal(received_props['analytics_logging'], logging)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_hour_metrics(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await bsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_minute_metrics(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await bsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        received_props = await bsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_cors(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_retention_no_days(self, resource_group, location, storage_account, storage_account_key):
        # Assert
        self.assertRaises(ValueError,
                          RetentionPolicy,
                          True, None)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_too_many_cors_rules(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        with self.assertRaises(HttpResponseError):
            await bsc.set_service_properties(None, None, None, cors)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_retention_too_long(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=366))

        # Assert
        with self.assertRaises(HttpResponseError):
            await bsc.set_service_properties(None, None, minute_metrics)

# ------------------------------------------------------------------------------
