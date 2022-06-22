# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_train_model_with_labels_async.py

DESCRIPTION:
    This sample demonstrates how to train a model with labels. For this sample, you can use the training
    forms found in https://aka.ms/azsdk/formrecognizer/sampletrainingfiles-v3.1

    More details on setting up a container and required file structure can be found here:
    https://docs.microsoft.com/azure/cognitive-services/form-recognizer/build-training-data-set

    To see how to label your documents, you can use the service's labeling tool to label your documents:
    https://docs.microsoft.com/azure/cognitive-services/form-recognizer/label-tool?tabs=v2-1. Follow the
    instructions to store these labeled files in your blob container with the other form files.
    See sample_recognize_custom_forms_async.py to recognize forms with your custom model.

USAGE:
    python sample_train_model_with_labels_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container with your labeled data.
"""

import os
import asyncio


class TrainModelWithLabelsSampleAsync(object):

    async def train_model_with_labels(self):
        from azure.ai.formrecognizer.aio import FormTrainingClient
        from azure.core.credentials import AzureKeyCredential

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        container_sas_url = os.environ["CONTAINER_SAS_URL_V2"]

        form_training_client = FormTrainingClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        async with form_training_client:
            poller = await form_training_client.begin_training(
                container_sas_url, use_training_labels=True, model_name="mymodel"
            )
            model = await poller.result()

            # Custom model information
            print("Model ID: {}".format(model.model_id))
            print("Status: {}".format(model.status))
            print("Model name: {}".format(model.model_name))
            print("Is this a composed model?: {}".format(model.properties.is_composed_model))
            print("Training started on: {}".format(model.training_started_on))
            print("Training completed on: {}".format(model.training_completed_on))

            print("Recognized fields:")
            # looping through the submodels, which contains the fields they were trained on
            # The labels are based on the ones you gave the training document.
            for submodel in model.submodels:
                print("...The submodel has model ID: {}".format(submodel.model_id))
                print("...The submodel with form type {} has an average accuracy '{}'".format(
                    submodel.form_type, submodel.accuracy
                ))
                for name, field in submodel.fields.items():
                    print("...The model found the field '{}' with an accuracy of {}".format(
                        name, field.accuracy
                    ))

            # Training result information
            for doc in model.training_documents:
                print("Document name: {}".format(doc.name))
                print("Document status: {}".format(doc.status))
                print("Document page count: {}".format(doc.page_count))
                print("Document errors: {}".format(doc.errors))


async def main():
    sample = TrainModelWithLabelsSampleAsync()
    await sample.train_model_with_labels()


if __name__ == '__main__':
    asyncio.run(main())
