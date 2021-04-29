# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_differentiate_output_labeled_tables_async.py

DESCRIPTION:
    This sample demonstrates the differences in output that arise when begin_recognize_custom_forms
    is called with custom models trained with fixed vs. dynamic table tags.
    The models used in this sample can be created in the sample_train_model_with_labels.py using the
    training files in
    https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_forms/labeled_tables

    Note that Form Recognizer automatically finds and extracts all tables in your documents whether the tables
    are tagged/labeled or not. Therefore, you don't have to label every table from your form with a table tag and your
    table tags don't have to replicate the structure of every table found in your form. Tables extracted
    automatically by Form Recognizer will be included in the `tables` property under `RecognizedForm.pages`.

    A conceptual explanation of using table tags to train your custom form model can be found in the
    service documentation: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/supervised-table-tags

USAGE:
    python sample_differentiate_output_labeled_tables_async.py

    Set the environment dynamics with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) MODEL_ID_FIXED_ROW_TABLES - the ID of your custom model trained with labels on fixed row tables
    4) MODEL_ID_DYNAMIC_ROW_TABLES - the ID of your custom model trained with labels on dynamic row tables
"""

import os
import asyncio


class TestDifferentiateOutputLabeledTablesAsync(object):

    async def test_recognize_tables_fixed_rows_async(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id_fixed_rows_table = os.environ["MODEL_ID_FIXED_ROW_TABLES"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "..", "./sample_forms/forms/label_table_fixed_rows1.pdf"))
        with open(path_to_sample_forms, "rb") as f:
            form = f.read()

        async with form_recognizer_client:
            poller = await form_recognizer_client.begin_recognize_custom_forms(
                model_id=model_id_fixed_rows_table, form=form
            )

            result = await poller.result()

        print("\n--------Recognizing labeled table with fixed rows--------\n")
        for form in result:
            for name, field in form.fields.items():
                # substitute "table" for the label given to the table tag during training
                # (if different than sample training docs)
                if name == "table":
                    for row_name, column in field.value.items():
                        print("Row '{}' has columns:".format(row_name))
                        for column_name, column_value in column.value.items():
                            print("...Column '{}' with value '{}' and a confidence score of {}".format(
                                column_name, column_value.value, column_value.confidence
                            ))
                else:  # non-table tagged FormField
                    print("...Field '{}' has value '{}' with a confidence score of {}".format(
                        name,
                        field.value,
                        field.confidence
                    ))

    async def test_recognize_tables_dynamic_rows_async(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id_dynamic_rows_table = os.environ["MODEL_ID_DYNAMIC_ROW_TABLES"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "..", "./sample_forms/forms/label_table_dynamic_rows1.pdf"))
        with open(path_to_sample_forms, "rb") as f:
            form = f.read()

        async with form_recognizer_client:
            poller = await form_recognizer_client.begin_recognize_custom_forms(
                model_id=model_id_dynamic_rows_table, form=form
            )

            result = await poller.result()

        print("\n\n--------Recognizing labeled table with dynamic rows--------\n")
        for form in result:
            for name, field in form.fields.items():
                # substitute "table" for the label given to the table tag during training
                # (if different than sample training docs)
                if name == "table":
                    for idx, row in enumerate(field.value):
                        print("Row {}".format(idx+1))
                        for column_name, row_value in row.value.items():
                            print("...Column '{}' with value '{}' and a confidence score of {}".format(
                                column_name, row_value.value, row_value.confidence
                            ))
                else:  # non-table tagged FormField
                    print("...Field '{}' has value '{}' with a confidence score of {}".format(
                        name,
                        field.value,
                        field.confidence
                    ))


async def main():
    sample = TestDifferentiateOutputLabeledTablesAsync()
    await sample.test_recognize_tables_fixed_rows_async()
    await sample.test_recognize_tables_dynamic_rows_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
