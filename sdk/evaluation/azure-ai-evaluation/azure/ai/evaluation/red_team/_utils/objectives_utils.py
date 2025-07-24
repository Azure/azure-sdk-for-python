"""
Utility functions for handling attack objectives in Red Team Agent.

This module provides functions for sampling, caching, and processing attack objectives
from various sources including custom prompts and RAI services.
"""

import random
import uuid
from typing import List, Dict, Optional, Tuple
from .logging_utils import log_error


def sample_objectives(
    custom_objectives: List[dict], 
    num_objectives: int, 
    risk_cat_value: str,
    logger
) -> List[dict]:
    """Sample objectives if we have more than needed.
    
    :param custom_objectives: List of available objectives
    :type custom_objectives: List[dict]
    :param num_objectives: Number of objectives needed
    :type num_objectives: int
    :param risk_cat_value: Risk category value for logging
    :type risk_cat_value: str
    :param logger: Logger instance
    :type logger: logging.Logger
    :return: Selected objectives
    :rtype: List[dict]
    """
    if len(custom_objectives) > num_objectives:
        selected_cat_objectives = random.sample(custom_objectives, num_objectives)
        logger.info(
            f"Sampled {num_objectives} objectives from {len(custom_objectives)} available for {risk_cat_value}"
        )
        # Log ids of selected objectives for traceability
        selected_ids = [obj.get("id", "unknown-id") for obj in selected_cat_objectives]
        logger.debug(f"Selected objective IDs for {risk_cat_value}: {selected_ids}")
    else:
        selected_cat_objectives = custom_objectives
        logger.info(f"Using all {len(custom_objectives)} available objectives for {risk_cat_value}")
    
    return selected_cat_objectives


async def apply_jailbreak_prefixes(
    selected_cat_objectives: List[dict], 
    generated_rai_client,
    retry_config: dict,
    logger
) -> None:
    """Apply jailbreak prefixes to objectives for jailbreak strategy.
    
    :param selected_cat_objectives: List of selected objectives to modify
    :type selected_cat_objectives: List[dict]
    :param generated_rai_client: RAI client instance
    :type generated_rai_client: GeneratedRAIClient
    :param retry_config: Retry configuration
    :type retry_config: dict
    :param logger: Logger instance
    :type logger: logging.Logger
    """
    from tenacity import retry
    import httpx
    
    logger.debug("Applying jailbreak prefixes to custom objectives")
    try:
        @retry(**retry_config["network_retry"])
        async def get_jailbreak_prefixes_with_retry():
            try:
                return await generated_rai_client.get_jailbreak_prefixes()
            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.ConnectError,
                httpx.HTTPError,
                ConnectionError,
            ) as e:
                logger.warning(
                    f"Network error when fetching jailbreak prefixes: {type(e).__name__}: {str(e)}"
                )
                raise

        jailbreak_prefixes = await get_jailbreak_prefixes_with_retry()
        for objective in selected_cat_objectives:
            if "messages" in objective and len(objective["messages"]) > 0:
                message = objective["messages"][0]
                if isinstance(message, dict) and "content" in message:
                    message["content"] = f"{random.choice(jailbreak_prefixes)} {message['content']}"
    except Exception as e:
        log_error(logger, "Error applying jailbreak prefixes to custom objectives", e)
        # Continue with unmodified prompts instead of failing completely


def extract_prompts_from_objectives(selected_cat_objectives: List[dict]) -> List[str]:
    """Extract prompt content from objective objects.
    
    :param selected_cat_objectives: List of objective dictionaries
    :type selected_cat_objectives: List[dict]
    :return: List of prompt content strings
    :rtype: List[str]
    """
    selected_prompts = []
    for obj in selected_cat_objectives:
        if "messages" in obj and len(obj["messages"]) > 0:
            message = obj["messages"][0]
            if isinstance(message, dict) and "content" in message:
                selected_prompts.append(message["content"])
    return selected_prompts


def create_objectives_by_category(selected_cat_objectives: List[dict], risk_cat_value: str) -> dict:
    """Create objectives organized by category for caching.
    
    :param selected_cat_objectives: List of selected objectives
    :type selected_cat_objectives: List[dict]
    :param risk_cat_value: Risk category value
    :type risk_cat_value: str
    :return: Objectives organized by category
    :rtype: dict
    """
    objectives_by_category = {risk_cat_value: []}

    for obj in selected_cat_objectives:
        obj_id = obj.get("id", f"obj-{uuid.uuid4()}")
        content = ""
        if "messages" in obj and len(obj["messages"]) > 0:
            content = obj["messages"][0].get("content", "")

        if content:
            obj_data = {"id": obj_id, "content": content}
            objectives_by_category[risk_cat_value].append(obj_data)

    return objectives_by_category


def cache_objectives(
    attack_objectives: dict,
    current_key: tuple, 
    objectives_by_category: dict, 
    strategy: Optional[str], 
    risk_cat_value: str, 
    selected_prompts: List[str], 
    selected_cat_objectives: List[dict]
) -> None:
    """Cache the objectives for future use.
    
    :param attack_objectives: Dictionary to store cached objectives
    :type attack_objectives: dict
    :param current_key: Cache key
    :type current_key: tuple
    :param objectives_by_category: Objectives organized by category
    :type objectives_by_category: dict
    :param strategy: Strategy name
    :type strategy: Optional[str]
    :param risk_cat_value: Risk category value
    :type risk_cat_value: str
    :param selected_prompts: Selected prompt content
    :type selected_prompts: List[str]
    :param selected_cat_objectives: Full objective objects
    :type selected_cat_objectives: List[dict]
    """
    attack_objectives[current_key] = {
        "objectives_by_category": objectives_by_category,
        "strategy": strategy,
        "risk_category": risk_cat_value,
        "selected_prompts": selected_prompts,
        "selected_objectives": selected_cat_objectives,
    }