# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_extract_key_phrases.py

DESCRIPTION:
    This sample demonstrates how to extract key phrases from a single string.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_extract_key_phrases.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_COGNITIVE_SERVICES_KEY - your cognitive services account key

OUTPUT:
    Key phrases found:

    King County
    United States
    Washington
    city
    miles
    Redmond
    Seattle
"""

import os


class SingleExtractKeyPhrasesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_COGNITIVE_SERVICES_KEY")

    def extract_key_phrases(self):
        from azure.cognitiveservices.language.textanalytics import single_extract_key_phrases

        text = "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle."

        result = single_extract_key_phrases(
            endpoint=self.endpoint,
            credential=self.key,
            text=text,
            language="en"
        )

        print("Key phrases found:\n")
        for phrase in result:
            print(phrase)


if __name__ == '__main__':
    sample = SingleExtractKeyPhrasesSample()
    sample.extract_key_phrases()
