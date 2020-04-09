# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_custom_forms_from_url_with_unsupervised_model.py

DESCRIPTION:
    This sample demonstrates how to analyze a form from a URL with a custom
    trained unsupervised model. To use a supervised model, see
    sample_recognize_custom_forms_from_url_with_supervised_model.py.
    To learn how to train your own unsupervised model, look at sample TODO
USAGE:
    python sample_recognize_custom_forms_from_url_with_unsupervised_model.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
    3) CUSTOM_TRAINED_UNSUPERVISED_MODEL_ID - the ID of your custom trained unsupervised model
"""

import os


class RecognizeCustomFormsFromURLWithUnsupervisedModelSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    unsupervised_model_id = os.environ["CUSTOM_TRAINED_UNSUPERVISED_MODEL_ID"]

    def recognize_custom_forms_from_url_with_unsupervised_model(self):
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient
        form_recognizer_client = FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"
        poller = form_recognizer_client.begin_recognize_custom_forms_from_url(
            model_id=self.unsupervised_model_id, url=url
        )
        forms = poller.result()

        for idx, form in enumerate(forms):
            print("========RECOGNIZING FORM #{}========".format(idx))
            print("Form has type {}".format(form.form_type))
            print("=======Fields=======")
            for label, field in form.fields.items():
                # each field is of type FormField
                # The value of the field can also be a FormField, or a list of FormFields
                # In our sample, it is not.
                print("{} has value '{}' with confidence score {}".format(
                    label, field.value, field.confidence
                ))
            print("====================")
            print("=======================================")


if __name__ == '__main__':
    sample = RecognizeCustomFormsFromURLWithUnsupervisedModelSample()
    sample.recognize_custom_forms_from_url_with_unsupervised_model()
