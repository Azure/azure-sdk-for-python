# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Strategy mapping between AttackStrategy and FoundryStrategy."""

from typing import Dict, List, Optional, Union

from pyrit.scenario.scenarios.foundry import FoundryStrategy

from .._attack_strategy import AttackStrategy


class StrategyMapper:
    """Maps AttackStrategy enums to FoundryStrategy enums.

    Provides bidirectional mapping between Azure AI Evaluation's AttackStrategy
    and PyRIT's FoundryStrategy enums. Also handles special cases like
    composed strategies and strategies that require special handling.
    """

    # Direct mapping from AttackStrategy to FoundryStrategy
    _STRATEGY_MAP: Dict[AttackStrategy, Optional[FoundryStrategy]] = {
        # Aggregate strategies
        AttackStrategy.EASY: FoundryStrategy.EASY,
        AttackStrategy.MODERATE: FoundryStrategy.MODERATE,
        AttackStrategy.DIFFICULT: FoundryStrategy.DIFFICULT,
        # Individual converter strategies (Easy)
        AttackStrategy.AnsiAttack: FoundryStrategy.AnsiAttack,
        AttackStrategy.AsciiArt: FoundryStrategy.AsciiArt,
        AttackStrategy.AsciiSmuggler: FoundryStrategy.AsciiSmuggler,
        AttackStrategy.Atbash: FoundryStrategy.Atbash,
        AttackStrategy.Base64: FoundryStrategy.Base64,
        AttackStrategy.Binary: FoundryStrategy.Binary,
        AttackStrategy.Caesar: FoundryStrategy.Caesar,
        AttackStrategy.CharacterSpace: FoundryStrategy.CharacterSpace,
        AttackStrategy.CharSwap: FoundryStrategy.CharSwap,
        AttackStrategy.Diacritic: FoundryStrategy.Diacritic,
        AttackStrategy.Flip: FoundryStrategy.Flip,
        AttackStrategy.Leetspeak: FoundryStrategy.Leetspeak,
        AttackStrategy.Morse: FoundryStrategy.Morse,
        AttackStrategy.ROT13: FoundryStrategy.ROT13,
        AttackStrategy.SuffixAppend: FoundryStrategy.SuffixAppend,
        AttackStrategy.StringJoin: FoundryStrategy.StringJoin,
        AttackStrategy.UnicodeConfusable: FoundryStrategy.UnicodeConfusable,
        AttackStrategy.UnicodeSubstitution: FoundryStrategy.UnicodeSubstitution,
        AttackStrategy.Url: FoundryStrategy.Url,
        AttackStrategy.Jailbreak: FoundryStrategy.Jailbreak,
        # Moderate strategies
        AttackStrategy.Tense: FoundryStrategy.Tense,
        # Multi-turn attack strategies (Difficult)
        AttackStrategy.MultiTurn: FoundryStrategy.MultiTurn,
        AttackStrategy.Crescendo: FoundryStrategy.Crescendo,
        # Special handling strategies (not directly mapped)
        AttackStrategy.Baseline: None,  # Handled via include_baseline parameter
        AttackStrategy.IndirectJailbreak: None,  # Handled via XPIA injection in dataset builder
    }

    # Strategies that require special handling and should not use Foundry directly
    SPECIAL_STRATEGIES = {
        AttackStrategy.Baseline,
        AttackStrategy.IndirectJailbreak,
    }

    # Multi-turn strategies that require adversarial_chat
    MULTI_TURN_STRATEGIES = {
        AttackStrategy.MultiTurn,
        AttackStrategy.Crescendo,
    }

    @classmethod
    def map_strategy(cls, strategy: AttackStrategy) -> Optional[FoundryStrategy]:
        """Map a single AttackStrategy to FoundryStrategy.

        :param strategy: The AttackStrategy to map
        :type strategy: AttackStrategy
        :return: Corresponding FoundryStrategy or None if special handling needed
        :rtype: Optional[FoundryStrategy]
        """
        return cls._STRATEGY_MAP.get(strategy)

    @classmethod
    def map_strategies(
        cls,
        strategies: List[Union[AttackStrategy, List[AttackStrategy]]],
    ) -> List[FoundryStrategy]:
        """Map a list of AttackStrategies to FoundryStrategies.

        Handles both single strategies and composed strategies (lists of strategies).
        Filters out strategies that require special handling.

        :param strategies: List of AttackStrategy or composed strategy lists
        :type strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
        :return: List of FoundryStrategy enums
        :rtype: List[FoundryStrategy]
        """
        foundry_strategies = []

        for strategy in strategies:
            if isinstance(strategy, list):
                # Composed strategy - map each component
                composed = cls._map_composed_strategy(strategy)
                if composed:
                    foundry_strategies.extend(composed)
            else:
                # Single strategy
                foundry_strategy = cls.map_strategy(strategy)
                if foundry_strategy is not None:
                    foundry_strategies.append(foundry_strategy)

        return foundry_strategies

    @classmethod
    def _map_composed_strategy(
        cls,
        strategies: List[AttackStrategy],
    ) -> List[FoundryStrategy]:
        """Map a composed strategy (list of strategies) to FoundryStrategies.

        :param strategies: List of AttackStrategy to compose
        :type strategies: List[AttackStrategy]
        :return: List of FoundryStrategy enums for composition
        :rtype: List[FoundryStrategy]
        """
        mapped = []
        for strategy in strategies:
            foundry_strategy = cls.map_strategy(strategy)
            if foundry_strategy is not None:
                mapped.append(foundry_strategy)
        return mapped

    @classmethod
    def requires_special_handling(cls, strategy: AttackStrategy) -> bool:
        """Check if a strategy requires special handling outside Foundry.

        :param strategy: The strategy to check
        :type strategy: AttackStrategy
        :return: True if strategy needs special handling
        :rtype: bool
        """
        return strategy in cls.SPECIAL_STRATEGIES

    @classmethod
    def is_multi_turn(cls, strategy: AttackStrategy) -> bool:
        """Check if a strategy is a multi-turn attack strategy.

        :param strategy: The strategy to check
        :type strategy: AttackStrategy
        :return: True if strategy is multi-turn
        :rtype: bool
        """
        return strategy in cls.MULTI_TURN_STRATEGIES

    @classmethod
    def filter_for_foundry(
        cls,
        strategies: List[Union[AttackStrategy, List[AttackStrategy]]],
    ) -> tuple:
        """Separate strategies into Foundry-compatible and special handling groups.

        :param strategies: List of strategies to filter
        :type strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
        :return: Tuple of (foundry_strategies, special_strategies)
        :rtype: tuple
        """
        foundry_compatible = []
        special_handling = []

        for strategy in strategies:
            if isinstance(strategy, list):
                # Composed strategy - check all components
                has_special = any(cls.requires_special_handling(s) for s in strategy)
                if has_special:
                    special_handling.append(strategy)
                else:
                    foundry_compatible.append(strategy)
            else:
                if cls.requires_special_handling(strategy):
                    special_handling.append(strategy)
                else:
                    foundry_compatible.append(strategy)

        return foundry_compatible, special_handling

    @classmethod
    def has_indirect_attack(
        cls,
        strategies: List[Union[AttackStrategy, List[AttackStrategy]]],
    ) -> bool:
        """Check if any strategy is an indirect/XPIA attack.

        :param strategies: List of strategies to check
        :type strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
        :return: True if IndirectJailbreak is in the strategies
        :rtype: bool
        """
        for strategy in strategies:
            if isinstance(strategy, list):
                if AttackStrategy.IndirectJailbreak in strategy:
                    return True
            elif strategy == AttackStrategy.IndirectJailbreak:
                return True
        return False

    @classmethod
    def requires_adversarial_chat(
        cls,
        strategies: List[Union[AttackStrategy, List[AttackStrategy]]],
    ) -> bool:
        """Check if any strategy requires adversarial chat for multi-turn.

        :param strategies: List of strategies to check
        :type strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
        :return: True if any strategy is multi-turn
        :rtype: bool
        """
        for strategy in strategies:
            if isinstance(strategy, list):
                if any(cls.is_multi_turn(s) for s in strategy):
                    return True
            elif cls.is_multi_turn(strategy):
                return True
        return False
