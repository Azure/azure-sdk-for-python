#!/usr/bin/env python
# coding=utf-8

import functools
import pytest
import time
import os
from datetime import datetime

from devtools_testutils import (
    AzureRecordedTestCase,
    PowerShellPreparer,
    recorded_by_proxy,
)
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.ai.anomalydetector.models import *
from azure.core.credentials import AzureKeyCredential

from test_data import get_test_data

AnomalyDetectorEnvPreparer = functools.partial(
    PowerShellPreparer,
    "anomaly_detector",
    anomaly_detector_endpoint="https://fake_ad_resource.cognitiveservices.azure.com/",
    anomaly_detector_key="00000000000000000000000000000000",
)


class TestAnomalyDetector(AzureRecordedTestCase):
    @AnomalyDetectorEnvPreparer()
    @recorded_by_proxy
    def test_entire_detect(self, anomaly_detector_endpoint, anomaly_detector_key):

        ad_client = AnomalyDetectorClient(anomaly_detector_endpoint, AzureKeyCredential(anomaly_detector_key))
        assert ad_client is not None

        data = get_test_data()
        series = []
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        for i in range(len(data["timestamp"])):
            series.append(
                TimeSeriesPoint(timestamp=datetime.strptime(data["timestamp"][i], time_format), value=data["value"][i])
            )

        request = UnivariateDetectionOptions(
            series=series,
            granularity=TimeGranularity.DAILY,
        )

        response = ad_client.detect_univariate_entire_series(request)
        detect_index = []
        for i, value in enumerate(response.is_anomaly):
            if value:
                detect_index.append(i)

        assert detect_index == [
            3,
            18,
            21,
            22,
            23,
            24,
            25,
            28,
            29,
            30,
            31,
            32,
            35,
            44,
        ]

    @AnomalyDetectorEnvPreparer()
    @recorded_by_proxy
    def test_multi_ad_list_model(self, anomaly_detector_endpoint, anomaly_detector_key):

        ad_client = AnomalyDetectorClient(anomaly_detector_endpoint, AzureKeyCredential(anomaly_detector_key))
        assert ad_client is not None

        models = ad_client.list_multivariate_models(skip=0, top=10)
        model_count = len(list(models))

        assert model_count >= 0
