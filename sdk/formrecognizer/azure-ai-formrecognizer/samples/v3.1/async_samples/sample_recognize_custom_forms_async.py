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

    The model can be trained using the training files found here:
    https://aka.ms/azsdk/formrecognizer/sampletrainingfiles-v3.1

USAGE:
    python sample_recognize_custom_forms_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer  resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CUSTOM_TRAINED_MODEL_ID - the ID of your custom trained model
        -OR-
       CONTAINER_SAS_URL_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container with your forms.
       A model will be trained and used to run the sample.
"""

import os
import asyncio


class RecognizeCustomFormsSampleAsync(object):

    async def recognize_custom_forms(self, custom_model_id):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "..", "..", "./sample_forms/forms/Form_1.jpg"))
        # [START recognize_custom_forms_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id = os.getenv("CUSTOM_TRAINED_MODEL_ID", custom_model_id)

        async with FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        ) as form_recognizer_client:

            # Make sure your form's type is included in the list of form types the custom model can recognize
            with open(path_to_sample_forms, "rb") as f:
                poller = await form_recognizer_client.begin_recognize_custom_forms(
                    model_id=model_id, form=f, include_field_elements=True
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

                # iterate over tables, lines, and selection marks on each page
                for page in form.pages:
                    for i, table in enumerate(page.tables):
                        print("\nTable {} on page {}".format(i + 1, table.page_number))
                        for cell in table.cells:
                            print("...Cell[{}][{}] has text '{}' with confidence {}".format(
                                cell.row_index, cell.column_index, cell.text, cell.confidence
                            ))
                    print("\nLines found on page {}".format(page.page_number))
                    for line in page.lines:
                        print("...Line '{}' is made up of the following words: ".format(line.text))
                        for word in line.words:
                            print("......Word '{}' has a confidence of {}".format(
                                word.text,
                                word.confidence
                            ))
                    if page.selection_marks:
                        print("\nSelection marks found on page {}".format(page.page_number))
                        for selection_mark in page.selection_marks:
                            print("......Selection mark is '{}' and has a confidence of {}".format(
                                selection_mark.state,
                                selection_mark.confidence
                            ))

                print("-----------------------------------")
        # [END recognize_custom_forms_async]


async def main():
    sample = RecognizeCustomFormsSampleAsync()
    model_id = None
    if os.getenv("CONTAINER_SAS_URL_V2"):

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormTrainingClient

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        form_training_client = FormTrainingClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        async with form_training_client:
            model = await (await form_training_client.begin_training(
                os.getenv("CONTAINER_SAS_URL_V2"), use_training_labels=True)).result()
            model_id = model.model_id

    await sample.recognize_custom_forms(model_id)


if __name__ == '__main__':
    asyncio.run(main())
