# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_sentiment.py

DESCRIPTION:
    This sample demonstrates how to run **sentiment analysis** over text.

USAGE:
    python sample_analyze_sentiment.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
"""

# [START analyze_sentiment]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextSentimentAnalysisInput,
    AnalyzeTextSentimentResult,
)


def sample_analyze_sentiment():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "The food and service were unacceptable, but the concierge were nice. "
        "After talking to them about the quality of the food and the process to get room service "
        "they refunded the money we spent at the restaurant and gave us a voucher for nearby restaurants."
    )

    body = TextSentimentAnalysisInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        )
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextSentimentResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            print(f"Overall sentiment: {doc.sentiment}")
            if doc.confidence_scores:
                print("Confidence scores:")
                print(f"  positive={doc.confidence_scores.positive}")
                print(f"  neutral={doc.confidence_scores.neutral}")
                print(f"  negative={doc.confidence_scores.negative}")

            if doc.sentences:
                print("\nSentence sentiments:")
                for s in doc.sentences:
                    print(f"  Text: {s.text}")
                    print(f"  Sentiment: {s.sentiment}")
                    if s.confidence_scores:
                        print(
                            "  Scores: "
                            f"pos={s.confidence_scores.positive}, "
                            f"neu={s.confidence_scores.neutral}, "
                            f"neg={s.confidence_scores.negative}"
                        )
                    print(f"  Offset: {s.offset}, Length: {s.length}\n")
            else:
                print("No sentence-level results returned.")
    else:
        print("No documents in the response or unexpected result type.")


# [END analyze_sentiment]


def main():
    sample_analyze_sentiment()


if __name__ == "__main__":
    main()
