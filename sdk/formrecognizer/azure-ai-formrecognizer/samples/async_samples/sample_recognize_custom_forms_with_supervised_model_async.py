# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_custom_forms_with_supervised_model_async.py

DESCRIPTION:
    This sample demonstrates how to analyze a form from a document with a custom
    trained supervised model. To use an unsupervised model, see
    sample_recognize_custom_forms_with_unsupervised_model.py.
    To learn how to train your own supervised model, look at sample TODO
USAGE:
    python sample_recognize_custom_forms_with_supervised_model_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
    3) CUSTOM_TRAINED_SUPERVISED_MODEL_ID - the ID of your custom trained supervised model
"""

import os
import asyncio


class RecognizeCustomFormsWithSupervisedModelSampleAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    supervised_model_id = os.environ["CUSTOM_TRAINED_SUPERVISED_MODEL_ID"]

    async def recognize_custom_forms_with_supervised_model(self):
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        form_recognizer_client = FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        with open("../sample_forms/forms/Form_1.jpg", "rb") as f:
            forms = await form_recognizer_client.recognize_custom_forms(
                model_id=self.supervised_model_id, stream=f.read()
            )

        for idx, form in enumerate(forms):
            print("========RECOGNIZING FORM #{}========".format(idx))
            print("Form has type {}".format(form.form_type))
            print("=======Fields=======")
            for label, field in form.fields.items():
                # each field is of type FormField
                # The value of the field can also be a FormField, or a list of FormFields
                # In our sample, it is not.
                print("Field '{}' has name '{}' and value '{}' with confidence score {}".format(
                    label, field.name, field.value, field.confidence
                ))
            print("====================")
            print("=======================================")
        await form_recognizer_client.close()


async def main():
    sample = RecognizeCustomFormsWithSupervisedModelSampleAsync()
    await sample.recognize_custom_forms_with_supervised_model()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
