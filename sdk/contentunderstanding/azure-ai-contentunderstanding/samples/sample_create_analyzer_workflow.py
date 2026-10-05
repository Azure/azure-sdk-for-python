# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_create_analyzer_workflow.py

DESCRIPTION:
    SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

    This sample demonstrates how to create custom analyzers with different workflow settings
    and compare analysis results on the same invoice.

    Omit ``workflow`` (or set ``ContentAnalyzerWorkflow.DEFAULT``) for standard extraction, or
    set ``ContentAnalyzerWorkflow.AGENTIC`` when an answer must be built from evidence across
    the document.

    ## Why use agentic workflow?

    For straightforward field extraction, use the default workflow. Use agentic mode when an
    answer must be **built from evidence** instead of extracted from a single location — for
    example multistep reasoning, calculations, validation, or analysis of complex tables and
    figures.

    In this sample, ``InvoiceId`` is a direct value that both workflows can extract.
    ``AverageItemPrice`` requires collecting many unit prices and calculating their mean, so it
    benefits from agentic reasoning. Agentic mode uses the **advanced contextualization** rate
    and typically consumes more model tokens and takes longer than the default workflow.

    Preview notes: In ``2026-06-01-preview``, analysis currently supports **one input file per
    request** regardless of workflow.

    Both workflows extract the direct ``InvoiceId`` field correctly. The default workflow can
    approximate the derived average, and its result can vary between runs. The agentic workflow
    uses reasoning and calculation to return the expected average item price of ``20.5``
    accurately.

USAGE:
    python sample_create_analyzer_workflow.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults.py for model deployment setup guidance.
"""


import os
import time
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AnalysisResult,
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentAnalyzerWorkflow,
    ContentFieldDefinition,
    ContentFieldSchema,
    ContentFieldType,
    DocumentContent,
    NumberField,
    StringField,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def _build_schema() -> ContentFieldSchema:
    # InvoiceId is a direct field; AverageItemPrice is a derived field used to highlight
    # workflow differences.
    return ContentFieldSchema(
        name="invoice_workflow_comparison",
        description="Invoice fields used to compare default and agentic workflows",
        fields={
            "InvoiceId": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                description="Invoice identifier printed on the invoice. Return only the identifier value without its label.",
            ),
            "AverageItemPrice": ContentFieldDefinition(
                type=ContentFieldType.NUMBER,
                description=(
                    "Calculate the arithmetic mean of all values in the UNIT PRICE column. "
                    "Use only unit prices, not quantities, line amounts, subtotals, taxes, or totals."
                ),
            ),
        },
    )


def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START create_analyzer_workflow]
    timestamp = int(time.time())
    default_analyzer_id = f"workflow_default_{timestamp}"
    agentic_analyzer_id = f"workflow_agentic_{timestamp}"

    field_schema = _build_schema()

    # ContentAnalyzerWorkflow.DEFAULT is selected when you omit workflow.
    # You can also set it explicitly: workflow=ContentAnalyzerWorkflow.DEFAULT
    default_analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Analyzer using default workflow",
        field_schema=field_schema,
        config=ContentAnalyzerConfig(return_details=True),
        models={"completion": "gpt-5.2"},
    )
    agentic_analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Analyzer using agentic workflow",
        field_schema=field_schema,
        config=ContentAnalyzerConfig(return_details=True, workflow=ContentAnalyzerWorkflow.AGENTIC),
        models={"completion": "gpt-5.2"},
    )

    try:
        client.begin_create_analyzer(
            analyzer_id=default_analyzer_id,
            resource=default_analyzer,
            allow_replace=True,
        ).result()
        client.begin_create_analyzer(
            analyzer_id=agentic_analyzer_id,
            resource=agentic_analyzer,
            allow_replace=True,
        ).result()

        with open("sample_files/workflow_invoice_20_items.pdf", "rb") as f:
            sample_invoice = f.read()

        default_result: AnalysisResult = client.begin_analyze(
            analyzer_id=default_analyzer_id,
            inputs=[AnalysisInput(data=sample_invoice)],
        ).result()
        agentic_result: AnalysisResult = client.begin_analyze(
            analyzer_id=agentic_analyzer_id,
            inputs=[AnalysisInput(data=sample_invoice)],
        ).result()

        default_doc = cast(DocumentContent, default_result.contents[0])
        agentic_doc = cast(DocumentContent, agentic_result.contents[0])

        default_invoice_id = (
            getattr(cast(StringField, default_doc.fields.get("InvoiceId")), "value", None)
            if default_doc.fields
            else None
        )
        default_avg = (
            getattr(
                cast(NumberField, default_doc.fields.get("AverageItemPrice")),
                "value",
                None,
            )
            if default_doc.fields
            else None
        )
        agentic_invoice_id = (
            getattr(cast(StringField, agentic_doc.fields.get("InvoiceId")), "value", None)
            if agentic_doc.fields
            else None
        )
        agentic_avg = (
            getattr(
                cast(NumberField, agentic_doc.fields.get("AverageItemPrice")),
                "value",
                None,
            )
            if agentic_doc.fields
            else None
        )

        print(f"Default workflow: InvoiceId={default_invoice_id}, AverageItemPrice={default_avg}")
        print(f"Agentic workflow: InvoiceId={agentic_invoice_id}, AverageItemPrice={agentic_avg}")
    finally:
        client.delete_analyzer(default_analyzer_id)
        client.delete_analyzer(agentic_analyzer_id)
    # [END create_analyzer_workflow]


if __name__ == "__main__":
    main()
