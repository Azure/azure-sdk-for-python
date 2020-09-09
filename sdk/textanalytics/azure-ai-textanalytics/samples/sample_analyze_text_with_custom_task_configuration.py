# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_text.py

DESCRIPTION:
    This sample demonstrates how to submit a collection of text documents for analysis using a custom task
    configuration.  Built-in tasks, such as Entity Recognition and PII Entity Recognition, can be configured
    with additional parameters.  User-defined text analysis tasks can also be added to the list of tasks
    to execute.

USAGE:
    python sample_analyze_text.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""


import os


class AnalyzeTextWithCustomTaskConfigurationSample(object):

    def analyze_text_with_custom_task_configuration(self):
        # [START analyze_text_with_task_configuration]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

        documents = [
            "I had a wonderful trip to Seattle last week.",
            "I'm flying to NYC tomorrow. See you there."
        ]

        poller = text_analytics_client.begin_analyze_text(
            documents,
            display_name="Analyze Text Sample",
            tasks=[
                EntitiesTask(),
                CustomTextAnalysisTask()
            ]
        )

        result = poller.result()