# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_differentiate_custom_forms_with_labelled_and_unlabelled_models_async.py

DESCRIPTION:
    This sample demonstrates the differences in output that arise when recognize_custom_forms
    is called with custom models trained with labelled and unlabelled data.
USAGE:
    python sample_differentiate_custom_forms_with_labelled_and_unlabelled_models_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
    3) CUSTOM_TRAINED_LABELLED_MODEL_ID - the ID of your custom model trained with labelled data
    4) CUSTOM_TRAINED_UNLABELLED_MODEL_ID - the ID of your custom model trained with unlabelled data
"""

import os
import asyncio


class DifferentiateCustomFormsWithLabelledAndUnlabelledModelsAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    labelled_model_id = os.environ["CUSTOM_TRAINED_LABELLED_MODEL_ID"]
    unlabelled_model_id = os.environ["CUSTOM_TRAINED_UNLABELLED_MODEL_ID"]

    async def recognize_custom_forms(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        async with FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as form_recognizer_client:
            with open("sample_forms/forms/Form_1.jpg", "rb") as f:
                stream = f.read()
            forms_with_labelled_model = await form_recognizer_client.recognize_custom_forms(
                model_id=self.labelled_model_id, stream=stream
            )
            forms_with_unlabelled_model = await form_recognizer_client.recognize_custom_forms(
                model_id=self.unlabelled_model_id, stream=stream
            )

            # The main difference is found in the labels of its fields
            # The form recognized with a labelled model will have the labels it was trained with,
            # the unlabelled one will be denoted with indices
            for labelled_form in forms_with_labelled_model:
                for label, field in labelled_form.fields.items():
                    print("Field '{}' has value '{}' with a confidence score of {}".format(
                            label, field.value, field.confidence
                        ))

            for unlabelled_form in forms_with_unlabelled_model:
                for label, field in unlabelled_form.fields.items():
                    print("Field '{}' has value '{}' with a confidence score of {}".format(
                            label, field.value, field.confidence
                        ))


async def main():
    sample = DifferentiateCustomFormsWithLabelledAndUnlabelledModelsAsync()
    await sample.recognize_custom_forms()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
