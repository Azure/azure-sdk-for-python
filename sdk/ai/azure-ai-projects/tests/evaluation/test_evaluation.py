# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
    recorded_by_proxy,
    get_credential,
    set_bodiless_matcher,
)

from azure.ai.projects.models import Evaluation, Dataset, EvaluatorConfiguration
from evaluation_test_base import EvaluationsTestBase, servicePreparerEvaluationsTests


class TestEvaluation(EvaluationsTestBase):

    @servicePreparerEvaluationsTests()
    @recorded_by_proxy
    def test_evaluation_create(self, **kwargs):
        set_bodiless_matcher()
        default_aoai_connection_name = kwargs.pop("azure_ai_projects_evaluations_tests_default_aoai_connection_name")
        project_client = self.get_sync_client(**kwargs)
        default_aoai_connection = project_client.connections.get(connection_name=default_aoai_connection_name)
        deployment_name = kwargs.get("azure_ai_projects_evaluations_tests_deployment_name")
        api_version = kwargs.get("azure_ai_projects_evaluations_tests_api_version")
        dataset_id = kwargs.get("azure_ai_projects_evaluations_tests_dataset_id")

        evaluation = Evaluation(
            display_name="Remote Evaluation E2E Test",
            description="Evaluation of dataset using F1Score and Relevance evaluators",
            data=Dataset(id=dataset_id),
            evaluators={
                "f1_score": EvaluatorConfiguration(
                    id="azureml://registries/azureml-staging/models/F1Score-Evaluator/versions/3",
                ),
                "relevance": EvaluatorConfiguration(
                    id="azureml://registries/azureml-staging/models/Relevance-Evaluator/versions/3",
                    init_params={
                        "model_config": default_aoai_connection.to_evaluator_model_config(
                            deployment_name=deployment_name, api_version=api_version
                        )
                    },
                ),
            },
        )

        created_evaluation = project_client.evaluations.create(evaluation)

        assert created_evaluation.id is not None
        assert created_evaluation.display_name == "Remote Evaluation E2E Test"
        assert created_evaluation.description == "Evaluation of dataset using F1Score and Relevance evaluators"
        assert created_evaluation.evaluators is not None

        assert created_evaluation.evaluators["f1_score"] is not None
        assert created_evaluation.evaluators["f1_score"].id is not None

        assert created_evaluation.evaluators["relevance"] is not None
        assert created_evaluation.evaluators["relevance"].id is not None

        retrieved_evaluation = project_client.evaluations.get(created_evaluation.id)

        assert retrieved_evaluation.id == created_evaluation.id
        assert retrieved_evaluation.id is not None
        assert retrieved_evaluation.display_name == "Remote Evaluation E2E Test"
        assert retrieved_evaluation.description == "Evaluation of dataset using F1Score and Relevance evaluators"
        assert retrieved_evaluation.evaluators is not None

        assert retrieved_evaluation.evaluators["f1_score"] is not None
        assert retrieved_evaluation.evaluators["f1_score"].id is not None

        assert retrieved_evaluation.evaluators["relevance"] is not None
        assert retrieved_evaluation.evaluators["relevance"].id is not None

        # This failed with error : AttributeError: 'InputData' object has no attribute 'id' # TODO : Fix this
        # assert created_evaluation.data.id == dataset_id

    @servicePreparerEvaluationsTests()
    @recorded_by_proxy
    def test_model_config_from_default_connection(self, **kwargs):
        set_bodiless_matcher()
        default_aoai_connection_name = kwargs.pop("azure_ai_projects_evaluations_tests_default_aoai_connection_name")
        project_client = self.get_sync_client(**kwargs)
        default_aoai_connection = project_client.connections.get(
            connection_name=default_aoai_connection_name, include_credentials=True
        )
        deployment_name = kwargs.get("azure_ai_projects_evaluations_tests_deployment_name")
        api_version = kwargs.get("azure_ai_projects_evaluations_tests_api_version")
        model_config = default_aoai_connection.to_evaluator_model_config(
            deployment_name=deployment_name, api_version=api_version, include_credentials=True
        )
        assert model_config["api_key"] == default_aoai_connection.key
