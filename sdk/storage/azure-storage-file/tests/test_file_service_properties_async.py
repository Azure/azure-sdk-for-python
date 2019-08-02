# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import asyncio

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.storage.file.aio import (
    FileServiceClient,
    Metrics,
    CorsRule,
    RetentionPolicy,
)

from filetestcase import (
    FileTestCase,
    TestMode,
    record,
    not_for_emulator,
)


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


class FileServicePropertiesTest(FileTestCase):
    def setUp(self):
        super(FileServicePropertiesTest, self).setUp()

        url = self.get_file_url()
        credential = self.get_shared_key_credential()
        self.fsc = FileServiceClient(url, credential=credential, transport=AiohttpTestTransport())

    # --Helpers-----------------------------------------------------------------
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
    async def _test_file_service_properties_async(self):
        # Arrange

        # Act
        resp = await self.fsc.set_service_properties(
            hour_metrics=Metrics(), minute_metrics=Metrics(), cors=list())

        # Assert
        self.assertIsNone(resp)
        props = await self.fsc.get_service_properties()
        self._assert_metrics_equal(props.hour_metrics, Metrics())
        self._assert_metrics_equal(props.minute_metrics, Metrics())
        self._assert_cors_equal(props.cors, list())

    @record
    def test_file_service_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_file_service_properties_async())

    # --Test cases per feature ---------------------------------------
    async def _test_set_hour_metrics_async(self):
        # Arrange
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await self.fsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        received_props = await self.fsc.get_service_properties()
        self._assert_metrics_equal(received_props.hour_metrics, hour_metrics)

    @record
    def test_set_hour_metrics_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_hour_metrics_async())

    async def _test_set_minute_metrics_async(self):
        # Arrange
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await self.fsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        received_props = await self.fsc.get_service_properties()
        self._assert_metrics_equal(received_props.minute_metrics, minute_metrics)

    @record
    def test_set_minute_metrics_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_minute_metrics_async())

    async def _test_set_cors_async(self):
        # Arrange
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
        await self.fsc.set_service_properties(cors=cors)

        # Assert
        received_props = await self.fsc.get_service_properties()
        self._assert_cors_equal(received_props.cors, cors)

    @record
    def test_set_cors_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_cors_async())

    # --Test cases for errors ---------------------------------------


    async def _test_too_many_cors_rules_async(self):
        # Arrange
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        with self.assertRaises(HttpResponseError):
            await self.fsc.set_service_properties(None, None, cors)       

    @record
    def test_too_many_cors_rules_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_too_many_cors_rules_async())


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
