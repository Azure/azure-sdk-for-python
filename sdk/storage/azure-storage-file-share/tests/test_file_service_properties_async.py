# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.fileshare import (
    CorsRule,
    Metrics,
    RetentionPolicy,
    ShareProtocolSettings,
    ShareSmbSettings,
    SmbMultichannel
)
from azure.storage.fileshare.aio import ShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer


# ------------------------------------------------------------------------------


class TestFileServicePropertiesAsync(AsyncStorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        url = self.account_url(storage_account_name, "file")
        credential = storage_account_key
        self.fsc = ShareServiceClient(url, credential=credential)

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass
    # --Helpers-----------------------------------------------------------------
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
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_file_service_properties(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")
        premium_storage_file_account_key = kwargs.pop("premium_storage_file_account_key")

        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)
        protocol_properties1 = ShareProtocolSettings(smb=ShareSmbSettings(multichannel=SmbMultichannel(enabled=False)))
        protocol_properties2 = ShareProtocolSettings(smb=ShareSmbSettings(multichannel=SmbMultichannel(enabled=True)))

        # Act
        resp = await self.fsc.set_service_properties(
            hour_metrics=Metrics(), minute_metrics=Metrics(), cors=list(), protocol=protocol_properties1)

        # Assert
        assert resp is None
        props = await self.fsc.get_service_properties()
        self._assert_metrics_equal(props['hour_metrics'], Metrics())
        self._assert_metrics_equal(props['minute_metrics'], Metrics())
        self._assert_cors_equal(props['cors'], list())
        assert props['protocol'].smb.multichannel.enabled == False
        # Assert
        with pytest.raises(ValueError):
            ShareProtocolSettings(smb=ShareSmbSettings(multichannel=SmbMultichannel()))
        with pytest.raises(ValueError):
            ShareProtocolSettings(smb=ShareSmbSettings())
        with pytest.raises(ValueError):
            ShareProtocolSettings()

        # Act
        await self.fsc.set_service_properties(
            hour_metrics=Metrics(), minute_metrics=Metrics(), cors=list(), protocol=protocol_properties2)
        props = await self.fsc.get_service_properties()
        assert props['protocol'].smb.multichannel.enabled == True

    # --Test cases per feature ---------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_hour_metrics(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await self.fsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        received_props = await self.fsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_minute_metrics(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await self.fsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        received_props = await self.fsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_cors(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        self._assert_cors_equal(received_props['cors'], cors)

    # --Test cases for errors ---------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_too_many_cors_rules(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        with pytest.raises(HttpResponseError):
            await self.fsc.set_service_properties(None, None, cors)
