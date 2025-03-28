# coding=utf-8

from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-documentintelligence
# USAGE
    python delete_document_classifier.py
"""


def main():
    client = DocumentIntelligenceClient(
        endpoint="https://myendpoint.cognitiveservices.azure.com",
        credential="CREDENTIAL",
    )

    client.delete_classifier(
        classifier_id="myClassifier",
    )


# x-ms-original-file: 2024-11-30/DeleteDocumentClassifier.json
if __name__ == "__main__":
    main()
