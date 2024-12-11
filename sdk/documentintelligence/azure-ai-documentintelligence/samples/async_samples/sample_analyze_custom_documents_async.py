# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_custom_documents_async.py

DESCRIPTION:
    This sample demonstrates how to analyze a document with a custom
    built model. The document must be of the same type as the documents the custom model
    was built on. To learn how to build your own models, look at
    sample_build_model.py.

USAGE:
    python sample_analyze_custom_documents_async.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
    3) CUSTOM_BUILT_MODEL_ID - the ID of your custom built model.
        -OR-
       DOCUMENTINTELLIGENCE_STORAGE_ADVANCED_CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your training files.
       A model will be built and used to run the sample.
"""

import os
import asyncio
from collections import Counter


def print_table(header_names, table_data):
    # Print a two-dimensional array like a table.
    max_len_list = []
    for i in range(len(header_names)):
        col_values = list(map(lambda row: len(str(row[i])), table_data))
        col_values.append(len(str(header_names[i])))
        max_len_list.append(max(col_values))

    row_format_str = "".join(map(lambda len: f"{{:<{len + 4}}}", max_len_list))

    print(row_format_str.format(*header_names))
    for row in table_data:
        print(row_format_str.format(*row))


async def analyze_custom_documents(custom_model_id):
    # For the Form_1.jpg, it should be the test file under the traning dataset which storage at the Azure Blob Storage path
    # combined by DOCUMENTINTELLIGENCE_STORAGE_ADVANCED_CONTAINER_SAS_URL and DOCUMENTINTELLIGENCE_STORAGE_PREFIX,
    # or it can also be a test file with the format similar to the training dataset.
    # Put it here locally just for presenting documents visually in sample.

    # Before analyzing a custom document, should upload the related training dataset into Azure Storage Blob and
    # train a model. For more information, see https://aka.ms/build-a-custom-model.
    path_to_sample_documents = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "..", "./sample_forms/forms/Form_1.jpg")
    )
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeResult

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
    model_id = os.getenv("CUSTOM_BUILT_MODEL_ID", custom_model_id)

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Make sure your document's type is included in the list of document types the custom model can analyze
    with open(path_to_sample_documents, "rb") as f:
        poller = await document_intelligence_client.begin_analyze_document(model_id=model_id, body=f)
    result: AnalyzeResult = await poller.result()

    if result.documents:
        for idx, document in enumerate(result.documents):
            print(f"--------Analyzing document #{idx + 1}--------")
            print(f"Document has type {document.doc_type}")
            print(f"Document has document type confidence {document.confidence}")
            print(f"Document was analyzed with model with ID {result.model_id}")
            if document.fields:
                for name, field in document.fields.items():
                    field_value = field.get("valueString") if field.get("valueString") else field.content
                    print(
                        f"......found field of type '{field.type}' with value '{field_value}' and with confidence {field.confidence}"
                    )

        # Extract table cell values
        SYMBOL_OF_TABLE_TYPE = "array"
        SYMBOL_OF_OBJECT_TYPE = "object"
        KEY_OF_VALUE_OBJECT = "valueObject"
        KEY_OF_CELL_CONTENT = "content"

        for doc in result.documents:
            if not doc.fields is None:
                for field_name, field_value in doc.fields.items():
                    # Dynamic Table cell information store as array in document field.
                    if field_value.type == SYMBOL_OF_TABLE_TYPE and field_value.value_array:
                        col_names = []
                        sample_obj = field_value.value_array[0]
                        if KEY_OF_VALUE_OBJECT in sample_obj:
                            col_names = list(sample_obj[KEY_OF_VALUE_OBJECT].keys())
                        print("----Extracting Dynamic Table Cell Values----")
                        table_rows = []
                        for obj in field_value.value_array:
                            if KEY_OF_VALUE_OBJECT in obj:
                                value_obj = obj[KEY_OF_VALUE_OBJECT]
                                extract_value_by_col_name = lambda key: (
                                    value_obj[key].get(KEY_OF_CELL_CONTENT)
                                    if key in value_obj and KEY_OF_CELL_CONTENT in value_obj[key]
                                    else "None"
                                )
                                row_data = list(map(extract_value_by_col_name, col_names))
                                table_rows.append(row_data)
                        print_table(col_names, table_rows)

                    # Fixed Table cell information store as object in document field.
                    elif (
                        field_value.type == SYMBOL_OF_OBJECT_TYPE
                        and KEY_OF_VALUE_OBJECT in field_value
                        and field_value[KEY_OF_VALUE_OBJECT] is not None
                    ):
                        rows_by_columns = list(field_value[KEY_OF_VALUE_OBJECT].values())
                        is_fixed_table = all(
                            (
                                rows_of_column["type"] == SYMBOL_OF_OBJECT_TYPE
                                and Counter(list(rows_by_columns[0][KEY_OF_VALUE_OBJECT].keys()))
                                == Counter(list(rows_of_column[KEY_OF_VALUE_OBJECT].keys()))
                            )
                            for rows_of_column in rows_by_columns
                        )

                        if is_fixed_table:
                            print("----Extracting Fixed Table Cell Values----")
                            col_names = list(field_value[KEY_OF_VALUE_OBJECT].keys())
                            row_dict: dict = {}
                            for rows_of_column in rows_by_columns:
                                rows = rows_of_column[KEY_OF_VALUE_OBJECT]
                                for row_key in list(rows.keys()):
                                    if row_key in row_dict:
                                        row_dict[row_key].append(rows[row_key].get(KEY_OF_CELL_CONTENT))
                                    else:
                                        row_dict[row_key] = [row_key, rows[row_key].get(KEY_OF_CELL_CONTENT)]

                            col_names.insert(0, "")
                            print_table(col_names, list(row_dict.values()))
    print("-----------------------------------")


async def main():
    model_id = None
    if os.getenv("DOCUMENTINTELLIGENCE_STORAGE_ADVANCED_CONTAINER_SAS_URL") and not os.getenv("CUSTOM_BUILT_MODEL_ID"):
        import uuid
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient
        from azure.ai.documentintelligence.models import (
            DocumentBuildMode,
            BuildDocumentModelRequest,
            AzureBlobContentSource,
        )

        endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")
        key = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        blob_container_sas_url = os.getenv("DOCUMENTINTELLIGENCE_STORAGE_ADVANCED_CONTAINER_SAS_URL")
        blob_prefix = os.getenv("DOCUMENTINTELLIGENCE_STORAGE_PREFIX")
        if blob_container_sas_url is not None:
            request = BuildDocumentModelRequest(
                model_id=str(uuid.uuid4()),
                build_mode=DocumentBuildMode.TEMPLATE,
                azure_blob_source=AzureBlobContentSource(container_url=blob_container_sas_url, prefix=blob_prefix),
            )
            document_intelligence_admin_client = DocumentIntelligenceAdministrationClient(
                endpoint=endpoint, credential=AzureKeyCredential(key)
            )
            async with document_intelligence_admin_client:
                poll = await document_intelligence_admin_client.begin_build_document_model(request)
                model = await poll.result()
            model_id = model.model_id
    await analyze_custom_documents(model_id)


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        asyncio.run(main())
    except HttpResponseError as error:
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
