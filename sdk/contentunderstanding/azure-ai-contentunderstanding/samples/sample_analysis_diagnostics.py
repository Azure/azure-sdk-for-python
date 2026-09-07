# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analysis_diagnostics.py

DESCRIPTION:
    SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

    This sample demonstrates how to read analysis diagnostics returned with an analysis result.

    Content Understanding analysis results can include diagnostic information in
    ``AnalysisResult.infos``. Diagnostics are represented as error-like values with a code and a
    human-readable message.

    Diagnostic messages are intended for troubleshooting and can change as the service evolves.
    Applications should not parse the message as structured telemetry. Use OpenTelemetry when you
    need structured telemetry for monitoring or automation.

    ## Analyze an invoice and read diagnostics

    The following example analyzes an invoice with the ``prebuilt-invoice`` analyzer, then
    inspects the ``infos`` collection on the completed result.

    Example output from the preview service::

        LLMStats: completion calls: 2; embedding calls: 1; avg completion latency: 5.75s; total completion latency: 11.50s; avg embedding latency: 0.94s; total embedding latency: 0.94s

    The service currently uses the ``LLMStats`` code for information about completion and
    embedding calls. Consumers should handle unknown codes because additional diagnostic codes
    may be introduced later.

USAGE:
    python sample_analysis_diagnostics.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults.py for model deployment setup guidance.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput, AnalysisResult
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START read_analysis_diagnostics]
    invoice_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-dotnet/main/ContentUnderstanding.Common/data/invoice.pdf"

    print("Analyzing invoice and reading diagnostics...")
    poller = client.begin_analyze(
        analyzer_id="prebuilt-invoice",
        inputs=[AnalysisInput(url=invoice_url)],
    )
    result: AnalysisResult = poller.result()

    # After a completed analysis, diagnostic information is available on the result.
    # Treat diagnostic messages as human-readable text. Use OpenTelemetry when you
    # need structured telemetry for monitoring or automation.
    for info in result.infos or []:
        print(f"{info.code}: {info.message}")
    # [END read_analysis_diagnostics]


if __name__ == "__main__":
    main()
