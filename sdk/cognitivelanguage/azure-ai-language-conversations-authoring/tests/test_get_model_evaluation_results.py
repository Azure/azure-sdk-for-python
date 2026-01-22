# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import StringIndexType

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsGetModelEvaluationResultsSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_get_model_evaluation_results(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "EmailApp"
        trained_model_label = "Model1"

        # Get trained-model scoped client and fetch the paged evaluation results
        project_client = authoring_client.get_project_client(project_name)
        results = project_client.trained_model.get_model_evaluation_results(
            trained_model_label=trained_model_label, string_index_type="Utf16CodeUnit"
        )

        # Iterate and print like the C# sample
        seen = 0
        for r in results:
            seen += 1
            print(f"Text: {getattr(r, 'text', None)}")
            print(f"Language: {getattr(r, 'language', None)}")

            intents_result = getattr(r, "intents_result", None)
            if intents_result:
                print(f"Expected Intent: {getattr(intents_result, 'expected_intent', None)}")
                print(f"Predicted Intent: {getattr(intents_result, 'predicted_intent', None)}")

            entities_result = getattr(r, "entities_result", None)
            if entities_result:
                expected_entities = getattr(entities_result, "expected_entities", []) or []
                print("Expected Entities:")
                for ent in expected_entities:
                    print(
                        f" - Category: {getattr(ent, 'category', None)}, Offset: {getattr(ent, 'offset', None)}, Length: {getattr(ent, 'length', None)}"
                    )

                predicted_entities = getattr(entities_result, "predicted_entities", []) or []
                print("Predicted Entities:")
                for ent in predicted_entities:
                    print(
                        f" - Category: {getattr(ent, 'category', None)}, Offset: {getattr(ent, 'offset', None)}, Length: {getattr(ent, 'length', None)}"
                    )

                print()

        # Basic assertion that call succeeded (pageable iterated, possibly empty)
        assert results is not None
