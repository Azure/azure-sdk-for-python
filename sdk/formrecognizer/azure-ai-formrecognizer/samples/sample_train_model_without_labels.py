# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_train_model_without_labels.py

DESCRIPTION:
    This sample demonstrates how to train a model with unlabelled data. See sample_recognize_custom_forms.py
    to recognize forms with your custom model.
USAGE:
    python sample_train_model_without_labels.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your forms.
                      See https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/quickstarts/label-tool#connect-to-the-sample-labeling-tool
                      for more detailed descriptions on how to get it.
"""

import os


class TrainModelWithoutLabelsSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CONTAINER_SAS_URL"]

    def train_model_without_labels(self):
        # [START training]
        from azure.ai.formrecognizer import FormTrainingClient
        from azure.core.credentials import AzureKeyCredential

        form_training_client = FormTrainingClient(self.endpoint, AzureKeyCredential(self.key))

        # Default for begin_train_model is `use_training_labels=False`
        poller = form_training_client.begin_train_model(self.container_sas_url)
        model = poller.result()

        # Custom model information
        print("Model ID: {}".format(model.model_id))
        print("Status: {}".format(model.status))
        print("Created on: {}".format(model.created_on))
        print("Last modified: {}".format(model.last_modified))

        print("Recognized fields:")
        # Looping through the submodels, which contains the fields they were trained on
        for submodel in model.models:
            print("...The submodel has form type '{}'".format(submodel.form_type))
            for name, field in submodel.fields.items():
                print("...The model found field '{}' to have label '{}'".format(
                    name, field.label
                ))
        # [END training]
        # Training result information
        for doc in model.training_documents:
            print("Document name: {}".format(doc.document_name))
            print("Document status: {}".format(doc.status))
            print("Document page count: {}".format(doc.page_count))
            print("Document errors: {}".format(doc.errors))

if __name__ == '__main__':
    sample = TrainModelWithoutLabelsSample()
    sample.train_model_without_labels()
