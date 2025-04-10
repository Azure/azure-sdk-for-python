# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Sample showing how to use the RedTeamToolProvider with Azure AI agents.

This sample demonstrates how to:
1. Initialize the RedTeamToolProvider
2. Register it with an Azure AI agent
3. Test it with sample requests including prompt conversion

Prerequisites:
- Azure AI agent set up
- Azure AI evaluation SDK installed
- Appropriate credentials and permissions

Installation:
pip install azure-ai-evaluation[red-team]
"""

import os
import asyncio
from typing import Dict, Any
import json

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation.red_team import RiskCategory
from azure.ai.evaluation.agent import RedTeamToolProvider, get_red_team_tools

# Optional: For local development, you can use environment variables for configuration
# os.environ["AZURE_SUBSCRIPTION_ID"] = "your-subscription-id"
# os.environ["AZURE_RESOURCE_GROUP"] = "your-resource-group"
# os.environ["AZURE_WORKSPACE_NAME"] = "your-workspace-name"

# Sample Azure AI agent implementation (replace with actual agent client)
class SimpleAgentClient:
    """Simple mock agent client for demonstration purposes."""
    
    def __init__(self, name):
        self.name = name
        self.tools = {}
        self.tool_implementations = {}
        
    def register_tool(self, name, description, parameters, implementation):
        """Register a tool with the agent."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters
        }
        self.tool_implementations[name] = implementation
        print(f"Registered tool: {name}")
        
    async def call_tool(self, name, **kwargs):
        """Call a registered tool with parameters."""
        if name not in self.tool_implementations:
            raise ValueError(f"Tool '{name}' not registered")
        
        implementation = self.tool_implementations[name]
        result = await implementation(**kwargs)
        return result
    
    def get_registered_tools(self):
        """Get the list of registered tools."""
        return self.tools


