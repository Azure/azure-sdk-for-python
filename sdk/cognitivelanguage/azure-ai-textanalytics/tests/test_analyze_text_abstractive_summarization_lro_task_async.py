import functools
import pytest

from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    AbstractiveSummarizationOperationAction,
    TextActions,
    AbstractiveSummarizationOperationResult,
    AbstractiveSummaryActionResult,
    AbstractiveSummary,
    SummaryContext,
)

TextAnalysisPreparer = functools.partial(
    EnvironmentVariableLoader,
    "text_analysis",
    text_analysis_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    text_analysis_key="fake_key",
)


class TestTextAnalysisAsync(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAnalysisClient:
        return TextAnalysisClient(endpoint, AzureKeyCredential(key))


class TestTextAnalysisCaseAsync(TestTextAnalysisAsync):
    @TextAnalysisPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_analyze_text_abstractive_summarization_lro_task_async(
        self, text_analysis_endpoint, text_analysis_key
    ):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:
            text_a = (
                "Windows 365 was in the works before COVID-19 sent companies around the world on a scramble to secure "
                "solutions to support employees suddenly forced to work from home, but “what really put the "
                "firecracker behind it was the pandemic, it accelerated everything,” McKelvey said. She explained "
                "that customers were asking, “How do we create an experience for people that makes them still feel "
                "connected to the company without the physical presence of being there?” In this new world of "
                "Windows 365, remote workers flip the lid on their laptop, boot up the family workstation or clip a "
                "keyboard onto a tablet, launch a native app or modern web browser and login to their Windows 365 "
                "account. From there, their Cloud PC appears with their background, apps, settings and content just "
                "as they left it when they last were last there – in the office, at home or a coffee shop. And "
                "then, when you’re done, you’re done. You won’t have any issues around security because you’re not "
                "saving anything on your device,” McKelvey said, noting that all the data is stored in the cloud. "
                "The ability to login to a Cloud PC from anywhere on any device is part of Microsoft’s larger "
                "strategy around tailoring products such as Microsoft Teams and Microsoft 365 for the post-pandemic "
                "hybrid workforce of the future, she added. It enables employees accustomed to working from home to "
                "continue working from home; it enables companies to hire interns from halfway around the world; it "
                "allows startups to scale without requiring IT expertise. “I think this will be interesting for "
                "those organizations who, for whatever reason, have shied away from virtualization. This is giving "
                "them an opportunity to try it in a way that their regular, everyday endpoint admin could manage,” "
                "McKelvey said. The simplicity of Windows 365 won over Dean Wells, the corporate chief information "
                "officer for the Government of Nunavut. His team previously attempted to deploy a traditional "
                "virtual desktop infrastructure and found it inefficient and unsustainable given the limitations of "
                "low-bandwidth satellite internet and the constant need for IT staff to manage the network and "
                "infrastructure. We didn’t run it for very long,” he said. “It didn’t turn out the way we had "
                "hoped. So, we actually had terminated the project and rolled back out to just regular PCs.” He "
                "re-evaluated this decision after the Government of Nunavut was hit by a ransomware attack in "
                "November 2019 that took down everything from the phone system to the government’s servers. "
                "Microsoft helped rebuild the system, moving the government to Teams, SharePoint, OneDrive and "
                "Microsoft 365. Manchester’s team recruited the Government of Nunavut to pilot Windows 365. Wells "
                "was intrigued, especially by the ability to manage the elastic workforce securely and seamlessly. "
                "“The impact that I believe we are finding, and the impact that we’re going to find going forward, "
                "is being able to access specialists from outside the territory and organizations outside the "
                "territory to come in and help us with our projects, being able to get people on staff with us to "
                "help us deliver the day-to-day expertise that we need to run the government,” he said. “Being able "
                "to improve healthcare, being able to improve education, economic development is going to improve "
                "the quality of life in the communities.”"
            )

            text_input = MultiLanguageTextInput(
                multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
            )

            poller = await client.begin_analyze_text_job(
                text_input=text_input,
                actions=[
                    AbstractiveSummarizationOperationAction(
                        name="AbsractiveSummarizationOperationActionSample",
                    )
                ],
            )

            assert poller is not None

            paged_actions = await poller.result()
            details = poller.details
            assert "operation_id" in details
            assert details.get("status") is not None
            assert paged_actions is not None

            found_abstractive = False

            async for actions_page in paged_actions:
                # Page container holding job results
                assert isinstance(actions_page, TextActions)
                assert actions_page.items_property is not None  # wire: "items"

                for op_result in actions_page.items_property:
                    if isinstance(op_result, AbstractiveSummarizationOperationResult):
                        found_abstractive = True
                        result = op_result.results
                        assert result is not None
                        assert result.documents is not None

                        for doc in result.documents:
                            assert isinstance(doc, AbstractiveSummaryActionResult)
                            assert doc.id is not None
                            assert doc.summaries is not None

                            for summary in doc.summaries:
                                assert isinstance(summary, AbstractiveSummary)
                                assert summary.text is not None

                                # contexts may be optional
                                if summary.contexts is not None:
                                    for ctx in summary.contexts:
                                        assert isinstance(ctx, SummaryContext)
                                        assert ctx.offset is not None
                                        assert ctx.length is not None

            assert (
                found_abstractive
            ), "Expected an AbstractiveSummarizationOperationResult in TextActions.items_property"
