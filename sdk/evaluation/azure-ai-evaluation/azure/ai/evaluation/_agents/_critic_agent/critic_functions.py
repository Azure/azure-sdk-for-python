# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import logging
from typing import Dict, Union, List, Optional, Any, Set, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import required modules for Azure AI evaluation
try:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from azure.ai.evaluation._converters._ai_services import AIAgentConverter
    from azure.ai.evaluation import (
        IntentResolutionEvaluator,
        ToolCallAccuracyEvaluator,
        TaskAdherenceEvaluator,
        AzureOpenAIModelConfiguration
    )
    from azure.ai.evaluation._common.utils import (
        reformat_conversation_history,
        reformat_tool_definitions,
        reformat_agent_response
    )
except ImportError as import_error:
    raise ImportError(f"Required Azure AI packages not available: {str(import_error)}. "
                      f"Please install azure-ai-projects, azure-identity, and azure-ai-evaluation packages.")

logger = logging.getLogger(__name__)

# Default agent evaluation metrics
DEFAULT_AGENT_EVALUATORS = ["IntentResolution", "ToolCallAccuracy", "TaskAdherence"]


def _fetch_agent_threads(azure_ai_project: Dict[str, str], agent_id: str, max_threads: int = 5) -> str:
    """
    Fetch conversation thread IDs for a specific agent from Azure AI Project.

    :param azure_ai_project: Azure AI project configuration containing azure_endpoint
    :type azure_ai_project: Dict[str, str]
    :param agent_id: The agent ID to fetch threads for
    :type agent_id: str
    :param max_threads: Maximum number of threads to fetch (default: 5)
    :type max_threads: int
    :return: JSON string containing list of thread IDs
    :rtype: str
    """
    try:
        project_client = AIProjectClient(
            endpoint=azure_ai_project.get("azure_endpoint"),
            credential=DefaultAzureCredential(),
        )

        threads = project_client.agents.threads.list()
        thread_ids = []

        count = 0
        for thread in threads:
            if count >= max_threads:
                break
            thread_ids.append(thread.id)
            count += 1

        result = {
            "agent_id": agent_id,
            "thread_ids": thread_ids,
            "total_threads": len(thread_ids)
        }

        logger.info(f"Fetched {len(thread_ids)} threads for agent {agent_id}.")
        return json.dumps(result)

    except Exception as e:
        error_result = {
            "error": f"Failed to fetch agent threads: {str(e)}",
            "agent_id": agent_id,
            "thread_ids": []
        }
        logger.error(f"Error fetching agent threads: {str(e)}")
        return json.dumps(error_result)


def _initialize_evaluators(model_config_json: str, evaluator_names: Optional[str] = None) -> str:
    """
    Initialize specified evaluators with the given model configuration.

    :param model_config_json: JSON string containing model configuration
    :type model_config_json: str
    :param evaluator_names: Comma-separated string of evaluator names (optional)
    :type evaluator_names: Optional[str]
    :return: JSON string containing initialized evaluator information
    :rtype: str
    """
    try:
        model_config_dict = json.loads(model_config_json)
        model_config = AzureOpenAIModelConfiguration(**model_config_dict)

        if evaluator_names:
            evaluator_list = [name.strip() for name in evaluator_names.split(",")]
        else:
            evaluator_list = DEFAULT_AGENT_EVALUATORS

        initialized_evaluators = {}

        for name in evaluator_list:
            if name == "IntentResolution":
                evaluator = IntentResolutionEvaluator(model_config=model_config)
                initialized_evaluators[name] = {"status": "initialized", "type": "IntentResolutionEvaluator"}
            elif name == "ToolCallAccuracy":
                evaluator = ToolCallAccuracyEvaluator(model_config=model_config)
                initialized_evaluators[name] = {"status": "initialized", "type": "ToolCallAccuracyEvaluator"}
            elif name == "TaskAdherence":
                evaluator = TaskAdherenceEvaluator(model_config=model_config)
                initialized_evaluators[name] = {"status": "initialized", "type": "TaskAdherenceEvaluator"}
            else:
                initialized_evaluators[name] = {"status": "unknown", "type": "Unknown evaluator"}
                logger.warning(f"Unknown evaluator: {name}")

        result = {
            "initialized_evaluators": initialized_evaluators,
            "total_evaluators": len(initialized_evaluators)
        }

        return json.dumps(result)

    except Exception as e:
        error_result = {
            "error": f"Failed to initialize evaluators: {str(e)}",
            "initialized_evaluators": {}
        }
        logger.error(f"Error initializing evaluators: {str(e)}")
        return json.dumps(error_result)


