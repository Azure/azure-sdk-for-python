# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_detailed_diagnostics_information.py

DESCRIPTION:
    This sample demonstrates how to retrieve batch statistics, the
    model version used, and the raw response returned from the service.

    It additionally shows an alternative way to pass in the input documents.
    Here we supply our own IDs and language hints along with the text.

USAGE:
    python sample_get_detailed_diagnostics_information.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key
"""

import os
import logging

_LOGGER = logging.getLogger(__name__)

class GetDetailedDiagnosticsInformationSample(object):
    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def get_detailed_diagnostics_information(self):
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))

        documents = [
            {"id": "0", "language": "en", "text": "I had the best day of my life."},
            {"id": "1", "language": "en",
             "text": "This was a waste of my time. The speaker put me to sleep."},
            {"id": "2", "language": "es", "text": "No tengo dinero ni nada que dar..."},
            {"id": "3", "language": "fr",
             "text": "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."}
        ]

        def callback(resp):
            for statistic, value in resp.statistics.items():
                _LOGGER.info("{}: {}".format(statistic, value))
            _LOGGER.info("model_version: {}".format(resp.model_version))
            _LOGGER.info("raw_response: {}".format(resp.raw_response))

        result = text_analytics_client.analyze_sentiment(
            documents,
            show_stats=True,
            model_version="latest",
            raw_response_hook=callback
        )


if __name__ == '__main__':
    sample = GetDetailedDiagnosticsInformationSample()
    sample.get_detailed_diagnostics_information()
