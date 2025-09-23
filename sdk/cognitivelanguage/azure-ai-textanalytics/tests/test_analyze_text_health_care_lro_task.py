import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    AnalyzeTextOperationAction,
    HealthcareLROTask,
    HealthcareLROResult,
    TextActions,
)

from azure.core.credentials import AzureKeyCredential

TextAnalysisPreparer = functools.partial(
    EnvironmentVariableLoader,
    "text_analysis",
    text_analysis_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    text_analysis_key="fake_key",
)


class TestTextAnalysis(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = TextAnalysisClient(endpoint, credential)
        return client

    ...


class TestTextAnalysisCase(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy
    def test_analyze_text_health_care_lro_task(self, text_analysis_endpoint, text_analysis_key):
        client = self.create_client(text_analysis_endpoint, text_analysis_key)

        text_a = "Prescribed 100mg ibuprofen, taken twice daily."

        text_input = MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(id="A", text=text_a, language="en"),
            ]
        )

        actions: list[AnalyzeTextOperationAction] = [
            HealthcareLROTask(
                name="HealthcareOperationActionSample",
            ),
        ]

        # begin LRO (sync) – custom poller returns ItemPaged[TextActions]
        poller = client.begin_analyze_text_job(
            text_input=text_input,
            actions=actions,
        )

        assert poller is not None

        paged_actions = poller.result()
        details = poller.details
        assert "operation_id" in details
        assert details.get("status") is not None

        assert paged_actions is not None

        found_healthcare = False

        for actions_page in paged_actions:
            assert isinstance(actions_page, TextActions)
            # NOTE: Python property is items_property (wire name "items")
            assert actions_page.items_property is not None

            for op_result in actions_page.items_property:
                if isinstance(op_result, HealthcareLROResult):
                    found_healthcare = True
                    hc_result = op_result.results
                    assert hc_result is not None
                    assert hc_result.documents is not None

                    for doc in hc_result.documents:
                        assert doc.id is not None
                        assert doc.entities is not None
                        assert doc.relations is not None

                        for entity in doc.entities:
                            assert entity is not None
                            assert entity.text is not None
                            assert entity.category is not None
                            assert entity.offset is not None
                            assert entity.length is not None
                            assert entity.confidence_score is not None

                            if entity.links is not None:
                                for link in entity.links:
                                    assert link is not None
                                    assert link.id is not None
                                    assert link.data_source is not None

                        for relation in doc.relations:
                            assert relation is not None
                            assert relation.relation_type is not None
                            assert relation.entities is not None
                            for rel_entity in relation.entities:
                                assert rel_entity.role is not None
                                assert rel_entity.ref is not None

        assert found_healthcare, "Expected a HealthcareLROResult in TextActions.items_property"
