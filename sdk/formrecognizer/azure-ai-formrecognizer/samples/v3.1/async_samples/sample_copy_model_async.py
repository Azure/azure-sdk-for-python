# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_copy_model_async.py

DESCRIPTION:
    This sample demonstrates how to copy a custom model from a source Form Recognizer resource
    to a target Form Recognizer resource. The resource id and the resource region can be found
    in the azure portal.

    The model used in this sample can be created in the sample_train_model_with_labels_async.py using the
    training files in https://aka.ms/azsdk/formrecognizer/sampletrainingfiles-v3.1

USAGE:
    python sample_copy_model_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT - the endpoint to your source Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_SOURCE_KEY - your source Form Recognizer API key
    3) AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT - the endpoint to your target Form Recognizer resource.
    4) AZURE_FORM_RECOGNIZER_TARGET_KEY - your target Form Recognizer API key
    5) AZURE_SOURCE_MODEL_ID - the model ID from the source resource to be copied over to the target resource.
        - OR -
       CONTAINER_SAS_URL_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container with your forms.
       A model will be trained and used to run the sample.
    6) AZURE_FORM_RECOGNIZER_TARGET_REGION - the region the target resource was created in
    7) AZURE_FORM_RECOGNIZER_TARGET_RESOURCE_ID - the entire resource ID to the target resource
"""

import os
import asyncio


class CopyModelSampleAsync(object):

    async def copy_model_async(self, custom_model_id):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormTrainingClient

        source_endpoint = os.environ["AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT"]
        source_key = os.environ["AZURE_FORM_RECOGNIZER_SOURCE_KEY"]
        target_endpoint = os.environ["AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT"]
        target_key = os.environ["AZURE_FORM_RECOGNIZER_TARGET_KEY"]
        source_model_id = os.getenv("AZURE_SOURCE_MODEL_ID", custom_model_id)
        target_region = os.environ["AZURE_FORM_RECOGNIZER_TARGET_REGION"]
        target_resource_id = os.environ["AZURE_FORM_RECOGNIZER_TARGET_RESOURCE_ID"]

        # [START get_copy_authorization_async]
        target_client = FormTrainingClient(endpoint=target_endpoint, credential=AzureKeyCredential(target_key))

        async with target_client:
            target = await target_client.get_copy_authorization(
                resource_region=target_region,
                resource_id=target_resource_id
            )
        # model ID that target client will use to access the model once copy is complete
        print("Model ID: {}".format(target["modelId"]))
        # [END get_copy_authorization_async]

        # [START copy_model_async]
        source_client = FormTrainingClient(endpoint=source_endpoint, credential=AzureKeyCredential(source_key))

        async with source_client:
            poller = await source_client.begin_copy_model(
                model_id=source_model_id,
                target=target  # output from target client's call to get_copy_authorization()
            )
            copied_over_model = await poller.result()

            print("Model ID: {}".format(copied_over_model.model_id))
            print("Status: {}".format(copied_over_model.status))
        # [END copy_model_async]


async def main():
    sample = CopyModelSampleAsync()
    model_id = None
    if os.getenv("CONTAINER_SAS_URL_V2"):

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormTrainingClient

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_SOURCE_KEY")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        form_training_client = FormTrainingClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        async with form_training_client:
            model = await (await form_training_client.begin_training(
                os.getenv("CONTAINER_SAS_URL_V2"), use_training_labels=True)).result()
            model_id = model.model_id

    await sample.copy_model_async(model_id)


if __name__ == '__main__':
    asyncio.run(main())
