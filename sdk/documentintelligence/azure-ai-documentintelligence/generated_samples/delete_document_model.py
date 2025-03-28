# coding=utf-8

from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-documentintelligence
# USAGE
    python delete_document_model.py
"""


def main():
    client = DocumentIntelligenceClient(
        endpoint="https://myendpoint.cognitiveservices.azure.com",
        credential="CREDENTIAL",
    )

    client.delete_model(
        model_id="myCustomModel",
    )


# x-ms-original-file: 2024-11-30/DeleteDocumentModel.json
if __name__ == "__main__":
    main()
