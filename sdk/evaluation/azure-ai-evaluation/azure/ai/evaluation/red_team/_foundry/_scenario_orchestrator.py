# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario orchestrator for Foundry-based attack execution."""

import logging
from typing import Any, Dict, List, Optional

from pyrit.models import AttackResult
from pyrit.models.scenario_result import ScenarioResult
from pyrit.prompt_target import PromptChatTarget
from pyrit.scenario import DatasetConfiguration
from pyrit.scenario.scenarios.foundry import FoundryScenario, FoundryStrategy

from ._rai_scorer import RAIServiceScorer


class ScenarioOrchestrator:
    """Orchestrates Foundry scenario execution for a risk category.

    This orchestrator creates and runs a Foundry scenario that batches
    all attack strategies for a single risk category. It delegates
    attack execution to PyRIT while using custom RAI scorers for
    evaluation.
    """

    def __init__(
        self,
        risk_category: str,
        objective_target: PromptChatTarget,
        rai_scorer: RAIServiceScorer,
        logger: logging.Logger,
        adversarial_chat_target: Optional[PromptChatTarget] = None,
    ):
        """Initialize the scenario orchestrator.

        :param risk_category: The risk category being tested (e.g., "violence")
        :type risk_category: str
        :param objective_target: The target to attack (chat target)
        :type objective_target: PromptChatTarget
        :param rai_scorer: Custom RAI scorer for evaluating responses
        :type rai_scorer: RAIServiceScorer
        :param logger: Logger instance
        :type logger: logging.Logger
        :param adversarial_chat_target: Optional adversarial chat for multi-turn attacks
        :type adversarial_chat_target: Optional[PromptChatTarget]
        """
        self.risk_category = risk_category
        self.objective_target = objective_target
        self.rai_scorer = rai_scorer
        self.logger = logger
        self.adversarial_chat_target = adversarial_chat_target
        self._scenario: Optional[FoundryScenario] = None
        self._scenario_result: Optional[ScenarioResult] = None

    async def execute(
        self,
        dataset_config: DatasetConfiguration,
        strategies: List[FoundryStrategy],
    ) -> "ScenarioOrchestrator":
        """Execute attacks for all strategies in this risk category.

        Creates a FoundryScenario with the provided dataset and strategies,
        then runs the attack asynchronously. Results are stored in PyRIT's
        memory and can be retrieved via get_attack_results().

        :param dataset_config: DatasetConfiguration with objectives and context
        :type dataset_config: DatasetConfiguration
        :param strategies: List of FoundryStrategy enums to execute
        :type strategies: List[FoundryStrategy]
        :return: Self for chaining
        :rtype: ScenarioOrchestrator
        """
        num_objectives = len(dataset_config.get_all_seed_groups())
        self.logger.info(
            f"Creating FoundryScenario for {self.risk_category} with "
            f"{len(strategies)} strategies and {num_objectives} objectives"
        )

        # Create scoring configuration from our RAI scorer
        # FoundryScenario expects an AttackScoringConfig
        scoring_config = self._create_scoring_config()

        # Create FoundryScenario
        self._scenario = FoundryScenario(
            adversarial_chat=self.adversarial_chat_target,
            attack_scoring_config=scoring_config,
            include_baseline=False,  # We handle baseline separately
        )

        # Initialize with dataset and strategies
        # Note: FoundryScenario.initialize_async expects specific parameters
        self.logger.info(f"Initializing FoundryScenario with strategies: {[s.value for s in strategies]}")

        await self._scenario.initialize_async(
            objective_target=self.objective_target,
            scenario_strategies=strategies,
            dataset_config=dataset_config,
        )

        # Run attack - PyRIT handles all execution
        self.logger.info(f"Executing attacks for {self.risk_category}...")
        self._scenario_result = await self._scenario.run_async()

        self.logger.info(f"Attack execution complete for {self.risk_category}")

        return self

    def _create_scoring_config(self) -> Any:
        """Create attack scoring configuration from RAI scorer.

        FoundryScenario uses AttackScoringConfig to configure how attacks are scored.
        We wrap our RAI scorer in the appropriate configuration.

        :return: Attack scoring configuration
        :rtype: Any
        """
        # Import here to avoid circular imports
        from pyrit.executor.attack import AttackScoringConfig

        return AttackScoringConfig(
            objective_scorer=self.rai_scorer,
            use_score_as_feedback=True,
        )

    def get_attack_results(self) -> List[AttackResult]:
        """Get attack results from the completed scenario.

        :return: List of AttackResult objects from the scenario
        :rtype: List[AttackResult]
        :raises RuntimeError: If scenario hasn't been executed
        """
        if not self._scenario_result:
            raise RuntimeError("Scenario has not been executed. Call execute() first.")

        # ScenarioResult.attack_results is a dict[str, List[AttackResult]]
        # Flatten all results into a single list
        all_results: List[AttackResult] = []
        for objective_id, results_list in self._scenario_result.attack_results.items():
            all_results.extend(results_list)

        return all_results

    def get_memory(self) -> Any:
        """Get the memory instance for querying conversations.

        :return: MemoryInterface instance
        :rtype: Any
        :raises RuntimeError: If scenario hasn't been executed
        """
        if not self._scenario:
            raise RuntimeError("Scenario has not been executed. Call execute() first.")

        from pyrit.memory import CentralMemory
        return CentralMemory.get_memory_instance()

    def calculate_asr(self) -> float:
        """Calculate Attack Success Rate from results.

        :return: Attack success rate as a float between 0 and 1
        :rtype: float
        """
        from pyrit.models import AttackOutcome

        results = self.get_attack_results()
        if not results:
            return 0.0

        successful = sum(1 for r in results if r.outcome == AttackOutcome.SUCCESS)
        return successful / len(results)

    def calculate_asr_by_strategy(self) -> Dict[str, float]:
        """Calculate Attack Success Rate grouped by strategy.

        :return: Dictionary mapping strategy name to ASR
        :rtype: Dict[str, float]
        """
        from pyrit.models import AttackOutcome

        results = self.get_attack_results()
        if not results:
            return {}

        strategy_stats: Dict[str, Dict[str, int]] = {}

        for result in results:
            strategy_name = result.attack_identifier.get("__type__", "Unknown")

            if strategy_name not in strategy_stats:
                strategy_stats[strategy_name] = {"total": 0, "successful": 0}

            strategy_stats[strategy_name]["total"] += 1
            if result.outcome == AttackOutcome.SUCCESS:
                strategy_stats[strategy_name]["successful"] += 1

        return {
            strategy: stats["successful"] / stats["total"] if stats["total"] > 0 else 0.0
            for strategy, stats in strategy_stats.items()
        }

    @property
    def scenario(self) -> Optional[FoundryScenario]:
        """Get the underlying FoundryScenario.

        :return: FoundryScenario instance or None if not executed
        :rtype: Optional[FoundryScenario]
        """
        return self._scenario
