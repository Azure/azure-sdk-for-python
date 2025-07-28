# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

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
        client = ConversationAuthoringClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_get_model_evaluation_summary(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "EmailApp"
        trained_model_label = "Model1"  # Replace with your actual trained model label

        trained_model_client = client.get_trained_model_client(project_name, trained_model_label)

        evaluation_summary = trained_model_client.get_model_evaluation_summary()

        assert evaluation_summary is not None

        # Entities evaluation summary
        entities_eval = evaluation_summary.entities_evaluation
        assert entities_eval is not None
        assert entities_eval.entities is not None
        assert entities_eval.micro_f1 is not None
        assert entities_eval.micro_precision is not None
        assert entities_eval.micro_recall is not None
        assert entities_eval.macro_f1 is not None
        assert entities_eval.macro_precision is not None
        assert entities_eval.macro_recall is not None

        for entity_key, entity_stats in entities_eval.entities.items():
            assert entity_key is not None
            assert entity_stats.f1 is not None
            assert entity_stats.precision is not None
            assert entity_stats.recall is not None
            assert entity_stats.true_positive_count is not None
            assert entity_stats.true_negative_count is not None
            assert entity_stats.false_positive_count is not None
            assert entity_stats.false_negative_count is not None

        # Intents evaluation summary
        intents_eval = evaluation_summary.intents_evaluation
        assert intents_eval is not None
        assert intents_eval.intents is not None
        assert intents_eval.micro_f1 is not None
        assert intents_eval.micro_precision is not None
        assert intents_eval.micro_recall is not None
        assert intents_eval.macro_f1 is not None
        assert intents_eval.macro_precision is not None
        assert intents_eval.macro_recall is not None

        for intent_key, intent_stats in intents_eval.intents.items():
            assert intent_key is not None
            assert intent_stats.f1 is not None
            assert intent_stats.precision is not None
            assert intent_stats.recall is not None
            assert intent_stats.true_positive_count is not None
            assert intent_stats.true_negative_count is not None
            assert intent_stats.false_positive_count is not None
            assert intent_stats.false_negative_count is not None