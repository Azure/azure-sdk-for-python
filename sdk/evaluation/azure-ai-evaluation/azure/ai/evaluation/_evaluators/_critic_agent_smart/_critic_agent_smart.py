import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import json

from azure.ai.evaluation._evaluate._evaluate import evaluate as _batch_evaluate

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._exceptions import (
    EvaluationException,
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
)
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._common.utils import (
    reformat_conversation_history,
    reformat_tool_definitions,
    reformat_agent_response,
)

# Import evaluator implementations
from azure.ai.evaluation._evaluators._intent_resolution import IntentResolutionEvaluator
from azure.ai.evaluation._evaluators._tool_call_accuracy import ToolCallAccuracyEvaluator
from azure.ai.evaluation._evaluators._task_adherence import TaskAdherenceEvaluator
from azure.ai.evaluation._evaluators._coherence import CoherenceEvaluator
from azure.ai.evaluation._evaluators._fluency import FluencyEvaluator
from azure.ai.evaluation._evaluators._relevance import RelevanceEvaluator


try:  # Azure project dependencies
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from azure.ai.evaluation._converters._ai_services import AIAgentConverter
except ImportError as e:  # pragma: no cover - environment dependency
    raise EvaluationException(
        message=f"Required Azure packages missing: {e}",
        internal_message="Missing azure-identity or azure-ai-projects for CriticAgentSmartEvaluator.",
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.MISSING_FIELD,
        target=ErrorTarget.CRITIC_AGENT,
    )

logger = logging.getLogger(__name__)


class _EvaluatorSelector(PromptyEvaluatorBase[Dict[str, Union[str, List[str]]]]):
    """Lightweight prompty-based selector replicating logic from critic_agent_2 without importing it."""
    _PROMPTY_FILE = "_critic_agent.prompty"
    _RESULT_KEY = "evaluator_selector"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    def __init__(self, model_config, **kwargs):  # noqa: D401
        prompty_path = os.path.join(os.path.dirname(__file__),  # _evaluators
            self._PROMPTY_FILE,
        )
        print(f"Prompty file loaded from: {prompty_path}")
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY, **kwargs)

    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[str, List[str]]]:  # type: ignore[override]
        eval_input["query"] = reformat_conversation_history(eval_input["query"], logger)
        eval_input["response"] = reformat_agent_response(eval_input["response"], logger)
        if eval_input.get("tool_definitions"):
            eval_input["tool_definitions"] = reformat_tool_definitions(eval_input["tool_definitions"], logger)
        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        if isinstance(llm_output, dict):
            return {
                "evaluators": llm_output.get("evaluators", []),
                "justification": llm_output.get("justification", ""),
                "distinct_assessments": llm_output.get("distinct_assessments", {}),
            }
        logger.warning("Evaluator selector LLM output not dict; returning empty selection.")
        return {"evaluators": [], "justification": "", "distinct_assessments": {}}


