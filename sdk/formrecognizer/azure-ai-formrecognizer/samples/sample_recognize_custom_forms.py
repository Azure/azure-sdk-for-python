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
    trained model. To learn how to train your own model, look at sample TODO
USAGE:
    python sample_recognize_custom_forms.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
    3) CUSTOM_TRAINED_MODEL_ID - the ID of your custom trained model
"""

import os


class RecognizeCustomFormsSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    model_id = os.environ["CUSTOM_TRAINED_MODEL_ID"]

    def recognize_custom_forms(self):
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient, FormField
        form_recognizer_client = FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        with open("sample_forms/forms/Form_1.jpg", "rb") as f:
            poller = form_recognizer_client.begin_recognize_custom_forms(model_id=self.model_id, stream=f.read())
        forms = poller.result()

        for idx, form in enumerate(forms):
            print("========RECOGNIZING FORM #{}========".format(idx))
            print("Form has type {}".format(form.form_type))
            for field_idx, field in enumerate(form.fields):
                # each field is of type FormField
                print("=======Fields=======")
                # The value of the field can also be a FormField, or a list of FormFields
                # In our sample, it is not.
                print("Field #{} has name {} and value {} with confidence score {}".format(
                    field_idx, field.name, field.value, field.confidence
                ))
                print("====================")
            print("=======================================")


if __name__ == '__main__':
    sample = RecognizeCustomFormsSample()
    sample.recognize_custom_forms()
