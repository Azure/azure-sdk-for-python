# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
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
        entities_summary = eval_summary.entities_evaluation
        if entities_summary is not None:
            print(
                f"Entities - Micro F1: {entities_summary.micro_f1}, "
                f"Micro Precision: {entities_summary.micro_precision}, "
                f"Micro Recall: {entities_summary.micro_recall}"
            )
            print(
                f"Entities - Macro F1: {entities_summary.macro_f1}, "
                f"Macro Precision: {entities_summary.macro_precision}, "
                f"Macro Recall: {entities_summary.macro_recall}"
            )

            # Per-entity details
            ent_map = entities_summary.entities or {}
            for name, summary in ent_map.items():
                print(f"Entity '{name}': F1 = {summary.f1}, Precision = {summary.precision}, Recall = {summary.recall}")
                print(
                    f"  True Positives: {summary.true_positive_count}, "
                    f"True Negatives: {summary.true_negative_count}"
                )
                print(
                    f"  False Positives: {summary.false_positive_count}, "
                    f"False Negatives: {summary.false_negative_count}"
                )

        # ----- Intents evaluation (micro/macro) -----
        intents_summary = eval_summary.intents_evaluation
        if intents_summary is not None:
            print(
                f"Intents - Micro F1: {intents_summary.micro_f1}, "
                f"Micro Precision: {intents_summary.micro_precision}, "
                f"Micro Recall: {intents_summary.micro_recall}"
            )
            print(
                f"Intents - Macro F1: {intents_summary.macro_f1}, "
                f"Macro Precision: {intents_summary.macro_precision}, "
                f"Macro Recall: {intents_summary.macro_recall}"
            )

            # Per-intent details
            intent_map = intents_summary.intents or {}
            for name, summary in intent_map.items():
                print(f"Intent '{name}': F1 = {summary.f1}, Precision = {summary.precision}, Recall = {summary.recall}")
                print(
                    f"  True Positives: {summary.true_positive_count}, "
                    f"True Negatives: {summary.true_negative_count}"
                )
                print(
                    f"  False Positives: {summary.false_positive_count}, "
                    f"False Negatives: {summary.false_negative_count}"
                )
