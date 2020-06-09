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
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


class ManageCustomModelsSampleAsync(object):

    async def manage_custom_models(self):
        # [START get_account_properties_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.core.exceptions import ResourceNotFoundError
        from azure.ai.formrecognizer.aio import FormTrainingClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        async with FormTrainingClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        ) as form_training_client:
            # First, we see how many custom models we have, and what our limit is
            account_properties = await form_training_client.get_account_properties()
            print("Our account has {} custom models, and we can have at most {} custom models".format(
                account_properties.custom_model_count, account_properties.custom_model_limit
            ))
            # [END get_account_properties_async]

            # Next, we get a paged list of all of our custom models
            # [START list_custom_models_async]
            custom_models = form_training_client.list_custom_models()

            print("We have models with the following ids:")

            # Let's pull out the first model
            first_model = None
            async for model in custom_models:
                print(model.model_id)
                if not first_model:
                    first_model = model
            # [END list_custom_models_async]

            # Now we'll get the first custom model in the paged list
            # [START get_custom_model_async]
            custom_model = await form_training_client.get_custom_model(model_id=first_model.model_id)
            print("Model ID: {}".format(custom_model.model_id))
            print("Status: {}".format(custom_model.status))
            print("Requested on: {}".format(custom_model.requested_on))
            print("Completed on: {}".format(custom_model.completed_on))
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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
