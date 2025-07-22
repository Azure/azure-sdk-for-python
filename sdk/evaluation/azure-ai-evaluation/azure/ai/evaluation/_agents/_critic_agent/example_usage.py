"""
Example usage of the enhanced CriticAgent for agent evaluation.

This demonstrates both conversation-based and agent-based evaluation modes.
"""

import os
from azure.ai.evaluation import AzureOpenAIModelConfiguration, AzureAIProject
from azure.ai.evaluation._agents._critic_agent import CriticAgent
from dotenv import load_dotenv


def example_conversation_evaluation():
    """Example of evaluating a conversation thread using CriticAgent."""

    # Initialize model configuration
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
    )

    # Initialize CriticAgent
    critic_agent = CriticAgent(model_config=model_config)

    # Example conversation history
    conversation_history = [
        {"role": "system", "content": "You are a helpful customer service agent."},
        {"role": "user", "content": [{"type": "text", "text": "What is the status of my order #123?"}]},
        {"role": "assistant", "content": [
            {"type": "tool_call", "tool_call": {
                "id": "tool_001",
                "type": "function",
                "function": {"name": "get_order", "arguments": {"order_id": "123"}}
            }}
        ]},
        {"role": "tool", "tool_call_id": "tool_001", "content": [
            {"type": "tool_result", "tool_result": '{"order": {"id": "123", "status": "shipped"}}'}
        ]},
        {"role": "assistant", "content": [{"type": "text", "text": "Your order #123 has been shipped."}]}
    ]

    tool_definitions = [
        {
            "name": "get_order",
            "description": "Get order details",
            "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}}
        }
    ]

    # Evaluate the conversation
    result = critic_agent.evaluate(
        identifier="thread_123",
        conversation_history=conversation_history,
        tool_definitions=tool_definitions
    )

    print("Conversation Evaluation Result:")
    print(result)
    return result


def example_agent_evaluation():
    """Example of evaluating an agent using agent_id and Azure AI Project."""

    # Initialize model configuration
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
    )

    # Initialize CriticAgent
    critic_agent = CriticAgent(model_config=model_config)

    # Azure AI Project configuration
    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "resource_group_name": os.environ.get("RESOURCE_GROUP_NAME"),
        "project_name": os.environ.get("PROJECT_NAME")
    }

    # Evaluate specific agent with default evaluators
    result_default = critic_agent.evaluate(
        identifier="agent_456",
        azure_ai_project=azure_ai_project
    )

    print("Agent Evaluation Result (Default Evaluators):")
    print(result_default)

    # Evaluate with specific evaluators
    result_specific = critic_agent.evaluate(
        identifier="asst_J3Z9NXjcDW8NrtQZIUcIp2Hr",
        azure_ai_project=azure_ai_project,
        evaluation=["IntentResolution", "TaskAdherence"]
    )

    print("Agent Evaluation Result (Specific Evaluators):")
    print(result_specific)

    return result_default, result_specific


def example_mixed_evaluation():
    """Example showing how to use different evaluation modes."""

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
    )
    #
    critic_agent = CriticAgent(model_config=model_config)
    azure_ai_project = {
        "azure_endpoint": os.environ.get("PROJECT_ENDPOINT"),

    }
    # Mode 1: Traditional evaluation (thread_id only)
    print("=== Mode 1: Thread Evaluation ===")
    try:
        thread_result = critic_agent.evaluate(
            identifier="thread_789",
            azure_ai_project=azure_ai_project,

        )
        print(thread_result)
    except Exception as e:
        print(f"Thread evaluation error (expected in demo): {e}")

    # Mode 2: Agent evaluation with Azure AI Project
    print("\n=== Mode 2: Agent Evaluation ===")
    # subscription_id: str
    # resource_group_name: str
    # project_name: str
    azure_ai_project = {
        "azure_endpoint": os.environ.get("PROJECT_ENDPOINT"),

    }

    try:
        # Streamlining
        agent_result = critic_agent.evaluate(
            identifier="asst_J3Z9NXjcDW8NrtQZIUcIp2Hr",
            azure_ai_project=azure_ai_project,
            evaluation=["IntentResolution", "ToolCallAccuracy", "TaskAdherence"]
        )

        # Routing
        agent_result = critic_agent.evaluate_route(
            identifier="asst_J3Z9NXjcDW8NrtQZIUcIp2Hr",
            azure_ai_project=azure_ai_project
        )
        print(agent_result)
    except Exception as e:
        print(f"Agent evaluation error (expected without proper setup): {e}")


