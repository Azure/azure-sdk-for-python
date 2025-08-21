# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsGetModelEvaluationSummarySync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_get_model_evaluation_summary(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "EmailApp"
        trained_model_label = "Model1"

        # Get trained-model scoped client and fetch the evaluation summary
        project_client = authoring_client.get_project_client(project_name)
        eval_summary = project_client.trained_model.get_model_evaluation_summary(trained_model_label)

        # Basic assertion the call returned something shaped like a summary
        assert eval_summary is not None

        # ----- Entities evaluation (micro/macro) -----
        entities_eval = getattr(eval_summary, "entities_evaluation", None)
        if entities_eval:
            print(f"Entities - Micro F1: {getattr(entities_eval, 'micro_f1', None)}, Micro Precision: {getattr(entities_eval, 'micro_precision', None)}, Micro Recall: {getattr(entities_eval, 'micro_recall', None)}")
            print(f"Entities - Macro F1: {getattr(entities_eval, 'macro_f1', None)}, Macro Precision: {getattr(entities_eval, 'macro_precision', None)}, Macro Recall: {getattr(entities_eval, 'macro_recall', None)}")

            # Per-entity details
            ent_map = getattr(entities_eval, "entities", {}) or {}
            for name, summary in ent_map.items():
                print(f"Entity '{name}': F1 = {getattr(summary, 'f1', None)}, Precision = {getattr(summary, 'precision', None)}, Recall = {getattr(summary, 'recall', None)}")
                print(f"  True Positives: {getattr(summary, 'true_positive_count', None)}, True Negatives: {getattr(summary, 'true_negative_count', None)}")
                print(f"  False Positives: {getattr(summary, 'false_positive_count', None)}, False Negatives: {getattr(summary, 'false_negative_count', None)}")

        # ----- Intents evaluation (micro/macro) -----
        intents_eval = getattr(eval_summary, "intents_evaluation", None)
        if intents_eval:
            print(f"Intents - Micro F1: {getattr(intents_eval, 'micro_f1', None)}, Micro Precision: {getattr(intents_eval, 'micro_precision', None)}, Micro Recall: {getattr(intents_eval, 'micro_recall', None)}")
            print(f"Intents - Macro F1: {getattr(intents_eval, 'macro_f1', None)}, Macro Precision: {getattr(intents_eval, 'macro_precision', None)}, Macro Recall: {getattr(intents_eval, 'macro_recall', None)}")

            # Per-intent details
            intent_map = getattr(intents_eval, "intents", {}) or {}
            for name, summary in intent_map.items():
                print(f"Intent '{name}': F1 = {getattr(summary, 'f1', None)}, Precision = {getattr(summary, 'precision', None)}, Recall = {getattr(summary, 'recall', None)}")
                print(f"  True Positives: {getattr(summary, 'true_positive_count', None)}, True Negatives: {getattr(summary, 'true_negative_count', None)}")
                print(f"  False Positives: {getattr(summary, 'false_positive_count', None)}, False Negatives: {getattr(summary, 'false_negative_count', None)}")
