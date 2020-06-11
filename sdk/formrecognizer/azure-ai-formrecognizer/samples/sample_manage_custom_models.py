# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_manage_custom_models.py

DESCRIPTION:
    This sample demonstrates how to manage the custom models on your account. To learn
    how to create and train a custom model, look at sample_train_unlabeled_model.py and
    sample_train_labeled_model.py.
USAGE:
    python sample_manage_custom_models.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


class ManageCustomModelsSample(object):

    def manage_custom_models(self):
        # [START get_account_properties]
        from azure.core.credentials import AzureKeyCredential
        from azure.core.exceptions import ResourceNotFoundError
        from azure.ai.formrecognizer import FormTrainingClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_training_client = FormTrainingClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        # First, we see how many custom models we have, and what our limit is
        account_properties = form_training_client.get_account_properties()
        print("Our account has {} custom models, and we can have at most {} custom models".format(
            account_properties.custom_model_count, account_properties.custom_model_limit
        ))
        # [END get_account_properties]

        # Next, we get a paged list of all of our custom models
        # [START list_custom_models]
        custom_models = form_training_client.list_custom_models()

        print("We have models with the following ids:")

        # Let's pull out the first model
        first_model = next(custom_models)
        print(first_model.model_id)
        for model in custom_models:
            print(model.model_id)
        # [END list_custom_models]

        # Now we'll get the first custom model in the paged list
        # [START get_custom_model]
        custom_model = form_training_client.get_custom_model(model_id=first_model.model_id)
        print("Model ID: {}".format(custom_model.model_id))
        print("Status: {}".format(custom_model.status))
        print("Requested on: {}".format(custom_model.requested_on))
        print("Completed on: {}".format(custom_model.completed_on))
        # [END get_custom_model]

        # Finally, we will delete this model by ID
        # [START delete_model]
        form_training_client.delete_model(model_id=custom_model.model_id)

        try:
            form_training_client.get_custom_model(model_id=custom_model.model_id)
        except ResourceNotFoundError:
            print("Successfully deleted model with id {}".format(custom_model.model_id))
        # [END delete_model]

if __name__ == '__main__':
    sample = ManageCustomModelsSample()
    sample.manage_custom_models()
