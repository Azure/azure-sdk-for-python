# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


# This sample demonstrates the Anomaly Detection service's two detection methods:
#    * Anomaly detection on an entire time-series dataset.
#    * Anomaly detection on the latest data point in a dataset.

# * Prerequisites:
#     * The Anomaly Detector client library for Python
#     * A .csv file containing a time-series data set with 
#        UTC-timestamp and numerical values pairings. 
#        Example data is included in this repo.

# <imports>
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.ai.anomalydetector.models import DetectRequest, TimeSeriesPoint, TimeGranularity, \
    AnomalyDetectorError
from azure.core.credentials import AzureKeyCredential
import pandas as pd
import os
# </imports>

# <initVars>
# This sample assumes you have created an environment variable for your key and endpoint
SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]

TIME_SERIES_DATA_PATH = "request-data.csv"
# </initVars>

# Create an Anomaly Detector client and add the 

# <client>
client = AnomalyDetectorClient(AzureKeyCredential(SUBSCRIPTION_KEY), ANOMALY_DETECTOR_ENDPOINT)
# </client>

# Load in the time series data file

# <loadDataFile>
series = []
data_file = pd.read_csv(TIME_SERIES_DATA_PATH, header=None, encoding='utf-8', parse_dates=[0])
for index, row in data_file.iterrows():
    series.append(TimeSeriesPoint(timestamp=row[0], value=row[1]))
# </loadDataFile>

# Create a request from the data file 

# <request>
request = DetectRequest(series=series, granularity=TimeGranularity.daily)
# </request>


# detect anomalies throughout the entire time series, as a batch

# <detectAnomaliesBatch>
print('Detecting anomalies in the entire time series.')

try:
    response = client.detect_entire_series(request)
except Exception as e:
    if isinstance(e, AnomalyDetectorError):
        print('Error code: {}'.format(e.error.code),
            'Error message: {}'.format(e.error.message))
    else:
        print(e)

if True in response.is_anomaly:
    print('An anomaly was detected at index:')
    for i in range(len(response.is_anomaly)):
        if response.is_anomaly[i]:
            print(i)
else:
    print('No anomalies were detected in the time series.')
# </detectAnomaliesBatch>

# Detect the anomaly status of the latest data point

# <latestPointDetection>
print('Detecting the anomaly status of the latest data point.')

try:
    response = client.detect_last_point(request)
except Exception as e:
    if isinstance(e, AnomalyDetectorError):
        print('Error code: {}'.format(e.error.code),
            'Error message: {}'.format(e.error.message))
    else:
        print(e)

if response.is_anomaly:
    print('The latest point is detected as anomaly.')
else:
    print('The latest point is not detected as anomaly.')
# </latestPointDetection>

# detect change points throughout the entire time series

# <detectChangePoint>
print('Detecting change points in the entire time series.')

try:
    response = client.detect_change_point(request)
except Exception as e:
    if isinstance(e, AnomalyDetectorError):
        print('Error code: {}'.format(e.error.code),
            'Error message: {}'.format(e.error.message))
    else:
        print(e)

if True in response.is_change_point:
    print('An change point was detected at index:')
    for i in range(len(response.is_change_point)):
        if response.is_change_point[i]:
            print(i)
else:
    print('No change point were detected in the time series.')
# </detectChangePoint>