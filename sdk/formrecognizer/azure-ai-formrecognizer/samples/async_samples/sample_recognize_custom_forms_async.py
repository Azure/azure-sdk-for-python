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
    sample_train_unlabeled_model_async.py and sample_train_labeled_model_async.py
USAGE:
    python sample_recognize_custom_forms_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CUSTOM_TRAINED_MODEL_ID - the ID of your custom trained model
"""

import os
import asyncio
from pathlib import Path


class RecognizeCustomFormsSampleAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    model_id = os.environ["CUSTOM_TRAINED_MODEL_ID"]

    async def recognize_custom_forms(self):
        # the sample forms are located in this file's parent's parent's files.
        path_to_sample_forms = Path(__file__).parent.parent.absolute() / Path("sample_forms/forms/Form_1.jpg")
        # [START recognize_custom_forms_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        async with FormRecognizerClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as form_recognizer_client:

            # Make sure your form's type is included in the list of form types the custom model can recognize
            with open(path_to_sample_forms, "rb") as f:
                forms = await form_recognizer_client.recognize_custom_forms(
                    model_id=self.model_id, stream=f.read()
                )

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
        # [END recognize_custom_forms_async]


async def main():
    sample = RecognizeCustomFormsSampleAsync()
    await sample.recognize_custom_forms()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
