# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_model_evaluation_results.py
DESCRIPTION:
    This sample demonstrates how to list **model evaluation results** for a trained model
    in a Text Authoring project (document-level metrics).
USAGE:
    python sample_list_model_evaluation_results.py
REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
OPTIONAL ENV VARS:
    PROJECT_NAME         # defaults to "<project-name>"
    TRAINED_MODEL_LABEL  # defaults to "<trained-model-label>"
"""

# [START text_authoring_get_model_evaluation_results]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CustomSingleLabelClassificationDocumentEvalResult,
    StringIndexType,
)


def sample_list_model_evaluation_results():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL_LABEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # trained-model–scoped call (pager of document-level evaluation results)
    project_client = client.get_project_client(project_name)
    results = project_client.trained_model.list_model_evaluation_results(
        trained_model_label,
        string_index_type=StringIndexType.UTF16_CODE_UNIT,
    )

    print("=== Model Evaluation Results ===")
    for result in results:
        # Base fields
        print(f"Document Location: {result.location}")
        print(f"Language: {result.language}")

        # Classification-specific fields (single-label)
        if isinstance(result, CustomSingleLabelClassificationDocumentEvalResult):
            classification = result.custom_single_label_classification_result
            print("  Classification:")
            print(f"    Expected:  {classification.expected_class}")
            print(f"    Predicted: {classification.predicted_class}")
        else:
            # If your project uses a different task type, handle other result kinds here
            print(f"  (Unsupported result type: {result.project_kind})")


# [END text_authoring_get_model_evaluation_results]


def main():
    sample_list_model_evaluation_results()


if __name__ == "__main__":
    main()
