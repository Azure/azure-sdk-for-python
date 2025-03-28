# coding=utf-8

from azure.ai.documentintelligence import DocumentIntelligenceClient

"""
# PREREQUISITES
    pip install azure-ai-documentintelligence
# USAGE
    python get_analyze_batch_documents_results.py
"""


def main():
    client = DocumentIntelligenceClient(
        endpoint="https://myendpoint.cognitiveservices.azure.com",
        credential="CREDENTIAL",
    )

    response = client.list_analyze_batch_results(
        model_id="prebuilt-invoice",
    )
    for item in response:
        print(item)


# x-ms-original-file: 2024-11-30/GetAnalyzeBatchDocumentsResults.json
if __name__ == "__main__":
    main()
