# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_train_model_with_labels_async.py

DESCRIPTION:
    This sample demonstrates how to train a model with labeled data. To see how to label your documents. You can use the service's labeling tool
    to label your documents: https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/quickstarts/label-tool, and follow their
    instructions to store these labeled files in your blob container with the other form files.
    See sample_recognize_custom_forms_async.py to recognize forms with your custom model.
USAGE:
    python sample_train_model_with_labels_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your labeled data.
                      See https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/quickstarts/python-labeled-data#train-a-model-using-labeled-data
                      for more detailed descriptions on how to get it.
"""

import os
import asyncio


class TrainModelWithLabelsSampleAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CONTAINER_SAS_URL"]

    async def train_model_with_labels(self):
        # [START create_form_training_client_async]
        from azure.ai.formrecognizer.aio import FormTrainingClient
        from azure.core.credentials import AzureKeyCredential

        form_training_client = FormTrainingClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )
        # [END create_form_training_client_async]
        async with form_training_client:

            model = await form_training_client.train_model(self.container_sas_url, use_labels=True)
            # Custom model information
            print("Model ID: {}".format(model.model_id))
            print("Status: {}".format(model.status))
            print("Created on: {}".format(model.created_on))
            print("Last modified: {}".format(model.last_modified))

            print("Recognized fields:")
            # looping through the submodels, which contains the fields they were trained on
            # The labels are based on the ones you gave the training document.
            for submodel in model.models:
                print("...The submodel has accuracy '{}'".format(submodel.accuracy))
                for name, field in submodel.fields.items():
                    print("...The model found field '{}' to have name '{}' with an accuracy of {}".format(
                        name, field.name, field.accuracy
                    ))

            # Training result information
            for doc in model.training_documents:
                print("Document name: {}".format(doc.document_name))
                print("Document status: {}".format(doc.status))
                print("Document page count: {}".format(doc.page_count))
                print("Document errors: {}".format(doc.errors))

async def main():
    sample = TrainModelWithLabelsSampleAsync()
    await sample.train_model_with_labels()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
