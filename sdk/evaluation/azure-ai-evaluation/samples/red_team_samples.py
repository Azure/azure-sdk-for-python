# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    These samples demonstrate usage of various classes and methods used in Red Team
    functionality within the azure-ai-evaluation library.
    
USAGE:
    python red_team_samples.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SUBSCRIPTION_ID - your Azure subscription ID
    2) AZURE_RESOURCE_GROUP_NAME - your resource group name
    3) AZURE_PROJECT_NAME - your Azure AI project name
    4) AZURE_OPENAI_ENDPOINT - your Azure OpenAI endpoint (for model samples)
    5) AZURE_OPENAI_KEY - your Azure OpenAI key (for model samples)
    6) AZURE_OPENAI_DEPLOYMENT - your Azure OpenAI deployment name (for model samples)
"""

import os
import asyncio
from azure.ai.evaluation.red_team import (
    RedTeam, 
    AttackStrategy, 
    RiskCategory
)
from azure.identity import DefaultAzureCredential


class RedTeamSamples(object):
    def __init__(self):
        # Setup Azure AI Project connection
        self.azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        self.credential = DefaultAzureCredential()
        
        # Setup Azure OpenAI config for model testing
        self.azure_openai_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

    async def basic_callback_example(self):
        """
        This example demonstrates the most basic usage of Red Team with a
        simple callback function. It shows how to initialize the agent with specific risk
        categories and then use it to scan a target function with basic attack strategies.
        """
        # [START red_team_basic_callback]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(azure_ai_project=azure_ai_project, credential=credential, risk_categories=[RiskCategory.Violence, RiskCategory.HateUnfairness], num_objectives=2) 

        # Define a simple callback function that simulates a chatbot
        def simple_callback(query: str) -> str:
            # Your implementation to call your application (e.g., RAG system, chatbot)
            return "I'm an AI assistant that follows ethical guidelines. I cannot provide harmful content."

        # Run the scan with basic attack strategies
        results = await agent.scan(
            target=simple_callback,
            scan_name="Basic-Callback-Test",
            attack_strategies=[AttackStrategy.Base64, AttackStrategy.ROT13],
            application_scenario="A customer service chatbot for a retail company"
        )

        print(f"Scan completed with {len(results.redteaming_data) if results.redteaming_data else 0} conversations")
        # [END red_team_basic_callback]
        return results

    async def advanced_callback_example(self):
        """
        This example demonstrates a more advanced usage with a complex callback function
        that handles conversation state and formatting. It shows how to use Red Team
        with an asynchronous callback that processes message history in a chat format.
        """
        # [START red_team_advanced_callback]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(azure_ai_project=azure_ai_project, credential=credential, risk_categories=[
                RiskCategory.Violence, 
                RiskCategory.Sexual, 
                RiskCategory.SelfHarm, 
                RiskCategory.HateUnfairness
            ],
            num_objectives=2,)

        # Create a more complex callback function that handles conversation state
        async def advanced_callback(messages, stream=False, session_state=None, context=None):
            # Extract the latest message from the conversation history
            messages_list = [{"role": message.role, "content": message.content} 
                            for message in messages]
            latest_message = messages_list[-1]["content"]
            
            # In a real application, you might process the entire conversation history
            # Here, we're just simulating a response
            response = "I'm an AI assistant that follows safety guidelines. I cannot provide harmful content."
            
            # Format the response to follow the expected chat protocol format
            formatted_response = {
                "content": response,
                "role": "assistant"
            }
            
            return {"messages": [formatted_response]}

        # Run the scan with multiple attack strategies
        results = await agent.scan(
            target=advanced_callback,
            scan_name="Advanced-Callback-Test",
            attack_strategies=[
                AttackStrategy.Base64, 
                AttackStrategy.ROT13, 
                AttackStrategy.UnicodeConfusable
            ],
            application_scenario="An AI assistant for educational content"
        )

        print(f"Advanced scan completed with {len(results.redteaming_data) if results.redteaming_data else 0} conversations")
        # [END red_team_advanced_callback]
        return results

    async def direct_model_testing_example(self):
        """
        This example demonstrates how to test an Azure OpenAI model directly using the
        Red Team. Rather than providing a callback function, it shows how to 
        set up and pass configuration for a model to be tested directly.
        """
        # [START red_team_direct_model]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(azure_ai_project=azure_ai_project, credential=credential, risk_categories=[RiskCategory.Violence],
            num_objectives=1,)

        # Configuration for Azure OpenAI model
        azure_openai_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        # Run scan directly against a model configuration
        model_results = await agent.scan(
            target=azure_openai_config,
            scan_name="Direct-Model-Test",
            attack_strategies=[
                AttackStrategy.Flip,
                AttackStrategy.Tense,
                AttackStrategy.Compose([AttackStrategy.Base64, AttackStrategy.ROT13]),
            ],
            application_scenario="A legal document assistant for contract drafting",
            timeout=360
        )

        print(f"Model test completed with {len(model_results.redteaming_data) if model_results.redteaming_data else 0} conversations")
        # [END red_team_direct_model]
        return model_results

    async def strategy_complexity_levels_example(self):
        """
        This example demonstrates how to use different complexity levels of attack strategies.
        It shows how to use the predefined complexity groups (EASY, MODERATE, DIFFICULT) to
        test a target with attacks of varying sophistication.
        """
        # [START red_team_complexity_levels]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(azure_ai_project=azure_ai_project, credential=credential,risk_categories=[RiskCategory.Violence, RiskCategory.SelfHarm], num_objectives=2)

        # Create a simple callback function
        def callback(query: str) -> str:
            return "I'm a helpful assistant that follows ethical guidelines."

        # Run a scan with different complexity levels
        results = await agent.scan(
            target=callback,
            scan_name="Complexity-Levels-Test",
            attack_strategies=[
                AttackStrategy.EASY,      # Group of easy complexity attacks
                AttackStrategy.MODERATE,  # Group of moderate complexity attacks
                AttackStrategy.DIFFICULT  # Group of difficult complexity attacks
            ],
            application_scenario="A financial advisor chatbot"
        )

        print(f"Complexity levels test completed with {len(results.redteaming_data) if results.redteaming_data else 0} conversations")
        # [END red_team_complexity_levels]
        return results

    async def specific_attack_strategies_example(self):
        """
        This example demonstrates how to use specific attack strategies rather than
        complexity groups. It shows how to select individual attack techniques to test
        a target's resilience against particular evasion methods.
        """
        # [START red_team_specific_strategies]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(
            azure_ai_project=azure_ai_project, 
            credential=credential,
            risk_categories=[RiskCategory.SelfHarm, RiskCategory.HateUnfairness],
            num_objectives=2
        )

        # Define a simple callback function
        def callback(query: str) -> str:
            return "I'm a medical information assistant. I can provide general health information."

        # Run a scan with specific attack strategies
        results = await agent.scan(
            target=callback,
            scan_name="Specific-Strategies-Test",
            attack_strategies=[
                AttackStrategy.Base64,           # Encode prompts in Base64
                AttackStrategy.Flip,             # Flip text to evade detection
                AttackStrategy.CharacterSpace,   # Add character spaces
                AttackStrategy.ROT13,            # Use ROT13 encoding
                AttackStrategy.UnicodeConfusable # Use confusable Unicode characters
            ],
            application_scenario="A medical information assistant"
        )

        print(f"Specific strategies test completed with {len(results.redteaming_data) if results.redteaming_data else 0} conversations")
        # [END red_team_specific_strategies]
        return results

    async def data_only_mode_example(self):
        """
        This example demonstrates the data-only mode which collects conversation data
        without performing evaluations. This is useful for gathering attack attempts and
        responses for later analysis or when you want to implement your own evaluation.
        """
        # [START red_team_data_only]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(
            azure_ai_project=azure_ai_project, 
            credential=credential,
            risk_categories=[RiskCategory.Sexual, RiskCategory.HateUnfairness],
            num_objectives=2
        )

        # Define a simple callback function
        def callback(query: str) -> str:
            return "I'm a content moderation assistant. I help identify inappropriate content."

        # Run a data-only scan (without evaluations)
        results = await agent.scan(
            target=callback,
            scan_name="Data-Only-Test",
            attack_strategies=[AttackStrategy.Morse, AttackStrategy.Leetspeak],
            application_scenario="A content moderation system",
            data_only=True  # Only collect conversation data without evaluations
        )

        # Access the collected conversation data
        conversations = results.redteaming_data
        print(f"Collected {len(conversations) if conversations else 0} conversations without evaluation")
        # [END red_team_data_only]
        return results

    async def output_path_example(self):
        """
        This example demonstrates how to specify a custom output path for saving scan results.
        It shows how to create a timestamped directory and save the results to a specific
        location for later analysis.
        """
        # [START red_team_output_path]
        import os
        from datetime import datetime
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(
            azure_ai_project=azure_ai_project, 
            credential=credential,
            risk_categories=[RiskCategory.HateUnfairness, RiskCategory.Violence],
            num_objectives=2
        )

        # Create a timestamp-based output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"redteam_results_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "redteam_results.json")

        # Define a simple callback function
        def callback(query: str) -> str:
            return "I'm an educational assistant designed to help with learning."

        # Run a scan with custom output path
        results = await agent.scan(
            target=callback,
            scan_name="Output-Path-Test",
            attack_strategies=[AttackStrategy.AsciiArt, AttackStrategy.Binary],
            application_scenario="An educational assistant for students",
            output_path=output_path  # Specify where to save results
        )

        print(f"Results saved to: {output_path}")
        # [END red_team_output_path]
        return results

    async def custom_application_example(self):
        """
        This example demonstrates testing a more complex custom application with built-in
        content moderation capabilities. It shows how to create and test a more sophisticated
        target with its own guardrails and conversation tracking.
        """
        # [START red_team_custom_application]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential

        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(
            azure_ai_project=azure_ai_project, 
            credential=credential,
            risk_categories=[RiskCategory.HateUnfairness, RiskCategory.Violence],
            num_objectives=2
        )

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
                    response = "I'm a content creation assistant. I can help you draft blog posts and articles following ethical guidelines."
                
                # Add response to history
                self.conversation_history.append({"role": "assistant", "content": response})
                return response

        # Create an instance of the assistant
        assistant = ContentCreationAssistant()

        # Wrapper function for RedTeam
        def content_assistant_callback(query):
            return assistant.generate_response(query)

        print()

        # Run the scan with various attack strategies
        results = await agent.scan(
            target=content_assistant_callback,
            scan_name="Content-Assistant-Test",
            attack_strategies=[
                AttackStrategy.EASY,          # Easy complexity attacks
                AttackStrategy.Jailbreak      # Test jailbreak attempts
            ],
            application_scenario="A content creation assistant for bloggers and writers"
        )

        print(f"Custom application test completed with {len(results.redteaming_data) if results.redteaming_data else 0} conversations")
        # [END red_team_custom_application]
        return results

    async def pyrit_prompt_chat_target_example(self):
        """
        This example demonstrates how to use Red Team with a PyRIT PromptChatTarget.
        It shows integration with the PyRIT library for testing Azure OpenAI models using
        the more sophisticated target interfaces provided by PyRIT.
        """
        # [START red_team_pyrit_target]
        from azure.ai.evaluation import (
            RedTeam, 
            AttackStrategy,
            RiskCategory
        )
        from azure.identity import DefaultAzureCredential
        from pyrit.prompt_target import OpenAIChatTarget, PromptChatTarget
        
        # Initialize Red Team
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()
        agent = RedTeam(
            azure_ai_project=azure_ai_project, 
            credential=credential,
            risk_categories=[RiskCategory.SelfHarm, RiskCategory.HateUnfairness],
            num_objectives=2
        )

        # Create a PyRIT PromptChatTarget for an Azure OpenAI model
        # This could be any class that inherits from PromptChatTarget
        chat_target = OpenAIChatTarget(
            model_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_KEY")
        )
        
        # Run a scan using the PyRIT PromptChatTarget directly
        results = await agent.scan(
            target=chat_target,  # PyRIT PromptChatTarget instance
            scan_name="PyRIT-Target-Test",
            attack_strategies=[
                AttackStrategy.Base64,
                AttackStrategy.ROT13
            ],
            application_scenario="A general-purpose AI assistant"
        )
        
        print(f"PyRIT target scan completed with {len(results.redteaming_data) if results.redteaming_data else 0} conversations")
        # [END red_team_pyrit_target]
        return results


async def run_samples():
    """Run all Red Team samples."""
    print("Running Red Team samples...")
    
    samples = RedTeamSamples()
    
    # Uncomment the samples you want to run
    sample_runners = [
        # samples.basic_callback_example(),
        # samples.advanced_callback_example(),
        samples.direct_model_testing_example(),
        # samples.strategy_complexity_levels_example(),
        # samples.specific_attack_strategies_example(),
        # samples.data_only_mode_example(),
        # samples.output_path_example(),
        # samples.custom_application_example(),
        # samples.pyrit_prompt_chat_target_example(),
    ]
    
    # Run the selected samples
    await asyncio.gather(*sample_runners)
    
    print("All samples completed!")


if __name__ == "__main__":
    print("Azure AI Evaluation Red Team Samples")
    print("==========================================")
    print("Set the following environment variables before running:")
    print("  AZURE_SUBSCRIPTION_ID")
    print("  AZURE_RESOURCE_GROUP_NAME")
    print("  AZURE_PROJECT_NAME")
    print("  AZURE_OPENAI_ENDPOINT (for model testing examples)")
    print("  AZURE_OPENAI_KEY (for model testing examples)")
    print("  AZURE_OPENAI_DEPLOYMENT (for model testing examples)")
    print("\nRunning samples...\n")
    from dotenv import load_dotenv
    load_dotenv()
    # Run the async samples
    asyncio.run(run_samples())
