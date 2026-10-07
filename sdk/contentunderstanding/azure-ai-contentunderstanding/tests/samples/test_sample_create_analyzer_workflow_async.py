# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_create_analyzer_workflow_async.py

DESCRIPTION:
    Async tests for sample_create_analyzer_workflow_async.py.
"""

import pytest
import os
import uuid
from typing import Dict
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBaseAsync,
)
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentAnalyzerWorkflow,
    ContentFieldDefinition,
    ContentFieldSchema,
    NumberField,
    StringField,
)


pytestmark = pytest.mark.preview


class TestSampleCreateAnalyzerWorkflowAsync(ContentUnderstandingClientTestBaseAsync):
    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_create_analyzer_workflow_async(
        self, contentunderstanding_endpoint: str, **kwargs
    ) -> Dict[str, str]:
        variables = kwargs.pop("variables", {})
        client = self.create_preview_async_client(endpoint=contentunderstanding_endpoint)

        default_id = variables.setdefault(
            "workflowDefaultAnalyzerId",
            f"test_workflow_default_{uuid.uuid4().hex[:16]}",
        )
        agentic_id = variables.setdefault(
            "workflowAgenticAnalyzerId",
            f"test_workflow_agentic_{uuid.uuid4().hex[:16]}",
        )

        schema = ContentFieldSchema(
            name="invoice_workflow_comparison",
            description="Invoice fields used to compare default and agentic workflows",
            fields={
                "InvoiceId": ContentFieldDefinition(
                    type="string",
                    description=(
                        "Invoice identifier printed on the invoice. "
                        "Return only the identifier value without its label."
                    ),
                ),
                "AverageItemPrice": ContentFieldDefinition(
                    type="number",
                    description=(
                        "Calculate the arithmetic mean of all values in the UNIT PRICE column. "
                        "Use only unit prices, not quantities, line amounts, subtotals, taxes, or totals."
                    ),
                ),
            },
        )

        # ContentAnalyzerWorkflow.DEFAULT is selected when workflow is omitted.
        default_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Analyzer using default workflow",
            field_schema=schema,
            config=ContentAnalyzerConfig(return_details=True),
            models={"completion": "gpt-5.2"},
        )
        agentic_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Analyzer using agentic workflow",
            field_schema=schema,
            config=ContentAnalyzerConfig(return_details=True, workflow=ContentAnalyzerWorkflow.AGENTIC),
            models={"completion": "gpt-5.2"},
        )

        async with client:
            try:
                default_create = await client.begin_create_analyzer(default_id, default_analyzer, allow_replace=True)
                await default_create.result()
                agentic_create = await client.begin_create_analyzer(agentic_id, agentic_analyzer, allow_replace=True)
                await agentic_create.result()

                default_response = await client.get_analyzer(default_id)
                agentic_response = await client.get_analyzer(agentic_id)

                assert default_response.config is not None
                assert agentic_response.config is not None

                default_workflow = str(default_response.config.workflow or "")
                assert default_workflow, "Default analyzer should have a resolved workflow"
                assert not default_workflow.lower().startswith(
                    "agentic"
                ), f"Omitting workflow should resolve to a non-agentic workflow (got '{default_workflow}')"

                agentic_workflow = str(agentic_response.config.workflow or "")
                assert agentic_workflow.lower().startswith(
                    "agentic"
                ), f"Agentic analyzer should resolve to an agentic workflow (got '{agentic_workflow}')"

                tests_dir = os.path.dirname(os.path.dirname(__file__))
                file_path = os.path.join(tests_dir, "test_data", "workflow_invoice_20_items.pdf")
                with open(file_path, "rb") as f:
                    file_bytes = f.read()

                default_poller = await client.begin_analyze(
                    analyzer_id=default_id,
                    inputs=[AnalysisInput(data=file_bytes)],
                )
                default_result = await default_poller.result()
                agentic_poller = await client.begin_analyze(
                    analyzer_id=agentic_id,
                    inputs=[AnalysisInput(data=file_bytes)],
                )
                agentic_result = await agentic_poller.result()

                assert default_result.contents and len(default_result.contents) > 0
                assert agentic_result.contents and len(agentic_result.contents) > 0

                default_doc = default_result.contents[0]
                agentic_doc = agentic_result.contents[0]
                assert hasattr(default_doc, "fields") and hasattr(agentic_doc, "fields")

                default_fields = default_doc.fields or {}
                agentic_fields = agentic_doc.fields or {}
                assert "InvoiceId" in default_fields
                assert "InvoiceId" in agentic_fields
                assert isinstance(default_fields["InvoiceId"], StringField)
                assert isinstance(agentic_fields["InvoiceId"], StringField)
                assert default_fields["InvoiceId"].value == "INV-2048"
                assert agentic_fields["InvoiceId"].value == "INV-2048"

                expected_average = 20.5
                default_avg_field = default_fields.get("AverageItemPrice")
                default_avg = default_avg_field.value if isinstance(default_avg_field, NumberField) else None
                default_avg_error = abs(default_avg - expected_average) if default_avg is not None else float("inf")

                agentic_avg_field = agentic_fields.get("AverageItemPrice")
                assert agentic_avg_field is not None, "Agentic workflow should return the average item price"
                assert isinstance(agentic_avg_field, NumberField)
                assert agentic_avg_field.value is not None
                assert abs(agentic_avg_field.value - expected_average) <= 0.01

                print(f"Default average: {default_avg} (abs error {default_avg_error})")
                print(
                    f"Agentic average: {agentic_avg_field.value} "
                    f"(abs error {abs(agentic_avg_field.value - expected_average)})"
                )
            finally:
                await client.delete_analyzer(default_id)
                await client.delete_analyzer(agentic_id)

        return variables
