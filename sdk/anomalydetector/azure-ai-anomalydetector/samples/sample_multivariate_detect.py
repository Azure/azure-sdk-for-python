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

import json
import os
import time
from datetime import datetime, timezone

from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.anomalydetector.models import *


class MultivariateSample:
    def __init__(self, subscription_key, anomaly_detector_endpoint):
        self.sub_key = subscription_key
        self.end_point = anomaly_detector_endpoint

        # Create an Anomaly Detector client

        # <client>
        self.ad_client = AnomalyDetectorClient(self.end_point, AzureKeyCredential(self.sub_key))
        # </client>

    def list_models(self):

        # List models
        models = self.ad_client.list_multivariate_models(skip=0, top=10)
        return list(models)

    def train(self, body):

        # Number of models available now
        try:
            model_list = self.list_models()
            print("{:d} available models before training.".format(len(model_list)))

            # Use sample data to train the model
            print("Training new model...(it may take a few minutes)")
            model = self.ad_client.train_multivariate_model(body)
            trained_model_id = model.model_id
            print("Training model id is {}".format(trained_model_id))

            ## Wait until the model is ready. It usually takes several minutes
            model_status = None
            model = None

            while model_status != ModelStatus.READY and model_status != ModelStatus.FAILED:
                model = self.ad_client.get_multivariate_model(trained_model_id)
                print(model)
                model_status = model.model_info.status
                print("Model is {}".format(model_status))
                time.sleep(30)

            if model_status == ModelStatus.FAILED:
                print("Creating model failed.")
                print("Errors:")
                if len(model.model_info.errors) > 0:
                    print(
                        "Error code: {}. Message: {}".format(
                            model.model_info.errors[0].code,
                            model.model_info.errors[0].message,
                        )
                    )
                else:
                    print("None")

            if model_status == ModelStatus.READY:
                # Model list after training
                model_list = self.list_models()

                print("Done.\n--------------------")
                print("{:d} available models after training.".format(len(model_list)))

                # Return the latest model id
            return trained_model_id
        except HttpResponseError as e:
            print(
                "Error code: {}".format(e.error.code),
                "Error message: {}".format(e.error.message),
            )
        except Exception as e:
            raise e

        return None

    def batch_detect(self, model_id, body):

        # Detect anomaly in the same data source (but a different interval)
        try:
            result = self.ad_client.detect_multivariate_batch_anomaly(model_id, body)
            result_id = result.result_id

            # Get results (may need a few seconds)
            r = self.ad_client.get_multivariate_batch_detection_result(result_id)
            print("Get detection result...(it may take a few seconds)")

            while r.summary.status != MultivariateBatchDetectionStatus.READY and r.summary.status != MultivariateBatchDetectionStatus.FAILED:
                r = self.ad_client.get_multivariate_batch_detection_result(result_id)
                print("Detection is {}".format(r.summary.status))
                time.sleep(15)

            if r.summary.status == MultivariateBatchDetectionStatus.FAILED:
                print("Detection failed.")
                print("Errors:")
                if len(r.summary.errors) > 0:
                    print("Error code: {}. Message: {}".format(r.summary.errors[0].code, r.summary.errors[0].message))
                else:
                    print("None")
                return None

            return r

        except HttpResponseError as e:
            print(
                "Error code: {}".format(e.error.code),
                "Error message: {}".format(e.error.message),
            )
        except Exception as e:
            raise e

        return None

    def delete_model(self, model_id):

        # Delete the model
        self.ad_client.delete_multivariate_model(model_id)
        model_list = self.list_models()
        print("{:d} available models after deletion.".format(len(model_list)))

    def last_detect(self, model_id, variables):

        # Detect anomaly by sync api
        r = self.ad_client.detect_multivariate_last_anomaly(model_id, variables)
        print("Get last detection result")
        return r


if __name__ == "__main__":
    SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
    ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]

    ## Create a new sample and client
    sample = MultivariateSample(SUBSCRIPTION_KEY, ANOMALY_DETECTOR_ENDPOINT)

    # Train a new model
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    blob_url = "{Your Blob Url}"
    train_body = ModelInfo(
        data_source=blob_url,
        start_time=datetime.strptime("2021-01-02T00:00:00Z", time_format),
        end_time=datetime.strptime("2021-01-02T05:00:00Z", time_format),
        data_schema=DataSchema.MULTI_TABLE,
        display_name="sample",
        sliding_window=200,
        align_policy=AlignPolicy(
            align_mode=AlignMode.OUTER,
            fill_n_a_method=FillNAMethod.LINEAR,
            padding_value=0,
        ),
    )
    model_id = sample.train(train_body)

    # Batch Inference
    batch_inference_body = MultivariateBatchDetectionOptions(
        data_source=blob_url,
        top_contributor_count=10,
        start_time=datetime.strptime("2021-01-02T00:00:00Z", time_format),
        end_time=datetime.strptime("2021-01-02T05:00:00Z", time_format),
    )
    result = sample.batch_detect(model_id, batch_inference_body)
    assert result is not None

    print("Result ID:\t", result.result_id)
    print("Result status:\t", result.summary.status)
    print("Result length:\t", len(result.results))

    # See detailed inference result
    for r in result.results:
        print(
            "timestamp: {}, is_anomaly: {:<5}, anomaly score: {:.4f}, severity: {:.4f}, contributor count: {:<4d}".format(
                r.timestamp,
                r.value.is_anomaly,
                r.value.score,
                r.value.severity,
                len(r.value.interpretation) if r.value.is_anomaly else 0,
            )
        )
        if r.value.interpretation:
            for contributor in r.value.interpretation:
                print(
                    "\tcontributor variable: {:<10}, contributor score: {:.4f}".format(
                        contributor.variable, contributor.contribution_score
                    )
                )

    # *******************************************************************************************************************
    # use your own inference data sending to last detection api, you should define your own variables and detectingPoints
    # *****************************************************************************************************************
    # define "<YOUR OWN variables>"
    # variables = [
    #    {
    #        "name": "variables_name1",
    #        "timestamps": ['2021-01-01T00:00:00Z', '2021-01-01T00:01:00Z', ...],
    #        "values": [0, 0, ...]
    #    },
    #    {
    #        "name": "variables_name2",
    #        "timestamps": ['2021-01-01T00:00:00Z', '2021-01-01T00:01:00Z', ...],
    #        "values": [0, 0, ...]
    #    }
    # ]

    # Last detection
    with open("./sample_data/multivariate_sample_data.json") as f:
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
    last_detect_result = sample.last_detect(model_id, last_inference_body)

    assert last_detect_result is not None

    print("Variable States:\t", last_detect_result.variable_states)
    print("Variable States length:\t", len(last_detect_result.variable_states))
    print("Results:\t", last_detect_result.results)
    print("Results length:\t", len(last_detect_result.results))

    # Delete model
    sample.delete_model(model_id)
