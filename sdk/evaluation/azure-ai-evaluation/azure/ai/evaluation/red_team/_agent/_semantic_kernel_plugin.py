# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This module provides Semantic Kernel Plugin for Red Team Tools.
These plugins can be used as functions in a Semantic Kernel agent for red teaming purposes.
"""

import asyncio
import json
from typing import Annotated, Dict, Any, Optional, Callable

from semantic_kernel.functions import kernel_function

from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider
from azure.identity import DefaultAzureCredential

class RedTeamPlugin:
    """
    A Semantic Kernel plugin that provides red teaming capabilities.
    This plugin wraps around the RedTeamToolProvider to provide red teaming functions
    as Semantic Kernel functions.
    
    Example:
        ```python
        # Method 1: Create a plugin with individual environment variables
        plugin = RedTeamPlugin(
            azure_ai_project_endpoint=os.environ.get("AZURE_AI_PROJECT_ENDPOINT"),
            target_func=lambda x: "Target model response"
        )
        
        # Create a Semantic Kernel agent with the plugin
        agent = ChatCompletionAgent(
            service=service,
            name="RedTeamAgent",
            instructions="You are a red team agent...",
            plugins=[plugin],
        )
        ```
    """
    
    def __init__(self, azure_ai_project_endpoint: str, target_func: Optional[Callable[[str], str]] = None, *,
                 application_scenario: str = "", **kwargs):
        """
        Initialize the RedTeamPlugin with the necessary configuration components.

        :param azure_ai_project_endpoint: The Azure AI project endpoint (e.g., 'https://your-resource-name.services.ai.azure.com/api/projects/your-project-name')
        :param target_func: Optional function to call with prompts
        :param application_scenario: The application scenario for the tool provider
        """
        
        # Initialize credential and tool provider
        self.credential = DefaultAzureCredential()
        self.tool_provider = RedTeamToolProvider(
            azure_ai_project_endpoint=azure_ai_project_endpoint,
            credential=self.credential,
            application_scenario=application_scenario
        )
        
        # Store the target function
        self.target_function = target_func
        
        # Dictionary to store fetched prompts for reference
        self.fetched_prompts = {}
    
    @kernel_function(description="Fetch a harmful prompt for a specific risk category to test content filters")
    async def fetch_harmful_prompt(
        self, 
        risk_category: Annotated[str, "The risk category (e.g., 'violence', 'hate_unfairness', 'sexual', 'self_harm')"],
        strategy: Annotated[str, "Attack strategy to use (e.g., 'baseline', 'jailbreak')"] = "baseline",
        convert_with_strategy: Annotated[str, "Optional strategy to convert the prompt"] = ""
    ) -> Annotated[str, "A JSON string with the harmful prompt and metadata"]:
        """
        Fetch a harmful prompt for a specific risk category to test content filters.
        
        :param risk_category: The risk category (e.g., 'violence', 'hate_unfairness', 'sexual', 'self_harm')
        :param strategy: Attack strategy to use (e.g., 'baseline', 'jailbreak')
        :param convert_with_strategy: Optional strategy to convert the prompt
        :return: A JSON string with the harmful prompt and metadata
        """
        # Convert empty string to None
        if not convert_with_strategy:
            convert_with_strategy = None
            
        # Directly await the async method instead of using asyncio.run()
        result = await self.tool_provider.fetch_harmful_prompt(
            risk_category_text=risk_category,
            strategy=strategy,
            convert_with_strategy=convert_with_strategy
        )
        
        # Store the prompt for later conversion if successful
        if result["status"] == "success" and "prompt_id" in result:
            prompt_id = result["prompt_id"]
            if "prompt" in result:
                self.fetched_prompts[prompt_id] = result["prompt"]
                # Also update the tool provider's cache
                self.tool_provider._fetched_prompts[prompt_id] = result["prompt"]
        
        return json.dumps(result)
    
    @kernel_function(description="Convert a prompt using a specified strategy")
    async def convert_prompt(
        self,
        prompt_or_id: Annotated[str, "Either a prompt text or a prompt ID from a previous fetch"],
        strategy: Annotated[str, "The strategy to use for conversion"]
    ) -> Annotated[str, "A JSON string with the original and converted prompt"]:
        """
        Convert a prompt or a previously fetched prompt ID using a specified strategy.
        
        :param prompt_or_id: Either a prompt text or a prompt ID from a previous fetch
        :param strategy: The strategy to use for conversion
        :return: A JSON string with the original and converted prompt
        """
        # Check if input is a prompt ID we have stored
        if prompt_or_id in self.fetched_prompts:
            # Update the provider's cache
            self.tool_provider._fetched_prompts[prompt_or_id] = self.fetched_prompts[prompt_or_id]
        
        # Directly await the async method instead of using asyncio.run()
        result = await self.tool_provider.convert_prompt(
            prompt_or_id=prompt_or_id,
            strategy=strategy
        )
        
        return json.dumps(result)
    
    @kernel_function(description="Get a harmful prompt for a specific risk category and optionally convert it")
    async def red_team_unified(
        self,
        category: Annotated[str, "The risk category (e.g., 'violence', 'hate_unfairness', 'sexual', 'self_harm')"],
        strategy: Annotated[str, "Optional strategy to convert the prompt"] = ""
    ) -> Annotated[str, "A JSON string with the harmful prompt and metadata"]:
        """
        Get a harmful prompt for a specific risk category and optionally convert it.
        
        :param category: The risk category (e.g., 'violence', 'hate_unfairness', 'sexual', 'self_harm')
        :param strategy: Optional strategy to convert the prompt
        :return: A JSON string with the harmful prompt and metadata
        """
        # Convert empty string to None
        strategy_param = strategy if strategy else None
            
        # Directly await the async method instead of using asyncio.run()
        result = await self.tool_provider.red_team(
            category=category,
            strategy=strategy_param
        )
        
        # Store the prompt for later conversion if it's a success and we didn't convert it
        if result["status"] == "success":
            if "prompt_id" in result and "prompt" in result:
                prompt_id = result["prompt_id"]
                self.fetched_prompts[prompt_id] = result["prompt"]
                # Also update the tool provider's cache
                self.tool_provider._fetched_prompts[prompt_id] = result["prompt"]
        
        return json.dumps(result)
    
    @kernel_function(description="Get a list of all available prompt conversion strategies")
    async def get_available_strategies(self) -> Annotated[str, "A JSON string with available conversion strategies"]:
        """
        Get a list of all available prompt conversion strategies.
        
        :return: A JSON string with available conversion strategies
        """
        # This method calls a synchronous function, but we make the method itself async
        # for consistency with the rest of the interface
        strategies = self.tool_provider.get_available_strategies()
        
        return json.dumps({
            "status": "success",
            "available_strategies": strategies
        })
    
    @kernel_function(description="Explain the purpose and responsible use of red teaming tools")
    async def explain_purpose(self) -> Annotated[str, "A JSON string with information about red teaming tools"]:
        """
        Explain the purpose and responsible use of red teaming tools.
        
        :return: A JSON string with information about red teaming tools
        """
        # This method doesn't use any async functions, but we make it async
        # for consistency with the rest of the interface
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
    
    @kernel_function(description="Send a prompt to the target function and return the response")
    async def send_to_target(
        self,
        prompt: Annotated[str, "The prompt text to send to the target function"]
    ) -> Annotated[str, "A JSON string with the response from the target"]:
        """
        Send a prompt to the target function and return the response.
        
        :param prompt: The prompt text to send to the target function
        :return: A JSON string with the response from the target
        """
        # This method doesn't use any async functions, but we make it async
        # for consistency with the rest of the interface
        if self.target_function is None:
            return json.dumps({
                "status": "error",
                "message": "Target function not initialized. Make sure to pass a target_func when initializing the plugin."
            })
        
        try:
            # Call the target function with the prompt
            response = self.target_function(prompt)
            
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
