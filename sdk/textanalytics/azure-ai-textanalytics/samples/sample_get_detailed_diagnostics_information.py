# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_detailed_diagnostics_information.py

DESCRIPTION:
    This sample demonstrates how to retrieve batch statistics, the
    model version used, and the raw response in JSON format returned from the service.

USAGE:
    python sample_get_detailed_diagnostics_information.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

import os
import logging
import json

_LOGGER = logging.getLogger(__name__)


def sample_get_detailed_diagnostics_information():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    # This client will log detailed information about its HTTP sessions, at DEBUG level
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key), logging_enable=True)

    documents = [
        """I had the best day of my life. I decided to go sky-diving and it made me appreciate my whole life so much more.
        I developed a deep-connection with my instructor as well.
        """,
        "This was a waste of my time. The speaker put me to sleep.",
        "No tengo dinero ni nada que dar...",
        "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."
    ]

    json_responses = []

    def callback(resp):
        _LOGGER.debug("document_count: {}".format(resp.statistics["document_count"]))
        _LOGGER.debug("valid_document_count: {}".format(resp.statistics["valid_document_count"]))
        _LOGGER.debug("erroneous_document_count: {}".format(resp.statistics["erroneous_document_count"]))
        _LOGGER.debug("transaction_count: {}".format(resp.statistics["transaction_count"]))
        _LOGGER.debug(f"model_version: {resp.model_version}")
        json_response = json.dumps(resp.raw_response)
        json_responses.append(json_response)

    result = text_analytics_client.extract_key_phrases(
        documents,
        show_stats=True,
        model_version="latest",
        raw_response_hook=callback
    )
    for doc in result:
        _LOGGER.warning(f"Doc with id {doc.id} has these warnings: {doc.warnings}")

    _LOGGER.debug(f"json response: {json_responses[0]}")


if __name__ == '__main__':
    sample_get_detailed_diagnostics_information()
