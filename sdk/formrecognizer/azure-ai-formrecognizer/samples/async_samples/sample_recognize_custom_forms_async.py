# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_custom_forms_async.py

DESCRIPTION:
    This sample demonstrates how to analyze a form from a document with a custom
    trained model. The form must be of the same type as the forms the custom model
    was trained on. To learn how to train your own models, look at
    sample_train_model_without_labels_async.py and sample_train_model_with_labels_async.py

USAGE:
    python sample_recognize_custom_forms_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CUSTOM_TRAINED_MODEL_ID - the ID of your custom trained model
"""

import os
import asyncio


class RecognizeCustomFormsSampleAsync(object):

    async def recognize_custom_forms(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "..", "./sample_forms/forms/Form_1.jpg"))
        # [START recognize_custom_forms_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id = os.environ["CUSTOM_TRAINED_MODEL_ID"]

        async with FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        ) as form_recognizer_client:

            # Make sure your form's type is included in the list of form types the custom model can recognize
            with open(path_to_sample_forms, "rb") as f:
                poller = await form_recognizer_client.begin_recognize_custom_forms(
                    model_id=model_id, form=f
                )
            forms = await poller.result()

            for idx, form in enumerate(forms):
                print("--------Recognizing Form #{}--------".format(idx+1))
                print("Form has type {}".format(form.form_type))
                print("Form has form type confidence {}".format(form.form_type_confidence))
                print("Form was analyzed with model with ID {}".format(form.model_id))
                for name, field in form.fields.items():
                    # each field is of type FormField
                    # label_data is populated if you are using a model trained without labels,
                    # since the service needs to make predictions for labels if not explicitly given to it.
                    if field.label_data:
                        print("...Field '{}' has label '{}' with a confidence score of {}".format(
                            name,
                            field.label_data.text,
                            field.confidence
                        ))

                    print("...Label '{}' has value '{}' with a confidence score of {}".format(
                        field.label_data.text if field.label_data else name, field.value, field.confidence
                    ))

                print("-----------------------------------")
        # [END recognize_custom_forms_async]


async def main():
    sample = RecognizeCustomFormsSampleAsync()
    await sample.recognize_custom_forms()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
