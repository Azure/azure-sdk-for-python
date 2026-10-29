# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_entities_vietnamese.py

DESCRIPTION:
    This sample demonstrates named entity recognition for Vietnamese documents.

USAGE:
    python sample_recognize_entities_vietnamese.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key.
"""


def sample_recognize_entities_vietnamese() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    documents = [
        {
            "id": "1",
            "language": "vi",
            "text": "Tập đoàn FPT mở văn phòng mới tại Thành phố Hồ Chí Minh vào tháng này.",
        },
        {
            "id": "2",
            "language": "vi",
            "text": "Ngân hàng Việt Nam ký thỏa thuận hợp tác với Công ty ABC tại Hà Nội.",
        },
    ]

    result = client.recognize_entities(documents)
    for index, document in enumerate(result):
        if document.is_error:
            print(f"Error analyzing document {index + 1}: {document.error}")
        else:
            print(f"Entities in document {index + 1}:")
            for entity in document.entities:
                print(f"  {entity.text}: {entity.category} ({entity.confidence_score:.2f})")


if __name__ == "__main__":
    sample_recognize_entities_vietnamese()