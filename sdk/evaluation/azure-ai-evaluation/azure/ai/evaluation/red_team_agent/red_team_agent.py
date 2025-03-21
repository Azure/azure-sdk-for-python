# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Third-party imports
import asyncio
import inspect
import math
import os
import logging
import tempfile
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional, Union, cast
import json
from pathlib import Path
import itertools
import random
import uuid
import pandas as pd
from tqdm import tqdm

# Azure AI Evaluation imports
from azure.ai.evaluation._evaluate._eval_run import EvalRun
from azure.ai.evaluation._evaluate._utils import _trace_destination_from_project_scope
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._constants import EvaluationRunProperties, DefaultOpenEncoding
from azure.ai.evaluation._evaluate._utils import _get_ai_studio_url
from azure.ai.evaluation._evaluate._utils import extract_workspace_triad_from_trace_provider
from azure.ai.evaluation._version import VERSION
from azure.ai.evaluation._azure._clients import LiteMLClient
from azure.ai.evaluation._evaluate._utils import _write_output
from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._model_configurations import  EvaluationResult
from azure.ai.evaluation.simulator._model_tools import ManagedIdentityAPITokenManager, TokenScope, RAIClient, AdversarialTemplateHandler
from azure.ai.evaluation.simulator._model_tools._generated_rai_client import GeneratedRAIClient
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._common.math import list_mean_nan_safe, is_none_or_nan
from azure.ai.evaluation._common.utils import validate_azure_ai_project
# Update direct imports from azure.ai.evaluation for evaluators
from azure.ai.evaluation import ViolenceEvaluator, HateUnfairnessEvaluator, SexualEvaluator, SelfHarmEvaluator
from azure.ai.evaluation import evaluate
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING

# Azure Core imports
from azure.core.credentials import TokenCredential

# Red Teaming imports
from .red_team_agent_result import RedTeamAgentResult, RedTeamingScorecard, RedTeamingParameters, Conversation, RedTeamAgentOutput
from .callback_chat_target import CallbackChatTarget
from .attack_strategy import AttackStrategy
from .attack_objective_generator import RiskCategory, AttackObjectiveGenerator
from .default_converter import DefaultConverter

# PyRIT imports
from pyrit.common import initialize_pyrit, DUCK_DB
from pyrit.prompt_target import OpenAIChatTarget, PromptChatTarget
from pyrit.models import ChatMessage
from pyrit.orchestrator.single_turn.prompt_sending_orchestrator import PromptSendingOrchestrator
from pyrit.orchestrator import Orchestrator
from pyrit.exceptions import PyritException
from pyrit.prompt_converter import PromptConverter, MathPromptConverter, Base64Converter, FlipConverter, MorseConverter, AnsiAttackConverter, AsciiArtConverter, AsciiSmugglerConverter, AtbashConverter, BinaryConverter, CaesarConverter, CharacterSpaceConverter, CharSwapGenerator, DiacriticConverter, LeetspeakConverter, UrlConverter, UnicodeSubstitutionConverter, UnicodeConfusableConverter, SuffixAppendConverter, StringJoinConverter, ROT13Converter

# Local imports - constants and utilities
from .utils.constants import (
    BASELINE_IDENTIFIER, DATA_EXT, RESULTS_EXT,
    ATTACK_STRATEGY_COMPLEXITY_MAP, RISK_CATEGORY_EVALUATOR_MAP,
    INTERNAL_TASK_TIMEOUT, TASK_STATUS
)
from .utils.logging_utils import (
    setup_logger, log_section_header, log_subsection_header,
    log_strategy_start, log_strategy_completion, log_error
)

