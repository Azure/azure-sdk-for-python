# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# flake8: noqa: F401
# flake8: noqa: F841


import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call, ANY

import pytest

from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator


@pytest.fixture()
def async_callback():
    async def callback(x):
        return x
    return callback


@pytest.mark.unittest
class TestSimulator:
    @patch("azure.ai.evaluation.simulator._model_tools._rai_client.RAIClient._get_service_discovery_url")
    @patch(
        "azure.ai.evaluation.simulator._model_tools.AdversarialTemplateHandler._get_content_harm_template_collections"
    )
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator._simulate_async")
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator._ensure_service_dependencies")
    def test_initialization_with_all_valid_scenarios(
        self,
        mock_ensure_service_dependencies,
        mock_get_content_harm_template_collections,
        mock_simulate_async,
        mock_get_service_discovery_url,
        azure_cred,
    ):
        mock_get_service_discovery_url.return_value = "http://some.url/discovery/"
        mock_simulate_async.return_value = MagicMock()
        mock_get_content_harm_template_collections.return_value = [
            Mock(template_parameters=["param1"]),
            Mock(template_parameters=["param2"]),
            Mock(template_parameters=["param3"]),
            Mock(template_parameters=["param4"]),
            Mock(template_parameters=["param5"]),
            Mock(template_parameters=["param6"]),
            Mock(template_parameters=["param7"]),
        ]
        mock_ensure_service_dependencies.return_value = True
        azure_ai_project = {
            "subscription_id": "test_subscription",
            "resource_group_name": "test_resource_group",
            "project_name": "test_workspace",
        }
        available_scenarios = [
            AdversarialScenario.ADVERSARIAL_CONVERSATION,
            AdversarialScenario.ADVERSARIAL_QA,
            AdversarialScenario.ADVERSARIAL_SUMMARIZATION,
            AdversarialScenario.ADVERSARIAL_SEARCH,
            AdversarialScenario.ADVERSARIAL_REWRITE,
            AdversarialScenario.ADVERSARIAL_CONTENT_GEN_UNGROUNDED,
            AdversarialScenario.ADVERSARIAL_CONTENT_GEN_GROUNDED,
        ]
        for scenario in available_scenarios:
            simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)
            assert callable(simulator)

    @patch("azure.ai.evaluation.simulator._model_tools._rai_client.RAIClient._get_service_discovery_url")
    @patch(
        "azure.ai.evaluation.simulator._model_tools.AdversarialTemplateHandler._get_content_harm_template_collections"
    )
    def test_simulator_raises_validation_error_with_unsupported_scenario(
        self, _get_content_harm_template_collections, _get_service_discovery_url, azure_cred, async_callback
    ):
        _get_content_harm_template_collections.return_value = [
            Mock(template_parameters=["param1"]),
            Mock(template_parameters=["param2"]),
        ]
        _get_service_discovery_url.return_value = "some-url"
        azure_ai_project = {
            "subscription_id": "test_subscription",
            "resource_group_name": "test_resource_group",
            "project_name": "test_workspace",
        }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)
        with pytest.raises(EvaluationException):
            asyncio.run(
                simulator(
                    scenario="unknown-scenario",
                    max_conversation_turns=1,
                    max_simulation_results=3,
                    target=async_callback,  # Pass the fixture directly
                )
            )

    @patch("azure.ai.evaluation.simulator._model_tools._rai_client.RAIClient._get_service_discovery_url")
    @patch(
        "azure.ai.evaluation.simulator._model_tools.AdversarialTemplateHandler._get_content_harm_template_collections"
    )
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator._simulate_async")
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator._ensure_service_dependencies")
    def test_initialization_parity_with_evals(
        self,
        mock_ensure_service_dependencies,
        mock_get_content_harm_template_collections,
        mock_simulate_async,
        mock_get_service_discovery_url,
    ):
        mock_get_service_discovery_url.return_value = "http://some.url/discovery/"
        mock_simulate_async.return_value = MagicMock()
        mock_get_content_harm_template_collections.return_value = [
            Mock(template_parameters=["param1"]),
            Mock(template_parameters=["param2"]),
            Mock(template_parameters=["param3"]),
            Mock(template_parameters=["param4"]),
            Mock(template_parameters=["param5"]),
            Mock(template_parameters=["param6"]),
            Mock(template_parameters=["param7"]),
        ]
        azure_ai_project = {
            "subscription_id": "test_subscription",
            "resource_group_name": "test_resource_group",
            "project_name": "test_workspace",
        }
        available_scenarios = [
            AdversarialScenario.ADVERSARIAL_CONVERSATION,
            AdversarialScenario.ADVERSARIAL_QA,
            AdversarialScenario.ADVERSARIAL_SUMMARIZATION,
            AdversarialScenario.ADVERSARIAL_SEARCH,
            AdversarialScenario.ADVERSARIAL_REWRITE,
            AdversarialScenario.ADVERSARIAL_CONTENT_GEN_UNGROUNDED,
            AdversarialScenario.ADVERSARIAL_CONTENT_GEN_GROUNDED,
        ]
        for scenario in available_scenarios:
            simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential="test_credential")
            assert callable(simulator)

    @patch("azure.ai.evaluation.simulator._model_tools._rai_client.RAIClient._get_service_discovery_url")
    @patch(
        "azure.ai.evaluation.simulator._model_tools.AdversarialTemplateHandler._get_content_harm_template_collections"
    )
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator._simulate_async")
    def test_simulate_with_valid_scenario_and_max_conversation_turns(
        self,
        mock_simulate_async,
        _get_content_harm_template_collections,
        _get_service_discovery_url,
        async_callback,
        azure_cred
    ):
        _get_service_discovery_url.return_value = "http://some.url/discovery/"
        _get_content_harm_template_collections.return_value = [
            Mock(template_parameters=["param1"]),
            Mock(template_parameters=["param2"])
        ]
        mock_simulate_async.return_value = [
            Mock(template_parameters=["param1", "param2"]),
            Mock(template_parameters=["param3"])
        ]

        azure_ai_project = {
            "subscription_id": "test_subscription",
            "resource_group_name": "test_resource_group",
            "project_name": "test_workspace",
        }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)
        asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
                max_conversation_turns=5,
                max_simulation_results=10,
                target=async_callback,  # Pass the fixture directly
            )
        )

        assert mock_simulate_async.call_count == 2  # Expecting 2 calls due to 2 templates

    @patch("azure.ai.evaluation.simulator._model_tools._rai_client.RAIClient._get_service_discovery_url")
    @patch(
        "azure.ai.evaluation.simulator._model_tools.AdversarialTemplateHandler._get_content_harm_template_collections"
    )
    def test_simulate_async_with_invalid_target_type(
        self, _get_content_harm_template_collections, _get_service_discovery_url, azure_cred
    ):
        _get_content_harm_template_collections.return_value = [
            Mock(template_parameters=["param1"]),
            Mock(template_parameters=["param2"])
        ]
        _get_service_discovery_url.return_value = "http://some.url/discovery/"

        azure_ai_project = {
            "subscription_id": "test_subscription",
            "resource_group_name": "test_resource_group",
            "project_name": "test_workspace",
        }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        with pytest.raises(AttributeError):
            asyncio.run(
                simulator(
                    scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
                    max_conversation_turns=5,
                    max_simulation_results=10,
                    target="not_async_callback"  # Should be a Callable
                )
            )

    @patch("azure.ai.evaluation.simulator._model_tools._rai_client.RAIClient._get_service_discovery_url")
    @patch(
        "azure.ai.evaluation.simulator._model_tools.AdversarialTemplateHandler._get_content_harm_template_collections"
    )
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator._simulate_async")
    def test_simulate_async_with_error(
        self,
        mock_simulate_async,
        _get_content_harm_template_collections,
        _get_service_discovery_url,
        async_callback,
        azure_cred
    ):
        _get_service_discovery_url.return_value = "http://some.url/discovery/"
        _get_content_harm_template_collections.return_value = [
            Mock(template_parameters=["param1"]),
            Mock(template_parameters=["param2"])
        ]
        mock_simulate_async.side_effect = EvaluationException("Simulate error")

        azure_ai_project = {
            "subscription_id": "test_subscription",
            "resource_group_name": "test_resource_group",
            "project_name": "test_workspace",
        }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        with pytest.raises(EvaluationException):
            asyncio.run(
                simulator(
                    scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
                    max_conversation_turns=5,
                    max_simulation_results=10,
                    target=async_callback  # Pass the fixture directly
                )
            )

        # Ensure _simulate_async was called twice
        assert mock_simulate_async.call_count == 2

        # Verify 'scenario', 'template', and 'target' in each call
        for call_args in mock_simulate_async.call_args_list:
            assert call_args.kwargs['scenario'] == AdversarialScenario.ADVERSARIAL_CONVERSATION
            assert call_args.kwargs['target'] == async_callback
            assert call_args.kwargs['template'] in _get_content_harm_template_collections.return_value