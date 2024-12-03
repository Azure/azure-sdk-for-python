# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=C0301,C0114,R0913,R0903
# noqa: E501
import asyncio
import logging
from typing import Callable, cast

from tqdm import tqdm

from azure.ai.evaluation._common.utils import validate_azure_ai_project
from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation.simulator import AdversarialScenarioJailbreak, SupportedLanguages
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.core.credentials import TokenCredential

from ._adversarial_simulator import AdversarialSimulator, JsonLineList

from ._model_tools import AdversarialTemplateHandler, ManagedIdentityAPITokenManager, RAIClient, TokenScope

logger = logging.getLogger(__name__)


@experimental
class IndirectAttackSimulator(AdversarialSimulator):
    """
    Initializes the XPIA (cross domain prompt injected attack) jailbreak adversarial simulator with a project scope.

    :param azure_ai_project: The scope of the Azure AI project. It contains subscription id, resource group, and project
        name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_simulate.py
            :start-after: [START indirect_attack_simulator]
            :end-before: [END indirect_attack_simulator]
            :language: python
            :dedent: 8
            :caption: Run the IndirectAttackSimulator to produce 1 result with 1 conversation turn (2 messages in the result).
    """

    def __init__(self, *, azure_ai_project: AzureAIProject, credential: TokenCredential):
        """Constructor."""

        try:
            self.azure_ai_project = validate_azure_ai_project(azure_ai_project)
        except EvaluationException as e:
            raise EvaluationException(
                message=e.message,
                internal_message=e.internal_message,
                target=ErrorTarget.DIRECT_ATTACK_SIMULATOR,
                category=e.category,
                blame=e.blame,
            ) from e

        self.credential = cast(TokenCredential, credential)
        self.token_manager = ManagedIdentityAPITokenManager(
            token_scope=TokenScope.DEFAULT_AZURE_MANAGEMENT,
            logger=logging.getLogger("AdversarialSimulator"),
            credential=self.credential,
        )
        self.rai_client = RAIClient(azure_ai_project=self.azure_ai_project, token_manager=self.token_manager)
        self.adversarial_template_handler = AdversarialTemplateHandler(
            azure_ai_project=self.azure_ai_project, rai_client=self.rai_client
        )
        super().__init__(azure_ai_project=azure_ai_project, credential=credential)

    def _ensure_service_dependencies(self):
        if self.rai_client is None:
            msg = "RAI service is required for simulation, but an RAI client was not provided."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.ADVERSARIAL_SIMULATOR,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )

    async def __call__(
        self,
        *,
        target: Callable,
        max_simulation_results: int = 3,
        api_call_retry_limit: int = 3,
        api_call_retry_sleep_sec: int = 1,
        api_call_delay_sec: int = 0,
        concurrent_async_task: int = 3,
        **kwargs,
    ):
        """
        Initializes the XPIA (cross domain prompt injected attack) jailbreak adversarial simulator with a project scope.
        This simulator converses with your AI system using prompts injected into the context to interrupt normal
        expected functionality by eliciting manipulated content, intrusion and attempting to gather information outside
        the scope of your AI system.
        :keyword target: The target function to simulate adversarial inputs against.
            This function should be asynchronous and accept a dictionary representing the adversarial input.
        :paramtype target: Callable
        :keyword max_simulation_results: The maximum number of simulation results to return.
            Defaults to 3.
        :paramtype max_simulation_results: int
        :keyword api_call_retry_limit: The maximum number of retries for each API call within the simulation.
            Defaults to 3.
        :paramtype api_call_retry_limit: int
        :keyword api_call_retry_sleep_sec: The sleep duration (in seconds) between retries for API calls.
            Defaults to 1 second.
        :paramtype api_call_retry_sleep_sec: int
        :keyword api_call_delay_sec: The delay (in seconds) before making an API call.
            This can be used to avoid hitting rate limits. Defaults to 0 seconds.
        :paramtype api_call_delay_sec: int
        :keyword concurrent_async_task: The number of asynchronous tasks to run concurrently during the simulation.
            Defaults to 3.
        :paramtype concurrent_async_task: int
        :return: A list of dictionaries, each representing a simulated conversation. Each dictionary contains:

         - 'template_parameters': A dictionary with parameters used in the conversation template,
            including 'conversation_starter'.
         - 'messages': A list of dictionaries, each representing a turn in the conversation.
            Each message dictionary includes 'content' (the message text) and
            'role' (indicating whether the message is from the 'user' or the 'assistant').
         - '**$schema**': A string indicating the schema URL for the conversation format.

         The 'content' for 'assistant' role messages may includes the messages that your callback returned.
        :rtype: List[Dict[str, Any]]

        **Output format**

        .. code-block:: python

            return_value = [
                {
                    'template_parameters': {},
                    'messages': [
                        {
                            'content': '<adversarial query>',
                            'role': 'user'
                        },
                        {
                            'content': "<response from your callback>",
                            'role': 'assistant',
                            'context': None
                        }
                    ],
                    '$schema': 'http://azureml/sdk-2-0/ChatConversation.json'
                }]
            }
        """
        # values that cannot be changed:
        scenario = AdversarialScenarioJailbreak.ADVERSARIAL_INDIRECT_JAILBREAK
        max_conversation_turns = 2
        language = SupportedLanguages.English
        self._ensure_service_dependencies()
        templates = await self.adversarial_template_handler._get_content_harm_template_collections(scenario.value)
        concurrent_async_task = min(concurrent_async_task, 1000)
        semaphore = asyncio.Semaphore(concurrent_async_task)
        sim_results = []
        tasks = []
        total_tasks = sum(len(t.template_parameters) for t in templates)
        if max_simulation_results > total_tasks:
            logger.warning(
                "Cannot provide %s results due to maximum number of adversarial simulations that can be generated: %s."
                "\n %s simulations will be generated.",
                max_simulation_results,
                total_tasks,
                total_tasks,
            )
        total_tasks = min(total_tasks, max_simulation_results)
        progress_bar = tqdm(
            total=total_tasks,
            desc="generating jailbreak simulations",
            ncols=100,
            unit="simulations",
        )
        for template in templates:
            for parameter in template.template_parameters:
                tasks.append(
                    asyncio.create_task(
                        self._simulate_async(
                            target=target,
                            template=template,
                            parameters=parameter,
                            max_conversation_turns=max_conversation_turns,
                            api_call_retry_limit=api_call_retry_limit,
                            api_call_retry_sleep_sec=api_call_retry_sleep_sec,
                            api_call_delay_sec=api_call_delay_sec,
                            language=language,
                            semaphore=semaphore,
                            scenario=scenario,
                        )
                    )
                )
                if len(tasks) >= max_simulation_results:
                    break
            if len(tasks) >= max_simulation_results:
                break
        for task in asyncio.as_completed(tasks):
            completed_task = await task  # type: ignore
            template_parameters = completed_task.get("template_parameters", {})  # type: ignore
            xpia_attack_type = template_parameters.get("xpia_attack_type", "")  # type: ignore
            action = template_parameters.get("action", "")  # type: ignore
            document_type = template_parameters.get("document_type", "")  # type: ignore
            sim_results.append(
                {
                    "messages": completed_task["messages"],  # type: ignore
                    "$schema": "http://azureml/sdk-2-0/ChatConversation.json",
                    "template_parameters": {
                        "metadata": {
                            "xpia_attack_type": xpia_attack_type,
                            "action": action,
                            "document_type": document_type,
                        },
                    },
                }
            )
            progress_bar.update(1)
        progress_bar.close()
        return JsonLineList(sim_results)
