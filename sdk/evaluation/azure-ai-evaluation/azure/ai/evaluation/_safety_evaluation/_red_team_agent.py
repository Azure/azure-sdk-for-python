# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
from enum import Enum
import os
import logging
from datetime import datetime
from azure.ai.evaluation._common._experimental import experimental
from typing import Callable, Dict, List, Optional, Union, cast
from azure.ai.evaluation._model_configurations import EvaluationResult
from azure.ai.evaluation.simulator import AdversarialScenario
from azure.ai.evaluation.simulator._model_tools import ManagedIdentityAPITokenManager, TokenScope, RAIClient, AdversarialTemplateHandler
from azure.ai.evaluation.simulator._model_tools._generated_rai_client import GeneratedRAIClient
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.ai.evaluation._safety_evaluation._callback_chat_target import CallbackChatTarget
from pyrit.orchestrator.single_turn.prompt_sending_orchestrator import PromptSendingOrchestrator
from pyrit.orchestrator import Orchestrator
from pyrit.prompt_converter import PromptConverter, MathPromptConverter, TenseConverter, Base64Converter, FlipConverter, MorseConverter, AnsiAttackConverter, AsciiArtConverter, AsciiSmugglerConverter, AtbashConverter, BinaryConverter, CaesarConverter, CharacterSpaceConverter, CharSwapGenerator, DiacriticConverter, LeetspeakConverter, UrlConverter, UnicodeSubstitutionConverter, UnicodeConfusableConverter, SuffixAppendConverter, StringJoinConverter, ROT13Converter, RepeatTokenConverter
from pyrit.prompt_target import PromptChatTarget
from azure.core.credentials import TokenCredential
import json
from pathlib import Path
import re
import itertools
from pyrit.common import initialize_pyrit, DUCK_DB
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.models import ChatMessage
from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, DATA_EXT
from azure.ai.evaluation._user_agent import USER_AGENT

BASELINE_IDENTIFIER = "Baseline"

