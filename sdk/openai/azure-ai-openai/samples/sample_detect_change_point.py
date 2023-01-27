# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_detect_change_point.py

DESCRIPTION:
    This sample demonstrates how to detect entire series change points.

Prerequisites:
     * The Anomaly Detector client library for Python
     * A .csv file containing a time-series data set with
        UTC-timestamp and numerical values pairings.
        Example data is included in this repo.

USAGE:
    python sample_detect_change_point.py

    Set the environment variables with your own values before running the sample:
    1) ANOMALY_DETECTOR_KEY - your source Form Anomaly Detector API key.
    2) ANOMALY_DETECTOR_ENDPOINT - the endpoint to your source Anomaly Detector resource.
"""

import os
import pandas as pd

from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import *


class DetectChangePointsSample(object):
    def detect_change_point(self):
        SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
        ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]
        TIME_SERIES_DATA_PATH = os.path.join("sample_data", "request-data.csv")

        # Create an Anomaly Detector client

        # <client>
        client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))
        # </client>

        # Load in the time series data file

        # <loadDataFile>
        series = []
        data_file = pd.read_csv(TIME_SERIES_DATA_PATH, header=None, encoding="utf-8", parse_dates=[0])
        for index, row in data_file.iterrows():
            series.append(TimeSeriesPoint(timestamp=row[0], value=row[1]))
        # </loadDataFile>

        # Create a request from the data file

        # <request>
        request = UnivariateChangePointDetectionOptions(
            series=series,
            granularity=TimeGranularity.DAILY,
        )
        # </request>

        # detect change points throughout the entire time series

        # <detectChangePoint>
        print("Detecting change points in the entire time series.")

        try:
            response = client.detect_univariate_change_point(request)

        except Exception as e:
            print(
                "Error code: {}".format(e.error.code),
                "Error message: {}".format(e.error.message),
            )

        if any(response.is_change_point):
            print("An change point was detected at index:")
            for i, value in enumerate(response.is_change_point):
                if value:
                    print(i)
        else:
            print("No change point were detected in the time series.")
        # </detectChangePoint>


if __name__ == "__main__":
    sample = DetectChangePointsSample()
    sample.detect_change_point()
