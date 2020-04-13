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
    trained model. To learn how to train your own models, look at
    sample_train_unlabelled_model_async.py and sample_train_labelled_model_async.py
USAGE:
    python sample_recognize_custom_forms_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
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
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        async with FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key)) as form_recognizer_client:
            with open(path_to_sample_forms, "rb") as f:
                forms = await form_recognizer_client.recognize_custom_forms(
                    model_id=self.model_id, stream=f.read()
                )

            for idx, form in enumerate(forms):
                print("--------Recognizing Form #{}--------".format(idx))
                print("Form has type {}".format(form.form_type))
                for label, field in form.fields.items():
                    # each field is of type FormField
                    # The value of the field can also be a FormField, or a list of FormFields
                    # In our sample, it is not.
                    print("Field '{}' has value '{}' based on '{}' within bounding box '{}', with a confidence score of {}".format(
                        label,
                        field.value,
                        field.value_data.text,
                        ", ".join(["[{}, {}]".format(p.x, p.y) for p in field.value_data.bounding_box]) if field.value_data.bounding_box else "N/A",
                        field.confidence
                    ))
                print("-----------------------------------")


async def main():
    sample = RecognizeCustomFormsSampleAsync()
    await sample.recognize_custom_forms()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
