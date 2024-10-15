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

logger = logging.getLogger(__name__)

def _setup_logger():
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
        if "credential" in azure_ai_project:
            return azure_ai_project["credential"]
        return credential or DefaultAzureCredential()

    def _validate_azure_ai_project(self, *, azure_ai_project):
        required_keys = ["subscription_id", "resource_group_name", "project_name"]
        if not all(key in azure_ai_project for key in required_keys):
            raise EvaluationException(
                message="azure_ai_project must contain required keys", target="CUSTOM_ADVERSARIAL_SIMULATOR"
            )

        if not all(azure_ai_project[key] for key in required_keys):
            raise EvaluationException(message="None values in required keys", target="CUSTOM_ADVERSARIAL_SIMULATOR")

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

    def _join_conversation_starter(self, *, parameters, to_join):
        key = "conversation_starter"
        if key in parameters.keys():
            parameters[key] = f"{to_join} {parameters[key]}"
        else:
            parameters[key] = to_join

        return parameters

    def _validate_inputs(self, scenario, max_conversation_turns, max_simulation_results):
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
        if randomize_order:
            if seed is not None:
                random.seed(seed)
            random.shuffle(pairs)
        return pairs

    def _get_template_parameter_pairs(self, templates, randomize_order, randomization_seed):
        template_parameter_pairs = [
            (template, parameter.copy()) for template in templates for parameter in template.template_parameters
        ]
        return self._shuffle_pairs(template_parameter_pairs, randomize_order, randomization_seed)

    def _to_chat_protocol(self, *, conversation_history, template_parameters: Dict = None):
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
    ):
        self.logger.info(f"User inputs: scenario={scenario}, max_conversation_turns={max_conversation_turns}, "
                     f"max_simulation_results={max_simulation_results}, api_call_retry_limit={api_call_retry_limit}, "
                     f"api_call_retry_sleep_sec={api_call_retry_sleep_sec}, api_call_delay_sec={api_call_delay_sec}, "
                     f"concurrent_async_task={concurrent_async_task}, _jailbreak_type={_jailbreak_type}, "
                     f"language={language}, randomize_order={randomize_order}, randomization_seed={randomization_seed}, "
                     f"personality={personality}, application_scenario={application_scenario}")

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
            templates, randomize_order=randomize_order, randomization_seed=randomization_seed
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
            )
            for template, parameter in template_parameter_pairs[:max_simulation_results]
        ]
        all_conversation_histories = await asyncio.gather(*tasks)
        progress_bar.close()
        return all_conversation_histories

    def _setup_bots(self, *, template, parameter, target):
        user_bot = self._setup_bot(role=ConversationRole.USER, template=template, parameters=parameter)
        system_bot = self._setup_bot(
            role=ConversationRole.ASSISTANT, template=template, parameters=parameter, target=target
        )
        return user_bot, system_bot

    def _setup_bot(self, *, role, template, parameters, target: Callable = None):
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
    ):
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
    ):
        async with semaphore:
            user_bot, system_bot = self._setup_bots(template=template, parameter=parameter, target=target)
            session = self._create_retry_session(
                api_call_retry_limit=api_call_retry_limit, api_call_retry_sleep_sec=api_call_retry_sleep_sec
            )
            extra_kwargs = {key: value for key, value in parameter.items() if isinstance(value, str)}
            await asyncio.sleep(api_call_delay_sec)
            self.logger.info(f"Customizing this: template_key={template.template_name}, extra_kwargs={extra_kwargs}, ")
            start_time = time.time()
            first_turn, first_turn_full_response = await self.rai_client.customize_first_turn(
                template_key=template.template_name,
                personality=personality,
                application_scenario=application_scenario,
                other_template_kwargs=extra_kwargs,
                logger=self.logger,
            )
            end_time = time.time()
            time_taken = end_time - start_time
            self.logger.info(f"Generated response for customizing first turn. Time taken: {time_taken:.4f} seconds")
            self.logger.info(f"Response: {first_turn}")

            try:
                first_prompt = first_turn
                if language != SupportedLanguages.English:
                    if not isinstance(language, SupportedLanguages) or language not in SupportedLanguages:
                        raise Exception(
                            f"Language option '{language}' isn't supported. Select a supported language option from "
                            f"azure.ai.evaluation.simulator.SupportedLanguages: {[f'{e}' for e in SupportedLanguages]}"
                        )
                    first_prompt += f" {SUPPORTED_LANGUAGES_MAPPING[language]}"

                conversation_history = [
                    ConversationTurn(
                        role=user_bot.role,
                        name=user_bot.name,
                        message=first_prompt,
                        full_response=first_turn_full_response,
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

                chat_protocol_output = self._to_chat_protocol(
                    conversation_history=conversation_history, template_parameters=parameter
                )
                json_line_list = JsonLineList([chat_protocol_output])
                return json_line_list

            except Exception as e:
                logger.error(f"Simulation error: {e}")
                return []