if __name__ == "__main__":
    print("CriticAgent Usage Examples")
    print("=" * 50)
    # load_dotenv("C:\\Users\\ghyadav\\work\\ghyadav_azure_sdk\\azure-sdk-for-python\\sdk\\evaluation\\azure-ai-evaluation\\critic_agent\\ghyadav.env")  # Load environment variables from .env file
    # Run examples (will require proper environment setup)

    load_dotenv(
        "C:\\Users\\ghyadav\\work\\ghyadav_azure_sdk\\azure-sdk-for-python\\sdk\\evaluation\\azure-ai-evaluation\\azure\\ai\\evaluation\\_agents\\_critic_agent\\eval_ws.env")
    try:
        example_mixed_evaluation()
        # Sample result: [{'thread_id': 'thread_NSyMJiQscTGAPehOOq6RpGU3', 'results': {'IntentResolution': {'intent_resolution': 5.0, 'intent_resolution_result': 'pass', 'intent_resolution_threshold': 3, 'intent_resolution_reason': "The user asked how the agent is doing. The agent responded appropriately, acknowledging its non-human nature and expressing readiness to help, then reciprocated the question. This fully satisfies the user's intent in a friendly and relevant manner."}}, 'justification': "The user's query was a casual greeting ('How are you'), and the agent responded appropriately by acknowledging its non-human status and reciprocating the question. There were no explicit tasks, instructions, or tool usage involved, so TaskAdherence and ToolAccuracy are not relevant. IntentResolution is appropriate to assess whether the agent understood and responded to the user's intent in a natural and helpful way.", 'distinct_assessments': {'IntentResolution': "This evaluator will assess whether the agent correctly interpreted the user's casual inquiry and responded in a way that maintains conversational flow and engagement."}}, {'thread_id': 'thread_oDhHDz6HgjTqSLE8FVJy6Ord', 'results': {'IntentResolution': {'intent_resolution': 5.0, 'intent_resolution_result': 'pass', 'intent_resolution_threshold': 3, 'intent_resolution_reason': "The user asked for the location of Mumbai. The agent provided the city's position within India, its state, country, coordinates, and relevant geographic context. The response is accurate, thorough, and directly fulfills the user's intent."}, 'TaskAdherence': {'task_adherence': 5.0, 'task_adherence_result': 'pass', 'task_adherence_threshold': 3, 'task_adherence_reason': "The assistant accurately provided Mumbai's location, including city, state, country, coordinates, and relevant context. There were no system constraints or tool requirements, and the user's request was fully satisfied."}}, 'justification': "The agent was asked to fetch the location of Mumbai. There were no tool requirements or constraints specified, so TaskAdherence is relevant to check if the agent followed the instruction and provided the requested information. IntentResolution is also applicable to assess whether the agent understood the user's intent (to get the location of Mumbai) and provided a comprehensive and helpful response. ToolAccuracy is not applicable as there are no tools defined or used.", 'distinct_assessments': {'TaskAdherence': "This evaluator will assess whether the agent directly addressed the user's request to fetch the location of Mumbai, ensuring all required details were provided and the instruction was followed.", 'IntentResolution': "This evaluator will assess whether the agent correctly understood the user's intent (to obtain the location of Mumbai) and provided a holistic, informative, and contextually appropriate response."}}]
    except Exception as e:
        print(f"Demo completed with expected configuration errors: {e}")
