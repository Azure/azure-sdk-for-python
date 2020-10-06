# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_composed_model_async.py

DESCRIPTION:
    This sample demonstrates how to create a composed model using existing custom models that
    were trained with labels.

USAGE:
    python sample_create_composed_model_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


class ComposedModelSampleAsync(object):

    async def create_composed_model_async(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormTrainingClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_training_client = FormTrainingClient(endpoint=endpoint, credential=AzureKeyCredential(key))

        models_trained_with_labels = ["6f4f1583-8f73-4be8-9337-ccc105f1fdff", "4408815d-b870-4b15-86b0-fb1ea69f9853"]
        async with form_training_client:
            poller = await form_training_client.begin_create_composed_model(
                models_trained_with_labels, display_name="my_composed_model"
            )
            model = await poller.result()

        # Custom model information
        print("Model ID: {}".format(model.model_id))
        print("Model display name: {}".format(model.display_name))
        print("Is this a composed model?: {}".format(model.properties.is_composed_model))
        print("Status: {}".format(model.status))
        print("Composed model creation started on: {}".format(model.training_started_on))
        print("Creation completed on: {}".format(model.training_completed_on))

        print("Recognized fields:")
        for submodel in model.submodels:
            print("The submodel has model ID: {}".format(submodel.model_id))
            print("...The submodel with form type {} has an average accuracy '{}'".format(
                submodel.form_type, submodel.accuracy
            ))
            for name, field in submodel.fields.items():
                print("...The model found the field '{}' with an accuracy of {}".format(
                    name, field.accuracy
                ))

        # Training result information
        for doc in model.training_documents:
            print("Document was used to train model with ID: {}".format(doc.model_id))
            print("Document name: {}".format(doc.name))
            print("Document status: {}".format(doc.status))
            print("Document page count: {}".format(doc.page_count))
            print("Document errors: {}".format(doc.errors))


async def main():
    sample = ComposedModelSampleAsync()
    await sample.create_composed_model_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
