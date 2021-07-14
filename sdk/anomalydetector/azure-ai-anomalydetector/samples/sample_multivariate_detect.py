# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
FILE: sample_multivariate_detect.py

DESCRIPTION:
    This sample demonstrates how to use multivariate dataset to train a model and use the model to detect anomalies.

Prerequisites:
     * The Anomaly Detector client library for Python
     * A valid data feed

USAGE:
    python sample_multivariate_detect.py

    Set the environment variables with your own values before running the sample:
    1) ANOMALY_DETECTOR_KEY - your source Form Anomaly Detector API key.
    2) ANOMALY_DETECTOR_ENDPOINT - the endpoint to your source Anomaly Detector resource.
"""

import os
import time
from datetime import datetime, timezone

from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.ai.anomalydetector.models import DetectionRequest, ModelInfo
from azure.ai.anomalydetector.models import ModelStatus, DetectionStatus
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError


class MultivariateSample:

    def __init__(self, subscription_key, anomaly_detector_endpoint, data_source=None):
        self.sub_key = subscription_key
        self.end_point = anomaly_detector_endpoint

        # Create an Anomaly Detector client

        # <client>
        self.ad_client = AnomalyDetectorClient(AzureKeyCredential(self.sub_key), self.end_point)
        # </client>

        self.data_source = data_source

    def train(self, start_time, end_time):

        # Number of models available now
        model_list = list(self.ad_client.list_multivariate_model(skip=0, top=10000))
        print("{:d} available models before training.".format(len(model_list)))

        # Use sample data to train the model
        print("Training new model...(it may take a few minutes)")
        data_feed = ModelInfo(start_time=start_time, end_time=end_time, source=self.data_source)
        response_header = \
            self.ad_client.train_multivariate_model(data_feed, cls=lambda *args: [args[i] for i in range(len(args))])[
                -1]
        trained_model_id = response_header['Location'].split("/")[-1]

        # Wait until the model is ready. It usually takes several minutes
        model_status = None

        while model_status != ModelStatus.READY and model_status != ModelStatus.FAILED:
            model_info = self.ad_client.get_multivariate_model(trained_model_id).model_info
            model_status = model_info.status
            time.sleep(1)

        if model_status == ModelStatus.FAILED:
            print("Creating model failed.")
            print("Errors:")
            if model_info.errors:
                for error in model_info.errors:
                    print("Error code: {}. Message: {}".format(error.code, error.message))
            else:
                print("None")
            return None

        if model_status == ModelStatus.READY:
            # Model list after training
            new_model_list = list(self.ad_client.list_multivariate_model(skip=0, top=10000))

            print("Done.\n--------------------")
            print("{:d} available models after training.".format(len(new_model_list)))

            # Return the latest model id
            return trained_model_id


    def detect(self, model_id, start_time, end_time):

        # Detect anomaly in the same data source (but a different interval)
        try:
            detection_req = DetectionRequest(source=self.data_source, start_time=start_time, end_time=end_time)
            response_header = self.ad_client.detect_anomaly(model_id, detection_req,
                                                            cls=lambda *args: [args[i] for i in range(len(args))])[-1]
            result_id = response_header['Location'].split("/")[-1]

            # Get results (may need a few seconds)
            r = self.ad_client.get_detection_result(result_id)
            print("Get detection result...(it may take a few seconds)")

            while r.summary.status != DetectionStatus.READY and r.summary.status != DetectionStatus.FAILED:
                r = self.ad_client.get_detection_result(result_id)
                time.sleep(1)

            if r.summary.status == DetectionStatus.FAILED:
                print("Detection failed.")
                print("Errors:")
                if r.summary.errors:
                    for error in r.summary.errors:
                        print("Error code: {}. Message: {}".format(error.code, error.message))
                else:
                    print("None")
                return None

        except HttpResponseError as e:
            print('Error code: {}'.format(e.error.code), 'Error message: {}'.format(e.error.message))
        except Exception as e:
            raise e

        return r

    def export_model(self, model_id, model_path="model.zip"):

        # Export the model
        model_stream_generator = self.ad_client.export_model(model_id)
        with open(model_path, "wb") as f_obj:
            while True:
                try:
                    f_obj.write(next(model_stream_generator))
                except StopIteration:
                    break
                except Exception as e:
                    raise e

    def delete_model(self, model_id):

        # Delete the mdoel
        self.ad_client.delete_multivariate_model(model_id)
        model_list_after_delete = list(self.ad_client.list_multivariate_model(skip=0, top=10000))
        print("{:d} available models after deletion.".format(len(model_list_after_delete)))


if __name__ == '__main__':
    SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
    ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]

    # *****************************
    # Use your own data source here
    # *****************************
    data_source = "<YOUR OWN DATA SOURCE>"

    # Create a new sample and client
    sample = MultivariateSample(SUBSCRIPTION_KEY, ANOMALY_DETECTOR_ENDPOINT, data_source)

    # Train a new model
    model_id = sample.train(datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                            datetime(2021, 1, 2, 12, 0, 0, tzinfo=timezone.utc))
    assert model_id is not None

    # Reference
    result = sample.detect(model_id, datetime(2021, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
                           datetime(2021, 1, 3, 0, 0, 0, tzinfo=timezone.utc))
    assert result is not None

    print("Result ID:\t", result.result_id)
    print("Result summary:\t", result.summary)
    print("Result length:\t", len(result.results))

    # Export model
    sample.export_model(model_id, "model.zip")

    # Delete model
    sample.delete_model(model_id)
