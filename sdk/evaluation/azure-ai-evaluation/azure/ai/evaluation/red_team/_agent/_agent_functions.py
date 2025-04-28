# ------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------

"""
Red Team Tools as Functions for Azure AI Agent
This module provides functions that can be used as tools in Azure AI Agent for red teaming purposes.
"""

import json
import asyncio
from typing import Any, Callable, Set, Optional
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation.red_team._agent import RedTeamToolProvider


# Initialize the credential and tool provider (will be created when first needed)
credential = None
tool_provider = None
azure_ai_project = None
target_function = None

def _get_tool_provider() -> RedTeamToolProvider:
    """Get or create the RedTeamToolProvider instance."""
    global credential, tool_provider, azure_ai_project
    if tool_provider is None:
        credential = DefaultAzureCredential()
        tool_provider = RedTeamToolProvider(
            azure_ai_project=azure_ai_project,
            credential=credential,
            application_scenario="A customer service chatbot for a retail website"  # Optional context
        )
    return tool_provider

# Dictionary to store fetched prompts for reference
fetched_prompts = {}

def red_team_fetch_harmful_prompt(risk_category: str, strategy: str = "baseline", convert_with_strategy: Optional[str] = None) -> str:
    """
    Fetch a harmful prompt for a specific risk category to test content filters.
    
    This function retrieves a prompt that could potentially trigger content filters
    and can be used for red teaming AI systems.
    
    :param risk_category (str): The risk category to get a harmful prompt for (e.g., 'violence', 'hate_unfairness', 'sexual', 'self_harm').
    :param strategy (str, optional): The attack strategy to use (e.g., 'baseline', 'jailbreak'). Defaults to 'baseline'.
    :param convert_with_strategy (Optional[str], optional): Optional strategy to convert the prompt (e.g., 'morse_converter', 'binary_converter'). Defaults to None.
    :return: A JSON string containing the harmful prompt and related metadata.
    :rtype: str
    """
    provider = _get_tool_provider()
    
    # Run the async method in a new event loop
    result = asyncio.run(provider.fetch_harmful_prompt(
        risk_category_text=risk_category,
        strategy=strategy,
        convert_with_strategy=convert_with_strategy
    ))
    
    # Store the prompt for later conversion if successful
    if result["status"] == "success" and "prompt_id" in result:
        prompt_id = result["prompt_id"]
        if "prompt" in result:
            fetched_prompts[prompt_id] = result["prompt"]
    
    return json.dumps(result)

def red_team_convert_prompt(prompt_or_id: str, strategy: str) -> str:
    """
    Convert a prompt or a previously fetched prompt ID using a specified strategy.
    
    This function can be used to transform prompts in ways that might bypass content filters
    for testing AI system defenses.
    
    :param prompt_or_id (str): Either a prompt text or a prompt ID from a previous fetch_harmful_prompt call.
    :param strategy (str): The strategy to use for conversion (e.g., 'morse_converter', 'binary_converter', 'base64_converter').
    :return: A JSON string containing the original and converted prompt.
    :rtype: str
    """
    provider = _get_tool_provider()
    
    # Check if input is a prompt ID we have stored
    if prompt_or_id in fetched_prompts:
        # Update the provider's cache
        provider._fetched_prompts[prompt_or_id] = fetched_prompts[prompt_or_id]
    
    # Run the async method in a new event loop
    result = asyncio.run(provider.convert_prompt(
        prompt_or_id=prompt_or_id,
        strategy=strategy
    ))
    
    return json.dumps(result)

def red_team_unified(category: str, strategy: Optional[str] = None) -> str:
    """
    Get a harmful prompt for a specific risk category and optionally convert it.
    
    This function combines fetching and converting harmful prompts in one call,
    making it easier to test AI system defenses.
    
    :param category (str): The risk category to get a harmful prompt for (e.g., 'violence', 'hate_unfairness', 'sexual', 'self_harm').
    :param strategy (Optional[str], optional): Optional strategy to convert the prompt (e.g., 'morse_converter', 'binary_converter'). Defaults to None.
    :return: A JSON string containing the harmful prompt and related metadata.
    :rtype: str
    """
    provider = _get_tool_provider()
    
    # Run the async method in a new event loop
    result = asyncio.run(provider.red_team(
        category=category,
        strategy=strategy
    ))
    
    # Store the prompt for later conversion if it's a success and we didn't convert it
    if result["status"] == "success":
        if "prompt_id" in result and "prompt" in result:
            prompt_id = result["prompt_id"]
            fetched_prompts[prompt_id] = result["prompt"]
    
    return json.dumps(result)

