# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Orchestrator management module for Red Team Agent.

This module handles PyRIT orchestrator initialization, execution, and management
for different attack strategies including single-turn, multi-turn, and crescendo attacks.
"""

import asyncio
import math
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Callable
from tqdm import tqdm

# PyRIT imports
from pyrit.orchestrator.single_turn.prompt_sending_orchestrator import PromptSendingOrchestrator
from pyrit.orchestrator.multi_turn.red_teaming_orchestrator import RedTeamingOrchestrator
from pyrit.orchestrator.multi_turn.crescendo_orchestrator import CrescendoOrchestrator
from pyrit.orchestrator import Orchestrator
from pyrit.prompt_converter import PromptConverter
from pyrit.prompt_target import PromptChatTarget

# Local imports
from ._callback_chat_target import _CallbackChatTarget

# Retry imports
import httpx
import httpcore
import tenacity
from tenacity import retry

# Local imports
from ._attack_strategy import AttackStrategy
from ._attack_objective_generator import RiskCategory
from ._utils._rai_service_target import AzureRAIServiceTarget
from ._utils._rai_service_true_false_scorer import AzureRAIServiceTrueFalseScorer
from ._utils._rai_service_eval_chat_target import RAIServiceEvalChatTarget
from ._utils.constants import DATA_EXT, TASK_STATUS
from ._utils.logging_utils import log_strategy_start, log_error
from ._utils.formatting_utils import write_pyrit_outputs_to_file


def network_retry_decorator(retry_config, logger, strategy_name, risk_category_name, prompt_idx=None):
    """Create a reusable retry decorator for network operations.

    :param retry_config: Retry configuration dictionary
    :param logger: Logger instance for logging warnings
    :param strategy_name: Name of the attack strategy
    :param risk_category_name: Name of the risk category
    :param prompt_idx: Optional prompt index for detailed logging
    :return: Configured retry decorator
    """

    def decorator(func):
        @retry(**retry_config["network_retry"])
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.ConnectError,
                httpx.HTTPError,
                ConnectionError,
                TimeoutError,
                OSError,
                asyncio.TimeoutError,
                httpcore.ReadTimeout,
                httpx.HTTPStatusError,
            ) as e:
                prompt_detail = f" for prompt {prompt_idx}" if prompt_idx is not None else ""
                logger.warning(
                    f"Retrying network error{prompt_detail} for {strategy_name}/{risk_category_name}: {type(e).__name__}: {str(e)}"
                )
                await asyncio.sleep(2)
                raise
            except ValueError as e:
                # Treat missing converted prompt text as a transient transport issue so tenacity will retry.
                if "Converted prompt text is None" in str(e):
                    prompt_detail = f" for prompt {prompt_idx}" if prompt_idx is not None else ""
                    logger.warning(
                        f"Endpoint produced empty converted prompt{prompt_detail} for {strategy_name}/{risk_category_name}; retrying."
                    )
                    await asyncio.sleep(2)
                    raise httpx.HTTPError(
                        "Converted prompt text is None; treating as transient endpoint failure"
                    ) from e
                raise
            except Exception as e:
                message = str(e)
                cause = e.__cause__
                if "Error sending prompt with conversation ID" in message and isinstance(
                    cause,
                    (
                        httpx.HTTPError,
                        httpx.ConnectTimeout,
                        httpx.ReadTimeout,
                        httpcore.ReadTimeout,
                        asyncio.TimeoutError,
                        ConnectionError,
                        TimeoutError,
                        OSError,
                        ValueError,
                    ),
                ):
                    prompt_detail = f" for prompt {prompt_idx}" if prompt_idx is not None else ""
                    logger.warning(
                        f"Wrapped network error{prompt_detail} for {strategy_name}/{risk_category_name}: {message}. Retrying."
                    )
                    await asyncio.sleep(2)
                    raise httpx.HTTPError(message) from cause
                raise

        return wrapper

    return decorator


class OrchestratorManager:
    """Manages PyRIT orchestrators for different attack strategies."""

    def __init__(
        self,
        logger,
        generated_rai_client,
        credential,
        azure_ai_project,
        one_dp_project,
        retry_config,
        scan_output_dir=None,
        red_team=None,
    ):
        """Initialize the orchestrator manager.

        :param logger: Logger instance for logging
        :param generated_rai_client: RAI client for service interactions
        :param credential: Authentication credential
        :param azure_ai_project: Azure AI project configuration
        :param one_dp_project: Whether this is a OneDP project
        :param retry_config: Retry configuration for network errors
        :param scan_output_dir: Directory for scan outputs
        :param red_team: Reference to RedTeam instance for accessing prompt mappings
        """
        self.logger = logger
        self.generated_rai_client = generated_rai_client
        self.credential = credential
        self.azure_ai_project = azure_ai_project
        self._one_dp_project = one_dp_project
        self.retry_config = retry_config
        self.scan_output_dir = scan_output_dir
        self.red_team = red_team

    def _calculate_timeout(self, base_timeout: int, orchestrator_type: str) -> int:
        """Calculate appropriate timeout based on orchestrator type.

        Multi-turn and crescendo orchestrators need more generous timeouts due to their
        iterative nature and multiple API calls per prompt.

        :param base_timeout: Base timeout value in seconds
        :param orchestrator_type: Type of orchestrator ('single', 'multi_turn', 'crescendo')
        :return: Calculated timeout in seconds
        """
        timeout_multipliers = {
            "single": 1.0,  # Standard timeout for single-turn
            "multi_turn": 3.0,  # 3x timeout for multi-turn interactions
            "crescendo": 4.0,  # 4x timeout for crescendo with backtracks
        }

        multiplier = timeout_multipliers.get(orchestrator_type, 1.0)
        calculated_timeout = int(base_timeout * multiplier)

        self.logger.debug(
            f"Calculated timeout for {orchestrator_type} orchestrator: {calculated_timeout}s "
            f"(base: {base_timeout}s, multiplier: {multiplier}x)"
        )

        return calculated_timeout

    def get_orchestrator_for_attack_strategy(
        self, attack_strategy: Union[AttackStrategy, List[AttackStrategy]]
    ) -> Callable:
        """Get appropriate orchestrator function for the specified attack strategy.

        :param attack_strategy: Attack strategy to get orchestrator for
        :type attack_strategy: Union[AttackStrategy, List[AttackStrategy]]
        :return: Callable orchestrator function
        :rtype: Callable
        """
        if isinstance(attack_strategy, list):
            if AttackStrategy.MultiTurn in attack_strategy or AttackStrategy.Crescendo in attack_strategy:
                self.logger.error("MultiTurn and Crescendo strategies are not supported in composed attacks.")
                raise ValueError("MultiTurn and Crescendo strategies are not supported in composed attacks.")
        elif AttackStrategy.MultiTurn == attack_strategy:
            return self._multi_turn_orchestrator
        elif AttackStrategy.Crescendo == attack_strategy:
            return self._crescendo_orchestrator
        return self._prompt_sending_orchestrator

    async def _prompt_sending_orchestrator(
        self,
        chat_target: PromptChatTarget,
        all_prompts: List[str],
        converter: Union[PromptConverter, List[PromptConverter]],
        *,
        strategy_name: str = "unknown",
        risk_category_name: str = "unknown",
        risk_category: Optional[RiskCategory] = None,
        timeout: int = 120,
        red_team_info: Dict = None,
        task_statuses: Dict = None,
        prompt_to_context: Dict[str, str] = None,
    ) -> Orchestrator:
        """Send prompts via the PromptSendingOrchestrator.

        :param chat_target: The target to send prompts to
        :type chat_target: PromptChatTarget
        :param all_prompts: List of prompts to process and send
        :type all_prompts: List[str]
        :param converter: Prompt converter or list of converters to transform prompts
        :type converter: Union[PromptConverter, List[PromptConverter]]
        :param strategy_name: Name of the attack strategy being used
        :type strategy_name: str
        :param risk_category_name: Name of the risk category being evaluated
        :type risk_category_name: str
        :param risk_category: Risk category being evaluated
        :type risk_category: Optional[RiskCategory]
        :param timeout: Timeout in seconds for each prompt
        :type timeout: int
        :param red_team_info: Dictionary to store file paths and results
        :type red_team_info: Dict
        :param task_statuses: Dictionary to track task statuses
        :type task_statuses: Dict
        :param prompt_to_context: Dictionary mapping prompts to their contexts (string or dict format)
        :type prompt_to_context: Dict[str, Union[str, Dict]]
        :return: Configured and initialized orchestrator
        :rtype: Orchestrator
        """
        task_key = f"{strategy_name}_{risk_category_name}_orchestrator"
        if task_statuses:
            task_statuses[task_key] = TASK_STATUS["RUNNING"]

        log_strategy_start(self.logger, strategy_name, risk_category_name)

        # Create converter list from single converter or list of converters
        converter_list = (
            [converter] if converter and isinstance(converter, PromptConverter) else converter if converter else []
        )

        # Log which converter is being used
        if converter_list:
            if isinstance(converter_list, list) and len(converter_list) > 0:
                converter_names = [c.__class__.__name__ for c in converter_list if c is not None]
                self.logger.debug(f"Using converters: {', '.join(converter_names)}")
            elif converter is not None:
                self.logger.debug(f"Using converter: {converter.__class__.__name__}")
        else:
            self.logger.debug("No converters specified")

        # Initialize orchestrator
        try:
            orchestrator = PromptSendingOrchestrator(objective_target=chat_target, prompt_converters=converter_list)

            if not all_prompts:
                self.logger.warning(f"No prompts provided to orchestrator for {strategy_name}/{risk_category_name}")
                if task_statuses:
                    task_statuses[task_key] = TASK_STATUS["COMPLETED"]
                return orchestrator

            # Initialize output path for memory labelling
            base_path = str(uuid.uuid4())

            # If scan output directory exists, place the file there
            if self.scan_output_dir:
                output_path = os.path.join(self.scan_output_dir, f"{base_path}{DATA_EXT}")
            else:
                output_path = f"{base_path}{DATA_EXT}"

            if red_team_info:
                red_team_info[strategy_name][risk_category_name]["data_file"] = output_path

            # Process prompts one at a time like multi-turn and crescendo orchestrators
            self.logger.debug(f"Processing {len(all_prompts)} prompts for {strategy_name}/{risk_category_name}")

            # Calculate appropriate timeout for single-turn orchestrator
            calculated_timeout = self._calculate_timeout(timeout, "single")

            for prompt_idx, prompt in enumerate(all_prompts):
                prompt_start_time = datetime.now()
                self.logger.debug(f"Processing prompt {prompt_idx+1}/{len(all_prompts)}")

                # Get context for this prompt
                context_data = prompt_to_context.get(prompt, {}) if prompt_to_context else {}

                # Normalize context_data: handle both string (legacy) and dict formats
                # If context_data is a string, convert it to the expected dict format
                if isinstance(context_data, str):
                    context_data = {"contexts": [{"content": context_data}]} if context_data else {"contexts": []}

                # context_data is now always a dict with a 'contexts' list
                # Each item in contexts is a dict with 'content' key
                # context_type and tool_name can be present per-context
                contexts = context_data.get("contexts", [])

                # Check if any context has agent-specific fields (context_type, tool_name)
                has_agent_fields = any(
                    isinstance(ctx, dict)
                    and ("context_type" in ctx and "tool_name" in ctx and ctx["tool_name"] is not None)
                    for ctx in contexts
                )

                # Build context_dict to pass via memory labels
                context_dict = {"contexts": contexts}

                # Get risk_sub_type for this prompt if it exists
                risk_sub_type = (
                    self.red_team.prompt_to_risk_subtype.get(prompt)
                    if self.red_team and hasattr(self.red_team, "prompt_to_risk_subtype")
                    else None
                )

                try:
                    # Create retry-enabled function using the reusable decorator
                    @network_retry_decorator(
                        self.retry_config, self.logger, strategy_name, risk_category_name, prompt_idx + 1
                    )
                    async def send_prompt_with_retry():
                        memory_labels = {
                            "risk_strategy_path": output_path,
                            "batch": prompt_idx + 1,
                            "context": context_dict,
                        }
                        if risk_sub_type:
                            memory_labels["risk_sub_type"] = risk_sub_type
                        return await asyncio.wait_for(
                            orchestrator.send_prompts_async(
                                prompt_list=[prompt],
                                memory_labels=memory_labels,
                            ),
                            timeout=calculated_timeout,
                        )

                    # Execute the retry-enabled function
                    await send_prompt_with_retry()
                    prompt_duration = (datetime.now() - prompt_start_time).total_seconds()
                    self.logger.debug(
                        f"Successfully processed prompt {prompt_idx+1} for {strategy_name}/{risk_category_name} in {prompt_duration:.2f} seconds"
                    )

                    # Print progress to console
                    if prompt_idx < len(all_prompts) - 1:  # Don't print for the last prompt
                        print(
                            f"Strategy {strategy_name}, Risk {risk_category_name}: Processed prompt {prompt_idx+1}/{len(all_prompts)}"
                        )

                except (asyncio.TimeoutError, tenacity.RetryError):
                    self.logger.warning(
                        f"Prompt {prompt_idx+1} for {strategy_name}/{risk_category_name} timed out after {calculated_timeout} seconds, continuing with remaining prompts"
                    )
                    print(f"⚠️ TIMEOUT: Strategy {strategy_name}, Risk {risk_category_name}, Prompt {prompt_idx+1}")
                    # Set task status to TIMEOUT for this specific prompt
                    batch_task_key = f"{strategy_name}_{risk_category_name}_prompt_{prompt_idx+1}"
                    if task_statuses:
                        task_statuses[batch_task_key] = TASK_STATUS["TIMEOUT"]
                    if red_team_info:
                        red_team_info[strategy_name][risk_category_name]["status"] = TASK_STATUS["INCOMPLETE"]
                    continue
                except Exception as e:
                    log_error(
                        self.logger,
                        f"Error processing prompt {prompt_idx+1}",
                        e,
                        f"{strategy_name}/{risk_category_name}",
                    )
                    if red_team_info:
                        red_team_info[strategy_name][risk_category_name]["status"] = TASK_STATUS["INCOMPLETE"]
                    continue

            if task_statuses:
                task_statuses[task_key] = TASK_STATUS["COMPLETED"]
            return orchestrator

        except Exception as e:
            log_error(
                self.logger,
                "Failed to initialize orchestrator",
                e,
                f"{strategy_name}/{risk_category_name}",
            )
            if task_statuses:
                task_statuses[task_key] = TASK_STATUS["FAILED"]
            raise

    async def _multi_turn_orchestrator(
        self,
        chat_target: PromptChatTarget,
        all_prompts: List[str],
        converter: Union[PromptConverter, List[PromptConverter]],
        *,
        strategy_name: str = "unknown",
        risk_category_name: str = "unknown",
        risk_category: Optional[RiskCategory] = None,
        timeout: int = 120,
        red_team_info: Dict = None,
        task_statuses: Dict = None,
        prompt_to_context: Dict[str, Union[str, Dict]] = None,
    ) -> Orchestrator:
        """Send prompts via the RedTeamingOrchestrator (multi-turn orchestrator).

        :param chat_target: The target to send prompts to
        :type chat_target: PromptChatTarget
        :param all_prompts: List of prompts to process and send
        :type all_prompts: List[str]
        :param converter: Prompt converter or list of converters to transform prompts
        :type converter: Union[PromptConverter, List[PromptConverter]]
        :param strategy_name: Name of the attack strategy being used
        :type strategy_name: str
        :param risk_category_name: Name of the risk category being evaluated
        :type risk_category_name: str
        :param risk_category: Risk category being evaluated
        :type risk_category: Optional[RiskCategory]
        :param timeout: Timeout in seconds for each prompt
        :type timeout: int
        :param red_team_info: Dictionary to store file paths and results
        :type red_team_info: Dict
        :param task_statuses: Dictionary to track task statuses
        :type task_statuses: Dict
        :return: Configured and initialized orchestrator
        :rtype: Orchestrator
        """
        max_turns = 5  # Set a default max turns value
        task_key = f"{strategy_name}_{risk_category_name}_orchestrator"
        if task_statuses:
            task_statuses[task_key] = TASK_STATUS["RUNNING"]

        log_strategy_start(self.logger, strategy_name, risk_category_name)
        converter_list = []
        # Create converter list from single converter or list of converters
        if converter and isinstance(converter, PromptConverter):
            converter_list = [converter]
        elif converter and isinstance(converter, list):
            # Filter out None values from the converter list
            converter_list = [c for c in converter if c is not None]

        # Log which converter is being used
        if converter_list:
            if isinstance(converter_list, list) and len(converter_list) > 0:
                converter_names = [c.__class__.__name__ for c in converter_list if c is not None]
                self.logger.debug(f"Using converters: {', '.join(converter_names)}")
            elif converter is not None:
                self.logger.debug(f"Using converter: {converter.__class__.__name__}")
        else:
            self.logger.debug("No converters specified")

        # Initialize output path for memory labelling
        base_path = str(uuid.uuid4())

        # If scan output directory exists, place the file there
        if self.scan_output_dir:
            # Ensure the directory exists
            os.makedirs(self.scan_output_dir, exist_ok=True)
            output_path = os.path.join(self.scan_output_dir, f"{base_path}{DATA_EXT}")
        else:
            output_path = f"{base_path}{DATA_EXT}"

        if red_team_info:
            red_team_info[strategy_name][risk_category_name]["data_file"] = output_path

        # Calculate appropriate timeout for multi-turn orchestrator
        calculated_timeout = self._calculate_timeout(timeout, "multi_turn")

        for prompt_idx, prompt in enumerate(all_prompts):
            prompt_start_time = datetime.now()
            self.logger.debug(f"Processing prompt {prompt_idx+1}/{len(all_prompts)}")

            # Get context for this prompt
            context_data = prompt_to_context.get(prompt, {}) if prompt_to_context else {}

            # Normalize context_data: handle both string (legacy) and dict formats
            # If context_data is a string, convert it to the expected dict format
            if isinstance(context_data, str):
                context_data = {"contexts": [{"content": context_data}]} if context_data else {"contexts": []}

            # context_data is now always a dict with a 'contexts' list
            # Each item in contexts is a dict with 'content' key
            # context_type and tool_name can be present per-context
            contexts = context_data.get("contexts", [])

            # Check if any context has agent-specific fields (context_type, tool_name)
            has_agent_fields = any(
                isinstance(ctx, dict) and ("context_type" in ctx or "tool_name" in ctx) for ctx in contexts
            )

            # Build context_dict to pass via memory labels
            context_dict = {"contexts": contexts}

            # Get risk_sub_type for this prompt if it exists
            risk_sub_type = (
                self.red_team.prompt_to_risk_subtype.get(prompt)
                if self.red_team and hasattr(self.red_team, "prompt_to_risk_subtype")
                else None
            )

            # For backwards compatibility with scoring, extract string context
            # This is used by AzureRAIServiceTrueFalseScorer which expects a string
            context_string = ""
            if contexts:
                context_string = "\n".join(
                    ctx.get("content", "") if isinstance(ctx, dict) else str(ctx) for ctx in contexts
                )

            try:
                azure_rai_service_scorer = AzureRAIServiceTrueFalseScorer(
                    client=self.generated_rai_client,
                    api_version=None,
                    model="gpt-4",
                    logger=self.logger,
                    credential=self.credential,
                    risk_category=risk_category,
                    azure_ai_project=self.azure_ai_project,
                    context=context_string,
                )

                azure_rai_service_target = AzureRAIServiceTarget(
                    client=self.generated_rai_client,
                    api_version=None,
                    model="gpt-4",
                    prompt_template_key="orchestrators/red_teaming/text_generation.yaml",
                    objective=prompt,
                    logger=self.logger,
                    is_one_dp_project=self._one_dp_project,
                )

                orchestrator = RedTeamingOrchestrator(
                    objective_target=chat_target,
                    adversarial_chat=azure_rai_service_target,
                    max_turns=max_turns,
                    prompt_converters=converter_list,
                    objective_scorer=azure_rai_service_scorer,
                    use_score_as_feedback=False,
                )

                try:
                    # Create retry-enabled function using the reusable decorator
                    @network_retry_decorator(
                        self.retry_config, self.logger, strategy_name, risk_category_name, prompt_idx + 1
                    )
                    async def send_prompt_with_retry():
                        memory_labels = {
                            "risk_strategy_path": output_path,
                            "batch": prompt_idx + 1,
                            "context": context_dict,
                        }
                        if risk_sub_type:
                            memory_labels["risk_sub_type"] = risk_sub_type
                        return await asyncio.wait_for(
                            orchestrator.run_attack_async(
                                objective=prompt,
                                memory_labels=memory_labels,
                            ),
                            timeout=calculated_timeout,
                        )

                    # Execute the retry-enabled function
                    await send_prompt_with_retry()
                    prompt_duration = (datetime.now() - prompt_start_time).total_seconds()
                    self.logger.debug(
                        f"Successfully processed prompt {prompt_idx+1} for {strategy_name}/{risk_category_name} in {prompt_duration:.2f} seconds"
                    )

                    # Write outputs to file after each prompt is processed
                    write_pyrit_outputs_to_file(
                        output_path=output_path,
                        logger=self.logger,
                        prompt_to_context=prompt_to_context,
                    )

                    # Print progress to console
                    if prompt_idx < len(all_prompts) - 1:  # Don't print for the last prompt
                        print(
                            f"Strategy {strategy_name}, Risk {risk_category_name}: Processed prompt {prompt_idx+1}/{len(all_prompts)}"
                        )

                except (asyncio.TimeoutError, tenacity.RetryError):
                    self.logger.warning(
                        f"Batch {prompt_idx+1} for {strategy_name}/{risk_category_name} timed out after {calculated_timeout} seconds, continuing with partial results"
                    )
                    print(f"⚠️ TIMEOUT: Strategy {strategy_name}, Risk {risk_category_name}, Batch {prompt_idx+1}")
                    # Set task status to TIMEOUT
                    batch_task_key = f"{strategy_name}_{risk_category_name}_prompt_{prompt_idx+1}"
                    if task_statuses:
                        task_statuses[batch_task_key] = TASK_STATUS["TIMEOUT"]
                    if red_team_info:
                        red_team_info[strategy_name][risk_category_name]["status"] = TASK_STATUS["INCOMPLETE"]
                    continue
                except Exception as e:
                    log_error(
                        self.logger,
                        f"Error processing prompt {prompt_idx+1}",
                        e,
                        f"{strategy_name}/{risk_category_name}",
                    )
                    if red_team_info:
                        red_team_info[strategy_name][risk_category_name]["status"] = TASK_STATUS["INCOMPLETE"]
                    continue
            except Exception as e:
                log_error(
                    self.logger,
                    "Failed to initialize orchestrator",
                    e,
                    f"{strategy_name}/{risk_category_name}",
                )
                if task_statuses:
                    task_statuses[task_key] = TASK_STATUS["FAILED"]
                raise
        if task_statuses:
            task_statuses[task_key] = TASK_STATUS["COMPLETED"]
        return orchestrator

    async def _crescendo_orchestrator(
        self,
        chat_target: PromptChatTarget,
        all_prompts: List[str],
        converter: Union[PromptConverter, List[PromptConverter]],
        *,
        strategy_name: str = "unknown",
        risk_category_name: str = "unknown",
        risk_category: Optional[RiskCategory] = None,
        timeout: int = 120,
        red_team_info: Dict = None,
        task_statuses: Dict = None,
        prompt_to_context: Dict[str, Union[str, Dict]] = None,
    ) -> Orchestrator:
        """Send prompts via the CrescendoOrchestrator with optimized performance.

        :param chat_target: The target to send prompts to
        :type chat_target: PromptChatTarget
        :param all_prompts: List of prompts to process and send
        :type all_prompts: List[str]
        :param converter: Prompt converter or list of converters to transform prompts
        :type converter: Union[PromptConverter, List[PromptConverter]]
        :param strategy_name: Name of the attack strategy being used
        :type strategy_name: str
        :param risk_category_name: Name of the risk category being evaluated
        :type risk_category_name: str
        :param risk_category: Risk category being evaluated
        :type risk_category: Optional[RiskCategory]
        :param timeout: Timeout in seconds for each prompt
        :type timeout: int
        :param red_team_info: Dictionary to store file paths and results
        :type red_team_info: Dict
        :param task_statuses: Dictionary to track task statuses
        :type task_statuses: Dict
        :return: Configured and initialized orchestrator
        :rtype: Orchestrator
        """
        max_turns = 10  # Set a default max turns value
        max_backtracks = 5
        task_key = f"{strategy_name}_{risk_category_name}_orchestrator"
        if task_statuses:
            task_statuses[task_key] = TASK_STATUS["RUNNING"]

        log_strategy_start(self.logger, strategy_name, risk_category_name)

        # Initialize output path for memory labelling
        base_path = str(uuid.uuid4())

        # If scan output directory exists, place the file there
        if self.scan_output_dir:
            output_path = os.path.join(self.scan_output_dir, f"{base_path}{DATA_EXT}")
        else:
            output_path = f"{base_path}{DATA_EXT}"

        if red_team_info:
            red_team_info[strategy_name][risk_category_name]["data_file"] = output_path

        # Calculate appropriate timeout for crescendo orchestrator
        calculated_timeout = self._calculate_timeout(timeout, "crescendo")

        for prompt_idx, prompt in enumerate(all_prompts):
            prompt_start_time = datetime.now()
            self.logger.debug(f"Processing prompt {prompt_idx+1}/{len(all_prompts)}")

            # Get context for this prompt
            context_data = prompt_to_context.get(prompt, {}) if prompt_to_context else {}

            # Normalize context_data: handle both string (legacy) and dict formats
            # If context_data is a string, convert it to the expected dict format
            if isinstance(context_data, str):
                context_data = {"contexts": [{"content": context_data}]} if context_data else {"contexts": []}

            # context_data is now always a dict with a 'contexts' list
            # Each item in contexts is a dict with 'content' key
            # context_type and tool_name can be present per-context
            contexts = context_data.get("contexts", [])

            # Check if any context has agent-specific fields (context_type, tool_name)
            has_agent_fields = any(
                isinstance(ctx, dict)
                and ("context_type" in ctx and "tool_name" in ctx and ctx["tool_name"] is not None)
                for ctx in contexts
            )

            # Build context_dict to pass via memory labels
            context_dict = {"contexts": contexts}

            # Get risk_sub_type for this prompt if it exists
            risk_sub_type = (
                self.red_team.prompt_to_risk_subtype.get(prompt)
                if self.red_team and hasattr(self.red_team, "prompt_to_risk_subtype")
                else None
            )

            # For backwards compatibility with scoring, extract string context
            # This is used by AzureRAIServiceTrueFalseScorer and RAIServiceEvalChatTarget which expect a string
            context_string = ""
            if contexts:
                context_string = "\n".join(
                    ctx.get("content", "") if isinstance(ctx, dict) else str(ctx) for ctx in contexts
                )

            try:
                red_llm_scoring_target = RAIServiceEvalChatTarget(
                    logger=self.logger,
                    credential=self.credential,
                    risk_category=risk_category,
                    azure_ai_project=self.azure_ai_project,
                    context=context_string,
                )

                azure_rai_service_target = AzureRAIServiceTarget(
                    client=self.generated_rai_client,
                    api_version=None,
                    model="gpt-4",
                    prompt_template_key="orchestrators/crescendo/crescendo_variant_1.yaml",
                    objective=prompt,
                    logger=self.logger,
                    crescendo_format=True,
                    is_one_dp_project=self._one_dp_project,
                )

                orchestrator = CrescendoOrchestrator(
                    objective_target=chat_target,
                    adversarial_chat=azure_rai_service_target,
                    max_turns=max_turns,
                    scoring_target=red_llm_scoring_target,
                    max_backtracks=max_backtracks,
                )

                orchestrator._objective_scorer = AzureRAIServiceTrueFalseScorer(
                    client=self.generated_rai_client,
                    api_version=None,
                    model="gpt-4",
                    logger=self.logger,
                    credential=self.credential,
                    risk_category=risk_category,
                    azure_ai_project=self.azure_ai_project,
                    context=context_string,
                )

                try:
                    # Create retry-enabled function using the reusable decorator
                    @network_retry_decorator(
                        self.retry_config, self.logger, strategy_name, risk_category_name, prompt_idx + 1
                    )
                    async def send_prompt_with_retry():
                        memory_labels = {
                            "risk_strategy_path": output_path,
                            "batch": prompt_idx + 1,
                            "context": context_dict,
                        }
                        if risk_sub_type:
                            memory_labels["risk_sub_type"] = risk_sub_type
                        return await asyncio.wait_for(
                            orchestrator.run_attack_async(
                                objective=prompt,
                                memory_labels=memory_labels,
                            ),
                            timeout=calculated_timeout,
                        )

                    # Execute the retry-enabled function
                    await send_prompt_with_retry()
                    prompt_duration = (datetime.now() - prompt_start_time).total_seconds()
                    self.logger.debug(
                        f"Successfully processed prompt {prompt_idx+1} for {strategy_name}/{risk_category_name} in {prompt_duration:.2f} seconds"
                    )

                    # Write outputs to file after each prompt is processed
                    write_pyrit_outputs_to_file(
                        output_path=output_path,
                        logger=self.logger,
                        prompt_to_context=prompt_to_context,
                    )

                    # Print progress to console
                    if prompt_idx < len(all_prompts) - 1:  # Don't print for the last prompt
                        print(
                            f"Strategy {strategy_name}, Risk {risk_category_name}: Processed prompt {prompt_idx+1}/{len(all_prompts)}"
                        )

                except (asyncio.TimeoutError, tenacity.RetryError):
                    self.logger.warning(
                        f"Batch {prompt_idx+1} for {strategy_name}/{risk_category_name} timed out after {calculated_timeout} seconds, continuing with partial results"
                    )
                    print(f"⚠️ TIMEOUT: Strategy {strategy_name}, Risk {risk_category_name}, Batch {prompt_idx+1}")
                    # Set task status to TIMEOUT
                    batch_task_key = f"{strategy_name}_{risk_category_name}_prompt_{prompt_idx+1}"
                    if task_statuses:
                        task_statuses[batch_task_key] = TASK_STATUS["TIMEOUT"]
                    if red_team_info:
                        red_team_info[strategy_name][risk_category_name]["status"] = TASK_STATUS["INCOMPLETE"]
                    continue
                except Exception as e:
                    log_error(
                        self.logger,
                        f"Error processing prompt {prompt_idx+1}",
                        e,
                        f"{strategy_name}/{risk_category_name}",
                    )
                    if red_team_info:
                        red_team_info[strategy_name][risk_category_name]["status"] = TASK_STATUS["INCOMPLETE"]
                    continue
            except Exception as e:
                log_error(
                    self.logger,
                    "Failed to initialize orchestrator",
                    e,
                    f"{strategy_name}/{risk_category_name}",
                )
                if task_statuses:
                    task_statuses[task_key] = TASK_STATUS["FAILED"]
                raise
        if task_statuses:
            task_statuses[task_key] = TASK_STATUS["COMPLETED"]
        return orchestrator
