# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_differentiate_output_models_trained_with_and_without_labels.py

DESCRIPTION:
    This sample demonstrates the differences in output that arise when recognize_custom_forms
    is called with custom models trained with labeled and unlabeled data. For a more general
    example of recognizing custom forms, see sample_recognize_custom_forms.py
USAGE:
    python sample_differentiate_output_models_trained_with_and_without_labels.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) ID_OF_MODEL_TRAINED_WITH_LABELS - the ID of your custom model trained with labels
    4) ID_OF_MODEL_TRAINED_WITHOUT_LABELS - the ID of your custom model trained without labels
"""

import os


def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

class DifferentiateOutputModelsTrainedWithAndWithoutLabels(object):

    def recognize_custom_forms(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_trained_with_labels_id = os.environ["ID_OF_MODEL_TRAINED_WITH_LABELS"]
        model_trained_without_labels_id = os.environ["ID_OF_MODEL_TRAINED_WITHOUT_LABELS"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
        # Make sure your form's type is included in the list of form types the custom model can recognize
        with open(path_to_sample_forms, "rb") as f:
            stream = f.read()
        forms_with_labeled_model_poller = form_recognizer_client.begin_recognize_custom_forms(
            model_id=model_trained_with_labels_id, form=stream
        )
        forms_with_unlabeled_model_poller = form_recognizer_client.begin_recognize_custom_forms(
            model_id=model_trained_without_labels_id, form=stream
        )

        # Calling result after kicking off each call allows for server-side paralellization
        forms_with_labeled_model = forms_with_labeled_model_poller.result()
        forms_with_unlabeled_model = forms_with_unlabeled_model_poller.result()


        # With a form recognized by a model trained with labels, this 'name' key will be its
        # training-time label, otherwise it will be denoted by numeric indices.
        # Label data is not returned for model trained with labels.
        print("---------Recognizing forms with models trained with labeled data---------")
        for labeled_form in forms_with_labeled_model:
            for name, field in labeled_form.fields.items():
                print("...Field '{}' has value '{}' based on '{}' within bounding box '{}', with a confidence score of {}".format(
                    name,
                    field.value,
                    field.value_data.text,
                    format_bounding_box(field.value_data.bounding_box),
                    field.confidence
                ))

        print("-----------------------------------------------------------------------")
        print("-------Recognizing forms with models trained with unlabeled data-------")
        for unlabeled_form in forms_with_unlabeled_model:
            for name, field in unlabeled_form.fields.items():
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


if __name__ == '__main__':
    sample = DifferentiateOutputModelsTrainedWithAndWithoutLabels()
    sample.recognize_custom_forms()
