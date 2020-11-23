# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import pytest

from azure.core.exceptions import HttpResponseError

from azure.storage.fileshare import (
    ShareServiceClient,
    Metrics,
    CorsRule,
    RetentionPolicy,
    ShareSmbSettings,
    SmbMultichannel,
    ShareProtocolSettings,
)

from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import (
    StorageTestCase,
    LogCaptured,
    GlobalStorageAccountPreparer
)


# ------------------------------------------------------------------------------


class FileServicePropertiesTest(StorageTestCase):
    def _setup(self, storage_account, storage_account_key):
        url = self.account_url(storage_account, "file")
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
    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_file_service_properties(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)

        protocol_properties1 = ShareProtocolSettings(smb=ShareSmbSettings(multichannel=SmbMultichannel(enabled=False)))
        protocol_properties2 = ShareProtocolSettings(smb=ShareSmbSettings(multichannel=SmbMultichannel(enabled=True)))

        # Act
        resp = self.fsc.set_service_properties(
            hour_metrics=Metrics(), minute_metrics=Metrics(), cors=list(), protocol=protocol_properties1)
        # Assert
        self.assertIsNone(resp)
        props = self.fsc.get_service_properties()
        self._assert_metrics_equal(props['hour_metrics'], Metrics())
        self._assert_metrics_equal(props['minute_metrics'], Metrics())
        self._assert_cors_equal(props['cors'], list())
        self.assertEqual(props['protocol'].smb.multichannel.enabled, False)
        # Assert
        with self.assertRaises(ValueError):
            ShareProtocolSettings(smb=ShareSmbSettings(multichannel=SmbMultichannel()))
        with self.assertRaises(ValueError):
            ShareProtocolSettings(smb=ShareSmbSettings())
        with self.assertRaises(ValueError):
            ShareProtocolSettings()

        # Act
        self.fsc.set_service_properties(
            hour_metrics=Metrics(), minute_metrics=Metrics(), cors=list(), protocol=protocol_properties2)
        props = self.fsc.get_service_properties()
        self.assertEqual(props['protocol'].smb.multichannel.enabled, True)

    # --Test cases per feature ---------------------------------------
    @GlobalStorageAccountPreparer()
    def test_set_hour_metrics(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        self.fsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        received_props = self.fsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @GlobalStorageAccountPreparer()
    def test_set_minute_metrics(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        self.fsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        received_props = self.fsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @GlobalStorageAccountPreparer()
    def test_set_cors(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
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
        self.fsc.set_service_properties(cors=cors)

        # Assert
        received_props = self.fsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

    # --Test cases for errors ---------------------------------------
    @GlobalStorageAccountPreparer()
    def test_retention_no_days(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        # Assert
        self.assertRaises(ValueError,
                          RetentionPolicy,
                          True, None)

    @GlobalStorageAccountPreparer()
    def test_too_many_cors_rules(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        self.assertRaises(HttpResponseError,
                          self.fsc.set_service_properties,
                          None, None, cors)


# ------------------------------------------------------------------------------