def _evaluate_conversation_thread(azure_ai_project_json: str, thread_id: str,
                                  model_config_json: str, evaluators: Optional[str] = None) -> str:
    """
    Evaluate a specific conversation thread using specified evaluators.

    :param azure_ai_project_json: JSON string containing Azure AI project configuration
    :type azure_ai_project_json: str
    :param thread_id: The ID of the conversation thread to evaluate
    :type thread_id: str
    :param model_config_json: JSON string containing model configuration
    :type model_config_json: str
    :param evaluators: Comma-separated string of evaluators to run (optional)
    :type evaluators: Optional[str]
    :return: JSON string containing evaluation results
    :rtype: str
    """
    try:
        azure_ai_project = json.loads(azure_ai_project_json)
        model_config_dict = json.loads(model_config_json)
        model_config = AzureOpenAIModelConfiguration(**model_config_dict)

        project_client = AIProjectClient(
            endpoint=azure_ai_project.get("azure_endpoint"),
            credential=DefaultAzureCredential(),
        )

        # Get conversation data
        converter = AIAgentConverter(project_client)
        conversation = converter.prepare_evaluation_data(thread_ids=thread_id)[-1]

        # Determine which evaluators to run
        if evaluators:
            evaluators_to_run = [name.strip() for name in evaluators.split(",")]
        else:
            evaluators_to_run = DEFAULT_AGENT_EVALUATORS

        # Initialize evaluators
        evaluator_instances = {}
        for name in evaluators_to_run:
            if name == "IntentResolution":
                evaluator_instances[name] = IntentResolutionEvaluator(model_config=model_config)
            elif name == "ToolCallAccuracy":
                evaluator_instances[name] = ToolCallAccuracyEvaluator(model_config=model_config)
            elif name == "TaskAdherence":
                evaluator_instances[name] = TaskAdherenceEvaluator(model_config=model_config)

        # Run evaluations
        evaluation_results = _run_evaluators_on_conversation(evaluator_instances, conversation)

        result = {
            "thread_id": thread_id,
            "evaluation_results": evaluation_results,
            "evaluators_used": list(evaluator_instances.keys())
        }

        return json.dumps(result)

    except Exception as e:
        error_result = {
            "error": f"Failed to evaluate conversation thread: {str(e)}",
            "thread_id": thread_id,
            "evaluation_results": {}
        }
        logger.error(f"Error evaluating conversation thread: {str(e)}")
        return json.dumps(error_result)


def _evaluate_agent_comprehensive(azure_ai_project_json: str, agent_id: str,
                                  model_config_json: str, evaluators: Optional[str] = None,
                                  max_threads: int = 5) -> str:
    """
    Evaluate an agent by fetching multiple conversation threads and running evaluations.

    :param azure_ai_project_json: JSON string containing Azure AI project configuration
    :type azure_ai_project_json: str
    :param agent_id: The ID of the agent to evaluate
    :type agent_id: str
    :param model_config_json: JSON string containing model configuration
    :type model_config_json: str
    :param evaluators: Comma-separated string of evaluators to run (optional)
    :type evaluators: Optional[str]
    :param max_threads: Maximum number of threads to evaluate (default: 5)
    :type max_threads: int
    :return: JSON string containing comprehensive evaluation results
    :rtype: str
    """
    try:
        azure_ai_project = json.loads(azure_ai_project_json)

        # First fetch thread IDs
        thread_result = _fetch_agent_threads(azure_ai_project, agent_id, max_threads)
        thread_data = json.loads(thread_result)

        if "error" in thread_data:
            return thread_result

        thread_ids = thread_data["thread_ids"]
        all_results = []

        # Evaluate each thread
        for thread_id in thread_ids:
            thread_evaluation = _evaluate_conversation_thread(
                azure_ai_project_json, thread_id, model_config_json, evaluators
            )
            thread_result = json.loads(thread_evaluation)
            if "error" not in thread_result:
                all_results.append(thread_result)

        result = {
            "agent_id": agent_id,
            "total_threads_evaluated": len(all_results),
            "thread_evaluations": all_results,
            "evaluators_used": evaluators.split(",") if evaluators else DEFAULT_AGENT_EVALUATORS
        }

        return json.dumps(result)

    except Exception as e:
        error_result = {
            "error": f"Failed to evaluate agent comprehensively: {str(e)}",
            "agent_id": agent_id,
            "thread_evaluations": []
        }
        logger.error(f"Error in comprehensive agent evaluation: {str(e)}")
        return json.dumps(error_result)