async def main():
    """Run the sample."""
    # Step 1: Set up Azure AI project configuration
    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID", "your-subscription-id"),
        "resource_group": os.environ.get("AZURE_RESOURCE_GROUP", "your-resource-group"),
        "workspace_name": os.environ.get("AZURE_WORKSPACE_NAME", "your-workspace-name")
    }
    
    # Step 2: Create credentials
    credential = DefaultAzureCredential()
    
    # Step 3: Create the RedTeamToolProvider
    print("Creating RedTeamToolProvider...")
    tool_provider = RedTeamToolProvider(
        azure_ai_project=azure_ai_project,
        credential=credential,
        application_scenario="A customer service chatbot for a retail website"  # Optional context
    )
    
    # Step 4: Get tool definitions for registration
    tools = get_red_team_tools()
    
    # Step 5: Create a simple agent client (replace with your actual agent client)
    agent = SimpleAgentClient(name="sample-agent")
    
    # Step 6: Register tools with the agent
    print("Registering tools with agent...")
    for tool in tools:
        agent.register_tool(
            name=tool["task"],
            description=tool["description"],
            parameters=tool["parameters"],
            implementation=getattr(tool_provider, tool["task"])
        )
    
    # Step 7: Use the registered tools
    print("\nRegistered tools:")
    for name, tool in agent.get_registered_tools().items():
        print(f"- {name}: {tool['description']}")
    
    # Define the supported risk categories based on the RiskCategory enum
    supported_risk_categories = [
        "violence",
        "hate_unfairness",
        "sexual",
        "self_harm"
    ]
    
    print("\n==============================")
    print("DEMONSTRATION 1: UNIFIED APPROACH")
    print("==============================")
    print("Using the 'red_team' tool to get a harmful prompt in one step")
    
    # Example 1: Using the unified red_team tool without a conversion strategy
    print("\n=== Example 1: Get a harmful prompt without conversion ===")
    risk_category = "violence"
    try:
        result = await agent.call_tool(
            "red_team", 
            category=risk_category
        )
        
        if result["status"] == "success":
            print(f"✅ Successfully fetched harmful prompt for {risk_category}")
            print(f"Risk Category: {result['risk_category']}")
            print(f"Prompt: {result['prompt'][:100]}..." if len(result['prompt']) > 100 else result['prompt'])
            print(f"Available conversion strategies: {', '.join(result['available_strategies'][:5])}...")
            print(f"Prompt ID for later reference: {result['prompt_id']}")
            
            # Store the prompt ID for later use
            prompt_id = result["prompt_id"]
        else:
            print(f"❌ Error: {result['message']}")
    except Exception as e:
        print(f"❌ Error calling tool: {str(e)}")

    # Example 2: Using the unified red_team tool with immediate conversion
    print("\n=== Example 2: Get a harmful prompt with immediate conversion ===")
    risk_category = "hate_unfairness"
    try:
        result = await agent.call_tool(
            "red_team",
            category=risk_category,
            strategy="morse"
        )
        
        if result["status"] == "success":
            print(f"✅ Successfully fetched and converted harmful prompt for {risk_category}")
            print(f"Risk Category: {result['risk_category']}")
            print(f"Strategy: {result['strategy']}")
            print(f"Original: {result['original_prompt'][:50]}...")
            print(f"Converted: {result['converted_prompt'][:100]}...")
        else:
            print(f"❌ Error: {result['message']}")
    except Exception as e:
        print(f"❌ Error calling tool: {str(e)}")

    print("\n==============================")
    print("DEMONSTRATION 2: STEP-BY-STEP APPROACH")
    print("==============================")
    print("Using the 'fetch_harmful_prompt' and 'convert_prompt' tools separately")
    
    # Example 3: First fetch a harmful prompt
    print("\n=== Example 3: Fetch a harmful prompt ===")
    risk_category = "sexual"
    try:
        result = await agent.call_tool(
            "fetch_harmful_prompt", 
            risk_category_text=risk_category
        )
        
        if result["status"] == "success":
            print(f"✅ Successfully fetched harmful prompt for {risk_category}")
            print(f"Risk Category: {result['risk_category']}")
            print(f"Prompt: {result['prompt'][:100]}..." if len(result['prompt']) > 100 else result['prompt'])
            print(f"Prompt ID for later reference: {result['prompt_id']}")
            
            # Store the prompt ID for later use
            prompt_id_sexual = result["prompt_id"]
        else:
            print(f"❌ Error: {result['message']}")
    except Exception as e:
        print(f"❌ Error calling tool: {str(e)}")

    # Example 4: Then convert the previously fetched prompt
    print("\n=== Example 4: Convert the previously fetched prompt ===")
    if 'prompt_id_sexual' in locals():
        try:
            result = await agent.call_tool(
                "convert_prompt",
                prompt_or_id=prompt_id_sexual,
                strategy="binary"
            )
            
            if result["status"] == "success":
                print(f"✅ Successfully converted prompt using binary strategy")
                print(f"Original: {result['original_prompt'][:50]}...")
                print(f"Converted: {result['converted_prompt'][:100]}...")
            else:
                print(f"❌ Error: {result['message']}")
        except Exception as e:
            print(f"❌ Error calling tool: {str(e)}")
    
    # Example 5: Fetch and convert in a single call using fetch_harmful_prompt
    print("\n=== Example 5: Fetch and convert in one call with fetch_harmful_prompt ===")
    risk_category = "self_harm"
    try:
        result = await agent.call_tool(
            "fetch_harmful_prompt", 
            risk_category_text=risk_category,
            convert_with_strategy="base64"
        )
        
        if result["status"] == "success":
            print(f"✅ Successfully fetched and converted harmful prompt for {risk_category}")
            print(f"Risk Category: {result['risk_category']}")
            print(f"Strategy: {result['conversion_strategy']}")
            print(f"Original: {result['original_prompt'][:50]}...")
            print(f"Converted: {result['converted_prompt'][:100]}...")
        else:
            print(f"❌ Error: {result['message']}")
    except Exception as e:
        print(f"❌ Error calling tool: {str(e)}")
    
    # Example 6: Convert a custom prompt
    print("\n=== Example 6: Convert a custom prompt ===")
    custom_prompt = "This is a custom prompt that wasn't fetched from the tool"
    try:
        result = await agent.call_tool(
            "convert_prompt",
            prompt_or_id=custom_prompt,
            strategy="leetspeak"
        )
        
        if result["status"] == "success":
            print(f"✅ Successfully converted custom prompt using leetspeak strategy")
            print(f"Original: {result['original_prompt']}")
            print(f"Converted: {result['converted_prompt']}")
        else:
            print(f"❌ Error: {result['message']}")
    except Exception as e:
        print(f"❌ Error calling tool: {str(e)}")

    print("\n==============================")
    print("AGENT CONVERSATION EXAMPLES")
    print("==============================")
    print("In a real agent conversation, users would interact like:")
    print("\n=== Example A: Using the unified approach ===")
    print("User: @red_team violence")
    print("Agent: Here's a harmful prompt for violence: \"...\"")
    print("       You can convert this with strategies like morse, binary, base64, etc.")
    print("User: @red_team violence morse")
    print("Agent: Here's the morse code version: \".--- ..- ... - / ....\"")
    
    print("\n=== Example B: Using the step-by-step approach ===")
    print("User: @fetch_harmful_prompt hate")
    print("Agent: Here's a harmful prompt for hate: \"...\"")
    print("       The prompt ID is prompt_1")
    print("User: @convert_prompt prompt_1 binary")
    print("Agent: Here's the binary version: \"01001000 01100101 01110010 01100101 ...\"")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
    

# Additional usage examples:
"""
# Example: Using with an actual Azure AI agent
# ---------------------------------------------
from azure.ai.agent import Agent  # Import the actual Azure AI Agent class

# Create your agent
agent = Agent(
    name="my-agent",
    endpoint="<endpoint>", 
    api_key="<api-key>"
)

# Register the tools with your agent
for tool in tools:
    agent.register_tool(
        name=tool["task"],
        description=tool["description"],
        parameters=tool["parameters"],
        implementation=getattr(tool_provider, tool["task"])
    )

# Now users can invoke the tools with commands like:
# Unified approach:
# @red_team violence
# @red_team hate morse

# Step-by-step approach:
# @fetch_harmful_prompt violence
# @convert_prompt prompt_1 morse


# Example: Using with direct API calls
# --------------------------------------
# Unified approach:
result = await tool_provider.red_team(
    category="violence",
    strategy="morse"  # Optional
)
print(json.dumps(result, indent=2))

# Step-by-step approach:
result1 = await tool_provider.fetch_harmful_prompt(
    risk_category_text="violence"
)
print(json.dumps(result1, indent=2))

result2 = await tool_provider.convert_prompt(
    prompt_or_id=result1["prompt"],
    strategy="morse"
)
print(json.dumps(result2, indent=2))
"""