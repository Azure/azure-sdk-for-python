# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
import os
import inspect
import logging
from datetime import datetime
from azure.ai.evaluation._common._experimental import experimental
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast
from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluationResult
from azure.ai.evaluation.simulator import Simulator, AdversarialSimulator, AdversarialScenario, AdversarialScenarioJailbreak, IndirectAttackSimulator, DirectAttackSimulator
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.ai.evaluation.simulator._model_tools import ManagedIdentityAPITokenManager, TokenScope, RAIClient, AdversarialTemplateHandler
from azure.ai.evaluation._common.utils import validate_azure_ai_project
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.ai.evaluation._safety_evaluation._callback_chat_target import CallbackChatTarget
from pyrit.orchestrator.single_turn.prompt_sending_orchestrator import PromptSendingOrchestrator
from pyrit.orchestrator import ManyShotJailbreakOrchestrator, SkeletonKeyOrchestrator, Orchestrator
from pyrit.prompt_converter import PromptConverter, MathPromptConverter, TenseConverter, Base64Converter, FlipConverter
from pyrit.prompt_target import PromptChatTarget
from azure.core.credentials import TokenCredential
import json
from pathlib import Path
import re
import itertools
from pyrit.common import initialize_pyrit, DUCK_DB
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.models import ChatMessage
from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, _SafetyEvaluator, DATA_EXT

