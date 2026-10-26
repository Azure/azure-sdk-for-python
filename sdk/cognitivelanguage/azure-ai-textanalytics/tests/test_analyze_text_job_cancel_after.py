# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import functools

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextOperationState,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiEntityRecognitionOperationResult,
    PiiLROTask,
    TextActions,
)


def deserialize_job_state(pipeline_response, _, __):
    return AnalyzeTextOperationState(pipeline_response.http_response.json())


TextAnalysisPreparer = functools.partial(
    PowerShellPreparer,
    "text_analysis",
    text_analysis_endpoint="https://Sanitized.cognitiveservices.azure.com/",
)


class TestTextAnalysis(AzureRecordedTestCase):
    def create_client(self, endpoint: str) -> TextAnalysisClient:
        credential = self.get_credential(TextAnalysisClient)
        return self.create_client_from_credential(
            TextAnalysisClient,
            credential=credential,
            endpoint=endpoint,
        )


class TestTextAnalysisCase(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy
    def test_analyze_text_job_cancel_after(self, text_analysis_endpoint):
        client = self.create_client(text_analysis_endpoint)
        text_input = MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(
                    id="1",
                    text="My name is John Doe. My SSN is 123-45-6789.",
                    language="en",
                ),
                MultiLanguageInput(
                    id="2",
                    text="Contact Jane Doe at jane@example.com.",
                    language="en",
                ),
            ]
        )

        poller = client.begin_analyze_text_job(
            text_input=text_input,
            actions=[PiiLROTask(name="PiiWithCancelAfter")],
            cancel_after=30,
            cls=deserialize_job_state,
        )

        job_state = poller.result()
        assert job_state.status == "succeeded"
        assert isinstance(job_state.actions, TextActions)
        assert job_state.actions.items_property is not None

        pii_results = [
            result
            for result in job_state.actions.items_property
            if isinstance(result, PiiEntityRecognitionOperationResult)
        ]
        assert len(pii_results) == 1
        assert len(pii_results[0].results.documents) == 2
        assert all(document.entities for document in pii_results[0].results.documents)
