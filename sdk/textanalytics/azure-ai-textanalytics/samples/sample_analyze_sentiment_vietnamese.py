# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_sentiment_vietnamese.py

DESCRIPTION:
    This sample demonstrates sentiment analysis for Vietnamese documents.

USAGE:
    python sample_analyze_sentiment_vietnamese.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key.
"""


def sample_analyze_sentiment_vietnamese() -> None:
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
            "text": "Dịch vụ giao hàng nhanh chóng và nhân viên hỗ trợ rất nhiệt tình.",
        },
        {
            "id": "2",
            "language": "vi",
            "text": "Ứng dụng thường xuyên bị lỗi và trải nghiệm thanh toán rất chậm.",
        },
    ]

    result = client.analyze_sentiment(documents)
    for document, analysis in zip(documents, result):
        if analysis.is_error:
            print(f"Error analyzing document: {analysis.error}")
        else:
            print(f"Document: {document}")
            print(f"Sentiment: {analysis.sentiment}")
            print(f"Confidence scores: {analysis.confidence_scores}\n")


if __name__ == "__main__":
    sample_analyze_sentiment_vietnamese()