@experimental
class AttackStrategy(Enum):
    """Budget levels for attacks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@experimental
class RedTeamAgent(_SafetyEvaluation):
    def __init__(self, azure_ai_project, credential):
        super().__init__(azure_ai_project, credential)
        self.token_manager = ManagedIdentityAPITokenManager(
            token_scope=TokenScope.DEFAULT_AZURE_MANAGEMENT,
            logger=logging.getLogger("AdversarialSimulator"),
            credential=cast(TokenCredential, credential),
        )

        self.rai_client = RAIClient(azure_ai_project=self.azure_ai_project, token_manager=self.token_manager)
        self.adversarial_template_handler = AdversarialTemplateHandler(
            azure_ai_project=self.azure_ai_project, rai_client=self.rai_client
        )

        initialize_pyrit(memory_db_type=DUCK_DB)

    async def _get_all_prompts(self, scenario: AdversarialScenario, num_rows: int = 3) -> List[str]:
        templates = await self.adversarial_template_handler._get_content_harm_template_collections(
                scenario.value
            )
        parameter_lists = [t.template_parameters for t in templates]
        zipped_parameters = list(zip(*parameter_lists))

        def fill_template(template_str, parameter):
            pattern = re.compile(r'{{\s*(.*?)\s*}}')
            def replacer(match):
                placeholder = match.group(1)
                return parameter.get(placeholder, f"{{{{ {placeholder} }}}}")
            filled_text = pattern.sub(replacer, template_str)
            return filled_text

        all_prompts = []
        count = 0
        for param_group in zipped_parameters:
            for _, parameter in zip(templates, param_group):
                filled_template = fill_template(parameter['conversation_starter'], parameter)
                all_prompts.append(filled_template)
                count += 1
                if count >= num_rows:
                    break
            if count >= num_rows:
                break
        return all_prompts
    
    def _message_to_dict(self, message: ChatMessage):
        return {
            "role": message.role,
            "content": message.content,
        }
    
    def _get_converters_for_budget(self, attack_strategy) -> List:
        converters = []
        if AttackStrategy.LOW in attack_strategy:
            converters.extend([Base64Converter(), FlipConverter()])
        return converters
    
    async def _many_shot_orchestrator(self, chat_target: PromptChatTarget, all_prompts: List[str]) -> Orchestrator:
            orchestrator = ManyShotJailbreakOrchestrator(
                objective_target=chat_target,
            )
            await orchestrator.send_prompts_async(prompt_list=all_prompts)
            return orchestrator
    
    async def _skeleton_key_orchestrator(self, chat_target: PromptChatTarget, all_prompts: List[str], converters: PromptConverter) -> List[Orchestrator]:
        orchestrators = []
        for converter in converters:
            orchestrator = SkeletonKeyOrchestrator(
                prompt_target=chat_target,
                prompt_converters=[converter]
            )
            await orchestrator.send_skeleton_key_with_prompts_async(prompt_list=all_prompts)
            orchestrators.append(orchestrator)
        return orchestrators
            
    
    async def _call_orchestrators_for_budget(self, attack_strategy: List[AttackStrategy], converters: PromptConverter, chat_target: PromptChatTarget, all_prompts: List[str]) -> Dict[str, str]:
        output_data_paths = {}
        if AttackStrategy.LOW in attack_strategy:
            # run many-shot orchestrator (does not handle converters)
            # TODO: Many shot is having trouble sneding prompts using the many shot template, ignoring for now 
            # many_shot_orchestrator = await self._many_shot_orchestrator(chat_target, all_prompts)
            # orchestrator_name = many_shot_orchestrator.get_identifier()["__type__"]
            # ouptut_path = f"{orchestrator_name}{DATA_EXT}"
            # ouptut_path = self._write_pyrit_outputs_to_file(many_shot_orchestrator, ouptut_path)
            # output_data_paths[orchestrator_name] = ouptut_path
            # run skeleton key orchestrator for each converter
            skeleton_key_orchestrators = await self._skeleton_key_orchestrator(chat_target, all_prompts, converters)
            for converter in converters:
                skeleton_key_orchestrator = skeleton_key_orchestrators.pop(0)
                converter_name = converter.get_identifier()["__type__"]
                orchestrator_name = skeleton_key_orchestrator.get_identifier()["__type__"]
                base_path = f"{orchestrator_name}_{converter_name}"
                ouptut_path = f"{base_path}{DATA_EXT}"
                ouptut_path = self._write_pyrit_outputs_to_file(skeleton_key_orchestrator, ouptut_path)
                output_data_paths[base_path] = ouptut_path
        return output_data_paths
    
    def _write_pyrit_outputs_to_file(self, orchestrator: Orchestrator, output_path: Union[str, os.PathLike]) -> Union[str, os.PathLike]:
        memory = orchestrator.get_memory()

        # Get conversations as a List[List[ChatMessage]]
        conversations = [[item.to_chat_message() for item in group] for conv_id, group in itertools.groupby(memory, key=lambda x: x.conversation_id)]
        
        #Convert to json lines
        json_lines = ""
        for conversation in conversations: # each conversation is a List[ChatMessage]
            json_lines += json.dumps({"conversation": {"messages": [self._message_to_dict(message) for message in conversation]}}) + "\n"

        with Path(output_path).open("w") as f:
            f.writelines(json_lines)
        return output_path
    
    def _get_chat_target(self, target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration]) -> PromptChatTarget:
        chat_target: OpenAIChatTarget = None
        if not isinstance(target, Callable):
            if "azure_deployment" in target and "azure_endpoint" in target: # Azure OpenAI
                api_key = target.get("api_key", None)
                if not api_key:
                    chat_target = OpenAIChatTarget(deployment_name=target["azure_deployment"], endpoint=target["azure_endpoint"], use_aad_auth=True)
                else: 
                    chat_target = OpenAIChatTarget(deployment_name=target["azure_deployment"], endpoint=target["azure_endpoint"], api_key=api_key)
            else: # OpenAI
                chat_target = OpenAIChatTarget(deployment=target["model"], endpoint=target.get("base_url", None), key=target["api_key"], is_azure_target=False)
        else:
            async def callback_target(
                messages: List[Dict],
                stream: bool = False,
                session_state: Optional[str] = None,
                context: Optional[Dict] = None
            ) -> dict:
                messages_list = [self._message_to_dict(chat_message) for chat_message in messages] # type: ignore
                latest_message = messages_list[-1]
                application_input = latest_message["content"]
                try:
                    response = target(query=application_input)
                except Exception as e:
                    response = f"Something went wrong {e!s}"

                ## We format the response to follow the openAI chat protocol format
                formatted_response = {
                    "content": response,
                    "role": "assistant",
                    "context":{},
                }
                ## NOTE: In the future, instead of appending to messages we should just return `formatted_response`
                messages_list.append(formatted_response) # type: ignore
                return {"messages": messages_list, "stream": stream, "session_state": session_state, "context": {}}
            
            chat_target = CallbackChatTarget(callback=callback_target) # type: ignore
        return chat_target
    
    async def _pyrit(
            self, 
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration], 
            num_rows: int = 1,
            attack_strategy: List[AttackStrategy] = []
        ) ->  Dict[str, str]:
        chat_target = self._get_chat_target(target)
        
        all_prompts_list = await self._get_all_prompts(scenario=AdversarialScenario.ADVERSARIAL_QA, num_rows=num_rows)

        # If user provided budget levels, get predefined strategies
        if attack_strategy:
            self.logger.info(f"Configuring PyRIT based on attack strategy: {attack_strategy}")
            converters = self._get_converters_for_budget(attack_strategy)
            data_paths = await self._call_orchestrators_for_budget(attack_strategy, converters, chat_target, all_prompts_list)
            return data_paths
        # TODO: Implement handling for pyrit strategies beyond budget levels
        else: 
            output_paths = {}
            orchestrator = PromptSendingOrchestrator(objective_target=chat_target)
            await orchestrator.send_prompts_async(prompt_list=all_prompts_list)
            orchestrator_name = orchestrator.get_identifier()["__type__"]
            base_path = f"{orchestrator_name}"
            ouptut_path = f"{base_path}{DATA_EXT}"
            output_paths[base_path] = self._write_pyrit_outputs_to_file(orchestrator, ouptut_path)
            return output_paths

    
    async def attack(
            self,             
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
            evaluation_name: Optional[str] = None,
            num_turns : int = 1,
            num_rows: int = 5,
            attack_strategy: List[AttackStrategy] = [],
            data_only: bool = False, 
            output_path: Optional[Union[str, os.PathLike]] = None):
        
        data_paths = await self._pyrit(
            target=target,
            num_rows=num_rows,
            attack_strategy=attack_strategy
        )

        await super().__call__(
            target=target,
            evaluation_name=evaluation_name,
            num_turns=num_turns,
            num_rows=num_rows,
            data_only=data_only,
            data_paths=data_paths,
            output_path=output_path
        )