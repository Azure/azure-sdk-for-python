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
        skip = 0

        next_link = None
        model_list = []

        while next_link != '':
            r = self.ad_client.list_multivariate_model(skip=skip, top=10000)
            next_link = r['nextLink'] 
            model_list.extend(r['models'])
            skip = skip + 10
        return model_list

    def train(self, body):

        # Number of models available now
        try:
            model_list = self.list_models()
            print("{:d} available models before training.".format(len(model_list)))

            # Use sample data to train the model
            print("Training new model...(it may take a few minutes)")
            response = self.ad_client.create_multivariate_model(body)
            trained_model_id = response['modelId']
            print("Training model id is ", trained_model_id)

            ## Wait until the model is ready. It usually takes several minutes
            model_status = None
            model_info = None

            while model_status != 'READY' and model_status != 'FAILED':
                model_info = self.ad_client.get_multivariate_model(trained_model_id)
                model_status = model_info['modelInfo']['status']
                print("Model is", model_status)
                time.sleep(1)

            print(model_info)
            if model_status == 'FAILED':
                print("Creating model failed.")
                print("Errors:")
                if len(model_info['errors']) > 0:
                    print("Error code: {}. Message: {}".format(model_info['errors'][0]['code'], model_info['errors'][0]['message']))
                else:
                    print("None")
                return None

            if model_status == 'READY':
                # Model list after training
                model_list = self.list_models()

                print("Done.\n--------------------")
                print("{:d} available models after training.".format(len(model_list)))

                # Return the latest model id
                return trained_model_id
        except HttpResponseError as e:
            print('Error code: {}'.format(e.error.code), 'Error message: {}'.format(e.error.message))
        except Exception as e:
            raise e

        return None


    def batch_detect(self, model_id, body):

        # Detect anomaly in the same data source (but a different interval)
        try:
            response = self.ad_client.batch_detect_anomaly(model_id, body)
            result_id = response['resultId']

            # Get results (may need a few seconds)
            r = self.ad_client.get_batch_detection_result(result_id)
            print("Get detection result...(it may take a few seconds)")

            while r['summary']['status'] != 'READY' and r['summary']['status'] != 'FAILED':
                r = self.ad_client.get_batch_detection_result(result_id)
                print("Detection is", r['summary']['status'])
                time.sleep(1)

            if r['summary']['status'] == 'FAILED':
                print("Detection failed.")
                print("Errors:")
                if lend(r['summary']['errors']) > 0:
                    print("Error code: {}. Message: {}".format(r['summary']['errors'][0]['code'], r['summary']['errors'][0]['message']))
                else:
                    print("None")
                return None

            return r 

        except HttpResponseError as e:
            print('Error code: {}'.format(e.error.code), 'Error message: {}'.format(e.error.message))
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
        r = self.ad_client.last_detect_anomaly(model_id, variables)
        print("Get last detection result")
        return r

if __name__ == '__main__':
    SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
    ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]

    ## Create a new sample and client
    sample = MultivariateSample(SUBSCRIPTION_KEY, ANOMALY_DETECTOR_ENDPOINT)

    # Train a new model
    train_body = {
        "slidingWindow": 200,
        "alignPolicy": {
            "alignMode": "Outer",
            "fillNAMethod": "Linear",
            "paddingValue": 0
        },
        "dataSource": "{blobUrl}",
        "dataSchema": "MultiTable",
        "startTime": "2021-01-02T00:00:00Z",
        "endTime": "2021-01-02T05:00:00Z",
        "displayName": "sample"
    }
    model_id = sample.train(train_body)

    # Batch Inference
    batch_inference_body = {
        "dataSource": "{blobUrl}",
        "startTime": "2021-01-02T00:00:00Z",
        "endTime": "2021-01-02T05:00:00Z",
        "topContributorCount": 10
    }
    result = sample.batch_detect(model_id, batch_inference_body)
    assert result is not None

    print("Result ID:\t", result['resultId'])
    print("Result status:\t", result['summary']['status'])
    print("Result length:\t", len(result['results']))

    # See detailed inference result
    for r in result['results']:
        print("timestamp: {}, is_anomaly: {:<5}, anomaly score: {:.4f}, severity: {:.4f}, contributor count: {:<4d}".format(r['timestamp'], r['value']['isAnomaly'], r['value']['score'], r['value']['severity'], len(r['value']['interpretation']) if r['value']['isAnomaly'] else 0))
        if r['value']['interpretation']:
            for contributor in r['value']['interpretation']:
                print("\tcontributor variable: {:<10}, contributor score: {:.4f}".format(contributor['variable'], contributor['contributionScore']))


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
    #]

    # Last detection
    with open('./samples/sample_data/multivariate_sample_data.json') as f:
        variables = json.load(f)
    last_detect_result = sample.last_detect(model_id, variables)

    assert last_detect_result is not None

    print("Variable States:\t", last_detect_result['variableStates'])
    print("Variable States length:\t", len(last_detect_result['variableStates']))
    print("Results:\t", last_detect_result['results'])
    print("Results length:\t", len(last_detect_result['results']))

    # Delete model
    sample.delete_model(model_id)
