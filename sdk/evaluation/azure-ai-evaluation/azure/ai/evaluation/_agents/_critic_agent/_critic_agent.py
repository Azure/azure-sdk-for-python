import asyncio
import os
import logging
from typing import Dict, Union, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._common.utils import reformat_conversation_history, reformat_tool_definitions, reformat_agent_response
from azure.ai.evaluation._common._experimental import experimental

# Import evaluators
from azure.ai.evaluation._evaluators._intent_resolution import IntentResolutionEvaluator
from azure.ai.evaluation._evaluators._tool_call_accuracy import ToolCallAccuracyEvaluator
from azure.ai.evaluation._evaluators._task_adherence import TaskAdherenceEvaluator

logger = logging.getLogger(__name__)

# Todo: This needs to be put at the right place if sdk version is less than *.b10. We can ship this to available only with the latest version of the SDK.
try:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from azure.ai.evaluation._converters._ai_services import AIAgentConverter
except ImportError as import_error:
    raise EvaluationException(
        message=f"Required Azure AI packages not available: {str(import_error)}. Please install azure-ai-projects and azure-identity packages.",
        internal_message=f"Missing required packages for agent evaluation: {str(import_error)}",
        # blame=ErrorBlame.USER_ERROR,
        # category=ErrorCategory.MISSING_FIELD,
        # target=ErrorTarget.CRITIC_AGENT,
    )


