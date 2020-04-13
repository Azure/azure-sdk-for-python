# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_manage_custom_models.py

DESCRIPTION:
    This sample demonstrates how to manage the custom models on your account.
USAGE:
    python sample_manage_custom_models.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
"""

import os


class ManageCustomModelsSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    def manage_custom_models(self):
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.core.exceptions import ResourceNotFoundError
        from azure.ai.formrecognizer import FormTrainingClient

        form_training_client = FormTrainingClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        # First, we see how many custom models we have, and what our limit is
        account_properties = form_training_client.get_account_properties()
        print("Our account has {} custom models, and we can have at most {} custom models".format(
            account_properties.custom_model_count, account_properties.custom_model_limit
        ))

        # Next, we get a paged list of all of our custom models
        custom_models = form_training_client.list_model_infos()

        print("We have models with the following ids:")

        # Let's pull out the first model
        first_model = next(custom_models)
        print(first_model.model_id)
        for model in custom_models:
            print(model.model_id)

        # Now we'll get the first custom model in the paged list
        custom_model = form_training_client.get_custom_model(model_id=first_model.model_id)
        print("Model ID: {}".format(custom_model.model_id))
        print("Status: {}".format(custom_model.status))
        print("Created on: {}".format(custom_model.created_on))
        print("Last updated on: {}".format(custom_model.last_updated_on))

        # Finally, we will delete this model by ID
        form_training_client.delete_model(model_id=custom_model.model_id)

        try:
            form_training_client.get_custom_model(model_id=custom_model.model_id)
        except ResourceNotFoundError:
            print("Successfully deleted model with id {}".format(custom_model.model_id))

if __name__ == '__main__':
    sample = ManageCustomModelsSample()
    sample.manage_custom_models()
