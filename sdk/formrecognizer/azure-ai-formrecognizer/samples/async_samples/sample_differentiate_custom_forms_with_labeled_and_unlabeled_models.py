# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_differentiate_forms_with_models_trained_with_labels_and_with_forms_only.py

DESCRIPTION:
    This sample demonstrates the differences in output that arise when recognize_custom_forms
    is called with custom models trained with labeled and unlabeled data. For a more general
    example of recognizing custom forms, see sample_recognize_custom_forms.py
USAGE:
    python sample_differentiate_custom_forms_with_labeled_and_unlabeled_models_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) ID_OF_MODEL_TRAINED_WITH_LABELS - the ID of your custom model trained with labeled data
    4) ID_OF_MODEL_TRAINED_WITH_FORMS_ONLY - the ID of your custom model trained with unlabeled data
"""

import os
import asyncio

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

class DifferentiateCustomFormsWithLabeledAndUnlabeledModelsAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    model_trained_with_labels_id = os.environ["ID_OF_MODEL_TRAINED_WITH_LABELS"]
    model_trained_with_forms_only_id = os.environ["ID_OF_MODEL_TRAINED_WITH_FORMS_ONLY"]

    async def recognize_custom_forms(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        async with FormRecognizerClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as form_recognizer_client:

            # Make sure your form's type is included in the list of form types the custom model can recognize
            with open("sample_forms/forms/Form_1.jpg", "rb") as f:
                stream = f.read()
            forms_with_labeled_model = await form_recognizer_client.recognize_custom_forms(
                model_id=self.model_trained_with_labels_id, stream=stream
            )
            forms_with_unlabeled_model = await form_recognizer_client.recognize_custom_forms(
                model_id=self.model_trained_with_forms_only_id, stream=stream
            )

            # The main difference is found in the names we have for the fields. Fields is returned as a dictionary, with the 'name'
            # key being the unique identifier of the form field.
            # With a form recognized by a model trained with labels, this 'name' key will be its training-time label. Otherwise,
            # the 'name' key is denoted with indices.
            #
            # When we access a field's 'label' property, we are referring to the title of the form field in the form, so do not
            # confuse a field's 'label' property with the unique identifier of a form field.
            print("--------Recognizing forms with models trained with labels--------")
            for labeled_form in forms_with_labeled_model:
                for name, field in labeled_form.fields.items():
                    # With your custom model trained with labels, you will not get back label data but will get back value data
                    # This is because your custom model didn't have to use any machine learning to deduce the label,
                    # the label was directly provided to it
                    # The training-time label is returned as the field's name
                    print("...Field '{}' has value '{}' based on '{}' within bounding box '{}', with a confidence score of {}".format(
                        name,
                        field.value,
                        field.value_data.text,
                        format_bounding_box(field.value_data.bounding_box),
                        field.confidence
                    ))

            print("-------------------------------------------------------------------")
            print("-------Recognizing forms with models trained with forms only-------")
            for unlabeled_form in forms_with_unlabeled_model:
                for name, field in unlabeled_form.fields.items():
                    # The form recognized with a model trained with forms only will also include data about your labels
                    print("...Field '{}' has label '{}' within bounding box '{}', with a confidence score of {}".format(
                        name,
                        field.label_data.text,
                        format_bounding_box(field.label_data.bounding_box),
                        field.confidence
                    ))
                    print("...Field '{}' has value '{}' based on '{}' within bounding box '{}', with a confidence score of {}".format(
                        name,
                        field.value,
                        field.value_data.text,
                        format_bounding_box(field.value_data.bounding_box),
                        field.confidence
                    ))



async def main():
    sample = DifferentiateCustomFormsWithLabeledAndUnlabeledModelsAsync()
    await sample.recognize_custom_forms()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
