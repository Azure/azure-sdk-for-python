"""
Utility functions for formatting, conversion, and processing in Red Team Agent.
"""

import json
import pandas as pd
import math
from datetime import datetime
from typing import Dict, List, Union, Any, Optional, cast
from .._attack_strategy import AttackStrategy
from .._red_team_result import _RedTeamResult
from pyrit.models import ChatMessage


def message_to_dict(message: ChatMessage) -> Dict[str, str]:
    """Convert a ChatMessage to dictionary format.
    
    :param message: The chat message to convert
    :type message: ChatMessage
    :return: Dictionary representation with role and content
    :rtype: Dict[str, str]
    """
    return {
        "role": message.role,
        "content": message.content,
    }


def get_strategy_name(attack_strategy: Union[AttackStrategy, List[AttackStrategy]]) -> str:
    """Get a string name for an attack strategy or list of strategies.
    
    :param attack_strategy: The attack strategy or list of strategies
    :type attack_strategy: Union[AttackStrategy, List[AttackStrategy]]
    :return: A string name for the strategy
    :rtype: str
    """
    if isinstance(attack_strategy, List):
        return "_".join([str(strategy.value) for strategy in attack_strategy])
    else:
        return str(attack_strategy.value)


def get_flattened_attack_strategies(attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]) -> List[Union[AttackStrategy, List[AttackStrategy]]]:
    """Flatten complex attack strategies into individual strategies.
    
    :param attack_strategies: List of attack strategies to flatten
    :type attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
    :return: Flattened list of attack strategies
    :rtype: List[Union[AttackStrategy, List[AttackStrategy]]]
    """
    flattened_strategies = [] 
    seen_strategies = set()
    attack_strategies_temp = attack_strategies.copy()
    
    if AttackStrategy.EASY in attack_strategies_temp:
        attack_strategies_temp.extend(
            [
                AttackStrategy.Base64, 
                AttackStrategy.Flip, 
                AttackStrategy.Morse
            ]
        )
        attack_strategies_temp.remove(AttackStrategy.EASY)
    
    if AttackStrategy.MODERATE in attack_strategies_temp:
        # TODO: change these before merging.
        attack_strategies_temp.extend([
            AttackStrategy.AsciiArt,
            AttackStrategy.Compose([
                AttackStrategy.Tense,
                AttackStrategy.Flip
            ]),
        ])
        attack_strategies_temp.remove(AttackStrategy.MODERATE)
    if AttackStrategy.DIFFICULT in attack_strategies_temp:
        # TODO: change these before merging.
        attack_strategies_temp.extend([
            AttackStrategy.Compose([
                AttackStrategy.Tense,
                AttackStrategy.Morse
            ]),
            AttackStrategy.Compose([
                AttackStrategy.Morse,
                AttackStrategy.Base64
            ]),
        ])
        attack_strategies_temp.remove(AttackStrategy.DIFFICULT)

    ## Baseline is always included    
    attack_strategies_temp.append(AttackStrategy.Baseline)

    for strategy in attack_strategies_temp:
        if isinstance(strategy, List) and tuple(strategy) not in seen_strategies: # For composed strategies
            flattened_strategies.append([s for s in strategy])
            seen_strategies.add(tuple(strategy))
        elif isinstance(strategy, AttackStrategy) and strategy not in seen_strategies: # For single strategies
            flattened_strategies.append(strategy)
            seen_strategies.add(strategy)
    
    return flattened_strategies


def get_attack_success(result: str) -> bool:
    """
    Based on EVALUATION_PASS_FAIL_MAPPING, returns True denoting attack success if result matches the value of the EVALUATION_PASS_FAIL_MAPPING key False. 
    """
    from .._red_team import EVALUATION_PASS_FAIL_MAPPING
    return result == EVALUATION_PASS_FAIL_MAPPING.get(False, "true")


def format_scorecard(redteam_result: _RedTeamResult) -> str:
    """Format the _RedTeamResult into a human-readable scorecard.
    
    The scorecard presents a summary of attack success rates across different risk categories
    and attack complexity levels in a tabular format.

    :param redteam_result: The _RedTeamResult object to format
    :type redteam_result: Dict[str, Any]
    :return: A formatted scorecard as a string
    :rtype: str
    """
    scorecard = redteam_result["redteaming_scorecard"]
    overall_asr = scorecard["risk_category_summary"][0]["overall_asr"] if scorecard["risk_category_summary"] else 0
    
    output = [f"Overall ASR: {overall_asr}%"]
    
    separator = "-" * 108
    output.append(separator)
    output.append(f"{'Risk Category':<15}| {'Baseline ASR':<14} | {'Easy-Complexity Attacks ASR':<28} | {'Moderate-Complexity Attacks ASR':<30} | {'Difficult-Complexity Attacks ASR':<30}")
    output.append(separator)
    
    for item in scorecard["joint_risk_attack_summary"]:
        risk_category = item["risk_category"].replace("_", "-").capitalize()
        baseline = f"{item['baseline_asr']}%" if 'baseline_asr' in item else "N/A"
        easy = f"{item['easy_complexity_asr']}%" if 'easy_complexity_asr' in item else "N/A"
        moderate = f"{item['moderate_complexity_asr']}%" if 'moderate_complexity_asr' in item else "N/A"
        difficult = f"{item['difficult_complexity_asr']}%" if 'difficult_complexity_asr' in item else "N/A"
        
        output.append(f"{risk_category:<15}| {baseline:<14} | {easy:<28} | {moderate:<31} | {difficult:<30}")
    
    return "\n".join(output)


def is_none_or_nan(value: Any) -> bool:
    """Check if a value is None or NaN."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def list_mean_nan_safe(data_list: List[Any]) -> float:
    """Calculate the mean of a list, handling None and NaN values safely.
    
    :param data_list: List of values to calculate mean for
    :type data_list: List[Any]
    :return: Mean value or 0.0 if list is empty after filtering
    :rtype: float
    """
    filtered_list = [x for x in data_list if not is_none_or_nan(x)]
    if not filtered_list:
        return 0.0
    return sum(filtered_list) / len(filtered_list)