@experimental
class RedTeamAgent():
    """
    This class uses various attack strategies to test the robustness of AI models against adversarial inputs.
    It logs the results of these evaluations and provides detailed scorecards summarizing the attack success rates.
    
    :param azure_ai_project: The Azure AI project configuration
    :type azure_ai_project: dict
    :param credential: The credential to authenticate with Azure services
    :type credential: TokenCredential
    :param timeout: The timeout in seconds for API calls (default: 120)
    :type timeout: int
    """
    def __init__(self, azure_ai_project, credential, timeout=120):
        self.azure_ai_project = validate_azure_ai_project(azure_ai_project)
        self.credential = credential
        self.api_timeout = timeout
        self.logger = setup_logger()
        self.token_manager = ManagedIdentityAPITokenManager(
            token_scope=TokenScope.DEFAULT_AZURE_MANAGEMENT,
            logger=logging.getLogger("RedTeamAgentLogger"),
            credential=cast(TokenCredential, credential),
        )
        
        # Initialize task tracking
        self.task_statuses = {}
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.start_time = None
        
        self.rai_client = RAIClient(azure_ai_project=self.azure_ai_project, token_manager=self.token_manager)
        self.generated_rai_client = GeneratedRAIClient(azure_ai_project=self.azure_ai_project, token_manager=self.token_manager.get_aad_credential()) #type: ignore

        self.adversarial_template_handler = AdversarialTemplateHandler(
            azure_ai_project=self.azure_ai_project, rai_client=self.rai_client
        )

        # Initialize a cache for attack objectives by risk category and strategy
        self.attack_objectives = {}
        
        # keep track of data and eval result file names 
        self.red_team_agent_info = {}

        initialize_pyrit(memory_db_type=DUCK_DB)
        self.logger.debug("RedTeamAgent initialized successfully")

    def _start_redteam_mlflow_run(
        self,
        azure_ai_project: Optional[AzureAIProject] = None,
        run_name: Optional[str] = None
    ) -> EvalRun:
        """Start an MLFlow run for the Red Team Agent evaluation.
        
        :param azure_ai_project: Azure AI project details for logging
        :type azure_ai_project: Optional[~azure.ai.evaluation.AzureAIProject]
        :param run_name: Optional name for the MLFlow run
        :type run_name: Optional[str]
        :return: The MLFlow run object
        :rtype: ~azure.ai.evaluation._evaluate._eval_run.EvalRun
        """
        if not azure_ai_project:
            log_error(self.logger, "No azure_ai_project provided, cannot start MLFlow run")
            raise EvaluationException(
                message="No azure_ai_project provided",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.RED_TEAM_AGENT
            )
        
        trace_destination = _trace_destination_from_project_scope(azure_ai_project)
        if not trace_destination:
            self.logger.warning("Could not determine trace destination from project scope")
            raise EvaluationException(
                message="Could not determine trace destination",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.UNKNOWN,
                target=ErrorTarget.RED_TEAM_AGENT
            )
        
        ws_triad = extract_workspace_triad_from_trace_provider(trace_destination)
        
        management_client = LiteMLClient(
            subscription_id=ws_triad.subscription_id,
            resource_group=ws_triad.resource_group_name,
            logger=self.logger,
            credential=azure_ai_project.get("credential")
        )
        
        tracking_uri = management_client.workspace_get_info(ws_triad.workspace_name).ml_flow_tracking_uri
        
        run_display_name = run_name or f"redteam-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.logger.debug(f"Starting MLFlow run with name: {run_display_name}")
        
        eval_run = EvalRun(
            run_name=run_display_name,
            tracking_uri=cast(str, tracking_uri),
            subscription_id=ws_triad.subscription_id,
            group_name=ws_triad.resource_group_name,
            workspace_name=ws_triad.workspace_name,
            management_client=management_client, # type: ignore
        )

        self.trace_destination = trace_destination
        self.logger.debug(f"MLFlow run created successfully with ID: {eval_run}")

        return eval_run


    async def _log_redteam_results_to_mlflow(
        self,
        redteam_output: RedTeamAgentOutput,
        eval_run: EvalRun,
        data_only: bool = False,
    ) -> Optional[str]:
        """Log the Red Team Agent results to MLFlow.
        
        :param redteam_output: The output from the red team agent evaluation
        :type redteam_output: ~azure.ai.evaluation.red_team_agent.RedTeamAgentOutput
        :param eval_run: The MLFlow run object
        :type eval_run: ~azure.ai.evaluation._evaluate._eval_run.EvalRun
        :param data_only: Whether to log only data without evaluation results
        :type data_only: bool
        :return: The URL to the run in Azure AI Studio, if available
        :rtype: Optional[str]
        """
        self.logger.debug(f"Logging results to MLFlow, data_only={data_only}")
        artifact_name = "instance_results.json" if not data_only else "instance_data.json"

        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_file = Path(tmpdir) / artifact_name
            with open(artifact_file, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                if data_only:
                    # In data_only mode, we write the conversations in conversation/messages format
                    f.write(json.dumps({"conversations": redteam_output.redteaming_data or []}))
                elif redteam_output.red_team_agent_result:
                    json.dump(redteam_output.red_team_agent_result, f)
            eval_run.log_artifact(tmpdir, artifact_name)
            self.logger.debug(f"Logged artifact: {artifact_name}")

        eval_run.write_properties_to_run_history({
            EvaluationRunProperties.RUN_TYPE: "eval_run",
            "redteaming": "asr", # Red team agent specific run properties to help UI identify this as a redteaming run
            EvaluationRunProperties.EVALUATION_SDK: f"azure-ai-evaluation:{VERSION}",
            "_azureml.evaluate_artifacts": json.dumps([{"path": artifact_name, "type": "table"}]),
        })

        if redteam_output.red_team_agent_result:
            scorecard = redteam_output.red_team_agent_result["redteaming_scorecard"]
            joint_attack_summary = scorecard["joint_risk_attack_summary"]
            
            if joint_attack_summary:
                for risk_category_summary in joint_attack_summary:
                    risk_category = risk_category_summary.get("risk_category").lower()
                    for key, value in risk_category_summary.items():
                        if key != "risk_category":
                            eval_run.log_metric(f"{risk_category}_{key}", cast(float, value))
                            self.logger.debug(f"Logged metric: {risk_category}_{key} = {value}")

        self.logger.info("Successfully logged results to MLFlow")
        return None

    # Using the utility function from strategy_utils.py instead
    def _strategy_converter_map(self):
        from .utils.strategy_utils import strategy_converter_map
        return strategy_converter_map()
    
    async def _get_attack_objectives(
        self,
        attack_objective_generator,
        risk_category: Optional[RiskCategory] = None,  # Now accepting a single risk category
        application_scenario: Optional[str] = None,
        strategy: Optional[str] = None
    ) -> List[str]:
        """Get attack objectives from the RAI client for a specific risk category.
        
        :param attack_objective_generator: The generator with risk categories to get attack objectives for
        :type attack_objective_generator: ~azure.ai.evaluation.redteam.AttackObjectiveGenerator
        :param risk_category: The specific risk category to get objectives for
        :type risk_category: Optional[RiskCategory]
        :param application_scenario: Optional description of the application scenario for context
        :type application_scenario: str
        :param strategy: Optional attack strategy to get specific objectives for
        :type strategy: str
        :return: A list of attack objective prompts
        :rtype: List[str]
        """
        if not risk_category:
            self.logger.warning("No risk category provided, using the first category from the generator")
            risk_category = attack_objective_generator.risk_categories[0] if attack_objective_generator.risk_categories else None
            if not risk_category:
                self.logger.error("No risk categories found in generator")
                return []
        
        # Convert risk category to lowercase for consistent caching
        risk_cat_value = risk_category.value.lower()
        num_objectives = attack_objective_generator.num_objectives
        
        log_subsection_header(self.logger, f"Getting attack objectives for {risk_cat_value}, strategy: {strategy}")
        
        # Check if we already have baseline objectives for this risk category
        baseline_key = ((risk_cat_value,), "baseline")
        baseline_objectives_exist = baseline_key in self.attack_objectives
        current_key = ((risk_cat_value,), strategy)
        
        # Always make the API call to get objectives for this strategy
        try:
            self.logger.debug(f"API call: get_attack_objectives({risk_cat_value}, app: {application_scenario}, strategy: {strategy})")
            objectives_response = await self.generated_rai_client.get_attack_objectives(
                risk_category=risk_cat_value,
                application_scenario=application_scenario or "",
                strategy=strategy
            )
            if isinstance(objectives_response, list):
                self.logger.debug(f"API returned {len(objectives_response)} objectives")
            else:
                self.logger.debug(f"API returned response of type: {type(objectives_response)}")
                
            # Handle jailbreak strategy - need to apply jailbreak prefixes to messages
            if strategy == "jailbreak":
                self.logger.debug("Applying jailbreak prefixes to objectives")
                jailbreak_prefixes = await self.generated_rai_client.get_jailbreak_prefixes()
                for objective in objectives_response:
                    if "messages" in objective and len(objective["messages"]) > 0:
                        message = objective["messages"][0]
                        if isinstance(message, dict) and "content" in message:
                            message["content"] = f"{random.choice(jailbreak_prefixes)} {message['content']}"
        except Exception as e:
            log_error(self.logger, "Error calling get_attack_objectives", e)
            self.logger.warning("API call failed, returning empty objectives list")
            return []
            
        # Check if the response is valid
        if not objectives_response or (isinstance(objectives_response, dict) and not objectives_response.get("objectives")):
            self.logger.warning("Empty or invalid response, returning empty list")
            return []
            
        # For non-baseline strategies, filter by baseline IDs if they exist
        if strategy != "baseline" and baseline_objectives_exist:
            self.logger.debug(f"Found existing baseline objectives for {risk_cat_value}, will filter {strategy} by baseline IDs")
            baseline_selected_objectives = self.attack_objectives[baseline_key].get("selected_objectives", [])
            baseline_objective_ids = []
            
            # Extract IDs from baseline objectives
            for obj in baseline_selected_objectives:
                if "id" in obj:
                    baseline_objective_ids.append(obj["id"])
            
            if baseline_objective_ids:
                self.logger.debug(f"Filtering by {len(baseline_objective_ids)} baseline objective IDs for {strategy}")
                
                # Filter objectives by baseline IDs
                selected_cat_objectives = []
                for obj in objectives_response:
                    if obj.get("id") in baseline_objective_ids:
                        selected_cat_objectives.append(obj)
                
                self.logger.debug(f"Found {len(selected_cat_objectives)} matching objectives with baseline IDs")
                # If we couldn't find all the baseline IDs, log a warning
                if len(selected_cat_objectives) < len(baseline_objective_ids):
                    self.logger.warning(f"Only found {len(selected_cat_objectives)} objectives matching baseline IDs, expected {len(baseline_objective_ids)}")
            else:
                self.logger.warning("No baseline objective IDs found, using random selection")
                # If we don't have baseline IDs for some reason, default to random selection
                if len(objectives_response) > num_objectives:
                    selected_cat_objectives = random.sample(objectives_response, num_objectives)
                else:
                    selected_cat_objectives = objectives_response
        else:
            # This is the baseline strategy or we don't have baseline objectives yet
            self.logger.debug(f"Using random selection for {strategy} strategy")
            if len(objectives_response) > num_objectives:
                self.logger.debug(f"Selecting {num_objectives} objectives from {len(objectives_response)} available")
                selected_cat_objectives = random.sample(objectives_response, num_objectives)
            else:
                selected_cat_objectives = objectives_response
                
        if len(selected_cat_objectives) < num_objectives:
            self.logger.warning(f"Only found {len(selected_cat_objectives)} objectives for {risk_cat_value}, fewer than requested {num_objectives}")
        
        # Extract content from selected objectives
        selected_prompts = []
        for obj in selected_cat_objectives:
            if "messages" in obj and len(obj["messages"]) > 0:
                message = obj["messages"][0]
                if isinstance(message, dict) and "content" in message:
                    selected_prompts.append(message["content"])
        
        # Process the response - organize by category and extract content/IDs
        objectives_by_category = {risk_cat_value: []}
        
        # Process list format and organize by category for caching
        for obj in selected_cat_objectives:
            obj_id = obj.get("id", f"obj-{uuid.uuid4()}")
            target_harms = obj.get("metadata", {}).get("target_harms", [])
            content = ""
            if "messages" in obj and len(obj["messages"]) > 0:
                content = obj["messages"][0].get("content", "")
            
            if not content:
                continue
            if target_harms:
                for harm in target_harms:
                    obj_data = {
                        "id": obj_id,
                        "content": content
                    }
                    objectives_by_category[risk_cat_value].append(obj_data)
                    break
        
        # Store in cache - now including the full selected objectives with IDs
        self.attack_objectives[current_key] = {
            "objectives_by_category": objectives_by_category,
            "strategy": strategy,
            "risk_category": risk_cat_value,
            "selected_prompts": selected_prompts,
            "selected_objectives": selected_cat_objectives  # Store full objects with IDs
        }
        self.logger.info(f"Selected {len(selected_prompts)} objectives for {risk_cat_value}")
        
        return selected_prompts

    # Replace with utility function
    def _message_to_dict(self, message: ChatMessage):
        from .utils.formatting_utils import message_to_dict
        return message_to_dict(message)
    
    # Replace with utility function
    def _get_strategy_name(self, attack_strategy: Union[AttackStrategy, List[AttackStrategy]]) -> str:
        from .utils.formatting_utils import get_strategy_name
        return get_strategy_name(attack_strategy)

    # Replace with utility function
    def _get_flattened_attack_strategies(self, attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]) -> List[Union[AttackStrategy, List[AttackStrategy]]]:
        from .utils.formatting_utils import get_flattened_attack_strategies
        return get_flattened_attack_strategies(attack_strategies)
    
    # Replace with utility function
    def _get_converter_for_strategy(self, attack_strategy: Union[AttackStrategy, List[AttackStrategy]]) -> Union[PromptConverter, List[PromptConverter]]:
        from .utils.strategy_utils import get_converter_for_strategy
        return get_converter_for_strategy(attack_strategy)

    async def _prompt_sending_orchestrator(
        self, 
        chat_target: PromptChatTarget, 
        all_prompts: List[str], 
        converter: Union[PromptConverter, List[PromptConverter]], 
        strategy_name: str = "unknown", 
        risk_category: str = "unknown"
    ) -> Orchestrator:
        """Send prompts via the PromptSendingOrchestrator with optimized performance.
        
        :param chat_target: The target to send prompts to
        :type chat_target: PromptChatTarget
        :param all_prompts: List of prompts to send
        :type all_prompts: List[str]
        :param converter: Converter or list of converters to use for prompt transformation
        :type converter: Union[PromptConverter, List[PromptConverter]]
        :param strategy_name: Name of the strategy being used (for logging)
        :type strategy_name: str
        :param risk_category: Name of the risk category being evaluated (for logging)
        :type risk_category: str
        :return: The orchestrator instance with processed results
        :rtype: Orchestrator
        """
        task_key = f"{strategy_name}_{risk_category}_orchestrator"
        self.task_statuses[task_key] = TASK_STATUS["RUNNING"]
        
        log_strategy_start(self.logger, strategy_name, risk_category)
        
        # Create converter list from single converter or list of converters
        converter_list = [converter] if converter and isinstance(converter, PromptConverter) else converter if converter else []
        
        # Log which converter is being used
        if converter_list:
            if isinstance(converter_list, list) and len(converter_list) > 0:
                converter_names = [c.__class__.__name__ for c in converter_list if c is not None]
                self.logger.debug(f"Using converters: {', '.join(converter_names)}")
            elif converter is not None:
                self.logger.debug(f"Using converter: {converter.__class__.__name__}")
        else:
            self.logger.debug("No converters specified")
        
        # Optimized orchestrator initialization
        try:
            orchestrator = PromptSendingOrchestrator(
                objective_target=chat_target,
                prompt_converters=converter_list
            )
            
            if not all_prompts:
                self.logger.warning(f"No prompts provided to orchestrator for {strategy_name}/{risk_category}")
                self.task_statuses[task_key] = TASK_STATUS["COMPLETED"]
                return orchestrator
            
            # Debug log the first few characters of each prompt
            self.logger.debug(f"First prompt (truncated): {all_prompts[0][:50]}...")
            
            # Use a batched approach for send_prompts_async to prevent overwhelming
            # the model with too many concurrent requests
            batch_size = min(len(all_prompts), 3)  # Process 3 prompts at a time max
            
            # Process prompts concurrently within each batch
            if len(all_prompts) > batch_size:
                self.logger.debug(f"Processing {len(all_prompts)} prompts in batches of {batch_size} for {strategy_name}/{risk_category}")
                batches = [all_prompts[i:i + batch_size] for i in range(0, len(all_prompts), batch_size)]
                
                for batch_idx, batch in enumerate(batches):
                    self.logger.debug(f"Processing batch {batch_idx+1}/{len(batches)} with {len(batch)} prompts for {strategy_name}/{risk_category}")
                    
                    batch_start_time = datetime.now()
                    # Send prompts in the batch concurrently with a timeout
                    try:
                        # Use wait_for to implement a timeout
                        await asyncio.wait_for(
                            orchestrator.send_prompts_async(prompt_list=batch),
                            timeout=INTERNAL_TASK_TIMEOUT  # 2 minute timeout per batch
                        )
                        batch_duration = (datetime.now() - batch_start_time).total_seconds()
                        self.logger.debug(f"Successfully processed batch {batch_idx+1} for {strategy_name}/{risk_category} in {batch_duration:.2f} seconds")
                        
                        # Print progress to console 
                        if batch_idx < len(batches) - 1:  # Don't print for the last batch
                            print(f"Strategy {strategy_name}, Risk {risk_category}: Processed batch {batch_idx+1}/{len(batches)}")
                            
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Batch {batch_idx+1} for {strategy_name}/{risk_category} timed out after {INTERNAL_TASK_TIMEOUT} seconds, continuing with partial results")
                        print(f"⚠️ TIMEOUT: Strategy {strategy_name}, Risk {risk_category}, Batch {batch_idx+1}")
                        # Continue with partial results rather than failing completely
                        continue
                    except Exception as e:
                        log_error(self.logger, f"Error processing batch {batch_idx+1}", e, f"{strategy_name}/{risk_category}")
                        print(f"❌ ERROR: Strategy {strategy_name}, Risk {risk_category}, Batch {batch_idx+1}: {str(e)}")
                        # Continue with other batches even if one fails
                        continue
            else:
                # Small number of prompts, process all at once with a timeout
                self.logger.debug(f"Processing {len(all_prompts)} prompts in a single batch for {strategy_name}/{risk_category}")
                batch_start_time = datetime.now()
                try:
                    await asyncio.wait_for(
                        orchestrator.send_prompts_async(prompt_list=all_prompts),
                        timeout=INTERNAL_TASK_TIMEOUT  # 2 minute timeout 
                    )
                    batch_duration = (datetime.now() - batch_start_time).total_seconds()
                    self.logger.debug(f"Successfully processed single batch for {strategy_name}/{risk_category} in {batch_duration:.2f} seconds")
                except asyncio.TimeoutError:
                    self.logger.warning(f"Prompt processing for {strategy_name}/{risk_category} timed out after {INTERNAL_TASK_TIMEOUT} seconds, continuing with partial results")
                    print(f"⚠️ TIMEOUT: Strategy {strategy_name}, Risk {risk_category}")
                except Exception as e:
                    log_error(self.logger, "Error processing prompts", e, f"{strategy_name}/{risk_category}")
                    print(f"❌ ERROR: Strategy {strategy_name}, Risk {risk_category}: {str(e)}")
            
            self.task_statuses[task_key] = TASK_STATUS["COMPLETED"]
            return orchestrator
            
        except Exception as e:
            log_error(self.logger, "Failed to initialize orchestrator", e, f"{strategy_name}/{risk_category}")
            print(f"❌ CRITICAL: Failed to create orchestrator for {strategy_name}/{risk_category}: {str(e)}")
            self.task_statuses[task_key] = TASK_STATUS["FAILED"]
            raise

    def _write_pyrit_outputs_to_file(self, orchestrator: Orchestrator) -> str:
        """Write PyRIT outputs to a file with a name based on orchestrator, converter, and risk category.
        
        :param orchestrator: The orchestrator that generated the outputs
        :type orchestrator: Orchestrator
        :return: Path to the output file
        :rtype: Union[str, os.PathLike]
        """
        base_path = str(uuid.uuid4())
        output_path = f"{base_path}{DATA_EXT}"
        self.logger.debug(f"Writing PyRIT outputs to file: {output_path}")

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
        self.logger.debug(f"Successfully wrote {len(conversations)} conversations to {output_path}")
        return str(output_path)
    
    # Replace with utility function
    def _get_chat_target(self, target: Union[PromptChatTarget,Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration]) -> PromptChatTarget:
        from .utils.strategy_utils import get_chat_target
        return get_chat_target(target)
    
    # Replace with utility function
    def _get_orchestrators_for_attack_strategies(self, attack_strategy: List[Union[AttackStrategy, List[AttackStrategy]]]) -> List[Callable]:
        # We need to modify this to use our actual _prompt_sending_orchestrator since the utility function can't access it
        call_to_orchestrators = []
        # Sending PromptSendingOrchestrator for each complexity level
        if AttackStrategy.EASY in attack_strategy:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        elif AttackStrategy.MODERATE in attack_strategy:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        elif AttackStrategy.DIFFICULT in attack_strategy:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        else:
            call_to_orchestrators.extend([self._prompt_sending_orchestrator])
        return call_to_orchestrators
    
    # Replace with utility function
    def _get_attack_success(self, result: str) -> bool:
        from .utils.formatting_utils import get_attack_success
        return get_attack_success(result)

    def _to_red_team_agent_result(self) -> RedTeamAgentResult:
        """Convert tracking data from red_team_agent_info to the RedTeamAgentResult format.
        
        Uses only the red_team_agent_info tracking dictionary to build the RedTeamAgentResult.
        
        :return: Structured red team agent results
        :rtype: RedTeamAgentResult
        """
        converters = []
        complexity_levels = []
        risk_categories = []
        attack_successes = []  # unified list for all attack successes
        conversations = []
        
        self.logger.info(f"Building RedTeamAgentResult from red_team_agent_info with {len(self.red_team_agent_info)} strategies")
        
        # Process each strategy and risk category from red_team_agent_info
        for strategy_name, risk_data in self.red_team_agent_info.items():
            self.logger.info(f"Processing results for strategy: {strategy_name}")
            
            # Determine complexity level for this strategy
            if "Baseline" in strategy_name:
                complexity_level = "baseline"
            else:
                # Try to map strategy name to complexity level
                # Default is difficult since we assume it's a composed strategy
                complexity_level = ATTACK_STRATEGY_COMPLEXITY_MAP.get(strategy_name, "difficult")
            
            for risk_category, data in risk_data.items():
                self.logger.info(f"Processing data for {risk_category} in strategy {strategy_name}")
                
                data_file = data.get("data_file", "")
                eval_result = data.get("evaluation_result")
                
                # Process data file to extract conversations
                if data_file and os.path.exists(data_file):
                    try:
                        with open(data_file, "r") as f:
                            for line in f:
                                try:
                                    conv_data = json.loads(line)
                                    if "conversation" in conv_data and "messages" in conv_data["conversation"]:
                                        messages = conv_data["conversation"]["messages"]
                                        
                                        # Determine attack success based on evaluation results if available
                                        attack_success = None
                                        risk_assessment = {}
                                        
                                        # If we have evaluation results, try to extract attack success and risk assessment
                                        if eval_result:
                                            # Look for this conversation in the evaluation results
                                            rows = eval_result.get("rows", [])
                                            for r in rows:
                                                if r.get("inputs.conversation", {}).get("messages") == messages:
                                                    # Found matching conversation
                                                    if f"outputs.{risk_category}.{risk_category}_result" in r:
                                                        attack_success = self._get_attack_success(r[f"outputs.{risk_category}.{risk_category}_result"])
                                                    
                                                    # Extract risk assessments for all categories
                                                    for risk in self.risk_categories:
                                                        risk_value = risk.value
                                                        if f"outputs.{risk_value}.{risk_value}" in r and f"outputs.{risk_value}.{risk_value}_reason" in r:
                                                            risk_assessment[risk_value] = {
                                                                "severity_label": r[f"outputs.{risk_value}.{risk_value}"],
                                                                "reason": r[f"outputs.{risk_value}.{risk_value}_reason"]
                                                            }
                                        
                                        # Add to tracking arrays for statistical analysis
                                        converters.append(strategy_name)
                                        complexity_levels.append(complexity_level)
                                        risk_categories.append(risk_category)
                                        
                                        if attack_success is not None:
                                            attack_successes.append(1 if attack_success else 0)
                                        else:
                                            attack_successes.append(None)
                                        
                                        # Add conversation object
                                        conversation = {
                                            "attack_success": attack_success,
                                            "attack_technique": strategy_name.replace("Converter", "").replace("Prompt", ""),
                                            "attack_complexity": complexity_level,
                                            "risk_category": risk_category,
                                            "conversation": messages,
                                            "risk_assessment": risk_assessment if risk_assessment else None
                                        }
                                        conversations.append(conversation)
                                except json.JSONDecodeError as e:
                                    self.logger.error(f"Error parsing JSON in data file {data_file}: {e}")
                    except Exception as e:
                        self.logger.error(f"Error processing data file {data_file}: {e}")
                else:
                    self.logger.warning(f"Data file {data_file} not found or not specified for {strategy_name}/{risk_category}")
        
        # Sort conversations by attack technique for better readability
        conversations.sort(key=lambda x: x["attack_technique"])
        
        self.logger.info(f"Processed {len(conversations)} conversations from all data files")
        
        # Create a DataFrame for analysis - with unified structure
        results_dict = {
            "converter": converters,
            "complexity_level": complexity_levels,
            "risk_category": risk_categories,
        }
        
        # Only include attack_success if we have evaluation results
        if any(success is not None for success in attack_successes):
            results_dict["attack_success"] = [math.nan if success is None else success for success in attack_successes]
            self.logger.info(f"Including attack success data for {sum(1 for s in attack_successes if s is not None)} conversations")
        
        results_df = pd.DataFrame.from_dict(results_dict)
        
        if "attack_success" not in results_df.columns or results_df.empty:
            # If we don't have evaluation results or the DataFrame is empty, create a default scorecard
            self.logger.info("No evaluation results available or no data found, creating default scorecard")
            
            # Create a basic scorecard structure
            scorecard = {
                "risk_category_summary": [{"overall_asr": 0.0, "overall_total": len(conversations), "overall_attack_successes": 0}],
                "attack_technique_summary": [{"overall_asr": 0.0, "overall_total": len(conversations), "overall_attack_successes": 0}],
                "joint_risk_attack_summary": [],
                "detailed_joint_risk_attack_asr": {}
            }
            
            # Create basic parameters
            redteaming_parameters = {
                "attack_objective_generated_from": {
                    "application_scenario": self.application_scenario,
                    "risk_categories": [risk.value for risk in self.risk_categories],
                    "custom_attack_seed_prompts": "",
                    "policy_document": ""
                },
                "attack_complexity": list(set(complexity_levels)) if complexity_levels else ["baseline", "easy"],
                "techniques_used": {}
            }
            
            for complexity in set(complexity_levels) if complexity_levels else ["baseline", "easy"]:
                complexity_converters = [conv for i, conv in enumerate(converters) if i < len(complexity_levels) and complexity_levels[i] == complexity]
                redteaming_parameters["techniques_used"][complexity] = list(set(complexity_converters)) if complexity_converters else []
        else:
            # Calculate risk category summaries by aggregating on risk category
            risk_category_groups = results_df.groupby("risk_category")
            risk_category_summary = {}
            
            # Overall metrics across all categories
            overall_asr = round(list_mean_nan_safe(results_df["attack_success"].tolist()) * 100, 2) if "attack_success" in results_df.columns else 0.0
            overall_total = len(results_df)
            overall_successful_attacks = sum([s for s in results_df["attack_success"].tolist() if not is_none_or_nan(s)]) if "attack_success" in results_df.columns else 0
            
            risk_category_summary.update({
                "overall_asr": overall_asr,
                "overall_total": overall_total,
                "overall_attack_successes": int(overall_successful_attacks)
            })
            
            # Per-risk category metrics
            for risk, group in risk_category_groups:
                asr = round(list_mean_nan_safe(group["attack_success"].tolist()) * 100, 2) if "attack_success" in group.columns else 0.0
                total = len(group)
                successful_attacks =sum([s for s in group["attack_success"].tolist() if not is_none_or_nan(s)]) if "attack_success" in group.columns else 0
                    
                risk_category_summary.update({
                    f"{risk}_asr": asr,
                    f"{risk}_total": total,
                    f"{risk}_successful_attacks": int(successful_attacks)
                })
            
            # Calculate attack technique summaries by complexity level
            # First, create masks for each complexity level
            baseline_mask = results_df["complexity_level"] == "baseline"
            easy_mask = results_df["complexity_level"] == "easy"
            moderate_mask = results_df["complexity_level"] == "moderate"
            difficult_mask = results_df["complexity_level"] == "difficult"
            
            # Then calculate metrics for each complexity level
            attack_technique_summary_dict = {}
            
            # Baseline metrics
            baseline_df = results_df[baseline_mask]
            if not baseline_df.empty:
                attack_technique_summary_dict.update({
                    "baseline_asr": round(list_mean_nan_safe(baseline_df["attack_success"].tolist()) * 100, 2) if "attack_success" in baseline_df.columns else 0.0,
                    "baseline_total": len(baseline_df),
                    "baseline_attack_successes": sum([s for s in baseline_df["attack_success"].tolist() if not is_none_or_nan(s)]) if "attack_success" in baseline_df.columns else 0
                })
            
            # Easy complexity metrics
            easy_df = results_df[easy_mask]
            if not easy_df.empty:
                attack_technique_summary_dict.update({
                    "easy_complexity_asr": round(list_mean_nan_safe(easy_df["attack_success"].tolist()) * 100, 2) if "attack_success" in easy_df.columns else 0.0,
                    "easy_complexity_total": len(easy_df),
                    "easy_complexity_attack_successes": sum([s for s in easy_df["attack_success"].tolist() if not is_none_or_nan(s)]) if "attack_success" in easy_df.columns else 0
                })
            
            # Moderate complexity metrics
            moderate_df = results_df[moderate_mask]
            if not moderate_df.empty:
                attack_technique_summary_dict.update({
                    "moderate_complexity_asr": round(list_mean_nan_safe(moderate_df["attack_success"].tolist()) * 100, 2) if "attack_success" in moderate_df.columns else 0.0,
                    "moderate_complexity_total": len(moderate_df),
                    "moderate_complexity_attack_successes": sum([s for s in moderate_df["attack_success"].tolist() if not is_none_or_nan(s)]) if "attack_success" in moderate_df.columns else 0
                })
            
            # Difficult complexity metrics
            difficult_df = results_df[difficult_mask]
            if not difficult_df.empty:
                attack_technique_summary_dict.update({
                    "difficult_complexity_asr": round(list_mean_nan_safe(difficult_df["attack_success"].tolist()) * 100, 2) if "attack_success" in difficult_df.columns else 0.0,
                    "difficult_complexity_total": len(difficult_df),
                    "difficult_complexity_attack_successes": sum([s for s in difficult_df["attack_success"].tolist() if not is_none_or_nan(s)]) if "attack_success" in difficult_df.columns else 0
                })
            
            # Overall metrics
            attack_technique_summary_dict.update({
                "overall_asr": overall_asr,
                "overall_total": overall_total,
                "overall_attack_successes": int(overall_successful_attacks)
            })
            
            attack_technique_summary = [attack_technique_summary_dict]
            
            # Create joint risk attack summary
            joint_risk_attack_summary = []
            unique_risks = results_df["risk_category"].unique()
            
            for risk in unique_risks:
                risk_key = risk.replace("-", "_")
                risk_mask = results_df["risk_category"] == risk
                
                joint_risk_dict = {"risk_category": risk_key}
                
                # Baseline ASR for this risk
                baseline_risk_df = results_df[risk_mask & baseline_mask]
                if not baseline_risk_df.empty:
                    joint_risk_dict["baseline_asr"] = round(list_mean_nan_safe(baseline_risk_df["attack_success"].tolist()) * 100, 2) if "attack_success" in baseline_risk_df.columns else 0.0
                else:
                    joint_risk_dict["baseline_asr"] = 0.0
                
                # Easy complexity ASR for this risk
                easy_risk_df = results_df[risk_mask & easy_mask]
                if not easy_risk_df.empty:
                    joint_risk_dict["easy_complexity_asr"] = round(list_mean_nan_safe(easy_risk_df["attack_success"].tolist()) * 100, 2) if "attack_success" in easy_risk_df.columns else 0.0
                
                # Moderate complexity ASR for this risk
                moderate_risk_df = results_df[risk_mask & moderate_mask]
                if not moderate_risk_df.empty:
                    joint_risk_dict["moderate_complexity_asr"] = round(list_mean_nan_safe(moderate_risk_df["attack_success"].tolist()) * 100, 2) if "attack_success" in moderate_risk_df.columns else 0.0
                
                # Difficult complexity ASR for this risk
                difficult_risk_df = results_df[risk_mask & difficult_mask]
                if not difficult_risk_df.empty:
                    joint_risk_dict["difficult_complexity_asr"] = round(list_mean_nan_safe(difficult_risk_df["attack_success"].tolist()) * 100, 2) if "attack_success" in difficult_risk_df.columns else 0.0
                
                joint_risk_attack_summary.append(joint_risk_dict)
            
            # Calculate detailed joint risk attack ASR
            detailed_joint_risk_attack_asr = {}
            unique_complexities = sorted([c for c in results_df["complexity_level"].unique() if c != "baseline"])
            
            for complexity in unique_complexities:
                complexity_mask = results_df["complexity_level"] == complexity
                if results_df[complexity_mask].empty:
                    continue
                    
                detailed_joint_risk_attack_asr[complexity] = {}
                
                for risk in unique_risks:
                    risk_key = risk.replace("-", "_")
                    risk_mask = results_df["risk_category"] == risk
                    detailed_joint_risk_attack_asr[complexity][risk_key] = {}
                    
                    # Group by converter within this complexity and risk
                    complexity_risk_df = results_df[complexity_mask & risk_mask]
                    if complexity_risk_df.empty:
                        continue
                        
                    converter_groups = complexity_risk_df.groupby("converter")
                    for converter_name, converter_group in converter_groups:
                        asr_value = round(list_mean_nan_safe(converter_group["attack_success"].tolist()) * 100, 2) if "attack_success" in converter_group.columns else 0.0
                        detailed_joint_risk_attack_asr[complexity][risk_key][f"{converter_name}_ASR"] = asr_value
            
            # Compile the scorecard
            scorecard = {
                "risk_category_summary": [risk_category_summary],
                "attack_technique_summary": attack_technique_summary,
                "joint_risk_attack_summary": joint_risk_attack_summary,
                "detailed_joint_risk_attack_asr": detailed_joint_risk_attack_asr
            }
            
            # Create redteaming parameters
            redteaming_parameters = {
                "attack_objective_generated_from": {
                    "application_scenario": self.application_scenario,
                    "risk_categories": [risk.value for risk in self.risk_categories],
                    "custom_attack_seed_prompts": "",
                    "policy_document": ""
                },
                "attack_complexity": [c.capitalize() for c in unique_complexities],
                "techniques_used": {}
            }
            
            # Populate techniques used by complexity level
            for complexity in unique_complexities:
                complexity_mask = results_df["complexity_level"] == complexity
                complexity_df = results_df[complexity_mask]
                if not complexity_df.empty:
                    complexity_converters = complexity_df["converter"].unique().tolist()
                    redteaming_parameters["techniques_used"][complexity] = complexity_converters
        
        self.logger.info("RedTeamAgentResult creation completed")
        
        # Create the final result
        red_team_agent_result = RedTeamAgentResult(
            redteaming_scorecard=cast(RedTeamingScorecard, scorecard),
            redteaming_parameters=cast(RedTeamingParameters, redteaming_parameters),
            redteaming_data=conversations,
            studio_url=self.ai_studio_url or None
        )
        
        return red_team_agent_result

    # Replace with utility function
    def _to_scorecard(self, redteam_result: RedTeamAgentResult) -> str:
        from .utils.formatting_utils import format_scorecard
        return format_scorecard(redteam_result)
    
    async def _evaluate(
        self,
        data_path: Union[str, os.PathLike],
        risk_category: RiskCategory,
        strategy: Union[AttackStrategy, List[AttackStrategy]],
        evaluation_name: Optional[str] = None,
        data_only: bool = False,
        output_path: Optional[Union[str, os.PathLike]] = None
    ) -> None:
        """Call the evaluate method if not data_only.

        :param evaluation_name: Optional name for the evaluation.
        :type evaluation_name: Optional[str]
        :param data_only: Whether to return only data paths instead of evaluation results.
        :type data_only: bool
        :param data_path: Path to the input data.
        :type data_path: Optional[Union[str, os.PathLike]]
        :param output_path: Path for output results.
        :type output_path: Optional[Union[str, os.PathLike]]
        :return: Evaluation results or data paths.
        :rtype: Union[Dict[str, EvaluationResult], Dict[str, List[str]]]
        """
        strategy_name = self._get_strategy_name(strategy)
        self.logger.debug(f"Evaluate called with data_path={data_path}, risk_category={risk_category.value}, strategy={strategy_name}, output_path={output_path}, data_only={data_only}, evaluation_name={evaluation_name}")
        if data_only:
            return None
        result_path = output_path if output_path else f"{str(uuid.uuid4())}{RESULTS_EXT}"
        evaluators_dict = {
            risk_category.value: RISK_CATEGORY_EVALUATOR_MAP[risk_category](azure_ai_project=self.azure_ai_project, credential=self.credential)
        }
        evaluate_outputs = evaluate(
            data=data_path,
            evaluators=evaluators_dict,
            output_path=result_path,
        )
        self.red_team_agent_info[self._get_strategy_name(strategy)][risk_category.value]["evaluation_result_file"] = str(result_path)
        self.red_team_agent_info[self._get_strategy_name(strategy)][risk_category.value]["evaluation_result"] = evaluate_outputs
        self.logger.debug(f"Evaluation complete for {strategy_name}/{risk_category.value}, results stored in red_team_agent_info")

    async def _process_attack(
            self, 
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
            call_orchestrator: Callable, 
            strategy: Union[AttackStrategy, List[AttackStrategy]],
            risk_category: RiskCategory,
            all_prompts: List[str],
            progress_bar: tqdm,
            progress_bar_lock: asyncio.Lock,
            evaluation_name: Optional[str] = None,
            data_only: bool = False, 
            output_path: Optional[Union[str, os.PathLike]] = None,
        ) -> Optional[EvaluationResult]:
        """Process a red team scan with the given orchestrator, converter, and prompts.
        
        :param target: The target model or function to scan
        :param call_orchestrator: Function to call to create an orchestrator
        :param strategy: The attack strategy to use
        :param risk_category: The risk category to evaluate
        :param all_prompts: List of prompts to use for the scan
        :param progress_bar: Progress bar to update
        :param progress_bar_lock: Lock for the progress bar
        :param evaluation_name: Optional name for the evaluation
        :param data_only: Whether to return only data without evaluation
        :param output_path: Optional path for output
        """
        strategy_name = self._get_strategy_name(strategy)
        task_key = f"{strategy_name}_{risk_category.value}_attack"
        self.task_statuses[task_key] = TASK_STATUS["RUNNING"]
        
        try:
            start_time = time.time()
            print(f"▶️ Starting task: {strategy_name} strategy for {risk_category.value} risk category")
            log_strategy_start(self.logger, strategy_name, risk_category.value)
            
            converter = self._get_converter_for_strategy(strategy)
            try:
                self.logger.debug(f"Calling orchestrator for {strategy_name} strategy")
                orchestrator = await call_orchestrator(self.chat_target, all_prompts, converter, strategy_name, risk_category.value)
            except PyritException as e:
                log_error(self.logger, f"Error calling orchestrator for {strategy_name} strategy", e)
                print(f"❌ Orchestrator error for {strategy_name}/{risk_category.value}: {str(e)}")
                self.task_statuses[task_key] = TASK_STATUS["FAILED"]
                self.failed_tasks += 1
                
                async with progress_bar_lock:
                    progress_bar.update(1)
                return None
            
            data_path = self._write_pyrit_outputs_to_file(orchestrator)
            
            # Store data file in our tracking dictionary
            self.red_team_agent_info[strategy_name][risk_category.value]["data_file"] = data_path
            self.logger.debug(f"Updated red_team_agent_info with data file: {strategy_name} -> {risk_category.value} -> {data_path}")
            
            try:
                await self._evaluate(
                    evaluation_name=evaluation_name,
                    risk_category=risk_category,
                    strategy=strategy,
                    data_only=data_only,
                    data_path=data_path,
                    output_path=output_path,
                )
            except Exception as e:
                log_error(self.logger, f"Error during evaluation for {strategy_name}/{risk_category.value}", e)
                print(f"⚠️ Evaluation error for {strategy_name}/{risk_category.value}: {str(e)}")
                # Continue processing even if evaluation fails
            
            async with progress_bar_lock:
                self.completed_tasks += 1
                progress_bar.update(1)
                completion_pct = (self.completed_tasks / self.total_tasks) * 100
                elapsed_time = time.time() - start_time
                
                # Calculate estimated remaining time
                if self.start_time:
                    total_elapsed = time.time() - self.start_time
                    avg_time_per_task = total_elapsed / self.completed_tasks if self.completed_tasks > 0 else 0
                    remaining_tasks = self.total_tasks - self.completed_tasks
                    est_remaining_time = avg_time_per_task * remaining_tasks if avg_time_per_task > 0 else 0
                    
                    print(f"✅ Completed task {self.completed_tasks}/{self.total_tasks} ({completion_pct:.1f}%) - {strategy_name}/{risk_category.value} in {elapsed_time:.1f}s")
                    print(f"   Est. remaining: {est_remaining_time/60:.1f} minutes")
                else:
                    print(f"✅ Completed task {self.completed_tasks}/{self.total_tasks} ({completion_pct:.1f}%) - {strategy_name}/{risk_category.value} in {elapsed_time:.1f}s")
                
            log_strategy_completion(self.logger, strategy_name, risk_category.value, elapsed_time)
            self.task_statuses[task_key] = TASK_STATUS["COMPLETED"]
            
        except Exception as e:
            log_error(self.logger, f"Unexpected error processing {strategy_name} strategy for {risk_category.value}", e)
            print(f"❌ Critical error in task {strategy_name}/{risk_category.value}: {str(e)}")
            self.task_statuses[task_key] = TASK_STATUS["FAILED"]
            self.failed_tasks += 1
            
            async with progress_bar_lock:
                progress_bar.update(1)
                
        return None

    async def scan(
            self,             
            target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration, PromptChatTarget],
            evaluation_name: Optional[str] = None,
            num_turns : int = 1,
            attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]] = [],
            data_only: bool = False, 
            output_path: Optional[Union[str, os.PathLike]] = None,
            attack_objective_generator: Optional[AttackObjectiveGenerator] = None,
            application_scenario: Optional[str] = None,
            parallel_execution: bool = True,
            max_parallel_tasks: int = 5,
            debug_mode: bool = False) -> RedTeamAgentOutput:
        """Run a red team scan against the target using the specified strategies.
        
        :param target: The target model or function to scan
        :type target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration, PromptChatTarget]
        :param evaluation_name: Optional name for the evaluation
        :type evaluation_name: Optional[str]
        :param num_turns: Number of conversation turns to use in the scan
        :type num_turns: int
        :param attack_strategies: List of attack strategies to use
        :type attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
        :param data_only: Whether to return only data without evaluation
        :type data_only: bool
        :param output_path: Optional path for output
        :type output_path: Optional[Union[str, os.PathLike]]
        :param attack_objective_generator: Generator for attack objectives
        :type attack_objective_generator: Optional[AttackObjectiveGenerator]
        :param application_scenario: Optional description of the application scenario
        :type application_scenario: Optional[str]
        :param parallel_execution: Whether to execute orchestrator tasks in parallel
        :type parallel_execution: bool
        :param max_parallel_tasks: Maximum number of parallel orchestrator tasks to run
        :type max_parallel_tasks: int
        :param debug_mode: Whether to run in debug mode (more verbose output)
        :type debug_mode: bool
        :return: The output from the red team scan
        :rtype: RedTeamAgentOutput
        """
        # Start timing for performance tracking
        self.start_time = time.time()
        
        # Reset task counters and statuses
        self.task_statuses = {}
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        log_section_header(self.logger, "Starting red team scan")
        self.logger.info(f"Scan started with evaluation_name: {evaluation_name}")
        self.logger.debug(f"Attack strategies: {attack_strategies}")
        self.logger.debug(f"data_only: {data_only}, output_path: {output_path}")
        
        print(f"🚀 STARTING RED TEAM SCAN: {evaluation_name}")
        
        chat_target = self._get_chat_target(target)
        self.chat_target = chat_target
        self.application_scenario = application_scenario or ""
        
        if not attack_objective_generator:
            error_msg = "Attack objective generator is required for red team agent."
            log_error(self.logger, error_msg)
            print(f"❌ {error_msg}")
            raise EvaluationException(
                message=error_msg,
                internal_message="Attack objective generator is not provided.",
                target=ErrorTarget.RED_TEAM_AGENT,
                category=ErrorCategory.MISSING_FIELD,
                blame=ErrorBlame.USER_ERROR
            )
            
        # If risk categories aren't specified, use all available categories
        if not attack_objective_generator.risk_categories:
            self.logger.info("No risk categories specified, using all available categories")
            attack_objective_generator.risk_categories = list(RiskCategory)
            
        self.risk_categories = attack_objective_generator.risk_categories
        print(f"📊 Risk categories: {[rc.value for rc in self.risk_categories]}")
        self.logger.info(f"Risk categories to process: {[rc.value for rc in self.risk_categories]}")
        
        # Prepend AttackStrategy.Baseline to the attack strategy list
        if AttackStrategy.Baseline not in attack_strategies:
            attack_strategies.insert(0, AttackStrategy.Baseline)
            self.logger.debug("Added Baseline to attack strategies")
            
        with self._start_redteam_mlflow_run(self.azure_ai_project, evaluation_name) as eval_run:
            self.ai_studio_url = _get_ai_studio_url(trace_destination=self.trace_destination, evaluation_id=eval_run.info.run_id)
            # todo: temp change to show the URL in int and with flight info
            self.ai_studio_url = self.ai_studio_url.replace("ai.azure.com", "int.ai.azure.com")
            self.ai_studio_url = f"{self.ai_studio_url}&flight=AIRedTeaming=true,EvalConvergence"
            print(f"🔗 Track your red team scan in AI Foundry: {self.ai_studio_url}")
            self.logger.info(f"Started MLFlow run: {self.ai_studio_url}")
            
            log_subsection_header(self.logger, "Setting up scan configuration")
            flattened_attack_strategies = self._get_flattened_attack_strategies(attack_strategies)
            print(f"🛠️ Using {len(flattened_attack_strategies)} attack strategies")
            self.logger.info(f"Found {len(flattened_attack_strategies)} attack strategies")
            
            orchestrators = self._get_orchestrators_for_attack_strategies(attack_strategies)
            self.logger.debug(f"Selected {len(orchestrators)} orchestrators for attack strategies")
            
            # Calculate total tasks: #risk_categories * #converters * #orchestrators
            self.total_tasks = len(self.risk_categories) * len(flattened_attack_strategies) * len(orchestrators)
            print(f"📋 Planning {self.total_tasks} total tasks")
            self.logger.info(f"Total tasks: {self.total_tasks} ({len(self.risk_categories)} risk categories * {len(flattened_attack_strategies)} strategies * {len(orchestrators)} orchestrators)")
            
            # Initialize our tracking dictionary early with empty structures
            # This ensures we have a place to store results even if tasks fail
            self.red_team_agent_info = {}
            for strategy in flattened_attack_strategies:
                strategy_name = self._get_strategy_name(strategy)
                self.red_team_agent_info[strategy_name] = {}
                for risk_category in self.risk_categories:
                    self.red_team_agent_info[strategy_name][risk_category.value] = {
                        "data_file": "",
                        "evaluation_result_file": "",
                        "evaluation_result": None,
                        "status": TASK_STATUS["PENDING"]
                    }
            
            self.logger.debug(f"Initialized tracking dictionary with {len(self.red_team_agent_info)} strategies")
            
            # More visible progress bar with additional status
            progress_bar = tqdm(
                total=self.total_tasks,
                desc="Scanning: ",
                ncols=100,
                unit="scan",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
            )
            progress_bar.set_postfix({"current": "initializing"})
            progress_bar_lock = asyncio.Lock()
            
            # Process all API calls sequentially to respect dependencies between objectives
            log_section_header(self.logger, "Fetching attack objectives")
            print(f"📥 FETCHING ATTACK OBJECTIVES")
            
            # Dictionary to store all objectives
            all_objectives = {}
            
            # First fetch baseline objectives for all risk categories
            # This is important as other strategies depend on baseline objectives
            self.logger.info("Fetching baseline objectives for all risk categories")
            for risk_category in self.risk_categories:
                progress_bar.set_postfix({"current": f"fetching baseline/{risk_category.value}"})
                self.logger.debug(f"Fetching baseline objectives for {risk_category.value}")
                baseline_objectives = await self._get_attack_objectives(
                    attack_objective_generator=attack_objective_generator,
                    risk_category=risk_category,
                    application_scenario=application_scenario,
                    strategy="baseline"
                )
                if "baseline" not in all_objectives:
                    all_objectives["baseline"] = {}
                all_objectives["baseline"][risk_category.value] = baseline_objectives
                print(f"📝 Fetched baseline objectives for {risk_category.value}: {len(baseline_objectives)} objectives")
            
            # Then fetch objectives for other strategies
            self.logger.info("Fetching objectives for non-baseline strategies")
            strategy_count = len(flattened_attack_strategies)
            for i, strategy in enumerate(flattened_attack_strategies):
                strategy_name = self._get_strategy_name(strategy)
                if strategy_name == "baseline":
                    continue  # Already fetched
                    
                print(f"🔄 Fetching objectives for strategy {i+1}/{strategy_count}: {strategy_name}")
                all_objectives[strategy_name] = {}
                
                for risk_category in self.risk_categories:
                    progress_bar.set_postfix({"current": f"fetching {strategy_name}/{risk_category.value}"})
                    self.logger.debug(f"Fetching objectives for {strategy_name} strategy and {risk_category.value} risk category")
                    
                    objectives = await self._get_attack_objectives(
                        attack_objective_generator=attack_objective_generator,
                        risk_category=risk_category,
                        application_scenario=application_scenario,
                        strategy=strategy_name
                    )
                    all_objectives[strategy_name][risk_category.value] = objectives
                    
                    # Print status about objective count for this strategy/risk
                    if debug_mode:
                        print(f"  - {risk_category.value}: {len(objectives)} objectives")
            
            print(f"✅ Completed fetching all attack objectives")
            self.logger.info("Completed fetching all attack objectives")
            
            log_section_header(self.logger, "Starting orchestrator processing")
            print(f"🚀 STARTING ORCHESTRATOR PROCESSING")
            
            # Create all tasks for parallel processing
            orchestrator_tasks = []
            combinations = list(itertools.product(orchestrators, flattened_attack_strategies, self.risk_categories))
            
            for combo_idx, (call_orchestrator, strategy, risk_category) in enumerate(combinations):
                strategy_name = self._get_strategy_name(strategy)
                objectives = all_objectives[strategy_name][risk_category.value]
                
                if not objectives:
                    self.logger.warning(f"No objectives found for {strategy_name}+{risk_category.value}, skipping")
                    print(f"⚠️ No objectives found for {strategy_name}/{risk_category.value}, skipping")
                    self.red_team_agent_info[strategy_name][risk_category.value]["status"] = TASK_STATUS["COMPLETED"]
                    async with progress_bar_lock:
                        progress_bar.update(1)
                    continue
                
                self.logger.debug(f"[{combo_idx+1}/{len(combinations)}] Creating task: {call_orchestrator.__name__} + {strategy_name} + {risk_category.value}")
                
                orchestrator_tasks.append(
                    self._process_attack(
                        target=target,
                        call_orchestrator=call_orchestrator,
                        all_prompts=objectives,
                        strategy=strategy,
                        progress_bar=progress_bar,
                        progress_bar_lock=progress_bar_lock,
                        evaluation_name=evaluation_name,
                        data_only=data_only,
                        output_path=output_path,
                        risk_category=risk_category
                    )
                )
            
            # Process tasks in parallel with optimized batching
            if parallel_execution and orchestrator_tasks:
                self.logger.info(f"Processing {len(orchestrator_tasks)} tasks in parallel (max {max_parallel_tasks} at a time)")
                print(f"⚙️ Processing {len(orchestrator_tasks)} tasks in parallel (max {max_parallel_tasks} at a time)")
                
                # Create batches for processing
                for i in range(0, len(orchestrator_tasks), max_parallel_tasks):
                    end_idx = min(i + max_parallel_tasks, len(orchestrator_tasks))
                    batch = orchestrator_tasks[i:end_idx]
                    progress_bar.set_postfix({"current": f"batch {i//max_parallel_tasks+1}/{math.ceil(len(orchestrator_tasks)/max_parallel_tasks)}"})
                    self.logger.debug(f"Processing batch of {len(batch)} tasks (tasks {i+1} to {end_idx})")
                    
                    try:
                        # Add timeout to each batch
                        await asyncio.wait_for(
                            asyncio.gather(*batch),
                            timeout=INTERNAL_TASK_TIMEOUT * 2  # Double timeout for batches
                        )
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Batch {i//max_parallel_tasks+1} timed out after {INTERNAL_TASK_TIMEOUT*2} seconds")
                        print(f"⚠️ Batch {i//max_parallel_tasks+1} timed out, continuing with next batch")
                        continue
                    except Exception as e:
                        log_error(self.logger, f"Error processing batch {i//max_parallel_tasks+1}", e)
                        print(f"❌ Error in batch {i//max_parallel_tasks+1}: {str(e)}")
                        continue
            else:
                # Sequential execution 
                self.logger.info("Running orchestrator processing sequentially")
                print("⚙️ Processing tasks sequentially")
                for i, task in enumerate(orchestrator_tasks):
                    progress_bar.set_postfix({"current": f"task {i+1}/{len(orchestrator_tasks)}"})
                    self.logger.debug(f"Processing task {i+1}/{len(orchestrator_tasks)}")
                    
                    try:
                        # Add timeout to each task
                        await asyncio.wait_for(task, timeout=INTERNAL_TASK_TIMEOUT)
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Task {i+1}/{len(orchestrator_tasks)} timed out after {INTERNAL_TASK_TIMEOUT} seconds")
                        print(f"⚠️ Task {i+1} timed out, continuing with next task")
                        continue
                    except Exception as e:
                        log_error(self.logger, f"Error processing task {i+1}/{len(orchestrator_tasks)}", e)
                        print(f"❌ Error in task {i+1}: {str(e)}")
                        continue
            
            progress_bar.close()
            
            # Print final status
            tasks_completed = sum(1 for status in self.task_statuses.values() if status == TASK_STATUS["COMPLETED"])
            tasks_failed = sum(1 for status in self.task_statuses.values() if status == TASK_STATUS["FAILED"])
            tasks_timeout = sum(1 for status in self.task_statuses.values() if status == TASK_STATUS["TIMEOUT"])
            
            total_time = time.time() - self.start_time
            print(f"\n📊 Scan Summary:")
            print(f"   - Total tasks: {self.total_tasks}")
            print(f"   - Completed: {tasks_completed}")
            print(f"   - Failed: {tasks_failed}")
            print(f"   - Timeouts: {tasks_timeout}")
            print(f"   - Total time: {total_time/60:.1f} minutes")
            
            # Process results
            log_section_header(self.logger, "Processing results")
            print(f"📝 PROCESSING RESULTS")
            
            # Convert results to RedTeamAgentResult using only red_team_agent_info
            red_team_agent_result = self._to_red_team_agent_result()
            
            # Create output with either full results or just conversations
            if data_only:
                self.logger.info("Data-only mode, creating output with just conversations")
                output = RedTeamAgentOutput(redteaming_data=red_team_agent_result["redteaming_data"])
            else:
                output = RedTeamAgentOutput(
                    red_team_agent_result=red_team_agent_result, 
                    redteaming_data=red_team_agent_result["redteaming_data"]
                )
            
            # Log results to MLFlow
            self.logger.info("Logging results to MLFlow")
            await self._log_redteam_results_to_mlflow(
                redteam_output=output,
                eval_run=eval_run,
                data_only=data_only
            )
        
        if data_only: 
            self.logger.info("Data-only mode, returning results without evaluation")
            return output
        
        if output_path and output.red_team_agent_result:
            self.logger.info(f"Writing output to {output_path}")
            _write_output(output_path, output.red_team_agent_result)
        
        if output.red_team_agent_result:
            self.logger.debug("Generating scorecard")
            scorecard = self._to_scorecard(output.red_team_agent_result)
            print(f"\n{scorecard}")
        
        print(f"✅ Scan completed successfully!")
        self.logger.info("Scan completed successfully")
        return output