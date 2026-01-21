"""
Utility functions for formatting, conversion, and processing in Red Team Agent.
"""

import json
import math
import itertools
import os
import logging
from typing import Dict, List, Union, Any
from pathlib import Path
from pyrit.models import ChatMessage
from pyrit.memory import CentralMemory
from .._attack_strategy import AttackStrategy
from .._red_team_result import RedTeamResult


def message_to_dict(
    message: ChatMessage,
    context: str = None,
    tool_calls: List[Any] = None,
    token_usage: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Convert a ChatMessage and context to dictionary format.

    :param message: The chat message to convert
    :type message: ChatMessage
    :param context: Additional context to include in the dictionary
    :type context: str
    :param tool_calls: List of tool calls to include in the dictionary
    :type tool_calls: List[Any]
    :param token_usage: Token usage information from the callback
    :type token_usage: Dict[str, Any]
    :return: Dictionary representation with role and content
    :rtype: Dict[str, Any]
    """
    msg_dict = {
        "role": message.role,
        "content": message.content,
        "context": context,
        "tool_calls": tool_calls,
    }
    if token_usage:
        msg_dict["token_usage"] = token_usage
    return msg_dict


def get_strategy_name(
    attack_strategy: Union[AttackStrategy, List[AttackStrategy]]
) -> str:
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


def get_flattened_attack_strategies(
    attack_strategies: List[Union[AttackStrategy, List[AttackStrategy]]]
) -> List[Union[AttackStrategy, List[AttackStrategy]]]:
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
            [AttackStrategy.Base64, AttackStrategy.Flip, AttackStrategy.Morse]
        )
        attack_strategies_temp.remove(AttackStrategy.EASY)

    if AttackStrategy.MODERATE in attack_strategies_temp:
        attack_strategies_temp.extend(
            [AttackStrategy.Tense],
        )
        attack_strategies_temp.remove(AttackStrategy.MODERATE)
    if AttackStrategy.DIFFICULT in attack_strategies_temp:
        attack_strategies_temp.extend(
            [
                AttackStrategy.Compose([AttackStrategy.Tense, AttackStrategy.Base64]),
            ]
        )
        attack_strategies_temp.remove(AttackStrategy.DIFFICULT)

    ## Baseline is always included
    attack_strategies_temp.append(AttackStrategy.Baseline)

    for strategy in attack_strategies_temp:
        if (
            isinstance(strategy, List) and tuple(strategy) not in seen_strategies
        ):  # For composed strategies
            flattened_strategies.append([s for s in strategy])
            seen_strategies.add(tuple(strategy))
        elif (
            isinstance(strategy, AttackStrategy) and strategy not in seen_strategies
        ):  # For single strategies
            flattened_strategies.append(strategy)
            seen_strategies.add(strategy)

    return flattened_strategies


def get_attack_success(result: str) -> bool:
    """
    Based on EVALUATION_PASS_FAIL_MAPPING, returns True denoting attack success if result matches the value of the EVALUATION_PASS_FAIL_MAPPING key False.
    """
    from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING

    return result == EVALUATION_PASS_FAIL_MAPPING.get(False, "true")


def format_scorecard(redteam_result: RedTeamResult) -> str:
    """Format the RedTeamResult into a human-readable scorecard.

    The scorecard presents a summary of attack success rates across different risk categories
    and attack complexity levels in a tabular format.

    :param redteam_result: The RedTeamResult object to format
    :type redteam_result: Dict[str, Any]
    :return: A formatted scorecard as a string
    :rtype: str
    """
    scorecard = redteam_result["scorecard"]
    risk_summary = (
        scorecard["risk_category_summary"][0]
        if scorecard["risk_category_summary"]
        else {}
    )
    overall_asr = risk_summary.get("overall_asr", 0)

    output = [f"Overall ASR: {overall_asr}%"]
    overall_successes = risk_summary.get("overall_successful_attacks", 0)
    overall_total = risk_summary.get("overall_total", 0)
    output.append(
        f"Attack Success: {overall_successes}/{overall_total} attacks were successful"
    )

    separator = "-" * 132
    output.append(separator)
    output.append(
        f"{'Risk Category':<21}| {'Baseline ASR':<14} | {'Easy-Complexity Attacks ASR':<28} | {'Moderate-Complexity Attacks ASR':<30} | {'Difficult-Complexity Attacks ASR':<30}"
    )
    output.append(separator)

    for item in scorecard["joint_risk_attack_summary"]:
        risk_category = item["risk_category"].replace("_", "-").capitalize()

        baseline_val = item.get("baseline_asr")
        easy_val = item.get("easy_complexity_asr")
        moderate_val = item.get("moderate_complexity_asr")
        difficult_val = item.get("difficult_complexity_asr")

        baseline = "N/A" if is_none_or_nan(baseline_val) else f"{baseline_val}%"
        easy = "N/A" if is_none_or_nan(easy_val) else f"{easy_val}%"
        moderate = "N/A" if is_none_or_nan(moderate_val) else f"{moderate_val}%"
        difficult = "N/A" if is_none_or_nan(difficult_val) else f"{difficult_val}%"

        output.append(
            f"{risk_category:<21}| {baseline:<14} | {easy:<28} | {moderate:<31} | {difficult:<30}"
        )

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


def format_content_by_modality(content: str, modality: str) -> str:
    """Format content based on the specified modality, returning one random format.

    :param content: The content to format
    :type content: str
    :param modality: The modality type (html, markdown, footnote, code, text)
    :type modality: str
    :return: Formatted content
    :rtype: str
    """
    import html
    import random

    def format_as_html(text):
        html_text = html.escape(text)
        return [
            f"<p>{html_text}</p>",
            f'<div style="display:none">{html_text}</div>',
            f'<span style="display:none">{html_text}</span>',
            f"<div hidden>{html_text}</div>",
            f'<meta content="{html_text}">',
        ]

    def format_as_markdown(text):
        markdown_text = text.replace(
            "\n", "  \n"
        )  # Convert newlines to Markdown line breaks
        return [
            f"\n**{markdown_text}**\n",  # Bold
            f"\n*{markdown_text}*\n",  # Italic
            f"\n`{markdown_text}`\n",  # Inline code
            f"\n```{markdown_text}```\n",  # Code block
            f"\n[Link]({markdown_text})\n",  # Link
        ]

    def format_as_footnote(text):
        footnote_text = text.replace("\n", " ")
        return [
            f"[^{footnote_text}]",  # Footnote reference
            f"\n[1] {footnote_text}\n",  # Footnote reference with number
            f"<sup>{footnote_text}</sup>",  # Superscript
            f'<span class="footnote">{footnote_text}</span>',  # Custom footnote span
            f'<div class="footnote">{footnote_text}</div>',  # Custom footnote div
        ]

    def format_as_code(text):
        code_text = text.replace("\n", " ")
        return [
            f"`{code_text}`",  # Inline code
            f"```\n{code_text}\n```",  # Code block
            f'"""\n{code_text}\n"""',  # Code block
            f"# {code_text}",  # Inline comment
            f'def function():\n    print("{code_text}")',  # Function call
        ]

    def format_as_text(text):
        return [f"<document>{text}</document>"]  # Return text in document tags

    # Mapping of modality types to formatting functions
    modality_formatters = {
        "html": format_as_html,
        "markdown": format_as_markdown,
        "footnote": format_as_footnote,
        "code": format_as_code,
        "text": format_as_text,
    }

    # Get formatter based on modality type
    if modality and modality.lower() in modality_formatters:
        formatter = modality_formatters[modality.lower()]
        formats = formatter(content)
        # Return one random format from the available options
        return random.choice(formats)
    else:
        # Return plain text if modality not recognized
        return content


def write_pyrit_outputs_to_file(
    *,
    output_path: str,
    logger: logging.Logger,
    prompt_to_context: Dict[str, str],
) -> str:
    """Write PyRIT outputs to a file with a name based on orchestrator, strategy, and risk category.

    :param output_path: Path to write the output file
    :type output_path: str
    :param logger: Logger instance for logging
    :type logger: logging.Logger
    :param prompt_to_context: Mapping of prompts to their context
    :type prompt_to_context: Dict[str, str]
    :return: Path to the output file
    :rtype: str
    :raises IOError: If the output file cannot be read or written
    :raises PermissionError: If there are insufficient permissions to access the output file
    :raises Exception: For other unexpected errors during file operations or memory retrieval
    """

    logger.debug(f"Writing PyRIT outputs to file: {output_path}")
    memory = CentralMemory.get_memory_instance()

    memory_label = {"risk_strategy_path": output_path}

    prompts_request_pieces = memory.get_prompt_request_pieces(labels=memory_label)

    conversations = [
        [
            (
                item.to_chat_message(),
                prompt_to_context.get(item.original_value, "")
                or item.labels.get("context", ""),
                item.labels.get("tool_calls", []),
                item.labels.get("risk_sub_type"),
                item.labels.get("token_usage"),
            )
            for item in group
        ]
        for conv_id, group in itertools.groupby(
            prompts_request_pieces, key=lambda x: x.conversation_id
        )
    ]

    # Check if we should overwrite existing file with more conversations
    if os.path.exists(output_path):
        existing_line_count = 0
        try:
            with open(output_path, "r") as existing_file:
                existing_line_count = sum(1 for _ in existing_file)

            if len(conversations) > existing_line_count:
                logger.debug(
                    f"Found more prompts ({len(conversations)}) than existing file lines ({existing_line_count}). Replacing content."
                )
                # Convert to json lines
                json_lines = ""
                for conversation in conversations:
                    if conversation[0][0].role == "system":
                        # Skip system messages in the output
                        continue
                    conv_dict = {
                        "conversation": {
                            "messages": [
                                message_to_dict(
                                    message[0],
                                    message[1],
                                    message[2],
                                    message[4] if len(message) > 4 else None,
                                )
                                for message in conversation
                            ]
                        }
                    }
                    # Add risk_sub_type if present (check first message for the label)
                    if (
                        conversation
                        and len(conversation) > 0
                        and len(conversation[0]) > 3
                    ):
                        risk_sub_type = conversation[0][3]
                        if risk_sub_type:
                            conv_dict["risk_sub_type"] = risk_sub_type
                    json_lines += json.dumps(conv_dict) + "\n"
                with Path(output_path).open("w") as f:
                    f.writelines(json_lines)
                logger.debug(
                    f"Successfully wrote {len(conversations)-existing_line_count} new conversation(s) to {output_path}"
                )
            else:
                logger.debug(
                    f"Existing file has {existing_line_count} lines, new data has {len(conversations)} prompts. Keeping existing file."
                )
                return output_path
        except Exception as e:
            logger.warning(f"Failed to read existing file {output_path}: {str(e)}")
    else:
        logger.debug(f"Creating new file: {output_path}")
        # Convert to json lines
        json_lines = ""

        for conversation in conversations:
            if conversation[0][0].role == "system":
                # Skip system messages in the output
                continue
            conv_dict = {
                "conversation": {
                    "messages": [
                        message_to_dict(
                            message[0],
                            message[1],
                            message[2],
                            message[4] if len(message) > 4 else None,
                        )
                        for message in conversation
                    ]
                }
            }
            # Add risk_sub_type if present (check first message for the label)
            if conversation and len(conversation) > 0 and len(conversation[0]) > 3:
                risk_sub_type = conversation[0][3]
                if risk_sub_type:
                    conv_dict["risk_sub_type"] = risk_sub_type
            json_lines += json.dumps(conv_dict) + "\n"
        with Path(output_path).open("w") as f:
            f.writelines(json_lines)
        logger.debug(
            f"Successfully wrote {len(conversations)} conversations to {output_path}"
        )
    return str(output_path)
