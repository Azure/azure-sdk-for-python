# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.text import TextAnalysisClient
from azure.ai.language.text.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    AbstractiveSummarizationOperationAction
)

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="fake_resource.servicebus.windows.net/",
    authoring_key="fake_key",
)

class TestConversations(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = TextAnalysisClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_create_project(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)
        textA = "xxxx"
        # Prepare input
        multi_language_text_input = MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(id="A", text=textA, language="en")
            ]
        )

        # Define the action
        actions = [
            AbstractiveSummarizationOperationAction(
                name="AbstractiveSummarizationOperationActionSample"
            )
        ]

        # Submit operation
        poller = client.begin_analyze_text_job(
            text_input=multi_language_text_input,
            actions=actions,
        )
        result = poller.result()
        
        # Iterate over action results
        for action_result in result.actions:
            if isinstance(action_result, AbstractiveSummarizationOperationAction):
                abstractive_result = action_result.results

                # Summaries
                for document in abstractive_result.documents:
                    print(f'Result for document with Id = "{document.id}":')
                    print("  Produced the following abstractive summaries:\n")
                    for summary in document.summaries:
                        print(f"  Text: {summary.text.replace('\\n', ' ')}")
                        print("  Contexts:")
                        for context in summary.contexts:
                            print(f"    Offset: {context.offset}")
                            print(f"    Length: {context.length}")
                    print()

                # Errors
                for error in abstractive_result.errors:
                    print(f"  Error in document: {error.id}!")
                    print(f"  Document error: {error.error}")