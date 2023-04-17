#!/usr/bin/env python
# coding=utf-8

import functools
import pytest
import time
import os
import json
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
    anomaly_detector_data_source="https://fake_ad_resource.blob.core.windows.net/adtestdata/adtestdata.csv"
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

    @AnomalyDetectorEnvPreparer()
    @recorded_by_proxy
    def test_multi_ad_train_and_get_model(self, anomaly_detector_endpoint, anomaly_detector_key, anomaly_detector_data_source):

        time_format = "%Y-%m-%dT%H:%M:%SZ"
        train_body = ModelInfo(
            data_source=anomaly_detector_data_source,
            start_time=datetime.strptime("2021-01-02T00:00:00Z", time_format),
            end_time=datetime.strptime("2021-01-02T05:00:00Z", time_format),
            data_schema=DataSchema.ONE_TABLE,
            display_name="sample",
            sliding_window=200,
            align_policy=AlignPolicy(
                align_mode=AlignMode.OUTER,
                fill_n_a_method=FillNAMethod.LINEAR,
                padding_value=0,
            ),
        )

        ad_client = AnomalyDetectorClient(anomaly_detector_endpoint, AzureKeyCredential(anomaly_detector_key))
        assert ad_client is not None

        model = ad_client.train_multivariate_model(train_body)
        assert model is not None and model.model_id is not None

        model_id = model.model_id
        
        ## Wait until the model is ready. It usually takes several minutes
        model_status = None
        model = None

        while model_status != ModelStatus.READY and model_status != ModelStatus.FAILED:
            model = ad_client.get_multivariate_model(model_id)
            assert model is not None and model.model_info is not None
            model_status = model.model_info.status
            assert model_status == ModelStatus.CREATED or model_status == ModelStatus.RUNNING or model_status == ModelStatus.READY or model_status == ModelStatus.FAILED
            time.sleep(10)

        assert model_status == ModelStatus.READY
        with open("modelid", "w") as f:
            f.write(model_id)
    
    @AnomalyDetectorEnvPreparer()
    @recorded_by_proxy
    def test_multi_ad_batch_detect_and_get_result(self, anomaly_detector_endpoint, anomaly_detector_key, anomaly_detector_data_source):
        # Detect anomaly in the same data source (but a different interval)
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        batch_inference_body = MultivariateBatchDetectionOptions(
            data_source=anomaly_detector_data_source,
            top_contributor_count=10,
            start_time=datetime.strptime("2021-01-02T00:00:00Z", time_format),
            end_time=datetime.strptime("2021-01-02T05:00:00Z", time_format),
        )

        ad_client = AnomalyDetectorClient(anomaly_detector_endpoint, AzureKeyCredential(anomaly_detector_key))
        assert ad_client is not None

        model_id = None
        with open("modelid", "r") as f:
            model_id = f.read()
 
        result = ad_client.detect_multivariate_batch_anomaly(model_id, batch_inference_body)
        assert result is not None and result.result_id is not None

        result_id = result.result_id

        # Get results (may need a few seconds)
        r = ad_client.get_multivariate_batch_detection_result(result_id)
        assert r is not None and r.summary is not None

        while (
            r.summary.status != MultivariateBatchDetectionStatus.READY
            and r.summary.status != MultivariateBatchDetectionStatus.FAILED
        ):
            r = ad_client.get_multivariate_batch_detection_result(result_id)
            time.sleep(15)

        assert r.summary.status == MultivariateBatchDetectionStatus.READY

    @AnomalyDetectorEnvPreparer()
    @recorded_by_proxy
    def test_multi_ad_last_detect(self, anomaly_detector_endpoint, anomaly_detector_key):
        #same variable number and variable name with training data, or it will fail.
        with open("./samples/sample_data/multivariate_sample_data.json") as f:
            variables_data = json.load(f)
            variables = []
            for item in variables_data["variables"]:
                variables.append(
                    VariableValues(
                        variable=item["variable"],
                        timestamps=item["timestamps"],
                        values=item["values"],
                    )
                )

            last_inference_body = MultivariateLastDetectionOptions(
                variables=variables,
                top_contributor_count=10,
            )

            ad_client = AnomalyDetectorClient(anomaly_detector_endpoint, AzureKeyCredential(anomaly_detector_key))
            assert ad_client is not None

            model_id = None
            with open("modelid", "r") as f:
                model_id = f.read()

            last_detect_result = ad_client.detect_multivariate_last_anomaly(model_id, last_inference_body)
            assert last_detect_result is not None

    @AnomalyDetectorEnvPreparer()
    @recorded_by_proxy
    def test_multi_ad_delete_model(self, anomaly_detector_endpoint, anomaly_detector_key):

        ad_client = AnomalyDetectorClient(anomaly_detector_endpoint, AzureKeyCredential(anomaly_detector_key))
        assert ad_client is not None

        model_id = None
        with open("modelid", "r") as f:
            model_id = f.read()

        ad_client.delete_multivariate_model(model_id)