def evaluate(azure_ai_project_json: str, agent_id: str = None, thread_id: str = None,
             model_config_json: str = "", evaluators: Optional[str] = None,
             max_threads: int = 5) -> str:
    """
    Evaluate an agent or conversation thread using specified evaluators.
    This is the main evaluation function that can handle both agent-level and thread-level evaluation.

    :param azure_ai_project_json: JSON string containing Azure AI project configuration
    :type azure_ai_project_json: str
    :param agent_id: The ID of the agent to evaluate (optional, for agent-level evaluation)
    :type agent_id: Optional[str]
    :param thread_id: The ID of the conversation thread to evaluate (optional, for thread-level evaluation)
    :type thread_id: Optional[str]
    :param model_config_json: JSON string containing model configuration
    :type model_config_json: str
    :param evaluators: Comma-separated string of evaluators to run (optional, defaults to all)
    :type evaluators: Optional[str]
    :param max_threads: Maximum number of threads to evaluate when evaluating an agent (default: 5)
    :type max_threads: int
    :return: JSON string containing evaluation results
    :rtype: str
    """
    try:
        if not agent_id and not thread_id:
            return json.dumps({
                "error": "Either agent_id or thread_id must be provided for evaluation.",
                "evaluation_results": {}
            })

        if agent_id and thread_id:
            return json.dumps({
                "error": "Please provide either agent_id OR thread_id, not both.",
                "evaluation_results": {}
            })

        # Agent-level evaluation
        if agent_id:
            return _evaluate_agent_comprehensive(
                azure_ai_project_json, agent_id, model_config_json, evaluators, max_threads
            )

        # Thread-level evaluation
        if thread_id:
            return _evaluate_conversation_thread(
                azure_ai_project_json, thread_id, model_config_json, evaluators
            )

    except Exception as e:
        error_result = {
            "error": f"Failed to perform evaluation: {str(e)}",
            "evaluation_results": {}
        }
        logger.error(f"Error in evaluate function: {str(e)}")
        return json.dumps(error_result)

# Todo: Auto evaluate would implement the routing capabilitlity similar to the evaluator sdk POC
def auto_evaluate(azure_ai_project_json: str, agent_id: str = None, thread_id: str = None,
                  model_config_json: str = "", max_threads: int = 5) -> str:
    """
    Auto-evaluate an agent or conversation thread using all available evaluators.
    This function automatically selects and runs all appropriate evaluators.

    :param azure_ai_project_json: JSON string containing Azure AI project configuration
    :type azure_ai_project_json: str
    :param agent_id: The ID of the agent to evaluate (optional, for agent-level evaluation)
    :type agent_id: Optional[str]
    :param thread_id: The ID of the conversation thread to evaluate (optional, for thread-level evaluation)
    :type thread_id: Optional[str]
    :param model_config_json: JSON string containing model configuration
    :type model_config_json: str
    :param max_threads: Maximum number of threads to evaluate when evaluating an agent (default: 5)
    :type max_threads: int
    :return: JSON string containing evaluation results
    :rtype: str
    """
    try:
        if not agent_id and not thread_id:
            return json.dumps({
                "error": "Either agent_id or thread_id must be provided for auto-evaluation.",
                "evaluation_results": {}
            })

        if agent_id and thread_id:
            return json.dumps({
                "error": "Please provide either agent_id OR thread_id, not both.",
                "evaluation_results": {}
            })

        # Use all default evaluators for auto-evaluation
        all_evaluators = ",".join(DEFAULT_AGENT_EVALUATORS)

        # Agent-level auto-evaluation
        if agent_id:
            result = _evaluate_agent_comprehensive(
                azure_ai_project_json, agent_id, model_config_json, all_evaluators, max_threads
            )
            # Add auto-evaluation metadata
            result_data = json.loads(result)
            result_data["evaluation_type"] = "auto_evaluation"
            result_data["auto_selected_evaluators"] = DEFAULT_AGENT_EVALUATORS
            return json.dumps(result_data)

        # Thread-level auto-evaluation
        if thread_id:
            result = _evaluate_conversation_thread(
                azure_ai_project_json, thread_id, model_config_json, all_evaluators
            )
            # Add auto-evaluation metadata
            result_data = json.loads(result)
            result_data["evaluation_type"] = "auto_evaluation"
            result_data["auto_selected_evaluators"] = DEFAULT_AGENT_EVALUATORS
            return json.dumps(result_data)

    except Exception as e:
        error_result = {
            "error": f"Failed to perform auto-evaluation: {str(e)}",
            "evaluation_results": {}
        }
        logger.error(f"Error in auto_evaluate function: {str(e)}")
        return json.dumps(error_result)

