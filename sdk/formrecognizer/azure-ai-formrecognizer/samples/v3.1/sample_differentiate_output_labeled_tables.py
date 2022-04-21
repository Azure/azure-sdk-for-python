# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_differentiate_output_labeled_tables.py

DESCRIPTION:
    This sample demonstrates the differences in output that arise when begin_recognize_custom_forms
    is called with custom models trained with fixed vs. dynamic table tags.
    The models used in this sample can be created in the sample_train_model_with_labels.py using the
    training files in https://aka.ms/azsdk/formrecognizer/sampletabletrainingfiles

    Note that Form Recognizer automatically finds and extracts all tables in your documents whether the tables
    are tagged/labeled or not. Tables extracted automatically by Form Recognizer will be included in the
    `tables` property under `RecognizedForm.pages`.

    A conceptual explanation of using table tags to train your custom form model can be found in the
    service documentation: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/supervised-table-tags

USAGE:
    python sample_differentiate_output_labeled_tables.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your  Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) MODEL_ID_FIXED_ROW_TABLES - the ID of your custom model trained with labels on fixed row tables
            -OR-
       CONTAINER_SAS_URL_FIXED_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container with
       your labeled data containing a fixed row table. A model will be trained and used to run the sample.
    4) MODEL_ID_DYNAMIC_ROW_TABLES - the ID of your custom model trained with labels on dynamic row tables
            -OR-
       CONTAINER_SAS_URL_DYNAMIC_V2 - The shared access signature (SAS) Url of your Azure Blob Storage container with
       your labeled data containing a dynamic row table. A model will be trained and used to run the sample.
"""

import os


class TestDifferentiateOutputLabeledTables(object):

    def test_recognize_tables_fixed_rows(self, custom_model_id):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id_fixed_rows_table = os.getenv("MODEL_ID_FIXED_ROW_TABLES", custom_model_id)

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "..", "./sample_forms/forms/label_table_fixed_rows1.pdf"))

        with open(path_to_sample_forms, "rb") as f:
            form = f.read()
        poller = form_recognizer_client.begin_recognize_custom_forms(
            model_id=model_id_fixed_rows_table, form=form
        )

        result = poller.result()

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

    def test_recognize_tables_dynamic_rows(self, custom_model_id):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
        model_id_dynamic_rows_table = os.getenv("MODEL_ID_DYNAMIC_ROW_TABLES", custom_model_id)

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "..", "./sample_forms/forms/label_table_dynamic_rows1.pdf"))

        with open(path_to_sample_forms, "rb") as f:
            form = f.read()
        poller = form_recognizer_client.begin_recognize_custom_forms(
            model_id=model_id_dynamic_rows_table, form=form
        )

        result = poller.result()

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


if __name__ == '__main__':
    sample = TestDifferentiateOutputLabeledTables()
    fixed_model_id = None
    dynamic_model_id = None
    if os.getenv("CONTAINER_SAS_URL_FIXED_V2") or os.getenv("CONTAINER_SAS_URL_DYNAMIC_V2"):

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormTrainingClient

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
        fixed = os.getenv("CONTAINER_SAS_URL_FIXED_V2")
        dynamic = os.getenv("CONTAINER_SAS_URL_DYNAMIC_V2")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        form_training_client = FormTrainingClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        if fixed:
            model = form_training_client.begin_training(fixed, use_training_labels=True).result()
            fixed_model_id = model.model_id
        if dynamic:
            model = form_training_client.begin_training(dynamic, use_training_labels=True).result()
            dynamic_model_id = model.model_id

    sample.test_recognize_tables_fixed_rows(fixed_model_id)
    sample.test_recognize_tables_dynamic_rows(dynamic_model_id)
