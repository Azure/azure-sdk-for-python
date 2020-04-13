# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_train_labelled_model.py

DESCRIPTION:
    This sample demonstrates how to train a model with labelled data.
USAGE:
    python sample_train_labelled_model.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
    3) BLOB_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your labelled data.
                      See https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/quickstarts/label-tool#connect-to-the-sample-labeling-tool
                      for more detailed descriptions on how to get it.
"""

import os


class TrainLabelledModelSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    blob_sas_url = os.environ["BLOB_SAS_URL"]

    def train_labelled_model(self):
        from azure.ai.formrecognizer import FormTrainingClient
        from azure.core.credentials import AzureKeyCredential

        form_training_client = FormTrainingClient(self.endpoint, AzureKeyCredential(self.key))

        poller = form_training_client.begin_training(self.blob_sas_url, use_labels=True)
        model = poller.result()

        # Custom model information
        print("Model ID: {}".format(model.model_id))
        print("Status: {}".format(model.status))
        print("Created on: {}".format(model.created_on))
        print("Last updated on: {}".format(model.last_updated_on))

        print("Recognized fields:")
        # looping through the submodels, which contains the fields they were trained on
        # The labels are based on the ones you gave the training document.
        for submodel in model.models:
            # Since the data is labelled, we are able to return the accuracy of the model
            print("The submodel has accuracy '{}'".format(submodel.accuracy))
            print("We have recognized the following fields:")
            for label, field in submodel.fields.items():
                print("The model found field '{}' to have name '{}' with an accuracy of {}".format(
                    label, field.name, field.accuracy
                ))

        # Training result information
        for doc in model.training_documents:
            print("Document name: {}".format(doc.document_name))
            print("Document status: {}".format(doc.status))
            print("Document page count: {}".format(doc.page_count))
            print("Document errors: {}".format(doc.errors))

if __name__ == '__main__':
    sample = TrainLabelledModelSample()
    sample.train_labelled_model()
