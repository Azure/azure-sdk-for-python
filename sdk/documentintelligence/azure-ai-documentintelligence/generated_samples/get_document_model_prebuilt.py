# coding=utf-8

from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-documentintelligence
# USAGE
    python get_document_model_prebuilt.py
"""


def main():
    client = DocumentIntelligenceClient(
        endpoint="https://myendpoint.cognitiveservices.azure.com",
        credential="CREDENTIAL",
    )

    response = client.get_model(
        model_id="prebuilt-invoice",
    )
    print(response)


# x-ms-original-file: 2024-11-30/GetDocumentModel_Prebuilt.json
if __name__ == "__main__":
    main()
