# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Third-party imports
import asyncio
import itertools
import logging
import math
import os
import random
import time
import uuid
from datetime import datetime
from typing import Callable, Dict, List, Optional, Union, cast, Any
from tqdm import tqdm

# Azure AI Evaluation imports
from azure.ai.evaluation._constants import TokenScope
from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._model_configurations import EvaluationResult
from azure.ai.evaluation.simulator._model_tools import ManagedIdentityAPITokenManager
from azure.ai.evaluation.simulator._model_tools._generated_rai_client import (
    GeneratedRAIClient,
)
from azure.ai.evaluation._user_agent import UserAgentSingleton
from azure.ai.evaluation._model_configurations import (
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)
from azure.ai.evaluation._exceptions import (
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
    EvaluationException,
)
from azure.ai.evaluation._common.utils import (
    validate_azure_ai_project,
    is_onedp_project,
)
from azure.ai.evaluation._evaluate._utils import _write_output

# Azure Core imports
from azure.core.credentials import TokenCredential

# Red Teaming imports
from ._red_team_result import RedTeamResult
from ._attack_strategy import AttackStrategy
from ._attack_objective_generator import (
    RiskCategory,
    _AttackObjectiveGenerator,
)

# PyRIT imports
from pyrit.common import initialize_pyrit, DUCK_DB
from pyrit.prompt_target import PromptChatTarget

# Local imports - constants and utilities
from ._utils.constants import TASK_STATUS
from ._utils.logging_utils import (
    setup_logger,
    log_section_header,
    log_subsection_header,
)
from ._utils.formatting_utils import (
    get_strategy_name,
    get_flattened_attack_strategies,
    write_pyrit_outputs_to_file,
    format_scorecard,
)
from ._utils.strategy_utils import get_chat_target, get_converter_for_strategy
from ._utils.retry_utils import create_standard_retry_manager
from ._utils.file_utils import create_file_manager
from ._utils.metric_mapping import get_attack_objective_from_risk_category

from ._orchestrator_manager import OrchestratorManager
from ._evaluation_processor import EvaluationProcessor
from ._mlflow_integration import MLflowIntegration
from ._result_processor import ResultProcessor


