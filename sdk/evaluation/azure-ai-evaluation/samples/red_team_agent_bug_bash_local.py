# type: ignore 
# # ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Red Team Agent Bug Bash Script

This script contains various examples of using the Red Team Agent for
vulnerability scanning. It includes similar content to the notebook version
but formatted as a standalone Python script.

Setup instructions:
1. Install uv: pip install uv
2. Create a virtual environment: uv venv --python 3.11
3. Activate the virtual environment:
   - Windows: .venv\Scripts\activate
   - macOS/Linux: source .venv/bin/activate
4. Install the SDK with redteam extra: uv pip install --upgrade "git+https://github.com/slister1001/azure-sdk-for-python.git@red-team-agent-init#subdirectory=sdk/evaluation/azure-ai-evaluation&egg=azure-ai-evaluation[redteam]"
"""

import os
import asyncio
import json
import random
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Import Azure AI Evaluation packages
from azure.ai.evaluation.red_team_agent import RedTeamAgent, AttackStrategy, RiskCategory
from azure.identity import DefaultAzureCredential

# Used for complex examples
try:
    import openai
    import pandas as pd
except ImportError:
    print("Some examples require additional packages: openai, pandas")
    print("Install them with: pip install openai pandas")


async def main():
    """Main function to run the Red Team Agent examples"""
    print("Azure AI Evaluation Red Team Agent Bug Bash Examples")
    print("==================================================")
    
    # Connect to an Azure AI Project
    # Note: Navigate to Azure AI Foundry Hub and select a project
    # URL: https://int.ai.azure.com/managementCenter/hub/overview?wsid=/subscriptions/4bf6b28a-452b-4af4-8080-8a196ee0ca4b/resourceGroups/naposani/providers/Microsoft.MachineLearningServices/workspaces/sydneylister-1523&flight=AIRedTeaming=true,EvalConvergence&tid=72f988bf-86f1-41af-91ab-2d7cd011db47
    azure_ai_project = {
        "subscription_id": "4bf6b28a-452b-4af4-8080-8a196ee0ca4b",
        "resource_group_name": "naposani",
        "project_name": "sydneylister-1523",  # INSERT THE PROJECT NAME HERE
    }
    
    # Initialize credentials
    credential = DefaultAzureCredential()
    
    # Create the RedTeamAgent instance
    agent = RedTeamAgent(azure_ai_project=azure_ai_project, credential=credential)
    
    # Select which examples to run
    examples_to_run = [
        "example1_basic_callback",
        # "example2_advanced_callback",
        # "example3_direct_model_testing",
        # "example4_strategy_complexity_levels",
        # "example5_specific_attack_strategies",
        # "example6_data_only_mode",
        # "example7_working_with_results",
        # "example8_custom_application",
        # "example9_output_path",
        # "example10_empty_attack_strategies",
        # "example11_empty_risk_categories",
        # "example12_duplicate_cases",
    ]

    result = None
    # Run the selected examples
    for example in examples_to_run:
        print(f"\n\nRunning example: {example}")
        print("-" * 50)
        
        if example == "example1_basic_callback":
            result = await example1_basic_callback(agent)
        elif example == "example2_advanced_callback":
            result = await example2_advanced_callback(agent)
        elif example == "example3_direct_model_testing":
            result = await example3_direct_model_testing(agent)
        elif example == "example4_strategy_complexity_levels":
            result = await example4_strategy_complexity_levels(agent)
        elif example == "example5_specific_attack_strategies":
            result = await example5_specific_attack_strategies(agent)
        elif example == "example6_data_only_mode":
            result = await example6_data_only_mode(agent)
        elif example == "example7_working_with_results":
            # This example uses results from a previous example
            if not result: 
                print("Example 7 requires results from a previous example")
            else: 
                await example7_working_with_results(result)
        elif example == "example8_custom_application":
            result = await example8_custom_application(agent)
        elif example == "example9_output_path":
            result = await example9_output_path(agent)
        elif example == "example10_empty_attack_strategies":
            result = await example10_empty_attack_strategies(agent) 
        elif example == "example11_empty_risk_categories":
            result = await example11_empty_risk_categories(agent)
        elif example == "example12_duplicate_cases":
            result = await example12_duplicate_cases(agent)


async def example1_basic_callback(agent: RedTeamAgent):
    """Example 1: Basic Red Team Scan with Callback Function

    This example shows how to use the RedTeamAgent with a simple callback function to test your application.
    """
    print("Running Example 1: Basic Red Team Scan with Callback")

    # Create a simple application callback function
    def simple_app_callback(query: str) -> str:
        """A simple application callback function that responds to user queries"""
        # Your implementation to call your application (e.g., RAG system, chatbot, etc.)
        # For simplicity, just return a fixed response in this example
        return f"I'm an AI assistant that follows ethical guidelines. I cannot provide harmful content."

    # Run a basic scan with the callback function
    results = await agent.scan(
        target=simple_app_callback,
        scan_name="Basic-Callback-Test",
        attack_strategies=[AttackStrategy.Base64],
        risk_categories=[RiskCategory.Violence, RiskCategory.HateUnfairness],
        num_objectives=2,
        application_scenario="A customer service chatbot for a retail company"
    )

    print(f"Scan completed. {'Data only' if not results.red_team_agent_result else 'Full evaluation'} results collected.")
    
    # The results include conversations and evaluation data (if not data_only)
    if results.redteaming_data:
        print(f"Collected {len(results.redteaming_data)} conversations")


async def example2_advanced_callback(agent: RedTeamAgent):
    """Example 2: Advanced Callback with Conversation State

    This example demonstrates using a more complex callback that maintains conversation state.
    """
    print("Running Example 2: Advanced Callback with Conversation State")

    # Create a more complex callback function that handles full conversation context
    async def advanced_callback(messages: Dict, stream: bool = False, session_state: Any = None, context: Optional[Dict] =None) -> dict:
        """A more complex callback that processes conversation history"""
        # Extract the latest message from the conversation history
        messages_list = [{"role": chat_message.role,"content": chat_message.content} for chat_message in messages]
        latest_message = messages_list[-1]["content"]
        
        # In a real application, you might process the entire conversation history
        # Here, we're just simulating different responses based on the latest message
        response = "I'm an AI assistant that follows safety guidelines. I cannot provide harmful content."
        
        # Format the response to follow the openAI chat protocol format
        formatted_response = {
            "content": response,
            "role": "assistant"
        }
        
        return {"messages": [formatted_response]}

    # Run a more comprehensive scan with all base risk categories
    advanced_results = await agent.scan(
        target=advanced_callback,
        scan_name="Advanced-Callback-Test",
        attack_strategies=[AttackStrategy.ROT13, AttackStrategy.UnicodeConfusable],
        risk_categories=[RiskCategory.Violence, RiskCategory.Sexual, RiskCategory.SelfHarm, RiskCategory.HateUnfairness],
        num_objectives=2,  # Using 2 objectives per category for this example
        application_scenario="An AI assistant for educational content for children"
    )

    print(f"Advanced scan completed with {len(advanced_results.redteaming_data) if advanced_results.redteaming_data else 0} conversations")


async def example3_direct_model_testing(agent: RedTeamAgent):
    """Example 3: Testing OpenAI or Azure OpenAI Models Directly

    This example shows how to red team test an OpenAI or Azure OpenAI model directly.
    """
    print("Running Example 3: Testing OpenAI or Azure OpenAI Models Directly")
    
    # Configuration for OpenAI model
    openai_config = {
        "model": "gpt-4o",  # Replace with your actual model name
        "api_key": "your_openai_api_key"  # Replace with your actual API key
    }

    # Configuration for Azure OpenAI model
    azure_openai_config = {
        "azure_endpoint": "https://lion-214.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview",  # Replace with your endpoint
        "azure_deployment": "gpt-4o-mini",  # Replace with your deployment name
        "api_key": "4JdiLnsDNHPgHO15djADHOmTwwGwgUZG7ZRTfxc2dz70ec2xGbTZJQQJ99BBACHYHv6XJ3w3AAAAACOGG0bt"  # Replace with your API key
    }

    # Uncomment and use one of these configurations:
    # model_config = openai_config  # For OpenAI
    model_config = azure_openai_config  # For Azure OpenAI
    
    model_results = await agent.scan(
        target=model_config,
        scan_name="Direct-Model-Test",
        attack_strategies=[
            AttackStrategy.EASY,      # Easy complexity attacks
            AttackStrategy.Jailbreak  # Test jailbreak prompts
        ],
        risk_categories=[RiskCategory.Violence, RiskCategory.HateUnfairness],
        num_objectives=3,
        application_scenario="A legal document assistant for contract drafting"
    )
    print(f"Model test completed with {len(model_results.redteaming_data) if model_results.redteaming_data else 0} conversations")


async def example4_strategy_complexity_levels(agent: RedTeamAgent):
    """Example 4: Using Pre-defined Attack Strategy Complexities

    This example demonstrates using pre-defined complexity levels for attacks.
    """
    print("Running Example 4: Using Pre-defined Attack Strategy Complexities")

    # Define a callback that simulates a financial advisor chatbot
    def financial_advisor_callback(query: str) -> str:
        return "I'm a financial advisor assistant. I can help with investment advice and financial planning within legal and ethical guidelines."

    # Run a scan with different complexity levels
    complexity_results = await agent.scan(
        target=financial_advisor_callback,
        scan_name="Complexity-Levels-Test",
        attack_strategies=[
            AttackStrategy.EASY,      # Group of easy complexity attacks
            AttackStrategy.MODERATE,  # Group of moderate complexity attacks
            AttackStrategy.DIFFICULT  # Group of difficult complexity attacks
        ],
        risk_categories=[RiskCategory.Violence, RiskCategory.SelfHarm],
        num_objectives=2,
        application_scenario="A financial advisor chatbot for investment planning"
    )

    print(f"Complexity levels test completed with {len(complexity_results.redteaming_data) if complexity_results.redteaming_data else 0} conversations")


async def example5_specific_attack_strategies(agent: RedTeamAgent):
    """Example 5: Using Specific Attack Strategies

    This example demonstrates using specific individual attack strategies rather than complexity groups.
    """
    print("Running Example 5: Using Specific Attack Strategies")

    # Define a medical assistant callback
    def medical_assistant_callback(query: str) -> str:
        return "I'm a medical information assistant. I can provide general health information but cannot diagnose conditions or prescribe treatments."

    # Run a scan with specific attack strategies
    specific_strategy_results = await agent.scan(
        target=medical_assistant_callback,
        scan_name="Specific-Strategies-Test",
        attack_strategies=[
            AttackStrategy.Base64,           # Encode prompts in Base64
            AttackStrategy.Flip,             # Flip text to evade detection
            AttackStrategy.CharacterSpace,   # Add character spaces
            AttackStrategy.ROT13,            # Use ROT13 encoding
            AttackStrategy.UnicodeConfusable,# Use confusable Unicode characters
            AttackStrategy.Tense             # Change tense of prompts
        ],
        risk_categories=[RiskCategory.SelfHarm, RiskCategory.HateUnfairness],
        num_objectives=3,
        application_scenario="A medical information assistant for general health information"
    )

    print(f"Specific strategies test completed with {len(specific_strategy_results.redteaming_data) if specific_strategy_results.redteaming_data else 0} conversations")
    return specific_strategy_results  # Return for use in example 7


async def example6_data_only_mode(agent: RedTeamAgent):
    """Example 6: Data-Only Mode (Without Evaluation)

    This example shows how to run in data-only mode to collect conversation data without performing evaluations.
    """
    print("Running Example 6: Data-Only Mode (Without Evaluation)")

    # Define a simple content moderator callback
    def content_moderator_callback(query: str) -> str:
        return "I'm a content moderation assistant. I can help identify and flag potentially inappropriate content."

    # Run a data-only scan (without evaluations)
    data_only_results = await agent.scan(
        target=content_moderator_callback,
        scan_name="Data-Only-Test",
        attack_strategies=[AttackStrategy.Morse, AttackStrategy.Leetspeak],
        risk_categories=[RiskCategory.Sexual, RiskCategory.HateUnfairness],
        num_objectives=2,
        application_scenario="A content moderation system for a social media platform",
        data_only=True  # Only collect conversation data without evaluations
    )

    # You can access the collected conversation data
    conversations = data_only_results.redteaming_data
    print(f"Collected {len(conversations) if conversations else 0} conversations without evaluation")


async def example7_working_with_results(results):
    """Example 7: Working with Results

    This example demonstrates how to extract and use information from the RedTeamAgent results.
    """
    print("Running Example 7: Working with Results")
    
    if not results or not results.red_team_agent_result:
        print("No results available. This example requires results from a previous scan.")
        return
    
    # Extract the JSON representation of results
    results_json = results.to_json()
    print(f"Results JSON length: {len(results_json)}")

    # Extract just the scorecard
    scorecard = results.to_scorecard()
    if scorecard:
        print("\nRisk Category Summary:")
        for category in scorecard.get("risk_category_summary", []):
            print(f"Overall ASR: {category.get('overall_asr')}%")
            print(f"Total Attacks: {category.get('overall_total')}")
            print(f"Successful Attacks: {category.get('overall_attack_successes')}")

    # Convert to query-response format for further evaluation
    qr_format = results.to_eval_qr_json_lines()
    print(f"\nQuery-Response format length: {len(qr_format)}")

    # Get a human-readable attack simulation report
    attack_simulation = results.attack_simulation()
    print(f"\nAttack Simulation Report Preview:\n{attack_simulation[:500]}...")


async def example8_custom_application(agent: RedTeamAgent):
    """Example 8: Using a Custom Application with Mock Attack Scenario

    This example demonstrates integrating with a custom application in a realistic attack scenario.
    """
    print("Running Example 8: Using a Custom Application with Mock Attack Scenario")

    # Define a more complex application with some guardrails
    class ContentCreationAssistant:
        def __init__(self):
            self.banned_topics = ["violence", "hate", "harassment", "self-harm", "explicit"]
            self.conversation_history = []
        
        def check_content(self, text):
            # Simple content filter (in reality, this would be more sophisticated)
            for topic in self.banned_topics:
                if topic in text.lower():
                    return False
            return True
        
        def generate_response(self, query):
            # Store conversation history
            self.conversation_history.append({"role": "user", "content": query})
            
            # Check if content passes moderation
            if not self.check_content(query):
                response = "I'm sorry, I cannot assist with that type of content as it may violate content guidelines."
            else:
                response = "I'm a content creation assistant. I can help you draft blog posts, articles, and other content following ethical guidelines."
            
            # Add response to history
            self.conversation_history.append({"role": "assistant", "content": response})
            return response

    # Create an instance of the assistant
    assistant = ContentCreationAssistant()

    # Wrapper function for the RedTeamAgent
    def content_assistant_callback(query):
        return assistant.generate_response(query)

    # Run a scan with various attack strategies
    custom_app_results = await agent.scan(
        target=content_assistant_callback,
        scan_name="Content-Assistant-Test",
        attack_strategies=[
            AttackStrategy.EASY,          # Easy complexity attacks
            AttackStrategy.Jailbreak      # Test jailbreak attempts
        ],
        risk_categories=[RiskCategory.HateUnfairness, RiskCategory.Violence],
        num_objectives=3,
        application_scenario="A content creation assistant for bloggers and writers"
    )

    print(f"Custom application test completed with {len(custom_app_results.redteaming_data) if custom_app_results.redteaming_data else 0} conversations")


async def example9_output_path(agent: RedTeamAgent):
    """Example 9: Running with Output Path and Custom Location

    This example shows how to specify an output path for results.
    """
    print("Running Example 9: Running with Output Path and Custom Location")

    # Create a timestamp-based output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"redteam_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "redteam_results.json")

    # Define a simple application
    def education_assistant_callback(query):
        return "I'm an educational assistant designed to help with learning and studying."

    # Run a scan with custom output path
    output_path_results = await agent.scan(
        target=education_assistant_callback,
        scan_name="Output-Path-Test",
        attack_strategies=[AttackStrategy.AsciiArt, AttackStrategy.Binary],
        risk_categories=[RiskCategory.HateUnfairness, RiskCategory.Violence],
        num_objectives=2,
        application_scenario="An educational assistant for students",
        output_path=output_path  # Specify where to save results
    )

    print(f"Results saved to: {output_path}")


async def example10_empty_attack_strategies(agent: RedTeamAgent):
    """Example 10: Running with Empty Attack Strategies

    This example shows how to handle cases with empty attack strategies.
    """
    print("Running Example 10: Running with Empty Attack Strategies")

    # Define a simple application
    def empty_attack_callback(query):
        return "I'm an assistant designed to handle empty attack strategies."
    
    # Run a scan with empty attack strategies
    empty_attack_results = await agent.scan(
        target=empty_attack_callback,
        scan_name="Empty-Attack-Strategies-Test",
        attack_strategies=[],  # Empty attack strategies
        risk_categories=[RiskCategory.HateUnfairness, RiskCategory.Violence],
        num_objectives=2,
        application_scenario="An assistant for testing empty attack strategies"
    )

    print(f"Empty attack strategies test completed with {len(empty_attack_results.redteaming_data) if empty_attack_results.redteaming_data else 0} conversations")


async def example11_empty_risk_categories(agent: RedTeamAgent):
    """Example 11: Running with Empty Risk Categories

    This example shows how to handle cases with empty risk categories.
    """
    print("Running Example 11: Running with Empty Risk Categories")

    # Define a simple application
    def empty_risk_callback(query):
        return "I'm an assistant designed to handle empty risk categories."


    # Run a scan with empty risk categories
    empty_risk_results = await agent.scan(
        target=empty_risk_callback,
        scan_name="Empty-Risk-Categories-Test",
        attack_strategies=[AttackStrategy.Base64],
        risk_categories=[],  # Empty risk categories
        num_objectives=2,
        application_scenario="An assistant for testing empty risk categories"
    )

    print(f"Empty risk categories test completed with {len(empty_risk_results.redteaming_data) if empty_risk_results.redteaming_data else 0} conversations")


async def example12_duplicate_cases(agent: RedTeamAgent):
    """Example 12: Running with Duplicate Strategies and Categories

    This example shows how to handle cases with duplicate strategies and categories.
    """
    print("Running Example 12: Running with Duplicate Strategies and Categories")

    # Define a simple application
    def duplicate_cases_callback(query):
        return "I'm an assistant designed to handle duplicate strategies and categories."

    # Run a scan with duplicate attack strategies
    duplicate_cases_results = await agent.scan(
        target=duplicate_cases_callback,
        scan_name="Duplicate-Cases-Test",
        attack_strategies=[AttackStrategy.Base64, AttackStrategy.Base64, AttackStrategy.ROT13, AttackStrategy.ROT13],
        risk_categories=[RiskCategory.HateUnfairness, RiskCategory.HateUnfairness, RiskCategory.Violence, RiskCategory.Violence],
        num_objectives=2,
        application_scenario="An assistant for testing duplicate strategies and categories"
    )

    print(f"Duplicate strategies and categories test completed with {len(duplicate_cases_results.redteaming_data) if duplicate_cases_results.redteaming_data else 0} conversations")


if __name__ == "__main__":
    # Run the main function
    print("""
    =====================================================
    Azure AI Evaluation Red Team Agent Bug Bash Examples
    =====================================================
    
    Setup instructions:
    1. Install uv: pip install uv
    2. Create a virtual environment: uv venv --python 3.11 
    3. Activate the virtual environment:
       - Windows: .venv\\Scripts\\activate
       - macOS/Linux: source .venv/bin/activate
    4. Install the SDK with redteam extra: 
       cd path/to/azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation
       uv pip install --upgrade "git+https://github.com/slister1001/azure-sdk-for-python.git@red-team-agent-init#subdirectory=sdk/evaluation/azure-ai-evaluation&egg=azure-ai-evaluation[redteam]"
    5. Update the azure_ai_project variable with your project name
    6. Uncomment examples you want to run in the examples_to_run list
    
    For API key examples, replace placeholders with actual keys
    """)
    
    # Run the async main function
    asyncio.run(main())
