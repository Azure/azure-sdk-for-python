# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_custom_forms.py

DESCRIPTION:
    This sample demonstrates how to analyze a form from a document with a custom
    trained model. The form must be of the same type as the forms the custom model
    was trained on. To learn how to train your own models, look at
    sample_train_model_without_labels.py and sample_train_model_with_labels.py
USAGE:
    python sample_recognize_custom_forms.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CUSTOM_TRAINED_MODEL_ID - the ID of your custom trained model
"""

import os


class RecognizeCustomForms(object):

    def recognize_custom_forms(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Form_1.jpg"))
        # [START recognize_custom_forms]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id = os.environ["CUSTOM_TRAINED_MODEL_ID"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        # Make sure your form's type is included in the list of form types the custom model can recognize
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_custom_forms(
                model_id=model_id, form=f
            )
        forms = poller.result()

        for idx, form in enumerate(forms):
            print("--------Recognizing Form #{}--------".format(idx))
            print("Form {} has type {}".format(idx, form.form_type))
            for name, field in form.fields.items():
                # each field is of type FormField
                # The value of the field can also be a FormField, or a list of FormFields
                # In our sample, it is just a FormField.
                print("...Field '{}' has value '{}' with a confidence score of {}".format(
                    name, field.value, field.confidence
                ))
                # label data is populated if you are using a model trained with unlabeled data, since the service needs to make predictions for
                # labels if not explicitly given to it.
                if field.label_data:
                    print("...Field '{}' has label '{}' with a confidence score of {}".format(
                        name,
                        field.label_data.text,
                        field.confidence
                    ))
            print("-----------------------------------")
        # [END recognize_custom_forms]


if __name__ == '__main__':
    sample = RecognizeCustomForms()
    sample.recognize_custom_forms()
