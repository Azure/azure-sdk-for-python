"""
Utility functions for orchestrator management in Red Team Agent.

This module provides functions for creating, configuring, and managing orchestrators
for different attack strategies.
"""

import asyncio
import os
import uuid
from datetime import datetime
from typing import List, Union
from pyrit.prompt_converter import PromptConverter
from pyrit.prompt_target import PromptChatTarget
from pyrit.orchestrator import PromptSendingOrchestrator
from tenacity import retry
from .logging_utils import log_error


def create_orchestrator(
    chat_target: PromptChatTarget, converter: Union[PromptConverter, List[PromptConverter]]
) -> PromptSendingOrchestrator:
    """Create and configure a PromptSendingOrchestrator.
    
    :param chat_target: The target to send prompts to
    :type chat_target: PromptChatTarget
    :param converter: Prompt converter or list of converters to transform prompts
    :type converter: Union[PromptConverter, List[PromptConverter]]
    :return: Configured orchestrator
    :rtype: PromptSendingOrchestrator
    """
    converter_list = normalize_converters(converter)
    return PromptSendingOrchestrator(objective_target=chat_target, prompt_converters=converter_list)


def normalize_converters(
    converter: Union[PromptConverter, List[PromptConverter]]
) -> List[PromptConverter]:
    """Normalize converter input to a list of converters.
    
    :param converter: Prompt converter or list of converters
    :type converter: Union[PromptConverter, List[PromptConverter]]
    :return: List of prompt converters
    :rtype: List[PromptConverter]
    """
    if not converter:
        return []
    if isinstance(converter, PromptConverter):
        return [converter]
    return converter if isinstance(converter, list) else []


def log_converter_info(logger, converter: Union[PromptConverter, List[PromptConverter]]) -> None:
    """Log information about the converters being used.
    
    :param logger: Logger instance
    :type logger: logging.Logger
    :param converter: Prompt converter or list of converters
    :type converter: Union[PromptConverter, List[PromptConverter]]
    """
    converter_list = normalize_converters(converter)
    
    if converter_list:
        converter_names = [c.__class__.__name__ for c in converter_list if c is not None]
        logger.debug(f"Using converters: {', '.join(converter_names)}")
    else:
        logger.debug("No converters specified")


def initialize_output_path(
    strategy_name: str, 
    risk_category_name: str, 
    scan_output_dir: str = None,
    red_team_info: dict = None,
    data_ext: str = ".jsonl"
) -> str:
    """Initialize output path for memory labelling.
    
    :param strategy_name: Name of the attack strategy
    :type strategy_name: str
    :param risk_category_name: Name of the risk category
    :type risk_category_name: str
    :param scan_output_dir: Base output directory
    :type scan_output_dir: str
    :param red_team_info: Red team info dictionary to update
    :type red_team_info: dict
    :param data_ext: File extension for data files
    :type data_ext: str
    :return: Output path for the data file
    :rtype: str
    """
    base_path = str(uuid.uuid4())
    
    if scan_output_dir:
        output_path = os.path.join(scan_output_dir, f"{base_path}{data_ext}")
    else:
        output_path = f"{base_path}{data_ext}"

    if red_team_info:
        red_team_info[strategy_name][risk_category_name]["data_file"] = output_path
    
    return output_path


async def send_prompts_with_retry(
    orchestrator: PromptSendingOrchestrator,
    all_prompts: List[str],
    output_path: str,
    strategy_name: str,
    risk_category_name: str,
    timeout: int,
    retry_config: dict,
    logger,
    task_statuses: dict = None,
    task_status: dict = None,
) -> None:
    """Send all prompts at once with retry logic and error handling.
    
    :param orchestrator: The orchestrator to use for sending prompts
    :type orchestrator: PromptSendingOrchestrator
    :param all_prompts: List of prompts to send
    :type all_prompts: List[str]
    :param output_path: Path for memory labelling
    :type output_path: str
    :param strategy_name: Name of the attack strategy
    :type strategy_name: str
    :param risk_category_name: Name of the risk category
    :type risk_category_name: str
    :param timeout: Timeout in seconds for the operation
    :type timeout: int
    :param retry_config: Retry configuration dictionary
    :type retry_config: dict
    :param logger: Logger instance
    :type logger: logging.Logger
    :param task_statuses: Task status tracking dictionary
    :type task_statuses: dict
    :param task_status: Task status constants
    :type task_status: dict
    """
    logger.debug(
        f"Processing {len(all_prompts)} prompts for {strategy_name}/{risk_category_name}"
    )
    start_time = datetime.now()
    task_key = f"{strategy_name}/{risk_category_name}"
    
    try:
        @retry(**retry_config["network_retry"])
        async def send_prompts_with_retry_inner():
            try:
                return await asyncio.wait_for(
                    orchestrator.send_prompts_async(
                        prompt_list=all_prompts,
                        memory_labels={"risk_strategy_path": output_path},
                    ),
                    timeout=timeout,
                )
            except asyncio.TimeoutError as e:
                logger.warning(
                    f"Timeout after {timeout}s while processing {len(all_prompts)} "
                    f"prompts for {strategy_name}/{risk_category_name}: {str(e)}"
                )
                raise
            except Exception as e:
                logger.error(
                    f"Error processing prompts for {strategy_name}/{risk_category_name}: {str(e)}"
                )
                raise

        await send_prompts_with_retry_inner()
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Successfully processed {len(all_prompts)} prompts for "
            f"{strategy_name}/{risk_category_name} in {elapsed_time:.2f}s"
        )
        
        if task_statuses and task_status:
            task_statuses[task_key] = task_status["COMPLETED"]

    except Exception as e:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        log_error(
            logger,
            f"Failed to process prompts after {elapsed_time:.2f}s",
            e,
            f"{strategy_name}/{risk_category_name}"
        )
        
        if task_statuses and task_status:
            task_statuses[task_key] = task_status["FAILED"]
        raise