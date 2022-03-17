# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_manage_custom_models_async.py

DESCRIPTION:
    This sample demonstrates how to manage the custom models on your account. To learn
    how to create and train a custom model, look at sample_train_model_without_labels.py and
    sample_train_model_with_labels.py.
USAGE:
    python sample_manage_custom_models_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container
"""

import os
import asyncio


class ManageCustomModelsSampleAsync(object):

    async def manage_custom_models(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.core.exceptions import ResourceNotFoundError
        from azure.ai.formrecognizer.aio import FormTrainingClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        container_sas_url = os.environ["CONTAINER_SAS_URL_V2"]

        # [START get_account_properties_async]
        async with FormTrainingClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        ) as form_training_client:
            # First, we see how many custom models we have, and what our limit is
            account_properties = await form_training_client.get_account_properties()
            print("Our account has {} custom models, and we can have at most {} custom models\n".format(
                account_properties.custom_model_count, account_properties.custom_model_limit
            ))
            # [END get_account_properties_async]

            # Next, we get a paged list of all of our custom models
            # [START list_custom_models_async]
            custom_models = form_training_client.list_custom_models()

            print("We have models with the following IDs:")
            async for model in custom_models:
                print(model.model_id)
            # [END list_custom_models_async]

            # let's train a model to use for this sample
            poller = await form_training_client.begin_training(container_sas_url, use_training_labels=False)
            model = await poller.result()

            # Now we'll get information for the model we just trained
            # [START get_custom_model_async]
            custom_model = await form_training_client.get_custom_model(model_id=model.model_id)
            print("\nModel ID: {}".format(custom_model.model_id))
            print("Status: {}".format(custom_model.status))
            print("Model name: {}".format(custom_model.model_name))
            print("Is this a composed model?: {}".format(custom_model.properties.is_composed_model))
            print("Training started on: {}".format(custom_model.training_started_on))
            print("Training completed on: {}".format(custom_model.training_completed_on))
            # [END get_custom_model_async]

            # Finally, we will delete this model by ID
            # [START delete_model_async]
            await form_training_client.delete_model(model_id=custom_model.model_id)

            try:
                await form_training_client.get_custom_model(model_id=custom_model.model_id)
            except ResourceNotFoundError:
                print("Successfully deleted model with id {}".format(custom_model.model_id))
            # [END delete_model_async]


async def main():
    sample = ManageCustomModelsSampleAsync()
    await sample.manage_custom_models()


if __name__ == '__main__':
    asyncio.run(main())