def red_team_get_available_strategies() -> str:
    """
    Get a list of all available prompt conversion strategies.
    
    This function lists all the strategies that can be used to convert prompts
    for red teaming purposes.
    
    :return: A JSON string containing a list of available conversion strategies.
    :rtype: str
    """
    provider = _get_tool_provider()
    strategies = provider.get_available_strategies()
    
    return json.dumps({
        "status": "success",
        "available_strategies": strategies
    })

def red_team_explain_purpose() -> str:
    """
    Explain the purpose and responsible use of red teaming tools.
    
    This function provides information about the ethical use of red teaming tools
    and their purpose in improving AI system safety.
    
    :return: A JSON string containing information about responsible use of red teaming tools.
    :rtype: str
    """
    explanation = {
        "purpose": "Red teaming tools are designed to test AI systems for vulnerabilities and safety issues.",
        "responsible_use": [
            "Only use these tools on systems you have permission to test.",
            "Use the results to improve system safety and robustness.",
            "Do not use these tools to cause harm or bypass legitimate safety measures in production systems."
        ],
        "risk_categories": {
            "violence": "Content related to physical harm, weapons, or dangerous activities",
            "hate_unfairness": "Content related to discrimination, bias, or prejudice",
            "sexual": "Explicit sexual content",
            "self_harm": "Content related to suicide, self-injury, or harmful behaviors"
        },
        "conversion_strategies": "Various encoding and obfuscation methods to test if harmful content can bypass detection"
    }
    
    return json.dumps(explanation)

def red_team_send_to_target(prompt: str) -> str:
    """
    Send a prompt to the target function (e.g., call_ollama) and return the response.
    
    This function allows sending prompts to an external model or service for 
    evaluation.
    
    :param prompt (str): The prompt text to send to the target function.
    :return: A JSON string containing the response from the target function.
    :rtype: str
    """
    global target_function
    
    if target_function is None:
        return json.dumps({
            "status": "error",
            "message": "Target function not initialized. Make sure to pass a target_func to initialize_tool_provider."
        })
    
    try:
        # Call the target function with the prompt
        response = target_function(prompt)
        
        return json.dumps({
            "status": "success",
            "prompt": prompt,
            "response": response
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error calling target function: {str(e)}",
            "prompt": prompt
        })

# Example User Input for Each Function
# 1. Red Team Fetch Harmful Prompt
#    User Input: "Fetch a harmful prompt in the 'violence' category."
#    User Input: "Fetch a harmful prompt in the 'hate_unfairness' category with a 'jailbreak' strategy."
#    User Input: "Fetch a harmful prompt in the 'self_harm' category and convert it with 'base64_converter'."

# 2. Red Team Convert Prompt
#    User Input: "Convert this prompt 'prompt_12345678' using the 'binary_converter' strategy."
#    User Input: "Convert the text 'This is a test prompt' using the 'morse_converter' strategy."

# 3. Red Team Unified
#    User Input: "Get a harmful prompt in the 'sexual' category."
#    User Input: "Get a harmful prompt in the 'violence' category and convert it with 'leetspeak_converter'."

# 4. Red Team Get Available Strategies
#    User Input: "What conversion strategies are available for red teaming?"

# 5. Red Team Explain Purpose
#    User Input: "What is the purpose of red teaming tools and how should they be used responsibly?"

# Statically defined user functions for fast reference
user_functions: Set[Callable[..., Any]] = {
    red_team_fetch_harmful_prompt,
    red_team_convert_prompt,
    red_team_unified,
    red_team_get_available_strategies,
    red_team_explain_purpose,
    red_team_send_to_target
}

def initialize_tool_provider(
        projects_connection_string: str,
        target_func: Optional[Callable[[str], str]] = None,
    ) -> Set[Callable[..., Any]]:
    """
    Initialize the RedTeamToolProvider with the Azure AI project and credential.
    This function is called when the module is imported.
    
    :param projects_connection_string: The Azure AI project connection string.
    :param target_func: A function that takes a string prompt and returns a string response.
    :return: A set of callable functions that can be used as tools.
    """
    # projects_connection_string is in the format: connection_string;subscription_id;resource_group;project_name
    # parse it to a dictionary called azure_ai_project
    global azure_ai_project, credential, tool_provider, target_function
    
    # Store the target function for later use
    if target_func is not None:
        globals()['target_function'] = target_func
    azure_ai_project = {
        "subscription_id": projects_connection_string.split(";")[1],
        "resource_group_name": projects_connection_string.split(";")[2],
        "project_name": projects_connection_string.split(";")[3]
    }
    if not credential:
        credential = DefaultAzureCredential()
    tool_provider = RedTeamToolProvider(
        azure_ai_project=azure_ai_project,
        credential=credential,
    )
    return user_functions