@experimental
class CriticAgent(PromptyEvaluatorBase[Dict[str, Union[str, List[str]]]]):
    """The CriticAgent evaluates which evaluator(s) to use based on the conversation history and tool definitions.
    1) It loads _critic_agent.prompty from the current directory, and uses it to select the appropriate evaluators.
    2) The constructor initializes the agent with the model configuration.
    3) The evaluate method supports multiple signatures:
       - evaluation_results = critic_agent.evaluate(thread_id, evaluation=Optional[None])
       - evaluation_results = critic_agent.evaluate(agent_id, azure_ai_project=Optional[str], evaluation=Optional[IntentResolution, ToolCallAccuracy, TaskAdherence])

    The data fetching from agent_id automates the code pattern from Azure AI Foundry agent evaluation samples.
    """

    _PROMPTY_FILE = "_critic_agent.prompty"
    _RESULT_KEY = "evaluator_selector"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    # Default agent evaluation metrics
    _DEFAULT_AGENT_EVALUATORS = ["IntentResolution", "ToolCallAccuracy", "TaskAdherence"]

    id = None
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, model_config, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY, **kwargs)
        self.model_config = model_config
        self.evaluator_instances = self._initialize_evaluators(self._DEFAULT_AGENT_EVALUATORS)

    def evaluate(self,
                 identifier: str,
                 azure_ai_project: Optional[Dict[str, str]] = None,
                 evaluation: Optional[Union[str, List[str]]] = None,
                 **kwargs) -> Dict[str, Any]:
        """
        Evaluate an agent using the specified evaluators.

        :param identifier: Either thread_id for conversation-based evaluation or agent_id for agent-based evaluation
        :type identifier: str
        :param azure_ai_project: Azure AI project configuration containing subscription_id, resource_group_name, project_name
        :type azure_ai_project: Optional[Dict[str, str]]
        :param evaluation: Specific evaluators to run. If None, runs default agent evaluators when azure_ai_project is provided
        :type evaluation: Optional[Union[str, List[str]]]
        :return: Evaluation results
        :rtype: Dict[str, Any]
        """
        # Todo: This needs to be fixed
        if identifier.startswith("thread_") or identifier.startswith("thread-"):
            # Agent-based evaluation with data fetching
            return self._evaluate_conversation(identifier, azure_ai_project, evaluation, **kwargs)
        else:
            # Thread/conversation-based evaluation
            return self._evaluate_agent(identifier, azure_ai_project, evaluation, **kwargs)


    def _evaluate_agent(self,
                        agent_id: str,
                        azure_ai_project: Dict[str, str],
                        evaluation: Optional[Union[str, List[str]]] = None,
                        **kwargs) -> List[Any]:
        """
        Evaluate an agent by fetching data from Azure AI Project and running specified evaluators.

        :param agent_id: The ID of the agent to evaluate
        :type agent_id: str
        :param azure_ai_project: Azure AI project configuration
        :type azure_ai_project: Dict[str, str]
        :param evaluation: Specific evaluators to run
        :type evaluation: Optional[Union[str, List[str]]]
        :return: Evaluation results
        :rtype: Dict[str, Any]
        """
        try:

            project_client = AIProjectClient(
                endpoint=azure_ai_project.get("azure_endpoint"),
                credential=DefaultAzureCredential(),
            )

            thread_ids = self._fetch_agent_threads(project_client, agent_id)
            results = []
            for thread_id in thread_ids:
                evaluated_result = self._evaluate_conversation(
                    thread_id=thread_id,
                    azure_ai_project=azure_ai_project,
                    evaluation=evaluation,
                    agent_id=agent_id,
                    **kwargs
                )
                if evaluated_result is not None:
                    results.append(evaluated_result)

            return results

        except Exception as e:
            logger.error(f"Error during agent evaluation: {str(e)}")
            raise EvaluationException(
                message=f"Failed to evaluate agent {agent_id}: {str(e)}",
                internal_message=f"Agent evaluation failed: {str(e)}",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                # target=ErrorTarget.CRITIC_AGENT,
            )

    def _evaluate_conversation(self,
                               thread_id: str,
                               azure_ai_project: Optional[Dict[str, str]] = None,
                               evaluation: Optional[Union[str, List[str]]] = None,
                                agent_id: Optional[str] = None,
                               **kwargs) -> Dict[str, Any]:
        """
        Evaluate a specific conversation thread.

        :param thread_id: The ID of the conversation thread
        :type thread_id: str
        :param evaluation: Specific evaluators to run
        :type evaluation: Optional[Union[str, List[str]]]
        :return: Evaluation results
        :rtype: Dict[str, Any]
        """
        # This would integrate with the existing async _do_eval method
        # For conversation-based evaluation using the prompty
        if not thread_id:
            raise EvaluationException(
                message="Thread ID must be provided for conversation evaluation.",
                internal_message="Missing thread ID in input.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.CRITIC_AGENT,
            )
        project_client = AIProjectClient(
            endpoint=azure_ai_project.get("azure_endpoint"),
            credential=DefaultAzureCredential(),
        )

        converter = AIAgentConverter(project_client)
        conversation = converter.prepare_evaluation_data(thread_ids=thread_id)[-1]
        # {'query': [
        #     {'createdAt': '2025-07-17T08:56:22Z', 'role': 'user', 'content': [{'type': 'text', 'text': "hey there'"}]},
        #     {'createdAt': '2025-07-17T08:56:23Z', 'run_id': 'run_MVHZIe0TNWWKPx0ppvUz3uAh',
        #      'assistant_id': 'asst_CLx2RNAXhAoFIbkLxZfoM6P4', 'role': 'assistant',
        #      'content': [{'type': 'text', 'text': 'Hey there! How can I help you today? 😊'}]},
        #     {'createdAt': '2025-07-17T08:56:29Z', 'role': 'user',
        #      'content': [{'type': 'text', 'text': 'How are you'}]}], 'response': [
        #     {'createdAt': '2025-07-17T08:56:31Z', 'run_id': 'run_vZU2pZ4a4QzxYB1tLoei7ycB',
        #      'assistant_id': 'asst_CLx2RNAXhAoFIbkLxZfoM6P4', 'role': 'assistant', 'content': [{'type': 'text',
        #                                                                                         'text': 'Thanks for asking! I’m just a bunch of code, but I’m here and ready to help you. How are you doing?'}]}],
        #  'tool_definitions': []}
        # Filter conversations if belongs to a specific agent
        if agent_id and conversation["response"][0]["assistant_id"] != agent_id:
            logger.info(f"Skipping conversation {thread_id} for agent {agent_id}.")
            return None


        evaluators_to_run = asyncio.run(self._select_evaluators(conversation))
        evaluator_instances = {name: self.evaluator_instances[name] for name in evaluators_to_run["evaluators"]}
        conversation_results = self._run_evaluators_on_conversation(
            evaluator_instances, conversation
        )
        return {
            "thread_id": thread_id,
            "results": conversation_results,
            "justification": evaluators_to_run.get("justification", ""),
            "distinct_assessments": evaluators_to_run.get("distinct_assessments", {})
        }

    def _fetch_agent_threads(self, project_client: Any, agent_id: str) -> List:
        """
        Fetch conversation data for an agent from Azure AI Project.
        This implements the pattern from the Azure AI samples for agent evaluation.

        :param project_client: The AI Project client
        :type project_client: AIProjectClient
        :param agent_id: The agent ID
        :type agent_id: str
        :return: List of thread IDs for the agent
        :rtype: List[str]
        """
        try:

            threads = project_client.agents.threads.list()
            # threads = project_client.agents.threads.list(agent_id=agent_id)

            thread_ids = []
            # threads = ["thread_oDhHDz6HgjTqSLE8FVJy6Ord"]
            for thread in threads:

                print(thread)
                thread_ids.append(thread.id)
                # Convert to evaluation format
            return thread_ids

        except Exception as e:
            logger.error(f"Error fetching agent threads: {str(e)}")
            raise

    def _initialize_evaluators(self, evaluator_names: List[str]) -> Dict[str, Any]:
        """
        Initialize the specified evaluators.

        :param evaluator_names: List of evaluator names to initialize
        :type evaluator_names: List[str]
        :return: Dictionary of initialized evaluators
        :rtype: Dict[str, Any]
        """
        evaluators = {}

        for name in evaluator_names:
            if name == "IntentResolution":
                evaluators[name] = IntentResolutionEvaluator(model_config=self.model_config)
            elif name == "ToolCallAccuracy":
                evaluators[name] = ToolCallAccuracyEvaluator(model_config=self.model_config)
            elif name == "TaskAdherence":
                evaluators[name] = TaskAdherenceEvaluator(model_config=self.model_config)
            else:
                logger.warning(f"Unknown evaluator: {name}")

        return evaluators

    def _run_evaluators_on_conversation(self,
                                        evaluators: Dict[str, Any],
                                        conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run multiple evaluators on a conversation in parallel.

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

    async def _select_evaluators(self, eval_input: Dict[str, Any]):
        """
        Select appropriate evaluators based on the conversation history and tool definitions.

        :param eval_input: Input dictionary containing conversation history and tool definitions
        :type eval_input: Dict[str, Any]
        """
        # This would use the prompty to select evaluators
        eval_input["query"] = reformat_conversation_history(eval_input["query"], logger)
        eval_input["response"] = reformat_agent_response(eval_input["response"], logger)
        tool_definitions = eval_input.get("tool_definitions", None)
        if tool_definitions:
            eval_input["tool_definitions"] = reformat_tool_definitions(tool_definitions, logger)

        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        if isinstance(llm_output, dict):
            evaluators = llm_output.get("evaluators", [])
            evaluators = [evaluator for evaluator in evaluators if evaluator in self._DEFAULT_AGENT_EVALUATORS]
            return {
                "evaluators": evaluators,
                "justification": llm_output.get("justification", ""),
                "distinct_assessments": llm_output.get("distinct_assessments", {}),
            }
        if logger:
            logger.warning("LLM output is not a dictionary, returning empty result.")
        return {"evaluators": [], "justification": "", "distinct_assessments": {}}

    # async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[str, List[str]]]:
    #     """Perform evaluator selection based on the provided inputs."""
    #     if "conversation_history" not in eval_input:
    #         raise EvaluationException(
    #             message="Conversation history must be provided as input to the CriticAgent.",
    #             internal_message="Missing conversation history in input.",
    #             blame=ErrorBlame.USER_ERROR,
    #             category=ErrorCategory.MISSING_FIELD,
    #             # target=ErrorTarget.CRITIC_AGENT,
    #         )
    #     eval_input["conversation_history"] = reformat_conversation_history(eval_input["conversation_history"], logger)
    #     if "tool_definitions" in eval_input and eval_input["tool_definitions"] is not None:
    #         eval_input["tool_definitions"] = reformat_tool_definitions(eval_input["tool_definitions"], logger)
    #     llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
    #     if isinstance(llm_output, dict):
    #         return {
    #             "evaluators": llm_output.get("evaluators", []),
    #             "justification": llm_output.get("justification", ""),
    #             "distinct_assessments": llm_output.get("distinct_assessments", {}),
    #         }
    #     if logger:
    #         logger.warning("LLM output is not a dictionary, returning empty result.")
    #     return {"evaluators": [], "justification": "", "distinct_assessments": {}}
