# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# type: ignore
# flake8: noqa
# noqa: E501
# pylint: disable=E0401,E0611
import asyncio
import logging
import random
import time
import itertools
from jinja2 import Template, TemplateSyntaxError, TemplateAssertionError
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from tqdm import tqdm
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import get_async_http_client
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation.simulator import AdversarialScenario
from azure.ai.evaluation.simulator._adversarial_scenario import _UnstableAdversarialScenario
from azure.core.pipeline.policies import AsyncRetryPolicy, RetryMode
from azure.identity import DefaultAzureCredential
from ._constants import SupportedLanguages
from ._conversation import CallbackConversationBot, ConversationBot, ConversationRole, ConversationTurn
from ._model_tools import (
    AdversarialTemplateHandler,
    ManagedIdentityAPITokenManager,
    ProxyChatCompletionsModel,
    RAIClient,
    TokenScope,
)
from ._utils import JsonLineList
from ._pyrit_strategies import BasePyritStrategy

logger = logging.getLogger(__name__)

def _setup_logger():
    """Configure and return a logger instance for the CustomAdversarialSimulator.

    :return: The logger instance.
    :rtype: logging.Logger
    """
    log_filename = datetime.now().strftime("%Y_%m_%d__%H_%M.log")
    logger = logging.getLogger("CustomAdversarialSimulatorLogger")
    logger.setLevel(logging.DEBUG)  
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class CustomAdversarialSimulator:
    def __init__(self, *, azure_ai_project: AzureAIProject, credential=None):
        """Initialize the CustomAdversarialSimulator.

        :keyword azure_ai_project: An AzureAIProject object or dict with required keys 
         ("subscription_id", "resource_group_name", "project_name").
        :paramtype azure_ai_project: azure.ai.evaluation._model_configurations.AzureAIProject
        :keyword credential: A credential object or None. Defaults to DefaultAzureCredential if absent.
        :paramtype credential: Any
        """
        self._validate_azure_ai_project(azure_ai_project=azure_ai_project)
        credential = self._get_credential(azure_ai_project=azure_ai_project, credential=credential)
        self.azure_ai_project = azure_ai_project
        self.token_manager = ManagedIdentityAPITokenManager(
            token_scope=TokenScope.DEFAULT_AZURE_MANAGEMENT,
            logger=logging.getLogger("AdversarialSimulator"),
            credential=credential,  # type: ignore
        )
        self.rai_client = RAIClient(azure_ai_project=azure_ai_project, token_manager=self.token_manager)
        self.adversarial_template_handler = AdversarialTemplateHandler(
            azure_ai_project=azure_ai_project, rai_client=self.rai_client
        )
        self.logger = _setup_logger()

    def _get_credential(self, *, azure_ai_project, credential):
        """Retrieve the credential from azure_ai_project or return DefaultAzureCredential if none found.

        :keyword azure_ai_project: Config dictionary or object containing a possible credential key.
        :paramtype azure_ai_project: azure.ai.evaluation._model_configurations.AzureAIProject
        :keyword credential: A manually provided credential or None.
        :paramtype credential: Any
        :return: A valid credential for the simulator.
        :rtype: Any
        """
        if "credential" in azure_ai_project:
            return azure_ai_project["credential"]
        return credential or DefaultAzureCredential()

    def _validate_azure_ai_project(self, *, azure_ai_project):
        """Validate that azure_ai_project has required keys and they are non-empty.

        :keyword azure_ai_project: Object or dict with "subscription_id", "resource_group_name", and "project_name".
        :paramtype azure_ai_project: azure.ai.evaluation._model_configurations.AzureAIProject
        :raises EvaluationException: If any required keys are missing or empty.
        """
        required_keys = ["subscription_id", "resource_group_name", "project_name"]
        if not all(key in azure_ai_project for key in required_keys):
            raise EvaluationException(
                message="azure_ai_project must contain required keys", target="CUSTOM_ADVERSARIAL_SIMULATOR"
            )

        if not all(azure_ai_project[key] for key in required_keys):
            raise EvaluationException(message="None values in required keys", target="CUSTOM_ADVERSARIAL_SIMULATOR")

    def _ensure_service_dependencies(self):
        """Check that RAIClient exists, raise an exception if missing.

        :raises EvaluationException: If RAIClient is not set.
        """
        if self.rai_client is None:
            msg = "RAI service is required for simulation, but an RAI client was not provided."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.ADVERSARIAL_SIMULATOR,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR,
            )

    def _join_conversation_starter(self, *, parameters, to_join):
        """Append or set the 'conversation_starter' key in parameters with 'to_join'.

        :keyword parameters: Dictionary of parameters to modify.
        :paramtype parameters: Dict[str, Any]
        :keyword to_join: String to prepend.
        :paramtype to_join: str
        :return: Updated parameters dictionary.
        :rtype: Dict[str, Any]
        """
        key = "conversation_starter"
        if key in parameters.keys():
            parameters[key] = f"{to_join} {parameters[key]}"
        else:
            parameters[key] = to_join

        return parameters

    def _validate_inputs(self, scenario, max_conversation_turns, max_simulation_results):
        """Validate scenario and numeric constraints for the simulation.

        :keyword scenario: Specifies the adversarial scenario.
        :paramtype scenario: azure.ai.evaluation.simulator.AdversarialScenario 
         or azure.ai.evaluation.simulator._adversarial_scenario._UnstableAdversarialScenario
        :keyword max_conversation_turns: Number of conversation turns.
        :paramtype max_conversation_turns: int
        :keyword max_simulation_results: Maximum number of simulations to run.
        :paramtype max_simulation_results: int
        :raises EvaluationException: If any validation fails.
        """
        if not isinstance(scenario, (AdversarialScenario, _UnstableAdversarialScenario)):
            raise EvaluationException(message=f"Invalid scenario: {scenario}", target="CUSTOM_ADVERSARIAL_SIMULATOR")
        if not isinstance(max_conversation_turns, int) or max_conversation_turns <= 0:
            raise EvaluationException(
                message="max_conversation_turns must be a positive integer", target="CUSTOM_ADVERSARIAL_SIMULATOR"
            )
        if not isinstance(max_simulation_results, int) or max_simulation_results <= 0:
            raise EvaluationException(
                message="max_simulation_results must be a positive integer", target="CUSTOM_ADVERSARIAL_SIMULATOR"
            )

    def _shuffle_pairs(self, pairs, randomize_order, seed=None):
        """Shuffle the list of (template, parameter) pairs if randomize_order is True.

        :keyword pairs: The pairs to possibly shuffle.
        :paramtype pairs: List[Tuple[Any, Any]]
        :keyword randomize_order: Whether to randomize ordering.
        :paramtype randomize_order: bool
        :keyword seed: Optional random seed for reproducibility.
        :paramtype seed: Optional[int]
        :return: The shuffled or original list of pairs.
        :rtype: List[Tuple[Any, Any]]
        """
        if randomize_order:
            if seed is not None:
                random.seed(seed)
            random.shuffle(pairs)
        return pairs
    
    def _get_template_parameter_pairs(
        self, templates, max_simulation_results, randomize_order=False, randomization_seed=None
    ):
        """Collect (template, parameter) pairs in a round-robin, up to max_simulation_results.

        :keyword templates: List of templates, each with template_parameters.
        :paramtype templates: List[Any]
        :keyword max_simulation_results: Maximum number of simulation pairs.
        :paramtype max_simulation_results: int
        :keyword randomize_order: If True, shuffle the final list of pairs.
        :paramtype randomize_order: bool
        :keyword randomization_seed: Optional seed for reproducible shuffles.
        :paramtype randomization_seed: Optional[int]
        :return: List of (template, parameter) tuples.
        :rtype: List[Tuple[Any, Dict[str, Any]]]
        """
        template_parameter_pairs = []
        
        # Extract the list of template_parameters from each template
        params_lists = [template.template_parameters for template in templates]
        
        # Iterate in a round-robin fashion using zip_longest
        for parameters in itertools.zip_longest(*params_lists):
            for template, parameter in zip(templates, parameters):
                if parameter is not None:
                    # Append the (template, parameter) pair
                    template_parameter_pairs.append((template, parameter.copy()))
                    
                    # Check if we've reached the maximum number of simulations
                    if len(template_parameter_pairs) >= max_simulation_results:
                        return template_parameter_pairs
        
        return template_parameter_pairs

    def _to_chat_protocol(self, *, conversation_history, template_parameters: Dict = None):
        """Convert the conversation history into a chat protocol payload.

        :keyword conversation_history: List of conversation turns.
        :paramtype conversation_history: List[ConversationTurn]
        :keyword template_parameters: Dictionary of additional template data.
        :paramtype template_parameters: Optional[Dict[str, Any]]
        :return: The chat protocol output with messages and metadata.
        :rtype: Dict[str, Any]
        """
        if template_parameters is None:
            template_parameters = {}
        messages = []
        for _, m in enumerate(conversation_history):
            message = {"content": m.message, "role": m.role.value}
            if "context" in m.full_response:
                message["context"] = m.full_response["context"]
            messages.append(message)
        conversation_category = template_parameters.pop("metadata", {}).get("Category")
        template_parameters["metadata"] = {}
        for key in (
            "conversation_starter",
            "group_of_people",
            "target_population",
            "topic",
            "ch_template_placeholder",
        ):
            template_parameters.pop(key, None)
        if conversation_category:
            template_parameters["category"] = conversation_category
        return {
            "template_parameters": template_parameters,
            "messages": messages,
            "$schema": "http://azureml/sdk-2-0/ChatConversation.json",
        }

    async def __call__(
        self,
        *,
        scenario: AdversarialScenario,
        target: Callable,
        max_conversation_turns: int = 1,
        max_simulation_results: int = 3,
        api_call_retry_limit: int = 3,
        api_call_retry_sleep_sec: int = 1,
        api_call_delay_sec: int = 15,
        concurrent_async_task: int = 3,
        _jailbreak_type: Optional[str] = None,
        language: SupportedLanguages = SupportedLanguages.English,
        randomize_order: bool = True,
        randomization_seed: Optional[int] = None,
        personality: Optional[str] = None,
        application_scenario: Optional[str] = None,
        code_based_strategies: Optional[List[BasePyritStrategy]] = [],
        rai_client_based_strategies: Optional[List[BasePyritStrategy]] = [],
    ):
        """Run adversarial simulations asynchronously.

        :keyword scenario: Specifies the scenario for generating adversarial inputs.
         Example:
           - :py:const:`azure.ai.evaluation.simulator.AdversarialScenario.ADVERSARIAL_QA`
           - :py:const:`azure.ai.evaluation.simulator.AdversarialScenario.ADVERSARIAL_CONVERSATION`
        :paramtype scenario: azure.ai.evaluation.simulator.AdversarialScenario
        :keyword target: The function to handle conversation messages from the assistant bot.
        :paramtype target: Callable[..., Any]
        :keyword max_conversation_turns: Maximum number of conversation turns.
        :paramtype max_conversation_turns: int
        :keyword max_simulation_results: Maximum number of scenarios to simulate.
        :paramtype max_simulation_results: int
        :keyword api_call_retry_limit: Maximum number of HTTP retries.
        :paramtype api_call_retry_limit: int
        :keyword api_call_retry_sleep_sec: Seconds to sleep between retries.
        :paramtype api_call_retry_sleep_sec: int
        :keyword api_call_delay_sec: Delay in seconds before making an API call.
        :paramtype api_call_delay_sec: int
        :keyword concurrent_async_task: Maximum concurrent async tasks.
        :paramtype concurrent_async_task: int
        :keyword _jailbreak_type: If set, modifies conversation parameters using a special jailbreak dataset.
        :paramtype _jailbreak_type: Optional[str]
        :keyword language: Language for the conversation simulation.
        :paramtype language: azure.ai.evaluation.simulator._constants.SupportedLanguages
        :keyword randomize_order: Whether to shuffle generated scenarios.
        :paramtype randomize_order: bool
        :keyword randomization_seed: An optional seed for reproducible random ordering.
        :paramtype randomization_seed: Optional[int]
        :keyword personality: Personality string to apply in conversation.
        :paramtype personality: Optional[str]
        :keyword application_scenario: Used to specify the scenario context if needed.
        :paramtype application_scenario: Optional[str]
        :return: A list of simulation results, each containing conversation histories.
        :rtype: List[Any]
        """
        self.logger.info(f"User inputs: scenario={scenario}, max_conversation_turns={max_conversation_turns}, "
                     f"max_simulation_results={max_simulation_results}, api_call_retry_limit={api_call_retry_limit}, "
                     f"api_call_retry_sleep_sec={api_call_retry_sleep_sec}, api_call_delay_sec={api_call_delay_sec}, "
                     f"concurrent_async_task={concurrent_async_task}, _jailbreak_type={_jailbreak_type}, "
                     f"language={language}, randomize_order={randomize_order}, randomization_seed={randomization_seed}, "
                     f"personality={personality}, application_scenario={application_scenario}, ")

        self._ensure_service_dependencies()
        self._validate_inputs(
            scenario=scenario,
            max_conversation_turns=max_conversation_turns,
            max_simulation_results=max_simulation_results,
        )
        if scenario != AdversarialScenario.ADVERSARIAL_CONVERSATION:
            max_conversation_turns = 2
        else:
            max_conversation_turns = max_conversation_turns * 2
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
        jailbreak_dataset = None
        if _jailbreak_type:
            jailbreak_dataset = await self.rai_client.get_jailbreaks_dataset(type=_jailbreak_type)
        progress_bar = tqdm(
            total=total_tasks,
            desc="generating jailbreak simulations" if _jailbreak_type else "generating simulations",
            ncols=100,
            unit="simulations",
        )
        template_parameter_pairs = self._get_template_parameter_pairs(
            templates, max_simulation_results=max_simulation_results, randomize_order=randomize_order, randomization_seed=randomization_seed
        )
        all_conversation_histories = []
        if personality is None:
            personality = ""
        if application_scenario is None:
            application_scenario = ""
        tasks = [
            self._create_simulation_task(
                template=template,
                parameter=parameter,
                target=target,
                semaphore=semaphore,
                max_conversation_turns=max_conversation_turns,
                personality=personality,
                application_scenario=application_scenario,
                language=language,
                api_call_retry_limit=api_call_retry_limit,
                api_call_retry_sleep_sec=api_call_retry_sleep_sec,
                api_call_delay_sec=api_call_delay_sec,
                progress_bar=progress_bar,
                jailbreak_dataset=jailbreak_dataset,
                _jailbreak_type=_jailbreak_type,
                code_based_strategies=code_based_strategies,
                rai_client_based_strategies=rai_client_based_strategies,
            )
            for template, parameter in template_parameter_pairs[:max_simulation_results]
        ]
        all_conversation_histories = await asyncio.gather(*tasks)
        progress_bar.close()
        return all_conversation_histories

    def _setup_bots(self, *, template, parameter, target):
        """Create user and assistant bots for a simulation.

        :keyword template: Contains the conversation template and metadata.
        :paramtype template: Any
        :keyword parameter: A dictionary of template parameters.
        :paramtype parameter: Dict[str, Any]
        :keyword target: A callback function to handle assistant messages.
        :paramtype target: Callable[..., Any]
        :return: A tuple of (user_bot, system_bot).
        :rtype: Tuple[ConversationBot, CallbackConversationBot]
        """
        user_bot = self._setup_bot(role=ConversationRole.USER, template=template, parameters=parameter)
        system_bot = self._setup_bot(
            role=ConversationRole.ASSISTANT, template=template, parameters=parameter, target=target
        )
        return user_bot, system_bot

    def _setup_bot(self, *, role, template, parameters, target: Callable = None):
        """Set up a conversation bot (user or assistant) using the given role, template, and parameters.

        :keyword role: The role of this bot (USER or ASSISTANT).
        :paramtype role: azure.ai.evaluation.simulator._conversation.ConversationRole
        :keyword template: Template with the conversation structure.
        :paramtype template: Any
        :keyword parameters: Parameters to substitute into the template.
        :paramtype parameters: Dict[str, Any]
        :keyword target: Callback function, only used if role=ASSISTANT.
        :paramtype target: Optional[Callable[..., Any]]
        :return: A ConversationBot for USER or CallbackConversationBot for ASSISTANT.
        :rtype: Any
        """
        if role == ConversationRole.USER:
            model = ProxyChatCompletionsModel(
                name="user_bot_model",
                template_key=template.template_name,
                template_parameters=parameters,
                token_manager=self.token_manager,
                endpoint_url=self.rai_client.simulation_submit_endpoint,
                api_version="2023-07-01-preview",
                max_tokens=1200,
                temperature=0.0,
            )
            return ConversationBot(
                role=role,
                model=model,
                conversation_template=str(template),
                instantiation_parameters=parameters,
            )

        elif role == ConversationRole.ASSISTANT:
            return CallbackConversationBot(
                callback=target,
                role=role,
                model=None,
                user_template=str(template),
                user_template_parameters=parameters,
                conversation_template="",
                instantiation_parameters={},
            )

    def _create_retry_session(self, *, api_call_retry_limit, api_call_retry_sleep_sec):
        """Construct an async retry session for HTTP calls.

        :keyword api_call_retry_limit: Maximum number of retries for HTTP calls.
        :paramtype api_call_retry_limit: int
        :keyword api_call_retry_sleep_sec: Sleep duration (in seconds) between retries.
        :paramtype api_call_retry_sleep_sec: int
        :return: An async HTTP client with retry policies.
        :rtype: Any
        """
        return get_async_http_client().with_policies(
            retry_policy=AsyncRetryPolicy(
                retry_total=api_call_retry_limit,
                retry_backoff_factor=api_call_retry_sleep_sec,
                retry_mode=RetryMode.Fixed,
            )
        )

    async def _perform_conversation_turns(
        self, user_bot, system_bot, session, max_conversation_turns, progress_bar, api_call_delay_sec
    ):
        """Perform turn-by-turn conversation, alternating between user_bot and system_bot.

        :keyword user_bot: The user bot instance.
        :paramtype user_bot: Any
        :keyword system_bot: The assistant bot instance.
        :paramtype system_bot: Any
        :keyword session: The HTTP session with retry behavior.
        :paramtype session: Any
        :keyword max_conversation_turns: Number of total turns to simulate.
        :paramtype max_conversation_turns: int
        :keyword progress_bar: Progress bar for tracking simulation steps.
        :paramtype progress_bar: Any
        :keyword api_call_delay_sec: Delay in seconds after each turn.
        :paramtype api_call_delay_sec: int
        :return: The final conversation history.
        :rtype: List[ConversationTurn]
        """
        conversation_history = []
        for current_turn in range(1, max_conversation_turns + 1):
            current_bot = user_bot if current_turn % 2 == 1 else system_bot
            response, _, _, full_response = await current_bot.generate_response(
                session=session, conversation_history=conversation_history, turn_number=current_turn
            )
            conversation_history.append(
                ConversationTurn(
                    role=current_bot.role,
                    name=current_bot.name,
                    message=response["samples"][0],
                    full_response=full_response,
                )
            )
            progress_bar.update(1)
            if api_call_delay_sec > 0:
                await asyncio.sleep(api_call_delay_sec)
        return conversation_history

    def _create_simulation_task(
        self,
        *,
        template,
        parameter,
        target,
        semaphore,
        max_conversation_turns,
        personality,
        application_scenario,
        language,
        api_call_retry_limit,
        api_call_retry_sleep_sec,
        api_call_delay_sec,
        progress_bar,
        jailbreak_dataset=None,
        _jailbreak_type=None,
        code_based_strategies=[],
        rai_client_based_strategies=[]
    ):
        """Create a single simulation asyncio task for an adversarial scenario.

        :keyword template: The conversation template object.
        :paramtype template: Any
        :keyword parameter: Key-value pairs to fill the template.
        :paramtype parameter: Dict[str, Any]
        :keyword target: The callback for the assistant bot's messages.
        :paramtype target: Callable[..., Any]
        :keyword semaphore: Controls concurrency for async tasks.
        :paramtype semaphore: asyncio.Semaphore
        :keyword max_conversation_turns: Number of conversation turns to simulate.
        :paramtype max_conversation_turns: int
        :keyword personality: Extra personality prompt data.
        :paramtype personality: str
        :keyword application_scenario: Contextual scenario name.
        :paramtype application_scenario: str
        :keyword language: Desired conversation language.
        :paramtype language: azure.ai.evaluation.simulator._constants.SupportedLanguages
        :keyword api_call_retry_limit: Maximum HTTP call retries.
        :paramtype api_call_retry_limit: int
        :keyword api_call_retry_sleep_sec: Sleep in seconds between retries.
        :paramtype api_call_retry_sleep_sec: int
        :keyword api_call_delay_sec: Delay in seconds before each turn.
        :paramtype api_call_delay_sec: int
        :keyword progress_bar: Progress bar for visual feedback.
        :paramtype progress_bar: Any
        :keyword jailbreak_dataset: Optional list of jailbreak prompts.
        :paramtype jailbreak_dataset: Optional[List[str]]
        :keyword _jailbreak_type: If set, modifies conversation with special jailbreak data.
        :paramtype _jailbreak_type: Optional[str]
        :return: The scheduled asyncio Task.
        :rtype: asyncio.Task
        """
        if _jailbreak_type == "upia" and jailbreak_dataset:
            parameter = self._join_conversation_starter(parameters=parameter, to_join=random.choice(jailbreak_dataset))

        return asyncio.create_task(
            self._simulate_conversation(
                template=template,
                parameter=parameter,
                target=target,
                semaphore=semaphore,
                max_conversation_turns=max_conversation_turns,
                personality=personality,
                application_scenario=application_scenario,
                language=language,
                api_call_retry_limit=api_call_retry_limit,
                api_call_retry_sleep_sec=api_call_retry_sleep_sec,
                api_call_delay_sec=api_call_delay_sec,
                progress_bar=progress_bar,
                code_based_strategies=code_based_strategies,
                rai_client_based_strategies=rai_client_based_strategies,
            )
        )

    async def _simulate_conversation(
        self,
        *,
        template,
        parameter,
        target,
        semaphore,
        max_conversation_turns,
        personality,
        application_scenario,
        language,
        api_call_retry_limit,
        api_call_retry_sleep_sec,
        api_call_delay_sec,
        progress_bar,
        code_based_strategies,
        rai_client_based_strategies
    ):
        """Perform a conversation simulation within a semaphore lock.

        :keyword template: The conversation template object.
        :paramtype template: Any
        :keyword parameter: Key-value pairs for the template.
        :paramtype parameter: Dict[str, Any]
        :keyword target: The callback for assistant messages.
        :paramtype target: Callable[..., Any]
        :keyword semaphore: Concurrency control for async tasks.
        :paramtype semaphore: asyncio.Semaphore
        :keyword max_conversation_turns: Number of conversation turns per simulation.
        :paramtype max_conversation_turns: int
        :keyword personality: Personality string for the user message.
        :paramtype personality: str
        :keyword application_scenario: Additional contextual data or scenario name.
        :paramtype application_scenario: str
        :keyword language: Language for the conversation.
        :paramtype language: azure.ai.evaluation.simulator._constants.SupportedLanguages
        :keyword api_call_retry_limit: Maximum HTTP retries.
        :paramtype api_call_retry_limit: int
        :keyword api_call_retry_sleep_sec: Sleep in seconds between HTTP retries.
        :paramtype api_call_retry_sleep_sec: int
        :keyword api_call_delay_sec: Delay in seconds before each turn.
        :paramtype api_call_delay_sec: int
        :keyword progress_bar: Progress tracking object.
        :paramtype progress_bar: Any
        :return: A JsonLineList containing the conversation output or empty on failure.
        :rtype: Any
        """
        async with semaphore:
            user_bot, system_bot = self._setup_bots(template=template, parameter=parameter, target=target)
            session = self._create_retry_session(
                api_call_retry_limit=api_call_retry_limit, api_call_retry_sleep_sec=api_call_retry_sleep_sec
            )
            extra_kwargs = {key: value for key, value in parameter.items() if isinstance(value, str)}
            await asyncio.sleep(api_call_delay_sec)
            
            file_content = extra_kwargs.get('file_content', '')
            first_turn = parameter.get('conversation_starter', '')
            try:
                jinja_template = Template(first_turn)
                first_turn = jinja_template.render(parameter)
            except (TemplateSyntaxError, TemplateAssertionError) as e:
                self.logger.error(f"Conversation starter template error: {e}")

            if code_based_strategies:
                    for strategy in code_based_strategies:
                        first_turn = strategy(first_turn)
            try:
                if language != SupportedLanguages.English:
                    if not isinstance(language, SupportedLanguages) or language not in SupportedLanguages:
                        raise Exception(
                            f"Language option '{language}' isn't supported. Select a supported language option from "
                            f"azure.ai.evaluation.simulator.SupportedLanguages: {[f'{e}' for e in SupportedLanguages]}"
                        )
                    first_turn += f" {SUPPORTED_LANGUAGES_MAPPING[language]}"
            
                # Append 'file_content' to the first prompt
                if file_content:
                    first_turn += f"\nFile Content: {file_content}"
                if rai_client_based_strategies:
                    for strategy in rai_client_based_strategies:
                        first_turn = await strategy(
                            message=first_turn, 
                            logger=self.logger, 
                            template=template, 
                            rai_client=self.rai_client, 
                            extra_kwargs=extra_kwargs
                        )
                
                self.logger.info(f"First turn after pyrit: {first_turn}")
                conversation_history = [
                    ConversationTurn(
                        role=user_bot.role,
                        name=user_bot.name,
                        message=first_turn,
                        full_response={},
                    )
                ]
                for current_turn in range(2, max_conversation_turns + 1):
                    current_bot = user_bot if current_turn % 2 == 1 else system_bot
                    start_time = time.time()
                    response, request, _, full_response = await current_bot.generate_response(
                        session=session,
                        conversation_history=conversation_history,
                        max_history=5,
                        turn_number=current_turn,
                    )
                    end_time = time.time()
                    time_taken = end_time - start_time
                    self.logger.info(f"Generated response for turn {current_turn}. Time taken: {time_taken:.4f} seconds")
                    self.logger.info(f"Response: {response}")
                    message = response["samples"][0]
            
                    conversation_history.append(
                        ConversationTurn(
                            role=current_bot.role,
                            name=current_bot.name,
                            message=message,
                            full_response=full_response,
                        )
                    )
                    progress_bar.update(1)
                    if api_call_delay_sec > 0:
                        await asyncio.sleep(api_call_delay_sec)
            
                chat_protocol_output = self._to_chat_protocol(
                    conversation_history=conversation_history, template_parameters=parameter
                )
                json_line_list = JsonLineList([chat_protocol_output])
                return json_line_list

            except Exception as e:
                logger.error(f"Simulation error: {e}")
                return []