def get_user_info(user_id: int) -> str:
    """Retrieves user information based on user ID.

    :param user_id (int): ID of the user.
    :rtype: int

    :return: User information as a JSON string.
    :rtype: str
    """
    mock_users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"},
        3: {"name": "Charlie", "email": "charlie@example.com"},
    }
    user_info = mock_users.get(user_id, {"error": "User not found."})
    return json.dumps({"user_info": user_info})

def _get_available_evaluators() -> str:
    """
    Internal helper function to get list of available evaluators and their descriptions.

    :return: JSON string containing available evaluators information
    :rtype: str
    """
    evaluators_info = {
        "available_evaluators": {
            "IntentResolution": {
                "description": "Evaluates if the agent correctly understands and resolves user intent",
                "required_inputs": ["query", "response", "tool_definitions (optional)"]
            },
            "ToolCallAccuracy": {
                "description": "Evaluates the accuracy of tool calls made by the agent",
                "required_inputs": ["query", "response", "tool_calls", "tool_definitions"]
            },
            "TaskAdherence": {
                "description": "Evaluates if the agent adheres to the given task requirements",
                "required_inputs": ["query", "response", "tool_definitions (optional)"]
            }
        },
        "default_evaluators": DEFAULT_AGENT_EVALUATORS
    }

    return json.dumps(evaluators_info)


def _run_evaluators_on_conversation(evaluators: Dict[str, Any], conversation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal helper function to run multiple evaluators on a conversation in parallel.

    :param evaluators: Dictionary of evaluator instances
    :type evaluators: Dict[str, Any]
    :param conversation_data: Conversation data to evaluate
    :type conversation_data: Dict[str, Any]
    :return: Evaluation results
    :rtype: Dict[str, Any]
    """
    results = {}

    # Extract evaluation inputs from conversation data
    query = conversation_data.get("query", "")
    response = conversation_data.get("response", "")
    tool_definitions = conversation_data.get("tool_definitions", [])
    tool_calls = conversation_data.get("tool_calls", [])

    # Run evaluators in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_evaluator = {}

        for name, evaluator in evaluators.items():
            if name == "IntentResolution":
                future = executor.submit(
                    evaluator,
                    query=query,
                    response=response,
                    tool_definitions=tool_definitions if tool_definitions else None
                )
            elif name == "ToolCallAccuracy":
                if tool_calls:  # Only run if there are tool calls
                    future = executor.submit(
                        evaluator,
                        query=query,
                        response=response,
                        tool_calls=tool_calls,
                        tool_definitions=tool_definitions
                    )
                else:
                    logger.info("No tool calls found, skipping ToolCallAccuracy evaluation.")
                    continue
            elif name == "TaskAdherence":
                future = executor.submit(
                    evaluator,
                    query=query,
                    response=response,
                    tool_definitions=tool_definitions if tool_definitions else None
                )
            else:
                continue

            future_to_evaluator[future] = name

        # Collect results
        for future in as_completed(future_to_evaluator):
            evaluator_name = future_to_evaluator[future]
            try:
                result = future.result()
                results[evaluator_name] = result
            except Exception as e:
                logger.error(f"Evaluator {evaluator_name} failed: {str(e)}")
                results[evaluator_name] = {"error": str(e)}

    return results


# Export only the two main functions for agent tool usage
user_functions: Set[Callable[..., Any]] = {
    evaluate,
    auto_evaluate,
    get_user_info
}
