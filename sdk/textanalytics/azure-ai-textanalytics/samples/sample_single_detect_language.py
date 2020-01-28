# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_detect_language.py

DESCRIPTION:
    This sample demonstrates how to detect the language of a single string.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_detect_language.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Language detected: English
    Confidence score: 1.0

    Document Statistics:
    Text character count: 42
    Transactions count: 1
"""

import os


class SingleDetectLanguageSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def detect_language(self):
        # [START single_detect_language]
        from azure.ai.textanalytics import single_detect_language, TextAnalyticsAPIKeyCredential

        text = "I need to take my cat to the veterinarian."

        result = single_detect_language(
            endpoint=self.endpoint,
            credential=TextAnalyticsAPIKeyCredential(self.key),
            input_text=text,
            country_hint="US",
            show_stats=True
        )

        print("Language detected: {}".format(result.primary_language.name))
        print("Confidence score: {}\n".format(result.primary_language.score))
        print("Document Statistics:")
        print("Text character count: {}".format(result.statistics.character_count))
        print("Transactions count: {}".format(result.statistics.transaction_count))
        # [END single_detect_language]


if __name__ == '__main__':
    sample = SingleDetectLanguageSample()
    sample.detect_language()
