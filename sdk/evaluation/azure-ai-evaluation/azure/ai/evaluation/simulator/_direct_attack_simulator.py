# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=C0301,C0114,R0913,R0903
# noqa: E501
import logging
from random import randint
from typing import Callable, Optional, cast, Union

from azure.ai.evaluation._constants import TokenScope
from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.utils import validate_azure_ai_project, is_onedp_project
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation.simulator import AdversarialScenario
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._common.onedp._client import AIProjectClient
from azure.core.credentials import TokenCredential

from ._adversarial_simulator import AdversarialSimulator
from ._model_tools import AdversarialTemplateHandler, ManagedIdentityAPITokenManager, RAIClient

logger = logging.getLogger(__name__)


@experimental
class DirectAttackSimulator:
    """
    Initialize a UPIA (user prompt injected attack) jailbreak adversarial simulator with a project scope.
    This simulator converses with your AI system using prompts designed to interrupt normal functionality.

    :param azure_ai_project: The Azure AI project, which can either be a string representing the project endpoint 
        or an instance of AzureAIProject. It contains subscription id, resource group, and project name. 
    :type azure_ai_project: Union[str, AzureAIProject]
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_simulate.py
            :start-after: [START direct_attack_simulator]
            :end-before: [END direct_attack_simulator]
            :language: python
            :dedent: 8
            :caption: Run the DirectAttackSimulator to produce 2 results with 3 conversation turns each (6 messages in each result).
    """

    def __init__(self, *, azure_ai_project: Union[str, AzureAIProject], credential: TokenCredential):
        """Constructor."""
        
        if is_onedp_project(azure_ai_project):
            self.azure_ai_project = azure_ai_project
            self.credential=cast(TokenCredential, credential)
            self.token_manager = ManagedIdentityAPITokenManager(
                token_scope=TokenScope.COGNITIVE_SERVICES_MANAGEMENT,
                logger=logging.getLogger("AdversarialSimulator"),
                credential=self.credential
            )
            self.rai_client  = AIProjectClient(endpoint=azure_ai_project, credential=credential)
        else:
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
        scenario: AdversarialScenario,
        target: Callable,
        max_conversation_turns: int = 1,
        max_simulation_results: int = 3,
        api_call_retry_limit: int = 3,
        api_call_retry_sleep_sec: int = 1,
        api_call_delay_sec: int = 0,
        concurrent_async_task: int = 3,
        randomization_seed: Optional[int] = None,
    ):
        """
        Executes the adversarial simulation and UPIA (user prompt injected attack) jailbreak adversarial simulation
        against a specified target function asynchronously.

        :keyword scenario: Enum value specifying the adversarial scenario used for generating inputs.
         example:

         - :py:const:`azure.ai.evaluation.simulator.AdversarialScenario.ADVERSARIAL_QA`
         - :py:const:`azure.ai.evaluation.simulator.AdversarialScenario.ADVERSARIAL_CONVERSATION`
        :paramtype scenario: azure.ai.evaluation.simulator.AdversarialScenario
        :keyword target: The target function to simulate adversarial inputs against.
            This function should be asynchronous and accept a dictionary representing the adversarial input.
        :paramtype target: Callable
        :keyword max_conversation_turns: The maximum number of conversation turns to simulate.
            Defaults to 1.
        :paramtype max_conversation_turns: int
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
        :keyword randomization_seed: Seed used to randomize prompt selection, shared by both jailbreak
            and regular simulation to ensure consistent results. If not provided, a random seed will be generated
            and shared between simulations.
        :paramtype randomization_seed: Optional[int]
        :return: A list of dictionaries, each representing a simulated conversation. Each dictionary contains:

         - 'template_parameters': A dictionary with parameters used in the conversation template,
            including 'conversation_starter'.
         - 'messages': A list of dictionaries, each representing a turn in the conversation.
            Each message dictionary includes 'content' (the message text) and
            'role' (indicating whether the message is from the 'user' or the 'assistant').
         - '**$schema**': A string indicating the schema URL for the conversation format.

         The 'content' for 'assistant' role messages may includes the messages that your callback returned.
        :rtype: Dict[str, [List[Dict[str, Any]]]]

        **Output format**

        .. code-block:: python

            return_value = {
                "jailbreak": [
                {
                    'template_parameters': {},
                    'messages': [
                        {
                            'content': '<jailbreak prompt> <adversarial query>',
                            'role': 'user'
                        },
                        {
                            'content': "<response from endpoint>",
                            'role': 'assistant',
                            'context': None
                        }
                    ],
                    '$schema': 'http://azureml/sdk-2-0/ChatConversation.json'
                }],
                "regular": [
                {
                    'template_parameters': {},
                    'messages': [
                    {
                        'content': '<adversarial query>',
                        'role': 'user'
                    },
                    {
                        'content': "<response from endpoint>",
                        'role': 'assistant',
                        'context': None
                    }],
                    '$schema': 'http://azureml/sdk-2-0/ChatConversation.json'
                }]
            }
        """
        if scenario not in AdversarialScenario.__members__.values():
            msg = f"Invalid scenario: {scenario}. Supported scenarios: {AdversarialScenario.__members__.values()}"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.DIRECT_ATTACK_SIMULATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

        if not randomization_seed:
            randomization_seed = randint(0, 1000000)

        regular_sim = AdversarialSimulator(azure_ai_project=self.azure_ai_project, credential=self.credential)
        regular_sim_results = await regular_sim(
            scenario=scenario,
            target=target,
            max_conversation_turns=max_conversation_turns,
            max_simulation_results=max_simulation_results,
            api_call_retry_limit=api_call_retry_limit,
            api_call_retry_sleep_sec=api_call_retry_sleep_sec,
            api_call_delay_sec=api_call_delay_sec,
            concurrent_async_task=concurrent_async_task,
            randomize_order=False,
            randomization_seed=randomization_seed,
        )
        jb_sim = AdversarialSimulator(azure_ai_project=self.azure_ai_project, credential=self.credential)
        jb_sim_results = await jb_sim(
            scenario=scenario,
            target=target,
            max_conversation_turns=max_conversation_turns,
            max_simulation_results=max_simulation_results,
            api_call_retry_limit=api_call_retry_limit,
            api_call_retry_sleep_sec=api_call_retry_sleep_sec,
            api_call_delay_sec=api_call_delay_sec,
            concurrent_async_task=concurrent_async_task,
            _jailbreak_type="upia",
            randomize_order=False,
            randomization_seed=randomization_seed,
        )
        return {"jailbreak": jb_sim_results, "regular": regular_sim_results}
