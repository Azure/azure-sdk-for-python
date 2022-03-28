# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_differentiate_output_models_trained_with_and_without_labels.py

DESCRIPTION:
    This sample demonstrates the differences in output that arise when begin_recognize_custom_forms
    is called with custom models trained with labeled and unlabeled data. The models used in this
    sample can be created in sample_train_model_with_labels.py and sample_train_model_without_labels.py
    using the training files found here: https://aka.ms/azsdk/formrecognizer/sampletrainingfiles-v3.1

    For a more general example of recognizing custom forms, see sample_recognize_custom_forms.py

    An explanation of the difference between training with and without labels can be found in the
    service documentation: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/overview#train-without-labels

USAGE:
    python sample_differentiate_output_models_trained_with_and_without_labels.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) ID_OF_MODEL_TRAINED_WITH_LABELS - the ID of your custom model trained with labels
        -OR-
       CONTAINER_SAS_URL_WITH_LABELS_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container
       with your labeled data. A model will be trained and used to run the sample.
    4) ID_OF_MODEL_TRAINED_WITHOUT_LABELS - the ID of your custom model trained without labels
        -OR-
       CONTAINER_SAS_URL_WITHOUT_LABELS_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container
       with your forms. A model will be trained and used to run the sample.
"""

import os


def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

class DifferentiateOutputModelsTrainedWithAndWithoutLabels(object):

    def recognize_custom_forms(self, labeled_model_id, unlabeled_model_id):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_trained_with_labels_id = os.getenv("ID_OF_MODEL_TRAINED_WITH_LABELS", labeled_model_id)
        model_trained_without_labels_id = os.getenv("ID_OF_MODEL_TRAINED_WITHOUT_LABELS", unlabeled_model_id)

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./sample_forms/forms/Form_1.jpg"))

        with open(path_to_sample_forms, "rb") as f:
            form = f.read()
        forms_with_labeled_model_poller = form_recognizer_client.begin_recognize_custom_forms(
            model_id=model_trained_with_labels_id, form=form
        )
        forms_with_unlabeled_model_poller = form_recognizer_client.begin_recognize_custom_forms(
            model_id=model_trained_without_labels_id, form=form
        )

        # Calling result() after kicking off each call allows for server-side parallelization
        forms_with_labeled_model = forms_with_labeled_model_poller.result()
        forms_with_unlabeled_model = forms_with_unlabeled_model_poller.result()

        # With a form recognized by a model trained with labels, the `name` key will be its label given during training.
        # `value` will contain the typed field value and `value_data` will contain information about the field value
        # `label_data` is not populated for a model trained with labels as this was the given label used to extract the key
        print("---------Recognizing forms using models trained with labeled data---------")
        for labeled_form in forms_with_labeled_model:
            for name, field in labeled_form.fields.items():
                print("...Field '{}' has value '{}' within bounding box '{}', with a confidence score of {}".format(
                    name,
                    field.value,
                    format_bounding_box(field.value_data.bounding_box),
                    field.confidence
                ))

        # Find a specific labeled field. Substitute "Merchant" with your specific training-time label
        try:
            print("\nValue for a specific labeled field using the training-time label:")
            training_time_label = "Merchant"
            for labeled_form in forms_with_labeled_model:
                print("The Merchant is {}\n".format(labeled_form.fields[training_time_label].value))
        except KeyError:
            print("'Merchant' training-time label does not exist. Substitute with your own training-time label.\n")

        # With a form recognized by a model trained without labels, the `name` key will be denoted by numeric indices.
        # Non-unique form field label names will be found in the `label_data.text`
        # Information about the form field label and the field value are found in `label_data` and `value_data`
        print("-----------------------------------------------------------------------")
        print("-------Recognizing forms using models trained with unlabeled data-------")
        for unlabeled_form in forms_with_unlabeled_model:
            for name, field in unlabeled_form.fields.items():
                print("...Field '{}' has label '{}' within bounding box '{}', with a confidence score of {}".format(
                    name,
                    field.label_data.text,
                    format_bounding_box(field.label_data.bounding_box),
                    field.confidence
                ))
                print("...Field '{}' has value '{}' within bounding box '{}', with a confidence score of {}".format(
                    name,
                    field.value,
                    format_bounding_box(field.value_data.bounding_box),
                    field.confidence
                ))

        # Find the value of a specific unlabeled field. Will only be found if sample training forms used
        print("\nValue for a specific unlabeled field:")
        field_label = "Vendor Name:"
        for unlabeled_form in forms_with_unlabeled_model:
            for name, field in unlabeled_form.fields.items():
                if field.label_data.text == field_label:
                    print("The Vendor Name is {}\n".format(field.value))


if __name__ == '__main__':
    sample = DifferentiateOutputModelsTrainedWithAndWithoutLabels()
    labeled_model_id = None
    unlabeled_model_id = None
    if os.getenv("CONTAINER_SAS_URL_WITH_LABELS_V2") or os.getenv("CONTAINER_SAS_URL_WITHOUT_LABELS_V2"):

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormTrainingClient

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
        labeled = os.getenv("CONTAINER_SAS_URL_WITH_LABELS_V2")
        unlabeled = os.getenv("CONTAINER_SAS_URL_WITHOUT_LABELS_V2")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        form_training_client = FormTrainingClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        if labeled:
            model = form_training_client.begin_training(labeled, use_training_labels=True).result()
            labeled_model_id = model.model_id
        if unlabeled:
            model = form_training_client.begin_training(unlabeled, use_training_labels=False).result()
            unlabeled_model_id = model.model_id

    sample.recognize_custom_forms(labeled_model_id, unlabeled_model_id)
