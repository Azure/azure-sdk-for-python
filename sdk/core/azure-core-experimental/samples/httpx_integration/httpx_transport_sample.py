# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example showing how to use httpx as the transport when using http based client libraries
"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.experimental.transport import HttpXTransport

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

credential = AzureKeyCredential(key)

text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=credential,
    transport=HttpXTransport(),
)

document = ["This is an example document."]

poller = text_analytics_client.begin_abstractive_summary(document)
abstractive_summary_results = poller.result()
