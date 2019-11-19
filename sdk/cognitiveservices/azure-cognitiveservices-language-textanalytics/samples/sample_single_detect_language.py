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
    2) AZURE_COGNITIVE_SERVICES_KEY - your cognitive services account key

OUTPUT:
    Language detected: English
    Confidence score: 1.0
"""

import os


class SingleDetectLanguageSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_COGNITIVE_SERVICES_KEY")

    def detect_language(self):
        from azure.cognitiveservices.language.textanalytics import single_detect_language

        text = "I need to take my cat to the veterinarian."

        result = single_detect_language(
            endpoint=self.endpoint,
            credential=self.key,
            text=text,
            country_hint="US"
        )

        print("Language detected: {}".format(result.name))
        print("Confidence score: {}".format(result.score))


if __name__ == '__main__':
    sample = SingleDetectLanguageSample()
    sample.detect_language()
