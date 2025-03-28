# coding=utf-8

from azure.ai.documentintelligence import DocumentIntelligenceClient

"""
# PREREQUISITES
    pip install azure-ai-documentintelligence
# USAGE
    python delete_analyze_document_result.py
"""


def main():
    client = DocumentIntelligenceClient(
        endpoint="https://myendpoint.cognitiveservices.azure.com",
        credential="CREDENTIAL",
    )

    client.delete_analyze_result(
        model_id="myCustomModel",
        result_id="3b31320d-8bab-4f88-b19c-2322a7f11034",
    )


# x-ms-original-file: 2024-11-30/DeleteAnalyzeDocumentResult.json
if __name__ == "__main__":
    main()
