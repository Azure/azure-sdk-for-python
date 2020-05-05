# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_copy_model.py

DESCRIPTION:
    This sample demonstrates how to copy a model from a source Form Recognizer resource
    to a target Form Recognizer resource.

USAGE:
    python sample_copy_model.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT - the endpoint to your source Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_SOURCE_KEY - your source Form Recognizer API key
    3) AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT - the endpoint to your target Form Recognizer resource.
    4) AZURE_FORM_RECOGNIZER_TARGET_KEY - your target Form Recognizer API key
    5) AZURE_SOURCE_MODEL_ID - the model ID from the source resource to be copied over to the target resource.
    6) AZURE_FORM_RECOGNIZER_TARGET_REGION - the region the target resource was created in
    7) AZURE_FORM_RECOGNIZER_TARGET_RESOURCE_ID - the entire resource ID to the target resource
"""

import os


class CopyModelSample(object):

    source_endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    source_key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    target_endpoint = os.environ["AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT"]
    target_key = os.environ["AZURE_FORM_RECOGNIZER_TARGET_KEY"]
    source_model_id = os.environ["AZURE_SOURCE_MODEL_ID"]
    target_region = os.environ["AZURE_FORM_RECOGNIZER_TARGET_REGION"]
    target_resource_id = os.environ["AZURE_FORM_RECOGNIZER_TARGET_RESOURCE_ID"]

    def begin_copy_model(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormTrainingClient

        source_client = FormTrainingClient(endpoint=self.source_endpoint, credential=AzureKeyCredential(self.source_key))
        target_client = FormTrainingClient(endpoint=self.target_endpoint, credential=AzureKeyCredential(self.target_key))

        poller = source_client.begin_copy_model(
            source_model_id=self.source_model_id,
            target_resource_region=self.target_region,
            target_resource_id=self.target_resource_id,
            target_endpoint=self.target_endpoint,
            target_credential=AzureKeyCredential(self.target_key)
        )
        copy = poller.result()

        copied_over_model = target_client.get_custom_model(copy.model_id)
        print(copied_over_model)


if __name__ == '__main__':
    sample = CopyModelSample()
    sample.begin_copy_model()