@experimental
class RedTeam:
    """
    This class uses various attack strategies to test the robustness of AI models against adversarial inputs.
    It logs the results of these evaluations and provides detailed scorecards summarizing the attack success rates.

    :param azure_ai_project: The Azure AI project, which can either be a string representing the project endpoint
        or an instance of AzureAIProject. It contains subscription id, resource group, and project name.
    :type azure_ai_project: Union[str, ~azure.ai.evaluation.AzureAIProject]
    :param credential: The credential to authenticate with Azure services
    :type credential: TokenCredential
    :param risk_categories: List of risk categories to generate attack objectives for (optional if custom_attack_seed_prompts is provided)
    :type risk_categories: Optional[List[RiskCategory]]
    :param num_objectives: Number of objectives to generate per risk category
    :type num_objectives: int
    :param application_scenario: Description of the application scenario for context
    :type application_scenario: Optional[str]
    :param custom_attack_seed_prompts: Path to a JSON file containing custom attack seed prompts (can be absolute or relative path)
    :type custom_attack_seed_prompts: Optional[str]
    :param output_dir: Directory to save output files (optional)
    :type output_dir: Optional[str]
    :param attack_success_thresholds: Threshold configuration for determining attack success.
        Should be a dictionary mapping risk categories (RiskCategory enum values) to threshold values,
        or None to use default binary evaluation (evaluation results determine success).
        When using thresholds, scores >= threshold are considered successful attacks.
    :type attack_success_thresholds: Optional[Dict[RiskCategory, int]]
    """

    def __init__(
        self,
        azure_ai_project: Union[dict, str],
        credential,
        *,
        risk_categories: Optional[List[RiskCategory]] = None,
        num_objectives: int = 10,
        application_scenario: Optional[str] = None,
        custom_attack_seed_prompts: Optional[str] = None,
        output_dir=".",
        attack_success_thresholds: Optional[Dict[RiskCategory, int]] = None,
    ):
        """Initialize a new Red Team agent for AI model evaluation.

        Creates a Red Team agent instance configured with the specified parameters.
        This initializes the token management, attack objective generation, and logging
        needed for running red team evaluations against AI models.

        :param azure_ai_project: The Azure AI project, which can either be a string representing the project endpoint
            or an instance of AzureAIProject. It contains subscription id, resource group, and project name.
        :type azure_ai_project: Union[str, ~azure.ai.evaluation.AzureAIProject]
        :param credential: Authentication credential for Azure services
        :type credential: TokenCredential
        :param risk_categories: List of risk categories to test (required unless custom prompts provided)
        :type risk_categories: Optional[List[RiskCategory]]
        :param num_objectives: Number of attack objectives to generate per risk category
        :type num_objectives: int
        :param application_scenario: Description of the application scenario
        :type application_scenario: Optional[str]
        :param custom_attack_seed_prompts: Path to a JSON file with custom attack prompts
        :type custom_attack_seed_prompts: Optional[str]
        :param output_dir: Directory to save evaluation outputs and logs. Defaults to current working directory.
        :type output_dir: str
        :param attack_success_thresholds: Threshold configuration for determining attack success.
            Should be a dictionary mapping risk categories (RiskCategory enum values) to threshold values,
            or None to use default binary evaluation (evaluation results determine success).
            When using thresholds, scores >= threshold are considered successful attacks.
        :type attack_success_thresholds: Optional[Dict[RiskCategory, int]]
        """

        self.azure_ai_project = validate_azure_ai_project(azure_ai_project)
        self.credential = credential
        self.output_dir = output_dir
        self._one_dp_project = is_onedp_project(azure_ai_project)

        # Configure attack success thresholds
        self.attack_success_thresholds = self._configure_attack_success_thresholds(attack_success_thresholds)

        # Initialize basic logger without file handler (will be properly set up during scan)
        self.logger = logging.getLogger("RedTeamLogger")
        self.logger.setLevel(logging.DEBUG)

        # Only add console handler for now - file handler will be added during scan setup
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_formatter = logging.Formatter("%(levelname)s - %(message)s")
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        if not self._one_dp_project:
            self.token_manager = ManagedIdentityAPITokenManager(
                token_scope=TokenScope.DEFAULT_AZURE_MANAGEMENT,
                logger=logging.getLogger("RedTeamLogger"),
                credential=cast(TokenCredential, credential),
            )
        else:
            self.token_manager = ManagedIdentityAPITokenManager(
                token_scope=TokenScope.COGNITIVE_SERVICES_MANAGEMENT,
                logger=logging.getLogger("RedTeamLogger"),
                credential=cast(TokenCredential, credential),
            )

        # Initialize task tracking
        self.task_statuses = {}
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.start_time = None
        self.scan_id = None
        self.scan_session_id = None
        self.scan_output_dir = None

        # Initialize RAI client
        self.generated_rai_client = GeneratedRAIClient(
            azure_ai_project=self.azure_ai_project,
            token_manager=self.token_manager.credential,
        )

        # Initialize a cache for attack objectives by risk category and strategy
        self.attack_objectives = {}

        # Keep track of data and eval result file names
        self.red_team_info = {}

        # keep track of prompt content to context mapping for evaluation
        self.prompt_to_context = {}

        # Initialize PyRIT
        initialize_pyrit(memory_db_type=DUCK_DB)

        # Initialize attack objective generator
        self.attack_objective_generator = _AttackObjectiveGenerator(
            risk_categories=risk_categories,
            num_objectives=num_objectives,
            application_scenario=application_scenario,
            custom_attack_seed_prompts=custom_attack_seed_prompts,
        )

        # Initialize component managers (will be set up during scan)
        self.orchestrator_manager = None
        self.evaluation_processor = None
        self.mlflow_integration = None
        self.result_processor = None

        # Initialize utility managers
        self.retry_manager = create_standard_retry_manager(logger=self.logger)
        self.file_manager = create_file_manager(base_output_dir=self.output_dir, logger=self.logger)

        self.logger.debug("RedTeam initialized successfully")

    def _configure_attack_success_thresholds(
        self, attack_success_thresholds: Optional[Dict[RiskCategory, int]]
    ) -> Dict[str, int]:
        """Configure attack success thresholds for different risk categories."""
        if attack_success_thresholds is None:
            return {}

        def validate_threshold(value: int, key: str = "threshold") -> None:
            if not isinstance(value, int) or not (0 <= value <= 7):
                raise ValueError(f"Attack success {key} must be an integer between 0 and 7, got: {value}")

        configured_thresholds = {}

        if not isinstance(attack_success_thresholds, dict):
            raise ValueError(
                f"attack_success_thresholds must be a dictionary mapping RiskCategory instances to thresholds, or None. Got: {type(attack_success_thresholds)}"
            )

        # Per-category thresholds
        for key, value in attack_success_thresholds.items():
            validate_threshold(value, f"threshold for {key}")

            # Normalize the key to string format
            if hasattr(key, "value"):
                category_key = key.value
            else:
                raise ValueError(f"attack_success_thresholds keys must be RiskCategory instance, got: {type(key)}")

            configured_thresholds[category_key] = value

        return configured_thresholds

    def _setup_component_managers(self):
        """Initialize component managers with shared configuration."""
        retry_config = self.retry_manager.get_retry_config()

        # Initialize orchestrator manager
        self.orchestrator_manager = OrchestratorManager(
            logger=self.logger,
            generated_rai_client=self.generated_rai_client,
            credential=self.credential,
            azure_ai_project=self.azure_ai_project,
            one_dp_project=self._one_dp_project,
            retry_config=retry_config,
            scan_output_dir=self.scan_output_dir,
        )

        # Initialize evaluation processor
        self.evaluation_processor = EvaluationProcessor(
            logger=self.logger,
            azure_ai_project=self.azure_ai_project,
            credential=self.credential,
            attack_success_thresholds=self.attack_success_thresholds,
            retry_config=retry_config,
            scan_session_id=self.scan_session_id,
            scan_output_dir=self.scan_output_dir,
        )

        # Initialize MLflow integration
        self.mlflow_integration = MLflowIntegration(
            logger=self.logger,
            azure_ai_project=self.azure_ai_project,
            generated_rai_client=self.generated_rai_client,
            one_dp_project=self._one_dp_project,
            scan_output_dir=self.scan_output_dir,
        )

        # Initialize result processor
        self.result_processor = ResultProcessor(
            logger=self.logger,
            attack_success_thresholds=self.attack_success_thresholds,
            application_scenario=getattr(self, "application_scenario", ""),
            risk_categories=getattr(self, "risk_categories", []),
            ai_studio_url=getattr(self.mlflow_integration, "ai_studio_url", None),
        )

    async def _get_attack_objectives(
        self,
        risk_category: Optional[RiskCategory] = None,
        application_scenario: Optional[str] = None,
        strategy: Optional[str] = None,
    ) -> List[str]:
        """Get attack objectives from the RAI client for a specific risk category or from a custom dataset.

        Retrieves attack objectives based on the provided risk category and strategy. These objectives
        can come from either the RAI service or from custom attack seed prompts if provided. The function
        handles different strategies, including special handling for jailbreak strategy which requires
        applying prefixes to messages. It also maintains a cache of objectives to ensure consistency
        across different strategies for the same risk category.

        :param risk_category: The specific risk category to get objectives for
        :type risk_category: Optional[RiskCategory]
        :param application_scenario: Optional description of the application scenario for context
        :type application_scenario: Optional[str]
        :param strategy: Optional attack strategy to get specific objectives for
        :type strategy: Optional[str]
        :return: A list of attack objective prompts
        :rtype: List[str]
        """
        attack_objective_generator = self.attack_objective_generator

        # Convert risk category to lowercase for consistent caching
        risk_cat_value = get_attack_objective_from_risk_category(risk_category).lower()
        num_objectives = attack_objective_generator.num_objectives

        log_subsection_header(
            self.logger,
            f"Getting attack objectives for {risk_cat_value}, strategy: {strategy}",
        )

        # Check if we already have baseline objectives for this risk category
        baseline_key = ((risk_cat_value,), "baseline")
        baseline_objectives_exist = baseline_key in self.attack_objectives
        current_key = ((risk_cat_value,), strategy)

        # Check if custom attack seed prompts are provided in the generator
        if attack_objective_generator.custom_attack_seed_prompts and attack_objective_generator.validated_prompts:
            return await self._get_custom_attack_objectives(risk_cat_value, num_objectives, strategy, current_key)
        else:
            return await self._get_rai_attack_objectives(
                risk_category,
                risk_cat_value,
                application_scenario,
                strategy,
                baseline_objectives_exist,
                baseline_key,
                current_key,
                num_objectives,
            )

    async def _get_custom_attack_objectives(
        self,
        risk_cat_value: str,
        num_objectives: int,
        strategy: str,
        current_key: tuple,
    ) -> List[str]:
        """Get attack objectives from custom seed prompts."""
        attack_objective_generator = self.attack_objective_generator

        self.logger.info(
            f"Using custom attack seed prompts from {attack_objective_generator.custom_attack_seed_prompts}"
        )

        # Get the prompts for this risk category
        custom_objectives = attack_objective_generator.valid_prompts_by_category.get(risk_cat_value, [])

        if not custom_objectives:
            self.logger.warning(f"No custom objectives found for risk category {risk_cat_value}")
            return []

        self.logger.info(f"Found {len(custom_objectives)} custom objectives for {risk_cat_value}")

        # Sample if we have more than needed
        if len(custom_objectives) > num_objectives:
            selected_cat_objectives = random.sample(custom_objectives, num_objectives)
            self.logger.info(
                f"Sampled {num_objectives} objectives from {len(custom_objectives)} available for {risk_cat_value}"
            )
        else:
            selected_cat_objectives = custom_objectives
            self.logger.info(f"Using all {len(custom_objectives)} available objectives for {risk_cat_value}")

        # Handle jailbreak strategy - need to apply jailbreak prefixes to messages
        if strategy == "jailbreak":
            selected_cat_objectives = await self._apply_jailbreak_prefixes(selected_cat_objectives)

        # Extract content from selected objectives
        selected_prompts = []
        for obj in selected_cat_objectives:
            if "messages" in obj and len(obj["messages"]) > 0:
                message = obj["messages"][0]
                if isinstance(message, dict) and "content" in message:
                    content = message["content"]
                    context = message.get("context", "")
                    selected_prompts.append(content)
                    # Store mapping of content to context for later evaluation
                    self.prompt_to_context[content] = context

        # Store in cache and return
        self._cache_attack_objectives(
            current_key,
            risk_cat_value,
            strategy,
            selected_prompts,
            selected_cat_objectives,
        )
        return selected_prompts

    async def _get_rai_attack_objectives(
        self,
        risk_category: RiskCategory,
        risk_cat_value: str,
        application_scenario: str,
        strategy: str,
        baseline_objectives_exist: bool,
        baseline_key: tuple,
        current_key: tuple,
        num_objectives: int,
    ) -> List[str]:
        """Get attack objectives from the RAI service."""
        content_harm_risk = None
        other_risk = ""
        if risk_cat_value in ["hate_unfairness", "violence", "self_harm", "sexual"]:
            content_harm_risk = risk_cat_value
        else:
            other_risk = risk_cat_value

        try:
            self.logger.debug(
                f"API call: get_attack_objectives({risk_cat_value}, app: {application_scenario}, strategy: {strategy})"
            )

            # Get objectives from RAI service
            if "tense" in strategy:
                objectives_response = await self.generated_rai_client.get_attack_objectives(
                    risk_type=content_harm_risk,
                    risk_category=other_risk,
                    application_scenario=application_scenario or "",
                    strategy="tense",
                    scan_session_id=self.scan_session_id,
                )
            else:
                objectives_response = await self.generated_rai_client.get_attack_objectives(
                    risk_type=content_harm_risk,
                    risk_category=other_risk,
                    application_scenario=application_scenario or "",
                    strategy=None,
                    scan_session_id=self.scan_session_id,
                )

            if isinstance(objectives_response, list):
                self.logger.debug(f"API returned {len(objectives_response)} objectives")

            # Handle jailbreak strategy
            if strategy == "jailbreak":
                objectives_response = await self._apply_jailbreak_prefixes(objectives_response)

        except Exception as e:
            self.logger.error(f"Error calling get_attack_objectives: {str(e)}")
            self.logger.warning("API call failed, returning empty objectives list")
            return []

        # Check if the response is valid
        if not objectives_response or (
            isinstance(objectives_response, dict) and not objectives_response.get("objectives")
        ):
            self.logger.warning("Empty or invalid response, returning empty list")
            return []

        # Filter and select objectives
        selected_cat_objectives = self._filter_and_select_objectives(
            objectives_response,
            strategy,
            baseline_objectives_exist,
            baseline_key,
            num_objectives,
        )

        # Extract content and cache
        selected_prompts = self._extract_objective_content(selected_cat_objectives)
        self._cache_attack_objectives(
            current_key,
            risk_cat_value,
            strategy,
            selected_prompts,
            selected_cat_objectives,
        )

        return selected_prompts

    async def _apply_jailbreak_prefixes(self, objectives_list: List) -> List:
        """Apply jailbreak prefixes to objectives."""
        self.logger.debug("Applying jailbreak prefixes to objectives")
        try:
            # Use centralized retry decorator
            @self.retry_manager.create_retry_decorator(context="jailbreak_prefixes")
            async def get_jailbreak_prefixes_with_retry():
                return await self.generated_rai_client.get_jailbreak_prefixes()

            jailbreak_prefixes = await get_jailbreak_prefixes_with_retry()
            for objective in objectives_list:
                if "messages" in objective and len(objective["messages"]) > 0:
                    message = objective["messages"][0]
                    if isinstance(message, dict) and "content" in message:
                        message["content"] = f"{random.choice(jailbreak_prefixes)} {message['content']}"
        except Exception as e:
            self.logger.error(f"Error applying jailbreak prefixes: {str(e)}")

        return objectives_list

    def _filter_and_select_objectives(
        self,
        objectives_response: List,
        strategy: str,
        baseline_objectives_exist: bool,
        baseline_key: tuple,
        num_objectives: int,
    ) -> List:
        """Filter and select objectives based on strategy and baseline requirements."""
        # For non-baseline strategies, filter by baseline IDs if they exist
        if strategy != "baseline" and baseline_objectives_exist:
            self.logger.debug(f"Found existing baseline objectives, will filter {strategy} by baseline IDs")
            baseline_selected_objectives = self.attack_objectives[baseline_key].get("selected_objectives", [])
            baseline_objective_ids = [obj.get("id") for obj in baseline_selected_objectives if "id" in obj]

            if baseline_objective_ids:
                self.logger.debug(f"Filtering by {len(baseline_objective_ids)} baseline objective IDs for {strategy}")
                selected_cat_objectives = [
                    obj for obj in objectives_response if obj.get("id") in baseline_objective_ids
                ]
                self.logger.debug(f"Found {len(selected_cat_objectives)} matching objectives with baseline IDs")
            else:
                self.logger.warning("No baseline objective IDs found, using random selection")
                selected_cat_objectives = random.sample(
                    objectives_response, min(num_objectives, len(objectives_response))
                )
        else:
            # This is the baseline strategy or we don't have baseline objectives yet
            self.logger.debug(f"Using random selection for {strategy} strategy")
            selected_cat_objectives = random.sample(objectives_response, min(num_objectives, len(objectives_response)))

        if len(selected_cat_objectives) < num_objectives:
            self.logger.warning(
                f"Only found {len(selected_cat_objectives)} objectives, fewer than requested {num_objectives}"
            )

        return selected_cat_objectives

    def _extract_objective_content(self, selected_objectives: List) -> List[str]:
        """Extract content from selected objectives."""
        selected_prompts = []
        for obj in selected_objectives:
            if "messages" in obj and len(obj["messages"]) > 0:
                message = obj["messages"][0]
                if isinstance(message, dict) and "content" in message:
                    content = message["content"]
                    context = message.get("context", "")
                    selected_prompts.append(content)
                    # Store mapping of content to context for later evaluation
                    self.prompt_to_context[content] = context
        return selected_prompts

    def _cache_attack_objectives(
        self,
        current_key: tuple,
        risk_cat_value: str,
        strategy: str,
        selected_prompts: List[str],
        selected_objectives: List,
    ) -> None:
        """Cache attack objectives for reuse."""
        objectives_by_category = {risk_cat_value: []}

        # Process list format and organize by category for caching
        for obj in selected_objectives:
            obj_id = obj.get("id", f"obj-{uuid.uuid4()}")
            target_harms = obj.get("metadata", {}).get("target_harms", [])
            content = ""
            context = ""
            if "messages" in obj and len(obj["messages"]) > 0:

                message = obj["messages"][0]
                content = message.get("content", "")
                context = message.get("context", "")
            if content:
                obj_data = {"id": obj_id, "content": content, "context": context}
                objectives_by_category[risk_cat_value].append(obj_data)

        self.attack_objectives[current_key] = {
            "objectives_by_category": objectives_by_category,
            "strategy": strategy,
            "risk_category": risk_cat_value,
            "selected_prompts": selected_prompts,
            "selected_objectives": selected_objectives,
        }
        self.logger.info(f"Selected {len(selected_prompts)} objectives for {risk_cat_value}")

    async def _process_attack(
        self,
        strategy: Union[AttackStrategy, List[AttackStrategy]],
        risk_category: RiskCategory,
        all_prompts: List[str],
        progress_bar: tqdm,
        progress_bar_lock: asyncio.Lock,
        scan_name: Optional[str] = None,
        skip_upload: bool = False,
        output_path: Optional[Union[str, os.PathLike]] = None,
        timeout: int = 120,
        _skip_evals: bool = False,
    ) -> Optional[EvaluationResult]:
        """Process a red team scan with the given orchestrator, converter, and prompts.

        Executes a red team attack process using the specified strategy and risk category against the
        target model or function. This includes creating an orchestrator, applying prompts through the
        appropriate converter, saving results to files, and optionally evaluating the results.
        The function handles progress tracking, logging, and error handling throughout the process.

        :param strategy: The attack strategy to use
        :type strategy: Union[AttackStrategy, List[AttackStrategy]]
        :param risk_category: The risk category to evaluate
        :type risk_category: RiskCategory
        :param all_prompts: List of prompts to use for the scan
        :type all_prompts: List[str]
        :param progress_bar: Progress bar to update
        :type progress_bar: tqdm
        :param progress_bar_lock: Lock for the progress bar
        :type progress_bar_lock: asyncio.Lock
        :param scan_name: Optional name for the evaluation
        :type scan_name: Optional[str]
        :param skip_upload: Whether to return only data without evaluation
        :type skip_upload: bool
        :param output_path: Optional path for output
        :type output_path: Optional[Union[str, os.PathLike]]
        :param timeout: The timeout in seconds for API calls
        :type timeout: int
        :param _skip_evals: Whether to skip the actual evaluation process
        :type _skip_evals: bool
        :return: Evaluation result if available
        :rtype: Optional[EvaluationResult]
        """
        strategy_name = get_strategy_name(strategy)
        task_key = f"{strategy_name}_{risk_category.value}_attack"
        self.task_statuses[task_key] = TASK_STATUS["RUNNING"]

        try:
            start_time = time.time()
            tqdm.write(f"▶️ Starting task: {strategy_name} strategy for {risk_category.value} risk category")

            # Get converter and orchestrator function
            converter = get_converter_for_strategy(strategy)
            call_orchestrator = self.orchestrator_manager.get_orchestrator_for_attack_strategy(strategy)

            try:
                self.logger.debug(f"Calling orchestrator for {strategy_name} strategy")
                orchestrator = await call_orchestrator(
                    chat_target=self.chat_target,
                    all_prompts=all_prompts,
                    converter=converter,
                    strategy_name=strategy_name,
                    risk_category=risk_category,
                    risk_category_name=risk_category.value,
                    timeout=timeout,
                    red_team_info=self.red_team_info,
                    task_statuses=self.task_statuses,
                    prompt_to_context=self.prompt_to_context,
                )
            except Exception as e:
                self.logger.error(f"Error calling orchestrator for {strategy_name} strategy: {str(e)}")
                self.task_statuses[task_key] = TASK_STATUS["FAILED"]
                self.failed_tasks += 1
                async with progress_bar_lock:
                    progress_bar.update(1)
                return None

            # Write PyRIT outputs to file
            data_path = write_pyrit_outputs_to_file(
                output_path=self.red_team_info[strategy_name][risk_category.value]["data_file"],
                logger=self.logger,
                prompt_to_context=self.prompt_to_context,
            )
            orchestrator.dispose_db_engine()

            # Store data file in our tracking dictionary
            self.red_team_info[strategy_name][risk_category.value]["data_file"] = data_path
            self.logger.debug(
                f"Updated red_team_info with data file: {strategy_name} -> {risk_category.value} -> {data_path}"
            )

            # Perform evaluation
            try:
                await self.evaluation_processor.evaluate(
                    scan_name=scan_name,
                    risk_category=risk_category,
                    strategy=strategy,
                    _skip_evals=_skip_evals,
                    data_path=data_path,
                    output_path=None,
                    red_team_info=self.red_team_info,
                )
            except Exception as e:
                self.logger.error(
                    self.logger,
                    f"Error during evaluation for {strategy_name}/{risk_category.value}",
                    e,
                )
                tqdm.write(f"⚠️ Evaluation error for {strategy_name}/{risk_category.value}: {str(e)}")
                self.red_team_info[strategy_name][risk_category.value]["status"] = TASK_STATUS["FAILED"]

            # Update progress
            async with progress_bar_lock:
                self.completed_tasks += 1
                progress_bar.update(1)
                completion_pct = (self.completed_tasks / self.total_tasks) * 100
                elapsed_time = time.time() - start_time

                if self.start_time:
                    total_elapsed = time.time() - self.start_time
                    avg_time_per_task = total_elapsed / self.completed_tasks if self.completed_tasks > 0 else 0
                    remaining_tasks = self.total_tasks - self.completed_tasks
                    est_remaining_time = avg_time_per_task * remaining_tasks if avg_time_per_task > 0 else 0

                    tqdm.write(
                        f"✅ Completed task {self.completed_tasks}/{self.total_tasks} ({completion_pct:.1f}%) - {strategy_name}/{risk_category.value} in {elapsed_time:.1f}s"
                    )
                    tqdm.write(f"   Est. remaining: {est_remaining_time/60:.1f} minutes")
                else:
                    tqdm.write(
                        f"✅ Completed task {self.completed_tasks}/{self.total_tasks} ({completion_pct:.1f}%) - {strategy_name}/{risk_category.value} in {elapsed_time:.1f}s"
                    )

            self.task_statuses[task_key] = TASK_STATUS["COMPLETED"]

        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {strategy_name} strategy for {risk_category.value}: {str(e)}"
            )
            self.task_statuses[task_key] = TASK_STATUS["FAILED"]
            self.failed_tasks += 1
            async with progress_bar_lock:
                progress_bar.update(1)

        return None

    async def scan(
        self,
        target: Union[
            Callable,
            AzureOpenAIModelConfiguration,
            OpenAIModelConfiguration,
            PromptChatTarget,
        ],
        *,
        scan_name: Optional[str] = None,
        attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]] = [],
        skip_upload: bool = False,
        output_path: Optional[Union[str, os.PathLike]] = None,
        application_scenario: Optional[str] = None,
        parallel_execution: bool = True,
        max_parallel_tasks: int = 5,
        timeout: int = 3600,
        skip_evals: bool = False,
        **kwargs: Any,
    ) -> RedTeamResult:
        """Run a red team scan against the target using the specified strategies.

        :param target: The target model or function to scan
        :type target: Union[Callable, AzureOpenAIModelConfiguration, OpenAIModelConfiguration, PromptChatTarget]
        :param scan_name: Optional name for the evaluation
        :type scan_name: Optional[str]
        :param attack_strategies: List of attack strategies to use
        :type attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
        :param skip_upload: Flag to determine if the scan results should be uploaded
        :type skip_upload: bool
        :param output_path: Optional path for output
        :type output_path: Optional[Union[str, os.PathLike]]
        :param application_scenario: Optional description of the application scenario
        :type application_scenario: Optional[str]
        :param parallel_execution: Whether to execute orchestrator tasks in parallel
        :type parallel_execution: bool
        :param max_parallel_tasks: Maximum number of parallel orchestrator tasks to run (default: 5)
        :type max_parallel_tasks: int
        :param timeout: The timeout in seconds for API calls (default: 120)
        :type timeout: int
        :param skip_evals: Whether to skip the evaluation process
        :type skip_evals: bool
        :return: The output from the red team scan
        :rtype: RedTeamResult
        """
        user_agent: Optional[str] = kwargs.get("user_agent", "(type=redteam; subtype=RedTeam)")
        with UserAgentSingleton().add_useragent_product(user_agent):
            # Initialize scan
            self._initialize_scan(scan_name, application_scenario)

            # Setup logging and directories FIRST
            self._setup_scan_environment()

            # Setup component managers AFTER scan environment is set up
            self._setup_component_managers()

            # Update result processor with AI studio URL
            self.result_processor.ai_studio_url = getattr(self.mlflow_integration, "ai_studio_url", None)

            # Update component managers with the new logger
            self.orchestrator_manager.logger = self.logger
            self.evaluation_processor.logger = self.logger
            self.mlflow_integration.logger = self.logger
            self.result_processor.logger = self.logger

            # Validate attack objective generator
            if not self.attack_objective_generator:
                raise EvaluationException(
                    message="Attack objective generator is required for red team agent.",
                    internal_message="Attack objective generator is not provided.",
                    target=ErrorTarget.RED_TEAM,
                    category=ErrorCategory.MISSING_FIELD,
                    blame=ErrorBlame.USER_ERROR,
                )

            # Set default risk categories if not specified
            if not self.attack_objective_generator.risk_categories:
                self.logger.info("No risk categories specified, using all available categories")
                self.attack_objective_generator.risk_categories = [
                    RiskCategory.HateUnfairness,
                    RiskCategory.Sexual,
                    RiskCategory.Violence,
                    RiskCategory.SelfHarm,
                ]

            self.risk_categories = self.attack_objective_generator.risk_categories
            self.result_processor.risk_categories = self.risk_categories

            # Show risk categories to user
            tqdm.write(f"📊 Risk categories: {[rc.value for rc in self.risk_categories]}")
            self.logger.info(f"Risk categories to process: {[rc.value for rc in self.risk_categories]}")

            # Setup attack strategies
            if AttackStrategy.Baseline not in attack_strategies:
                attack_strategies.insert(0, AttackStrategy.Baseline)

            # Start MLFlow run if not skipping upload
            if skip_upload:
                eval_run = {}
            else:
                eval_run = self.mlflow_integration.start_redteam_mlflow_run(self.azure_ai_project, scan_name)
                tqdm.write(f"🔗 Track your red team scan in AI Foundry: {self.mlflow_integration.ai_studio_url}")

                # Update result processor with the AI studio URL now that it's available
                self.result_processor.ai_studio_url = self.mlflow_integration.ai_studio_url

            # Process strategies and execute scan
            flattened_attack_strategies = get_flattened_attack_strategies(attack_strategies)
            self._validate_strategies(flattened_attack_strategies)

            # Calculate total tasks and initialize tracking
            self.total_tasks = len(self.risk_categories) * len(flattened_attack_strategies)
            tqdm.write(f"📋 Planning {self.total_tasks} total tasks")
            self._initialize_tracking_dict(flattened_attack_strategies)

            # Fetch attack objectives
            all_objectives = await self._fetch_all_objectives(flattened_attack_strategies, application_scenario)

            chat_target = get_chat_target(target, self.prompt_to_context)
            self.chat_target = chat_target

            # Execute attacks
            await self._execute_attacks(
                flattened_attack_strategies,
                all_objectives,
                scan_name,
                skip_upload,
                output_path,
                timeout,
                skip_evals,
                parallel_execution,
                max_parallel_tasks,
            )

            # Process and return results
            return await self._finalize_results(skip_upload, skip_evals, eval_run, output_path)

    def _initialize_scan(self, scan_name: Optional[str], application_scenario: Optional[str]):
        """Initialize scan-specific variables."""
        self.start_time = time.time()
        self.task_statuses = {}
        self.completed_tasks = 0
        self.failed_tasks = 0

        # Generate unique scan ID and session ID
        self.scan_id = (
            f"scan_{scan_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if scan_name
            else f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.scan_id = self.scan_id.replace(" ", "_")
        self.scan_session_id = str(uuid.uuid4())
        self.application_scenario = application_scenario or ""

    def _setup_scan_environment(self):
        """Setup scan output directory and logging."""
        # Use file manager to create scan output directory
        self.scan_output_dir = self.file_manager.get_scan_output_path(self.scan_id)

        # Re-initialize logger with the scan output directory
        self.logger = setup_logger(output_dir=self.scan_output_dir)

        # Setup logging filters
        self._setup_logging_filters()

        log_section_header(self.logger, "Starting red team scan")
        tqdm.write(f"🚀 STARTING RED TEAM SCAN")
        tqdm.write(f"📂 Output directory: {self.scan_output_dir}")

    def _setup_logging_filters(self):
        """Setup logging filters to suppress unwanted logs."""

        class LogFilter(logging.Filter):
            def filter(self, record):
                # Filter out promptflow logs and evaluation warnings about artifacts
                if record.name.startswith("promptflow"):
                    return False
                if "The path to the artifact is either not a directory or does not exist" in record.getMessage():
                    return False
                if "RedTeamResult object at" in record.getMessage():
                    return False
                if "timeout won't take effect" in record.getMessage():
                    return False
                if "Submitting run" in record.getMessage():
                    return False
                return True

        # Apply filter to root logger
        root_logger = logging.getLogger()
        log_filter = LogFilter()

        for handler in root_logger.handlers:
            for filter in handler.filters:
                handler.removeFilter(filter)
            handler.addFilter(log_filter)

    def _validate_strategies(self, flattened_attack_strategies: List):
        """Validate attack strategies."""
        if len(flattened_attack_strategies) > 2 and (
            AttackStrategy.MultiTurn in flattened_attack_strategies
            or AttackStrategy.Crescendo in flattened_attack_strategies
        ):
            self.logger.warning(
                "MultiTurn and Crescendo strategies are not compatible with multiple attack strategies."
            )
            raise ValueError("MultiTurn and Crescendo strategies are not compatible with multiple attack strategies.")
        if AttackStrategy.Tense in flattened_attack_strategies and (
            RiskCategory.XPIA in self.risk_categories or RiskCategory.UngroundedAttributes in self.risk_categories
        ):
            self.logger.warning(
                "Tense strategy is not compatible with XPIA or UngroundedAttributes risk categories. Skipping Tense strategy."
            )
            raise ValueError("Tense strategy is not compatible with XPIA or UngroundedAttributes risk categories.")

    def _initialize_tracking_dict(self, flattened_attack_strategies: List):
        """Initialize the red_team_info tracking dictionary."""
        self.red_team_info = {}
        for strategy in flattened_attack_strategies:
            strategy_name = get_strategy_name(strategy)
            self.red_team_info[strategy_name] = {}
            for risk_category in self.risk_categories:
                self.red_team_info[strategy_name][risk_category.value] = {
                    "data_file": "",
                    "evaluation_result_file": "",
                    "evaluation_result": None,
                    "status": TASK_STATUS["PENDING"],
                }

    async def _fetch_all_objectives(self, flattened_attack_strategies: List, application_scenario: str) -> Dict:
        """Fetch all attack objectives for all strategies and risk categories."""
        log_section_header(self.logger, "Fetching attack objectives")
        all_objectives = {}

        # First fetch baseline objectives for all risk categories
        self.logger.info("Fetching baseline objectives for all risk categories")
        for risk_category in self.risk_categories:
            baseline_objectives = await self._get_attack_objectives(
                risk_category=risk_category,
                application_scenario=application_scenario,
                strategy="baseline",
            )
            if "baseline" not in all_objectives:
                all_objectives["baseline"] = {}
            all_objectives["baseline"][risk_category.value] = baseline_objectives
            tqdm.write(
                f"📝 Fetched baseline objectives for {risk_category.value}: {len(baseline_objectives)} objectives"
            )

        # Then fetch objectives for other strategies
        strategy_count = len(flattened_attack_strategies)
        for i, strategy in enumerate(flattened_attack_strategies):
            strategy_name = get_strategy_name(strategy)
            if strategy_name == "baseline":
                continue

            tqdm.write(f"🔄 Fetching objectives for strategy {i+1}/{strategy_count}: {strategy_name}")
            all_objectives[strategy_name] = {}

            for risk_category in self.risk_categories:
                objectives = await self._get_attack_objectives(
                    risk_category=risk_category,
                    application_scenario=application_scenario,
                    strategy=strategy_name,
                )
                all_objectives[strategy_name][risk_category.value] = objectives

        return all_objectives

    async def _execute_attacks(
        self,
        flattened_attack_strategies: List,
        all_objectives: Dict,
        scan_name: str,
        skip_upload: bool,
        output_path: str,
        timeout: int,
        skip_evals: bool,
        parallel_execution: bool,
        max_parallel_tasks: int,
    ):
        """Execute all attack combinations."""
        log_section_header(self.logger, "Starting orchestrator processing")

        # Create progress bar
        progress_bar = tqdm(
            total=self.total_tasks,
            desc="Scanning: ",
            ncols=100,
            unit="scan",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
        )
        progress_bar.set_postfix({"current": "initializing"})
        progress_bar_lock = asyncio.Lock()

        # Create all tasks for parallel processing
        orchestrator_tasks = []
        combinations = list(itertools.product(flattened_attack_strategies, self.risk_categories))

        for combo_idx, (strategy, risk_category) in enumerate(combinations):
            strategy_name = get_strategy_name(strategy)
            objectives = all_objectives[strategy_name][risk_category.value]

            if not objectives:
                self.logger.warning(f"No objectives found for {strategy_name}+{risk_category.value}, skipping")
                tqdm.write(f"⚠️ No objectives found for {strategy_name}/{risk_category.value}, skipping")
                self.red_team_info[strategy_name][risk_category.value]["status"] = TASK_STATUS["COMPLETED"]
                async with progress_bar_lock:
                    progress_bar.update(1)
                continue

            orchestrator_tasks.append(
                self._process_attack(
                    all_prompts=objectives,
                    strategy=strategy,
                    progress_bar=progress_bar,
                    progress_bar_lock=progress_bar_lock,
                    scan_name=scan_name,
                    skip_upload=skip_upload,
                    output_path=output_path,
                    risk_category=risk_category,
                    timeout=timeout,
                    _skip_evals=skip_evals,
                )
            )

        # Process tasks
        await self._process_orchestrator_tasks(orchestrator_tasks, parallel_execution, max_parallel_tasks, timeout)
        progress_bar.close()

    async def _process_orchestrator_tasks(
        self,
        orchestrator_tasks: List,
        parallel_execution: bool,
        max_parallel_tasks: int,
        timeout: int,
    ):
        """Process orchestrator tasks either in parallel or sequentially."""
        if parallel_execution and orchestrator_tasks:
            tqdm.write(f"⚙️ Processing {len(orchestrator_tasks)} tasks in parallel (max {max_parallel_tasks} at a time)")

            # Process tasks in batches
            for i in range(0, len(orchestrator_tasks), max_parallel_tasks):
                end_idx = min(i + max_parallel_tasks, len(orchestrator_tasks))
                batch = orchestrator_tasks[i:end_idx]

                try:
                    await asyncio.wait_for(asyncio.gather(*batch), timeout=timeout * 2)
                except asyncio.TimeoutError:
                    self.logger.warning(f"Batch {i//max_parallel_tasks+1} timed out")
                    tqdm.write(f"⚠️ Batch {i//max_parallel_tasks+1} timed out, continuing with next batch")
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing batch {i//max_parallel_tasks+1}: {str(e)}")
                    continue
        else:
            # Sequential execution
            tqdm.write("⚙️ Processing tasks sequentially")
            for i, task in enumerate(orchestrator_tasks):
                try:
                    await asyncio.wait_for(task, timeout=timeout)
                except asyncio.TimeoutError:
                    self.logger.warning(f"Task {i+1} timed out")
                    tqdm.write(f"⚠️ Task {i+1} timed out, continuing with next task")
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing task {i+1}: {str(e)}")
                    continue

    async def _finalize_results(self, skip_upload: bool, skip_evals: bool, eval_run, output_path: str) -> RedTeamResult:
        """Process and finalize scan results."""
        log_section_header(self.logger, "Processing results")

        # Convert results to RedTeamResult
        red_team_result = self.result_processor.to_red_team_result(self.red_team_info)

        output = RedTeamResult(
            scan_result=red_team_result,
            attack_details=red_team_result["attack_details"],
        )

        # Log results to MLFlow if not skipping upload
        if not skip_upload:
            self.logger.info("Logging results to AI Foundry")
            await self.mlflow_integration.log_redteam_results_to_mlflow(
                redteam_result=output,
                eval_run=eval_run,
                red_team_info=self.red_team_info,
                _skip_evals=skip_evals,
            )

        # Write output to specified path
        if output_path and output.scan_result:
            abs_output_path = output_path if os.path.isabs(output_path) else os.path.abspath(output_path)
            self.logger.info(f"Writing output to {abs_output_path}")
            _write_output(abs_output_path, output.scan_result)

            # Also save a copy to the scan output directory if available
            if self.scan_output_dir:
                final_output = os.path.join(self.scan_output_dir, "final_results.json")
                _write_output(final_output, output.scan_result)
        elif output.scan_result and self.scan_output_dir:
            # If no output_path was specified but we have scan_output_dir, save there
            final_output = os.path.join(self.scan_output_dir, "final_results.json")
            _write_output(final_output, output.scan_result)

        # Display final scorecard and results
        if output.scan_result:
            scorecard = format_scorecard(output.scan_result)
            tqdm.write(scorecard)

            # Print URL for detailed results
            studio_url = output.scan_result.get("studio_url", "")
            if studio_url:
                tqdm.write(f"\nDetailed results available at:\n{studio_url}")

            # Print the output directory path
            if self.scan_output_dir:
                tqdm.write(f"\n📂 All scan files saved to: {self.scan_output_dir}")

        tqdm.write(f"✅ Scan completed successfully!")
        self.logger.info("Scan completed successfully")

        # Close file handlers
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self.logger.removeHandler(handler)

        return output
