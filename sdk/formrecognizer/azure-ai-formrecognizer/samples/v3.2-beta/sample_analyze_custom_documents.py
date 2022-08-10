# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_custom_documents.py

DESCRIPTION:
    This sample demonstrates how to analyze a document with a custom
    built model. The document must be of the same type as the documents the custom model
    was built on. To learn how to build your own models, look at
    sample_build_model.py.

    The model can be built using the training files found here:
    https://aka.ms/azsdk/formrecognizer/sampletrainingfiles

USAGE:
    python sample_analyze_custom_documents.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CUSTOM_BUILT_MODEL_ID - the ID of your custom built model
        -OR-
       CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your training files.
       A model will be built and used to run the sample.
"""

import os


def analyze_custom_documents(custom_model_id):
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__), "..", "..", "./sample_forms/forms/Form_1.jpg"
        )
    )
    # [START analyze_custom_documents]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    model_id = os.getenv("CUSTOM_BUILT_MODEL_ID", custom_model_id)

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Make sure your document's type is included in the list of document types the custom model can analyze
    with open(path_to_sample_documents, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            model_id=model_id, document=f
        )
    result = poller.result()

    for idx, document in enumerate(result.documents):
        print("--------Analyzing document #{}--------".format(idx + 1))
        print("Document has type {}".format(document.doc_type))
        print("Document has confidence {}".format(document.confidence))
        print("Document was analyzed by model with ID {}".format(result.model_id))
        for name, field in document.fields.items():
            field_value = field.value if field.value else field.content
            print("......found field of type '{}' with value '{}' and with confidence {}".format(field.value_type, field_value, field.confidence))


    # iterate over tables, lines, and selection marks on each page
    for page in result.pages:
        print("\nLines found on page {}".format(page.page_number))
        for line in page.lines:
            print("...Line '{}'".format(line.content))
        for word in page.words:
            print(
                "...Word '{}' has a confidence of {}".format(
                    word.content, word.confidence
                )
            )
        for selection_mark in page.selection_marks:
            print(
                "...Selection mark is '{}' and has a confidence of {}".format(
                    selection_mark.state, selection_mark.confidence
                )
            )

    for i, table in enumerate(result.tables):
        print("\nTable {} can be found on page:".format(i + 1))
        for region in table.bounding_regions:
            print("...{}".format(i + 1, region.page_number))
        for cell in table.cells:
            print(
                "...Cell[{}][{}] has content '{}'".format(
                    cell.row_index, cell.column_index, cell.content
                )
            )
    print("-----------------------------------")
    # [END analyze_custom_documents]


if __name__ == "__main__":
    model_id = None
    if os.getenv("CONTAINER_SAS_URL"):

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import DocumentModelAdministrationClient, ModelBuildMode

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        document_model_admin_client = DocumentModelAdministrationClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        model = document_model_admin_client.begin_build_model(
            ModelBuildMode.TEMPLATE, blob_container_url=os.getenv("CONTAINER_SAS_URL")
        ).result()
        model_id = model.model_id

    analyze_custom_documents(model_id)
