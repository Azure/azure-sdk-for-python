# coding=utf-8

from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-documentintelligence
# USAGE
    python get_document_classifier.py
"""


def main():
    client = DocumentIntelligenceClient(
        endpoint="https://myendpoint.cognitiveservices.azure.com",
        credential="CREDENTIAL",
    )

    response = client.get_classifier(
        classifier_id="myClassifier",
    )
    print(response)


# x-ms-original-file: 2024-11-30/GetDocumentClassifier.json
if __name__ == "__main__":
    main()
