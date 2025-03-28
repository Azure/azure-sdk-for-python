# coding=utf-8

from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-documentintelligence
# USAGE
    python get_document_models.py
"""


def main():
    client = DocumentIntelligenceClient(
        endpoint="https://myendpoint.cognitiveservices.azure.com",
        credential="CREDENTIAL",
    )

    response = client.list_models()
    for item in response:
        print(item)


# x-ms-original-file: 2024-11-30/GetDocumentModels.json
if __name__ == "__main__":
    main()