@experimental
class CriticAgentSmartEvaluator:
    """Aggregates multi-thread / agent evaluation using the CriticAgent.

    This class acts as a convenience *evaluator-style* wrapper that can be invoked with either:
        - an `agent_id` (all / first N threads will be fetched from the Azure AI Project)
        - an explicit list of `thread_ids`.

    For every thread, it reuses the CriticAgent's evaluator selection logic (when `evaluators` not supplied)
    and returns a consolidated structure similar to `CriticAgent.auto_evaluate` but packaged as a single call.

    Parameters
    ----------
    model_config: Any
        The model configuration passed through to the underlying `CriticAgent` and per-metric evaluators.
    max_threads: int, optional
        Maximum number of threads to fetch when `agent_id` is supplied (default 100).
    parallelism: int, optional
        Max number of threads to evaluate concurrently (default 8).
    credential: TokenCredential, optional
        (Reserved) Provided for future parity with other evaluators; currently the underlying CriticAgent
        constructs its own DefaultAzureCredential when needed.
    """

    # Not a PromptyEvaluatorBase subclass because it is an orchestration wrapper; individual metric
    # evaluators already follow the Prompty pattern. We still decorate with @experimental for parity.

    _DEFAULT_AGENT_EVALUATORS = ["IntentResolution", "ToolCallAccuracy", "TaskAdherence", "Coherence", "Fluency", "Relevance"]

    def __init__(
        self,
        model_config: Any,
        *,
        max_threads: int = 10,
        parallelism: int = 8,
        credential: Any = None,  # reserved for parity
        **selector_kwargs,
    ) -> None:
        self.model_config = model_config
        self.max_threads = max_threads
        self.parallelism = parallelism
        self._selector = _EvaluatorSelector(model_config=model_config, **selector_kwargs)
        # Preload default evaluator instances
        self.evaluator_instances = self._initialize_evaluators(self._DEFAULT_AGENT_EVALUATORS)

    # Public call interface to mimic other evaluator usage patterns
    def __call__(
        self,
        *,
        agent_id: Optional[str] = None,
        thread_ids: Optional[List[str]] = None,
        azure_ai_project: Optional[Dict[str, str]] = None,
        evaluators: Optional[Union[str, List[str]]] = None,
        max_threads: Optional[int] = None,
        parallelism: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute evaluation.

        One (and only one) of `agent_id` or `thread_ids` must be provided.

        Parameters
        ----------
        agent_id: str, optional
            Agent identifier to fetch recent threads from.
        thread_ids: List[str], optional
            Explicit thread identifiers to evaluate.
        azure_ai_project: Dict[str,str], optional
            Contains at minimum 'azure_endpoint'.
        evaluators: Union[str, List[str]], optional
            If provided, forces these evaluator names to be used for all threads (skips selector logic).
        max_threads: int, optional
            Override instance default for max fetched threads (only relevant with agent_id).
        parallelism: int, optional
            Override instance default concurrency level.
        kwargs: dict
            Additional passthrough arguments to underlying CriticAgent per-thread invocation.
        Returns
        -------
        Dict[str,Any]
            Aggregated evaluation result.
        """
        if not agent_id and not thread_ids:
            raise EvaluationException(
                message="Either agent_id or thread_ids must be provided.",
                internal_message="CriticAgentSmartEvaluator missing agent_id/thread_ids.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.CRITIC_AGENT,
            )
        if agent_id and thread_ids:
            logger.warning("Both agent_id and thread_ids supplied; using explicit thread_ids and ignoring agent_id.")

        max_threads = max_threads if max_threads is not None else self.max_threads
        parallelism = parallelism if parallelism is not None else self.parallelism

        # Resolve thread ids
        resolved_thread_ids: List[str]
        if thread_ids:
            resolved_thread_ids = thread_ids
        else:
            if not azure_ai_project:
                raise EvaluationException(
                    message="azure_ai_project config required when agent_id is used.",
                    internal_message="Missing azure_ai_project while resolving agent threads.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.MISSING_FIELD,
                    target=ErrorTarget.CRITIC_AGENT,
                )
            project_client = AIProjectClient(
                endpoint=azure_ai_project.get("azure_endpoint"),
                credential=DefaultAzureCredential(),
            )
            resolved_thread_ids = self._fetch_agent_threads(project_client, agent_id, max_threads=max_threads)

        # Ensure evaluator instances if explicit list provided
        if evaluators:
            if isinstance(evaluators, str):
                evaluators = [evaluators]
            missing = [e for e in evaluators if e not in self.evaluator_instances]
            if missing:
                self.evaluator_instances.update(self._initialize_evaluators(missing))

        evaluations: List[Dict[str, Any]] = []
        thread_errors: Dict[str, str] = {}

        def _evaluate_single(tid: str):
            try:
                return self._evaluate_conversation(
                    thread_id=tid,
                    azure_ai_project=azure_ai_project,
                    evaluators_to_run=evaluators,
                    agent_id=agent_id,
                    **kwargs,
                )
            except Exception as ex:  # capture and continue
                thread_errors[tid] = str(ex)
                logger.error("Failed evaluating thread %s: %s", tid, ex)
                return None

        # Parallel evaluation of threads
        with ThreadPoolExecutor(max_workers=parallelism) as executor:
            future_map = {executor.submit(_evaluate_single, tid): tid for tid in resolved_thread_ids}
            for fut in as_completed(future_map):
                res = fut.result()
                if res:
                    evaluations.append(res)

        return {
            "agent_id": agent_id,
            "thread_ids": resolved_thread_ids,
            "evaluation_count": len(evaluations),
            "evaluations": evaluations,
            "thread_errors": thread_errors,
        }

    # Lightweight thread fetch
    def _fetch_agent_threads(self, project_client: Any, agent_id: str, max_threads: int) -> List[str]:  # pragma: no cover - network
        try:
            threads = project_client.agents.threads.list()
            ids: List[str] = []
            for th in threads:
                if len(ids) >= max_threads:
                    break
                ids.append(th.id)
            logger.info("Fetched %d threads for agent %s", len(ids), agent_id)
            return ids
        except Exception as e:
            logger.error("Error fetching threads for agent %s: %s", agent_id, e)
            raise EvaluationException(
                message=f"Failed to fetch threads for agent {agent_id}: {e}",
                internal_message="Agent thread fetch failed in CriticAgentSmartEvaluator.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.CRITIC_AGENT,
            )

    def _initialize_evaluators(self, evaluator_names: List[str]) -> Dict[str, Any]:
        evaluators: Dict[str, Any] = {}
        for name in evaluator_names:
            if name == "IntentResolution":
                evaluators[name] = IntentResolutionEvaluator(model_config=self.model_config)
            elif name == "ToolCallAccuracy":
                evaluators[name] = ToolCallAccuracyEvaluator(model_config=self.model_config)
            elif name == "TaskAdherence":
                evaluators[name] = TaskAdherenceEvaluator(model_config=self.model_config)
            elif name == "Coherence":
                evaluators[name] = CoherenceEvaluator(model_config=self.model_config)
            elif name == "Fluency":
                evaluators[name] = FluencyEvaluator(model_config=self.model_config)
            elif name == "Relevance":
                evaluators[name] = RelevanceEvaluator(model_config=self.model_config)
            else:
                logger.debug("Evaluator %s not available or unknown.", name)
        return evaluators

    def _evaluate_conversation(
        self,
        *,
        thread_id: str,
        azure_ai_project: Optional[Dict[str, str]],
        evaluators_to_run: Optional[Union[str, List[str]]],
        agent_id: Optional[str] = None,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        if not thread_id:
            raise EvaluationException(
                message="thread_id required for conversation evaluation.",
                internal_message="Missing thread_id in _evaluate_conversation.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.CRITIC_AGENT,
            )
        project_client = AIProjectClient(
            endpoint=azure_ai_project.get("azure_endpoint") if azure_ai_project else None,
            credential=DefaultAzureCredential(),
        )
        converter = AIAgentConverter(project_client)
        try:
            conversation = converter.prepare_evaluation_data(thread_ids=thread_id)[-1]
        except Exception as e:  # pragma: no cover - network variability
            logger.error("Failed fetching conversation for thread %s: %s", thread_id, e)
            return None

        # Filter by agent if provided
        try:
            if agent_id and conversation.get("response", [{}])[0].get("assistant_id") != agent_id:
                logger.info("Skipping thread %s not matching agent %s", thread_id, agent_id)
                return None
        except Exception:  # pragma: no cover
            pass

        result: Dict[str, Any] = {"thread_id": thread_id, "conversation": conversation}

        if not evaluators_to_run:
            # Run selection prompty
            selection_input = {
                "query": conversation.get("query", []),
                "response": conversation.get("response", []),
                "tool_definitions": conversation.get("tool_definitions", []),
            }
            if not asyncio.get_event_loop().is_running():
                selection = asyncio.run(self._selector._do_eval(selection_input))  # pylint: disable=protected-access
            else:
                selection = asyncio.get_event_loop().run_until_complete(
                    self._selector._do_eval(selection_input)  # pylint: disable=protected-access
                )
            available = self._DEFAULT_AGENT_EVALUATORS
            chosen = [e for e in selection.get("evaluators", []) if e in available] or self._DEFAULT_AGENT_EVALUATORS
            evaluators_to_run = chosen
            result["justification"] = selection.get("justification", "")
            result["distinct_assessments"] = selection.get("distinct_assessments", {})
        elif isinstance(evaluators_to_run, str):
            evaluators_to_run = [evaluators_to_run]

        # Build evaluator instance subset
        evaluator_instances = {n: self.evaluator_instances[n] for n in evaluators_to_run if n in self.evaluator_instances}
        # Add any missing (lazy load)
        missing = [n for n in evaluators_to_run if n not in evaluator_instances]
        if missing:
            evaluator_instances.update(self._initialize_evaluators(missing))
            self.evaluator_instances.update(evaluator_instances)
        endpoint = azure_ai_project.get("azure_endpoint") if azure_ai_project else None
        conversation_results = self._run_evaluators_on_conversation(evaluator_instances, conversation, project_endpoint=endpoint)
        result["results"] = conversation_results
        return result

    def _run_evaluators_on_conversation(self, evaluators: Dict[str, Any], conversation: Dict[str, Any], project_endpoint: str) -> Dict[str, Any]:
        """Use unified evaluate() pipeline for a single conversation.

        We serialize the conversation to a one-row JSONL dataset containing columns matching
        evaluator __call__ argument names (query, response, tool_definitions). Then invoke the
        shared evaluate() function with the evaluator mapping. Finally, we extract per-evaluator
        outputs from the result row and normalize into the expected structure.
        """
        row = {
            "query": conversation.get("query", []),
            "response": conversation.get("response", []),
            "tool_definitions": conversation.get("tool_definitions", []),
        }
        # Create temp JSONL
        tmp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        try:
            tmp_file.write(json.dumps(row))
            tmp_file.write("\n")
            tmp_file.flush()
            tmp_path = tmp_file.name
        finally:
            tmp_file.close()

        # Prepare evaluators mapping (alias -> callable)
        evaluators_mapping = {name: inst for name, inst in evaluators.items()}
        try:
            eval_result = _batch_evaluate(data=tmp_path, evaluators=evaluators_mapping, azure_ai_project=project_endpoint)
        except Exception as e:  # pragma: no cover
            logger.error("Unified evaluate() failed for conversation: %s", e)
            return {name: {"error": str(e)} for name in evaluators_mapping.keys()}
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:  # pragma: no cover
                pass

        # Extract first row outputs
        rows = eval_result.get("rows", []) if isinstance(eval_result, dict) else []
        if not rows:
            return {}
        result_row = rows[0]
        # Keys in row: inputs.<col> and outputs.<EvaluatorName>.<metric>
        per_evaluator: Dict[str, Dict[str, Any]] = {}
        for key, value in result_row.items():
            if not isinstance(key, str) or not key.startswith("outputs."):
                continue
            # outputs.<Evaluator>.<metric>
            parts = key.split(".")
            if len(parts) < 3:
                continue
            _, eval_name, metric_name = parts[0], parts[1], ".".join(parts[2:])
            per_evaluator.setdefault(eval_name, {})[metric_name] = value
        return per_evaluator