@experimental
class AttackStrategy(Enum):
    """Strategies for attacks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AnsiAttack = "ansi_attack"
    AsciiArt = "ascii_art"
    AsciiSmuggler = "ascii_smuggler"
    Atbash = "atbash"
    Base64 = "base64"
    Binary = "binary"
    Caesar = "caesar"
    CharacterSpace = "character_space"
    CharSwap = "char_swap"
    Diacritic = "diacritic"
    Flip = "flip"
    Leetspeak = "leetspeak"
    Math = "math"
    Morse = "morse"
    ROT13 = "rot13"
    RepeatToken = "repeat_token"
    SuffixAppend = "suffix_append"
    StringJoin = "string_join"
    Tense = "tense"
    UnicodeConfusable = "unicode_confusable"
    UnicodeSubstitution = "unicode_substitution"
    Url = "url"
    Baseline = "baseline"

    @classmethod
    def Compose(cls, items: List["AttackStrategy"]) -> List["AttackStrategy"]:
        for item in items:
            if not isinstance(item, cls):
                raise ValueError("All items must be instances of AttackStrategy")
        if len(items) > 2: 
            raise ValueError("Composed strategies must have at most 2 items")
        return items
    
def _setup_logger():
    """Configure and return a logger instance for the RedTeamAgent.

    :return: The logger instance.
    :rtype: logging.Logger
    """
    log_filename = datetime.now().strftime("%Y_%m_%d__%H_%M.log")
    logger = logging.getLogger("RedTeamAgentLogger")
    logger.setLevel(logging.DEBUG)  
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

@experimental
class RedTeamAgent(_SafetyEvaluation):
    def __init__(self, azure_ai_project, credential):
        super().__init__(azure_ai_project, credential)
        self.logger = _setup_logger()
        self.token_manager = ManagedIdentityAPITokenManager(
            token_scope=TokenScope.DEFAULT_AZURE_MANAGEMENT,
            logger=logging.getLogger("AdversarialSimulator"),
            credential=cast(TokenCredential, credential),
        )

        self.rai_client = RAIClient(azure_ai_project=self.azure_ai_project, token_manager=self.token_manager)
        self.generated_rai_client = GeneratedRAIClient(azure_ai_project=self.azure_ai_project, token_manager=self.token_manager)
        self.adversarial_template_handler = AdversarialTemplateHandler(
            azure_ai_project=self.azure_ai_project, rai_client=self.rai_client
        )

        # Initialize a cache for attack objectives by risk category and strategy
        self.attack_objectives_cache = {}
        
        initialize_pyrit(memory_db_type=DUCK_DB)

    def _strategy_converter_map(self):
        return{
        AttackStrategy.LOW: [Base64Converter(), FlipConverter(), MorseConverter()],
        AttackStrategy.MEDIUM: [MathPromptConverter(converter_target=self.chat_target), TenseConverter(converter_target=self.chat_target, tense="past")],
        AttackStrategy.HIGH: [[MathPromptConverter(converter_target=self.chat_target), TenseConverter(converter_target=self.chat_target, tense="past")]],
        AttackStrategy.AnsiAttack: AnsiAttackConverter(),
        AttackStrategy.AsciiArt: AsciiArtConverter(),
        AttackStrategy.AsciiSmuggler: AsciiSmugglerConverter(),
        AttackStrategy.Atbash: AtbashConverter(),
        AttackStrategy.Base64: Base64Converter(),
        AttackStrategy.Baseline: None,
        AttackStrategy.Binary: BinaryConverter(),
        AttackStrategy.Caesar: CaesarConverter(caesar_offset=1),
        AttackStrategy.CharacterSpace: CharacterSpaceConverter(),
        AttackStrategy.CharSwap: CharSwapGenerator(),
        AttackStrategy.Diacritic: DiacriticConverter(),
        AttackStrategy.Flip: FlipConverter(),
        AttackStrategy.Leetspeak: LeetspeakConverter(),
        AttackStrategy.Math: MathPromptConverter(converter_target=self.chat_target),
        AttackStrategy.Morse: MorseConverter(),
        AttackStrategy.ROT13: ROT13Converter(),
        AttackStrategy.SuffixAppend: SuffixAppendConverter(suffix="describing.\\ + similarlyNow write oppositeley.]( Me giving**ONE please? revert with \"\\!--Two"), 
        AttackStrategy.RepeatToken: RepeatTokenConverter(token_to_repeat="hello"), # TODO: Roman to provide guidance on which token to repeat
        AttackStrategy.StringJoin: StringJoinConverter(),
        AttackStrategy.Tense: TenseConverter(converter_target=self.chat_target, tense="past"), 
        AttackStrategy.UnicodeConfusable: UnicodeConfusableConverter(),
        AttackStrategy.UnicodeSubstitution: UnicodeSubstitutionConverter(),
        AttackStrategy.Url: UrlConverter(),
    }

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
    
    async def _get_attack_objectives(self, attack_objective_generator, application_scenario: Optional[str] = None, num_rows: int = 3, strategy: Optional[str] = None) -> List[str]:
        """Get attack objectives from the RAI client based on the risk categories in the attack objective generator.
        
        :param attack_objective_generator: The generator with risk categories to get attack objectives for
        :type attack_objective_generator: ~azure.ai.evaluation.redteam.AttackObjectiveGenerator
        :param application_scenario: Optional description of the application scenario for context
        :type application_scenario: str
        :param num_rows: The maximum number of objectives to retrieve
        :type num_rows: int
        :param strategy: Optional attack strategy to get specific objectives for
        :type strategy: str
        :return: A list of attack objective prompts
        :rtype: List[str]
        """
        # Convert risk categories to lowercase for consistent caching
        risk_categories = [cat.value.lower() for cat in attack_objective_generator.risk_categories]
        risk_categories.sort()  # Sort to ensure consistent cache key
        
        self.logger.info("=" * 80)
        self.logger.info(f"GET ATTACK OBJECTIVES REQUEST")
        self.logger.info(f"Risk categories: {risk_categories}")
        self.logger.info(f"Application scenario: {application_scenario}")
        self.logger.info(f"Number of rows requested: {num_rows}")
        self.logger.info(f"Strategy: {strategy}")
        
        # Create a cache key based on risk categories and strategy
        cache_key = (tuple(risk_categories), strategy)
        
        # Check if we already have cached objectives for this combination
        if cache_key in self.attack_objectives_cache:
            cached_data = self.attack_objectives_cache[cache_key]
            self.logger.info(f"CACHE HIT - Found {len(cached_data)} cached objectives")
            self.logger.info(f"Returning {min(num_rows, len(cached_data))} objectives from cache")
            self.logger.info("Sample cached objectives:")
            for i, obj in enumerate(cached_data[:min(3, len(cached_data))]):
                self.logger.info(f"  [{i}] {obj[:100]}...")
            self.logger.info("=" * 80)
            return cached_data[:num_rows]  # Return only the requested number of rows
        
        self.logger.info(f"CACHE MISS - Need to fetch attack objectives from RAI client")

        # Fetch objectives from RAI client
        try:
            self.logger.info(f"Making API call to get_attack_objectives with:")
            self.logger.info(f"  - risk_categories={risk_categories}")
            self.logger.info(f"  - application_scenario={application_scenario}")
            self.logger.info(f"  - strategy={strategy}")
            
            objectives_response = await self.rai_client.get_attack_objectives(
                risk_categories=risk_categories,
                application_scenario=application_scenario,
                strategy=strategy
            )
            
            self.logger.info(f"API call successful - received response of type: {type(objectives_response)}")
            if isinstance(objectives_response, dict):
                self.logger.info(f"Response keys: {objectives_response.keys()}")
                if "objectives" in objectives_response:
                    self.logger.info(f"Found {len(objectives_response['objectives'])} objectives in response")
            elif isinstance(objectives_response, list):
                self.logger.info(f"Received list with {len(objectives_response)} objectives")
            else:
                self.logger.info(f"Response is of unexpected type: {type(objectives_response)}")
                
        except Exception as e:
            self.logger.error(f"Error calling get_attack_objectives: {str(e)}")
            self.logger.error(f"Exception type: {type(e)}")
            self.logger.exception("Stack trace:")
            objectives_response = {
                "objectives": [
                    {
                        "risk_category": cat,
                        "conversation_starter": f"This is a mocked attack objective for {cat}",
                        "metadata": {
                            "category": cat
                        }
                    } for cat in risk_categories
                ]
            }
            self.logger.info(f"Using mock response with {len(objectives_response['objectives'])} objectives")
        
        # Process the response
        filtered_objectives = []
        objectives_by_category = {cat: [] for cat in risk_categories}
        uncategorized_objectives = []

        # Detailed inspection of the response
        self.logger.info("Response inspection:")
        if isinstance(objectives_response, dict):
            self.logger.info(f"Response structure: {json.dumps(list(objectives_response.keys()))}")
            if "objectives" in objectives_response:
                sample_obj = objectives_response["objectives"][0] if objectives_response["objectives"] else {}
                self.logger.info(f"Sample objective structure: {json.dumps(list(sample_obj.keys()) if sample_obj else {})}")
        elif isinstance(objectives_response, list) and objectives_response:
            sample_obj = objectives_response[0]
            self.logger.info(f"Sample objective structure: {json.dumps(list(sample_obj.keys()) if sample_obj else {})}")

        # Handle different response formats
        if isinstance(objectives_response, list):
            self.logger.info(f"Processing list-format response with {len(objectives_response)} items")
            # Process list format
            for obj in objectives_response:
                target_harms = obj.get("Metadata", {}).get("TargetHarms", [])
                if not target_harms:
                    self.logger.info("No TargetHarms found, checking for Messages")
                    content = obj.get("Messages", [{}])[0].get("Content", "")
                    if content:
                        self.logger.info(f"Found uncategorized objective: {content[:50]}...")
                        uncategorized_objectives.append(content)
                    continue
                
                # Track which categories this objective belongs to
                matched_categories = []
                for harm in target_harms:
                    cat = harm.get("RiskType", "").lower()
                    if cat in risk_categories:
                        matched_categories.append(cat)
                        self.logger.info(f"Matched category: {cat}")
                
                if matched_categories:
                    content = obj.get("Messages", [{}])[0].get("Content", "")
                    if content:
                        filtered_objectives.append(obj)
                        for cat in matched_categories:
                            objectives_by_category[cat].append(content)
                            self.logger.info(f"Added objective to category {cat}: {content[:50]}...")
                            
        elif isinstance(objectives_response, dict) and "objectives" in objectives_response:
            self.logger.info(f"Processing dict-format response with {len(objectives_response['objectives'])} items")
            # Process dictionary format with "objectives" key
            for obj in objectives_response["objectives"]:
                cat = obj.get("risk_category", "").lower()
                content = obj.get("conversation_starter", "")
                
                if cat and cat in risk_categories and content:
                    objectives_by_category[cat].append(content)
                    self.logger.info(f"Added objective to category {cat}: {content[:50]}...")
                elif content:
                    uncategorized_objectives.append(content)
                    self.logger.info(f"Found uncategorized objective: {content[:50]}...")
        
        # Log summary of what we found
        self.logger.info("OBJECTIVE COUNTS BY CATEGORY:")
        for cat in risk_categories:
            self.logger.info(f"  - {cat}: {len(objectives_by_category[cat])} objectives")
        self.logger.info(f"  - uncategorized: {len(uncategorized_objectives)} objectives")
            
        # Build a balanced set of objectives
        all_prompts = []
        if risk_categories:
            prompts_per_category = max(1, num_rows // len(risk_categories))
            self.logger.info(f"Target prompts per category: {prompts_per_category}")
            remaining_slots = num_rows
            
            for cat in risk_categories:
                cat_objectives = objectives_by_category[cat]
                num_to_add = min(prompts_per_category, len(cat_objectives), remaining_slots)
                
                if len(cat_objectives) < prompts_per_category:
                    self.logger.info(f"⚠️ Category {cat} has fewer objectives ({len(cat_objectives)}) than desired ({prompts_per_category})")
                
                self.logger.info(f"Adding {num_to_add} objectives for {cat}")
                
                # Show which ones we're selecting
                for i in range(num_to_add):
                    if i < len(cat_objectives):
                        self.logger.info(f"  [{cat}][{i}] {cat_objectives[i][:50]}...")
                
                all_prompts.extend(cat_objectives[:num_to_add])
                remaining_slots -= num_to_add
            
            # Fill any remaining slots with uncategorized objectives
            if remaining_slots > 0 and uncategorized_objectives:
                num_to_add = min(remaining_slots, len(uncategorized_objectives))
                self.logger.info(f"Adding {num_to_add} uncategorized objectives to fill remaining {remaining_slots} slots")
                all_prompts.extend(uncategorized_objectives[:num_to_add])
        
        # If we couldn't fill all slots with categorized objectives, add uncategorized ones
        if not all_prompts and uncategorized_objectives:
            self.logger.info(f"No categorized objectives found, using {min(num_rows, len(uncategorized_objectives))} uncategorized objectives")
            all_prompts = uncategorized_objectives[:num_rows]
        
        total_objectives = len(all_prompts)
        self.logger.info(f"FINAL RESULTS: Retrieved a total of {total_objectives} attack objectives")
        
        # Show final objectives for debugging
        self.logger.info("Final objectives:")
        for i, obj in enumerate(all_prompts):
            self.logger.info(f"  [{i}] {obj[:100]}...")
        
        # Cache the full set of objectives for future use
        self.attack_objectives_cache[cache_key] = all_prompts
        self.logger.info("Objectives cached for future use")
        self.logger.info("=" * 80)
        
        return all_prompts

    def _message_to_dict(self, message: ChatMessage):
        return {
            "role": message.role,
            "content": message.content,
        }

    def _get_converters_for_budget(self, attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]) -> List[Union[PromptConverter, List[PromptConverter]]]:
        converters = [] 
        seen_strategies = set()
        if AttackStrategy.LOW in attack_strategies:
            attack_strategies.extend([AttackStrategy.Base64, AttackStrategy.Flip, AttackStrategy.Morse])
            attack_strategies.remove(AttackStrategy.LOW)
        if AttackStrategy.MEDIUM in attack_strategies:
            attack_strategies.extend([AttackStrategy.Math, AttackStrategy.Tense])
            attack_strategies.remove(AttackStrategy.MEDIUM)
        if AttackStrategy.HIGH in attack_strategies:
            attack_strategies.extend([AttackStrategy.Compose([AttackStrategy.Math, AttackStrategy.Tense])])
            attack_strategies.remove(AttackStrategy.HIGH)

        ## Baseline is always included    
        attack_strategies.append(AttackStrategy.Baseline)

        for strategy in attack_strategies:
            if isinstance(strategy, List) and tuple(strategy) not in seen_strategies: # For composed strategies
                converters.append([self._strategy_converter_map()[s] for s in strategy])
                seen_strategies.add(tuple(strategy))
            elif isinstance(strategy, AttackStrategy) and strategy not in seen_strategies: # For single strategies
                converters.append(self._strategy_converter_map()[strategy])
                seen_strategies.add(strategy)
            else:
                self.logger.info(f"Strategy {strategy} already used in attack. Skipping")
        self.logger.info(f"Using converters: {converters}")
        return converters

    async def _prompt_sending_orchestrator(self, chat_target:PromptChatTarget, all_prompts: List[str], converter: Union[PromptConverter, List[PromptConverter]]) -> Orchestrator:
        self.logger.info("Sending prompts via PromptSendingOrchestrator")
        orchestrator = PromptSendingOrchestrator(
            objective_target=chat_target,
            prompt_converters=[converter] if converter and isinstance(converter, PromptConverter) else converter if converter else []
        )
        await orchestrator.send_prompts_async(prompt_list=all_prompts)
        return orchestrator
    
    def _write_pyrit_outputs_to_file(self, orchestrator: Orchestrator, converter: Union[PromptConverter, List[PromptConverter]]) -> Union[str, os.PathLike]:
        orchestrator_name = orchestrator.get_identifier()["__type__"]
        if converter:
            if not isinstance(converter, list):
                converter_name = converter.get_identifier()["__type__"]
            else: 
                converter_name = "".join([c.get_identifier()["__type__"] for c in converter])
        else: 
            converter_name = BASELINE_IDENTIFIER
        base_path = f"{orchestrator_name}_{converter_name}"
        output_path = f"{base_path}{DATA_EXT}"

        memory = orchestrator.get_memory()

        # Get conversations as a List[List[ChatMessage]]
        conversations = [[item.to_chat_message() for item in group] for conv_id, group in itertools.groupby(memory, key=lambda x: x.conversation_id)]
        
        #Convert to json lines
        json_lines = ""
        for conversation in conversations: # each conversation is a List[ChatMessage]
            json_lines += json.dumps({"conversation": {"messages": [self._message_to_dict(message) for message in conversation]}}) + "\n"

        with Path(output_path).open("w") as f:
            f.writelines(json_lines)

        orchestrator.dispose_db_engine()
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
    
    def _get_orchestrators_for_budget(self, attack_strategy: List[Union[AttackStrategy, List[AttackStrategy]]]) -> List[Callable]:
        call_to_orchestrators = []
        #TODO: For now we are just using PromptSendingOrchestrator for each budget level
        if AttackStrategy.LOW in attack_strategy:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        elif AttackStrategy.MEDIUM in attack_strategy:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        elif AttackStrategy.HIGH in attack_strategy:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        else:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        return call_to_orchestrators
    
    async def _process_attack(
            self, 
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
            call_orchestrator: Callable, 
            converter: Union[PromptConverter, List[PromptConverter]], 
            all_prompts: List[str],
            evaluation_name: Optional[str] = None,
            data_only: bool = False, 
            output_path: Optional[Union[str, os.PathLike]] = None) -> Union[Dict[str, EvaluationResult], Dict[str, str], Dict[str, Union[str,os.PathLike]]]:
        orchestrator = await call_orchestrator(self.chat_target, all_prompts, converter)
        data_path = self._write_pyrit_outputs_to_file(orchestrator, converter)
        return await super().__call__(
            target=target,
            evaluation_name=evaluation_name,
            data_only=data_only,
            data_path=data_path,
            output_path=output_path
        )

    async def attack(
            self,             
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
            evaluation_name: Optional[str] = None,
            num_turns : int = 1,
            num_rows: int = 100,
            attack_strategy: List[Union[AttackStrategy, List[AttackStrategy]]] = [],
            data_only: bool = False, 
            output_path: Optional[Union[str, os.PathLike]] = None,
            attack_objective_generator = None,
            application_scenario: Optional[str] = None) -> Union[Dict[str, EvaluationResult], Dict[str, Union[str, os.PathLike]]]:
        
        chat_target = self._get_chat_target(target)
        self.chat_target = chat_target
        
        # Initialize a dictionary to track objectives by strategy
        strategy_objectives = {}
        
        # If using attack objective generator, fetch objectives for each strategy to ensure consistent indexing
        if attack_objective_generator:
            self.logger.info("Using AttackObjectiveGenerator to get attack objectives")
            
            # Process each strategy and get its objectives
            for strategy in attack_strategy:
                strategy_name = None
                
                # Handle Composed strategies
                if isinstance(strategy, List):
                    strategy_name = "_".join([s.value for s in strategy])
                else:
                    strategy_name = strategy.value if hasattr(strategy, "value") else str(strategy)
                
                # Fetch objectives for this strategy
                strategy_objectives[strategy_name] = await self._get_attack_objectives(
                    attack_objective_generator=attack_objective_generator,
                    application_scenario=application_scenario,
                    num_rows=num_rows,
                    strategy=strategy_name
                )
            
            # Use the first strategy's objectives as the default list
            all_prompts_list = list(strategy_objectives.values())[0] if strategy_objectives else []
        else:
            self.logger.info("Using default method to get attack prompts")
            all_prompts_list = await self._get_all_prompts(scenario=AdversarialScenario.ADVERSARIAL_QA, num_rows=num_rows)
        
        self.logger.info(f"Configuring PyRIT based on attack strategy: {attack_strategy}")

        converters = self._get_converters_for_budget(attack_strategy)
        orchestrators = self._get_orchestrators_for_budget(attack_strategy)

        tasks = []
        for call_orchestrator, converter in itertools.product(orchestrators, converters):
            # Determine which prompt list to use based on converter
            prompts_to_use = all_prompts_list
            if converter:
                converter_name = None
                if isinstance(converter, list):
                    converter_name = "_".join([c.get_identifier()["__type__"] for c in converter if c])
                else:
                    converter_name = converter.get_identifier()["__type__"] if converter else None
                
                # If we have strategy-specific objectives, use them
                if converter_name and converter_name in strategy_objectives:
                    prompts_to_use = strategy_objectives[converter_name]
            
            tasks.append(
                self._process_attack(
                    target=target,
                    call_orchestrator=call_orchestrator,
                    converter=converter,
                    all_prompts=prompts_to_use,
                    evaluation_name=evaluation_name,
                    data_only=data_only,
                    output_path=output_path
                )
            )

        results = await asyncio.gather(*tasks)
        merged_results = {}
        for d in results:
            merged_results.update(d)

        return merged_results