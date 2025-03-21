"""
Constants used in Red Team Agent.
"""

import os
# Update imports to use direct import from azure.ai.evaluation
from azure.ai.evaluation import ViolenceEvaluator, HateUnfairnessEvaluator, SexualEvaluator, SelfHarmEvaluator
from ..attack_strategy import AttackStrategy
from ..attack_objective_generator import RiskCategory

# File extensions
BASELINE_IDENTIFIER = "baseline"
DATA_EXT = ".jsonl"
RESULTS_EXT = ".json"

# Mapping of attack strategies to complexity levels
ATTACK_STRATEGY_COMPLEXITY_MAP = {
    "baseline": "baseline",
    AttackStrategy.Baseline.value: "baseline",
    "Baseline": "baseline",
    
    AttackStrategy.EASY.value: "easy",
    "EASY": "easy",
    
    AttackStrategy.MODERATE.value: "moderate",
    "MODERATE": "moderate",
    
    AttackStrategy.DIFFICULT.value: "difficult",
    "DIFFICULT": "difficult",
    
    # All specific strategies are difficult by default
    AttackStrategy.AnsiAttack.value: "difficult",
    AttackStrategy.AsciiArt.value: "difficult",
    AttackStrategy.AsciiSmuggler.value: "difficult",
    AttackStrategy.Atbash.value: "difficult",
    AttackStrategy.Base64.value: "difficult",
    AttackStrategy.Binary.value: "difficult",
    AttackStrategy.Caesar.value: "difficult",
    AttackStrategy.CharacterSpace.value: "difficult",
    AttackStrategy.CharSwap.value: "difficult",
    AttackStrategy.Diacritic.value: "difficult",
    AttackStrategy.Flip.value: "difficult",
    AttackStrategy.Leetspeak.value: "difficult",
    AttackStrategy.Morse.value: "difficult",
    AttackStrategy.ROT13.value: "difficult",
    AttackStrategy.StringJoin.value: "difficult",
    AttackStrategy.SuffixAppend.value: "difficult",
    AttackStrategy.Tense.value: "difficult",
    AttackStrategy.UnicodeConfusable.value: "difficult",
    AttackStrategy.UnicodeSubstitution.value: "difficult",
    AttackStrategy.Url.value: "difficult",
    AttackStrategy.Jailbreak.value: "difficult",
    
    # Keep the original strategy names as they were before
    "AnsiAttackConverter": "AnsiAttackConverter",
    "AsciiArtConverter": "AsciiArtConverter",
    "AsciiSmugglerConverter": "AsciiSmugglerConverter",
    "AtbashConverter": "AtbashConverter",
    "Base64Converter": "Base64Converter", 
    "BinaryConverter": "BinaryConverter",
    "CaesarConverter": "CaesarConverter",
    "CharacterSpaceConverter": "CharacterSpaceConverter",
    "CharSwapGenerator": "CharSwapGenerator",
    "DiacriticConverter": "DiacriticConverter",
    "FlipConverter": "FlipConverter",
    "LeetspeakConverter": "LeetspeakConverter",
    "MorseConverter": "MorseConverter",
    "ROT13Converter": "ROT13Converter",
    "StringJoinConverter": "StringJoinConverter",
    "SuffixAppendConverter": "SuffixAppendConverter",
    "UnicodeConfusableConverter": "UnicodeConfusableConverter",
    "UnicodeSubstitutionConverter": "UnicodeSubstitutionConverter",
    "UrlConverter": "UrlConverter",
    "DefaultConverter": "DefaultConverter",
}

# Mapping of risk categories to their evaluators
RISK_CATEGORY_EVALUATOR_MAP = {
    RiskCategory.Violence: ViolenceEvaluator,
    RiskCategory.HateUnfairness: HateUnfairnessEvaluator,
    RiskCategory.Sexual: SexualEvaluator,
    RiskCategory.SelfHarm: SelfHarmEvaluator
}

# Task timeouts and status codes
INTERNAL_TASK_TIMEOUT = 120

# Task status definitions
TASK_STATUS = {
    "PENDING": "pending",
    "RUNNING": "running",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "TIMEOUT": "timeout"
}
