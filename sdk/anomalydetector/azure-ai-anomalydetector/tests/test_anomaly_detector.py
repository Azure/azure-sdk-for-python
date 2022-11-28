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
    EnvironmentVariableLoader,
)
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.ai.anomalydetector.models import *
from azure.core.credentials import AzureKeyCredential

from test_data import get_test_data


class TestAnomalyDetector(AzureRecordedTestCase):
    @recorded_by_proxy
    def test_entire_detect(self, **kwargs):
        end_point = os.environ["ANOMALY_DETECTOR_ENDPOINT"]
        sub_key = os.environ["ANOMALY_DETECTOR_KEY"]

        ad_client = AnomalyDetectorClient(end_point, AzureKeyCredential(sub_key))
        assert ad_client is not None

        data = get_test_data()
        series = []
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        for i in range(len(data["timestamp"])):
            series.append(
                TimeSeriesPoint(timestamp=datetime.strptime(data["timestamp"][i], time_format), value=data["value"][i])
            )

        request = DetectRequest(
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
