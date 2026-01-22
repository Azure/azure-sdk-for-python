# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Foundry execution manager for coordinating scenario-based red team execution."""

import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from pyrit.prompt_target import PromptChatTarget
from pyrit.scenario.foundry import FoundryStrategy

from .._attack_objective_generator import RiskCategory
from .._attack_strategy import AttackStrategy
from ._dataset_builder import DatasetConfigurationBuilder
from ._foundry_result_processor import FoundryResultProcessor
from ._rai_scorer import RAIServiceScorer
from ._scenario_orchestrator import ScenarioOrchestrator
from ._strategy_mapping import StrategyMapper


class FoundryExecutionManager:
    """Manages Foundry-based red team execution.

    This manager coordinates the execution of Foundry scenarios across
    multiple risk categories. It handles:
    - Converting RAI objectives to DatasetConfiguration
    - Creating and configuring scenarios per risk category
    - Running attacks in parallel by risk category
    - Collecting and processing results
    """

    def __init__(
        self,
        credential: Any,
        azure_ai_project: Dict[str, str],
        logger: logging.Logger,
        output_dir: str,
        adversarial_chat_target: Optional[PromptChatTarget] = None,
    ):
        """Initialize the execution manager.

        :param credential: Azure credential for authentication
        :type credential: Any
        :param azure_ai_project: Azure AI project configuration
        :type azure_ai_project: Dict[str, str]
        :param logger: Logger instance
        :type logger: logging.Logger
        :param output_dir: Directory for output files
        :type output_dir: str
        :param adversarial_chat_target: Optional target for multi-turn attacks
        :type adversarial_chat_target: Optional[PromptChatTarget]
        """
        self.credential = credential
        self.azure_ai_project = azure_ai_project
        self.logger = logger
        self.output_dir = output_dir
        self.adversarial_chat_target = adversarial_chat_target

        self._scenarios: Dict[str, ScenarioOrchestrator] = {}
        self._dataset_configs: Dict[str, Any] = {}
        self._result_processors: Dict[str, FoundryResultProcessor] = {}

    async def execute_attacks(
        self,
        objective_target: PromptChatTarget,
        risk_categories: List[RiskCategory],
        attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]],
        objectives_by_risk: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Execute attacks for all risk categories using Foundry.

        :param objective_target: Target to attack
        :type objective_target: PromptChatTarget
        :param risk_categories: List of risk categories to test
        :type risk_categories: List[RiskCategory]
        :param attack_strategies: List of attack strategies to use
        :type attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
        :param objectives_by_risk: Dictionary mapping risk category to objectives
        :type objectives_by_risk: Dict[str, List[Dict[str, Any]]]
        :return: Dictionary mapping risk category to red_team_info style data
        :rtype: Dict[str, Any]
        """
        # Filter strategies for Foundry (exclude special handling strategies)
        foundry_strategies, special_strategies = StrategyMapper.filter_for_foundry(attack_strategies)
        mapped_strategies = StrategyMapper.map_strategies(foundry_strategies)

        self.logger.info(
            f"Executing Foundry attacks with {len(mapped_strategies)} strategies "
            f"across {len(risk_categories)} risk categories"
        )

        # Check if adversarial chat is needed
        needs_adversarial = StrategyMapper.requires_adversarial_chat(foundry_strategies)
        if needs_adversarial and not self.adversarial_chat_target:
            self.logger.warning(
                "Multi-turn strategies requested but no adversarial_chat_target provided. "
                "Multi-turn attacks will be skipped."
            )
            # Filter out multi-turn strategies
            mapped_strategies = [
                s for s in mapped_strategies
                if s not in (FoundryStrategy.MultiTurn, FoundryStrategy.Crescendo)
            ]

        # Check if we need XPIA handling
        has_indirect = StrategyMapper.has_indirect_attack(attack_strategies)

        red_team_info: Dict[str, Dict[str, Any]] = {}

        # Process each risk category
        for risk_category in risk_categories:
            risk_value = risk_category.value
            objectives = objectives_by_risk.get(risk_value, [])

            if not objectives:
                self.logger.info(f"No objectives for {risk_value}, skipping")
                continue

            self.logger.info(f"Processing {len(objectives)} objectives for {risk_value}")

            # Build dataset configuration
            dataset_config = self._build_dataset_config(
                risk_category=risk_value,
                objectives=objectives,
                is_indirect_attack=has_indirect,
            )
            self._dataset_configs[risk_value] = dataset_config

            # Create scorer for this risk category
            scorer = RAIServiceScorer(
                credential=self.credential,
                azure_ai_project=self.azure_ai_project,
                risk_category=risk_category,
                logger=self.logger,
                dataset_config=dataset_config,
            )

            # Create scenario orchestrator
            orchestrator = ScenarioOrchestrator(
                risk_category=risk_value,
                objective_target=objective_target,
                rai_scorer=scorer,
                logger=self.logger,
                adversarial_chat_target=self.adversarial_chat_target,
            )
            self._scenarios[risk_value] = orchestrator

            # Execute attacks
            try:
                await orchestrator.execute(
                    dataset_config=dataset_config,
                    strategies=mapped_strategies,
                )
            except Exception as e:
                self.logger.error(f"Error executing attacks for {risk_value}: {e}")
                # Use "Foundry" as fallback strategy name to match expected structure
                if "Foundry" not in red_team_info:
                    red_team_info["Foundry"] = {}
                red_team_info["Foundry"][risk_value] = {
                    "data_file": "",
                    "status": "failed",
                    "error": str(e),
                    "asr": 0.0,
                }
                continue

            # Process results
            result_processor = FoundryResultProcessor(
                scenario=orchestrator,
                dataset_config=dataset_config,
                risk_category=risk_value,
            )
            self._result_processors[risk_value] = result_processor

            # Generate JSONL output
            output_path = os.path.join(
                self.output_dir,
                f"{risk_value}_results.jsonl"
            )
            result_processor.to_jsonl(output_path)

            # Get summary stats
            stats = result_processor.get_summary_stats()

            # Build red_team_info entry for this risk category
            # Group results by strategy for compatibility with existing structure
            strategy_results = self._group_results_by_strategy(
                orchestrator=orchestrator,
                risk_value=risk_value,
                output_path=output_path,
            )

            for strategy_name, strategy_data in strategy_results.items():
                if strategy_name not in red_team_info:
                    red_team_info[strategy_name] = {}
                red_team_info[strategy_name][risk_value] = strategy_data

        return red_team_info

    def _build_dataset_config(
        self,
        risk_category: str,
        objectives: List[Dict[str, Any]],
        is_indirect_attack: bool = False,
    ) -> Any:
        """Build DatasetConfiguration from RAI objectives.

        :param risk_category: Risk category for objectives
        :type risk_category: str
        :param objectives: List of objective dictionaries from RAI service
        :type objectives: List[Dict[str, Any]]
        :param is_indirect_attack: Whether this is an XPIA attack
        :type is_indirect_attack: bool
        :return: DatasetConfiguration object
        :rtype: Any
        """
        builder = DatasetConfigurationBuilder(
            risk_category=risk_category,
            is_indirect_attack=is_indirect_attack,
        )

        for obj in objectives:
            # Extract objective content
            content = self._extract_objective_content(obj)
            if not content:
                continue

            # Extract context items
            context_items = self._extract_context_items(obj)

            # Extract metadata
            metadata = obj.get("metadata", {})
            objective_id = obj.get("id") or obj.get("objective_id")

            builder.add_objective_with_context(
                objective_content=content,
                objective_id=objective_id,
                context_items=context_items,
                metadata=metadata,
            )

        return builder.build()

    def _extract_objective_content(self, obj: Any) -> Optional[str]:
        """Extract objective content from various formats.

        :param obj: Objective dictionary or string
        :type obj: Any
        :return: Objective content string or None
        :rtype: Optional[str]
        """
        # Handle non-dict types
        if not isinstance(obj, dict):
            return None

        # Try different possible locations for the content
        if "messages" in obj and obj["messages"]:
            # Standard format: messages[0].content
            first_msg = obj["messages"][0]
            if isinstance(first_msg, dict):
                return first_msg.get("content")

        if "content" in obj:
            return obj["content"]

        if "objective" in obj:
            return obj["objective"]

        return None

    def _extract_context_items(self, obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract context items from objective.

        :param obj: Objective dictionary
        :type obj: Dict[str, Any]
        :return: List of context item dictionaries
        :rtype: List[Dict[str, Any]]
        """
        context_items = []

        if "messages" in obj and obj["messages"]:
            first_msg = obj["messages"][0]
            if isinstance(first_msg, dict):
                # Check for context in message
                if "context" in first_msg:
                    ctx = first_msg["context"]
                    if isinstance(ctx, list):
                        context_items.extend(ctx)
                    elif isinstance(ctx, dict):
                        context_items.append(ctx)

                # Also check for separate context fields
                if "context_type" in first_msg:
                    context_items.append({
                        "content": first_msg.get("content", ""),
                        "context_type": first_msg["context_type"],
                        "tool_name": first_msg.get("tool_name"),
                    })

        # Top-level context
        if "context" in obj:
            ctx = obj["context"]
            if isinstance(ctx, list):
                context_items.extend(ctx)
            elif isinstance(ctx, dict):
                context_items.append(ctx)

        return context_items

    def _group_results_by_strategy(
        self,
        orchestrator: ScenarioOrchestrator,
        risk_value: str,
        output_path: str,
    ) -> Dict[str, Dict[str, Any]]:
        """Group attack results by strategy for red_team_info format.

        :param orchestrator: Completed scenario orchestrator
        :type orchestrator: ScenarioOrchestrator
        :param risk_value: Risk category value
        :type risk_value: str
        :param output_path: Path to JSONL output file
        :type output_path: str
        :return: Dictionary mapping strategy name to result data
        :rtype: Dict[str, Dict[str, Any]]
        """
        asr_by_strategy = orchestrator.calculate_asr_by_strategy()

        results: Dict[str, Dict[str, Any]] = {}

        for strategy_name, asr in asr_by_strategy.items():
            # Clean strategy name for display
            clean_name = strategy_name.replace("Attack", "").replace("Converter", "")

            results[clean_name] = {
                "data_file": output_path,
                "status": "completed",
                "asr": asr,
            }

        # If no strategy-specific results, use overall stats
        if not results:
            results["Foundry"] = {
                "data_file": output_path,
                "status": "completed",
                "asr": orchestrator.calculate_asr(),
            }

        return results

    def get_scenarios(self) -> Dict[str, ScenarioOrchestrator]:
        """Get all executed scenarios.

        :return: Dictionary mapping risk category to scenario
        :rtype: Dict[str, ScenarioOrchestrator]
        """
        return self._scenarios

    def get_dataset_configs(self) -> Dict[str, Any]:
        """Get all dataset configurations.

        :return: Dictionary mapping risk category to dataset config
        :rtype: Dict[str, Any]
        """
        return self._dataset_configs
