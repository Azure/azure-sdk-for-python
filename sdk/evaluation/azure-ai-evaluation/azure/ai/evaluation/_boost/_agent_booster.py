import random
from typing import Callable, List, Dict, Any, Optional, Union
import json
import os
import tempfile
from datetime import datetime

from azure.ai.projects import AIProjectClient

from azure.ai.evaluation import (
    evaluate,
    EvaluationResult,
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)
from azure.ai.evaluation._converters._ai_services import AIAgentConverter
from azure.ai.evaluation._constants import DEFAULT_AOAI_API_VERSION, experimental
from azure.ai.evaluation._user_agent import UserAgentSingleton
from azure.ai.evaluation._aoai.aoai_grader import AzureOpenAIGrader

from openai import AzureOpenAI, OpenAI

from ._models import _EvaluationCase
from ._configuration import (
    _AgentBoosterConfig,
    _PromptConfiguration,
)
from ._utils import _CritiqueGenerator, _PromptImprover


@experimental
class _AgentBooster:
    """
    Comprehensive system for iterative prompt refinement using evaluation feedback.

    Features a streamlined human-in-the-loop workflow:
    1. Human specifies improvement intent in configuration (optional)
    2. AI analyzes evaluation results and generates targeted improvements
    3. Human reviews and approves final changes (optional)

    Data File Format:
    The refine() method expects a JSONL file where each line contains a JSON object with a "query" field:
    ```
    {"query": "What is the weather like today?"}
    {"query": "How do I reset my password?"}
    {"query": "Tell me about your capabilities"}
    ```

    Example usage:
    ```python
    booster = _AgentBooster(
        project_client=client,
        model_config=config,
        agent_id="agent_123",
        improvement_intent="Make responses more concise and technical",
        output_dir="/path/to/output",  # Optional: defaults to temp directory
    )

    # Run refinement with a JSONL file containing queries
    results = booster.refine("queries.jsonl")
    ```
    """

    def __init__(
        self,
        project_client: AIProjectClient,
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
        agent_id: str,
        evaluators: Optional[Dict[str, Union[Callable, AzureOpenAIGrader]]] = None,
        sample_size: int = 10,
        max_iterations: int = 3,
        improvement_intent: Optional[str] = None,
        output_dir: Optional[str] = None,
        # improvement_threshold: float = 0.1,
        # early_stopping: bool = True,
        verbose: bool = False,
    ):
        self._verbose = verbose

        # Initialize Azure AI Project client
        self._project_client = project_client
        self._model_config = model_config
        self._agent = self._project_client.agents.get_agent(agent_id)

        self._config: _AgentBoosterConfig = _AgentBoosterConfig(
            model_config=self._model_config,
            sample_size=sample_size,
            max_iterations=max_iterations,
            improvement_intent=improvement_intent,
        )

        # Set evaluators, defaulting to built-in ones if not provided
        self._evaluators = evaluators or self._get_default_evaluators()

        # Set output directory for refinement history
        self._output_dir = output_dir or tempfile.gettempdir()
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir, exist_ok=True)

        # Initialize critique generator and prompt improver with client factory
        self._openai_client = self._get_client()
        self._critique_generator = _CritiqueGenerator(self._openai_client, self._model_config)
        self._prompt_improver = _PromptImprover(self._openai_client, self._model_config)

        # Initialize refinement tracking
        self.refinement_history = []
        self.current_iteration = 0
        self.best_scores = {}
        self.best_iteration = 0

    def _generate_refinement_history_filename(self) -> str:
        """Generate a unique filename for refinement history with timestamp.

        :return: Full path to the refinement history file.
        :rtype: str
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        agent_id_safe = self._agent.id.replace("/", "_").replace(":", "_")
        filename = f"refinement_history_{agent_id_safe}_{timestamp}.json"
        return os.path.join(self._output_dir, filename)

    def _save_refinement_history(self, custom_filename: Optional[str] = None) -> str:
        """Save refinement history to a JSON file.

        :param custom_filename: Optional custom filename. If None, generates timestamp-based name.
        :type custom_filename: Optional[str]
        :return: Path to the saved file.
        :rtype: str
        """
        if custom_filename:
            output_path = os.path.join(self._output_dir, custom_filename)
        else:
            output_path = self._generate_refinement_history_filename()

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the file
        with open(output_path, "w") as f:
            json.dump(self.refinement_history, f, indent=2)

        if self._verbose:
            print(f"Refinement history saved to: {output_path}")

        return output_path

    def refine(
        self,
        data_file: str,
        max_iterations: Optional[int] = None,
        output_filename: Optional[str] = None,
        # improvement_threshold: Optional[float] = None,
        # early_stopping: Optional[bool] = None,
    ) -> Dict:
        """
        Run the complete iterative refinement process.

        The refinement history will be saved to a unique timestamped JSON file.

        :param data_file: Path to the JSONL file containing queries for refinement.
            Each line should be a valid JSON object with a "query" field containing the user query string.
            Example format:
            {"query": "What is the weather like today?"}
            {"query": "How do I reset my password?"}
            {"query": "Tell me about your capabilities"}
        :type data_file: str
        :param max_iterations: Maximum number of refinement iterations. If None, uses config value.
        :type max_iterations: Optional[int]
        :param output_filename: Optional custom filename for the refinement history.
        :type output_filename: Optional[str]
        :return: Dictionary containing refinement results and history file path.
        :rtype: Dict
        """
        # Use config values or method parameters
        max_iterations = max_iterations or self._config["max_iterations"]

        # TODO: Implement early stopping logic
        # improvement_threshold = (
        #     improvement_threshold or self._config["improvement_threshold"]
        # )
        # early_stopping = (
        #     early_stopping
        #     if early_stopping is not None
        #     else self._config["early_stopping"]
        # )

        self.refinement_history = []
        self.current_iteration = 0
        self.best_scores = {}
        self.best_iteration = 0

        current_prompt_config = _PromptConfiguration(
            system_prompt=self._agent.instructions,
            tools=[],  # TODO: Add logic to handle tools configuration
        )

        if self._verbose:
            print(f"Starting refinement with {max_iterations} max iterations")
            # print(f"Improvement threshold: {improvement_threshold}")
            print(f"Initial prompt: {current_prompt_config['system_prompt'][:100]}...")

        queries = self._load_queries(data_file)

        # Run iterations
        for iteration in range(max_iterations):
            # Sample queries
            sampled_queries = random.sample(queries, min(len(queries), self._config["sample_size"]))

            # Run single iteration
            iteration_result = self._run_single_iteration(
                prompt_config=current_prompt_config,
                queries=sampled_queries,
            )

            current_prompt_config = self._boost(
                iteration_result=iteration_result,
                prompt_config=current_prompt_config,
            )

            if self._verbose:
                print(f"Iteration {iteration + 1} completed")

            self.refinement_history.append(
                {
                    "iteration": iteration + 1,
                    "prompt_config": current_prompt_config,
                    "results": iteration_result,
                }
            )

        # Save refinement history using the robust atomic write method
        history_file_path = self._save_refinement_history(output_filename)

        if self._verbose:
            print(f"Refinement process completed. History saved to {history_file_path}")

        return {
            "final_prompt_config": current_prompt_config,
            "refinement_history": self.refinement_history,
            "best_iteration": self.best_iteration,
            "best_scores": self.best_scores,
            "history_file_path": history_file_path,
        }

    def boost(self, iteration_result: EvaluationResult) -> _PromptConfiguration:
        """Boost the agent based on the evaluation results.

        This method implements the logic to improve the prompt configuration.

        :param iteration_result: Results from evaluation containing scores and conversation data.
        :type iteration_result: EvaluationResult
        :return: Improved prompt configuration.
        :rtype: _PromptConfiguration
        :raises ValueError: If iteration_result is empty.
        """
        current_prompt_config = _PromptConfiguration(
            system_prompt=self._agent.instructions,
            tools=[],
        )

        new_prompt_config = self._boost(iteration_result, current_prompt_config)

        return new_prompt_config

    def _load_queries(self, data_file: str) -> List[str]:
        """Load queries from the provided data file as a JSONL file.

        Expected file format: Each line should contain a JSON object with a "query" field.
        Example content:
        {"query": "What is the weather like today?"}
        {"query": "How do I reset my password?"}
        {"query": "Tell me about your capabilities"}

        Lines that cannot be parsed as JSON will be skipped with a warning if verbose mode is enabled.

        :param data_file: Path to the JSONL file containing queries.
        :type data_file: str
        :return: List of queries loaded from the file.
        :rtype: List[str]
        :raises FileNotFoundError: If the data file does not exist.
        """
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file not found: {data_file}")

        queries = []
        with open(data_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    queries.append(data.get("query", ""))
                except json.JSONDecodeError:
                    if self._verbose:
                        print(f"Skipping invalid line: {line.strip()}")

        return queries

    def _generate_responses(self, queries: List[str], prompt_config: _PromptConfiguration) -> str:
        """Generate responses for the given queries using the current prompt configuration.

        :param queries: List of queries to generate responses for.
        :type queries: List[str]
        :param prompt_config: Current prompt configuration to use for generation.
        :type prompt_config: _PromptConfiguration
        :return: Path to the temporary file containing generated responses.
        :rtype: str
        """
        if self._verbose:
            print(f"Generating responses for {len(queries)} queries")

        thread_ids: List[str] = []

        for query in queries:
            thread = self._project_client.agents.threads.create()
            self._project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=query,
            )

            run = self._project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self._agent.id,
                instructions=prompt_config["system_prompt"],
            )

            if run.status == "failed":
                if self._verbose:
                    print(f"Run failed: {run.last_error}")
                continue

            thread_ids.append(thread.id)

        converter = AIAgentConverter(self._project_client)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as temp_file:
            converter.prepare_evaluation_data(thread_ids=thread_ids, filename=temp_file.name)  # type: ignore

        return temp_file.name

    def _get_default_evaluators(self) -> Dict:
        """Get default evaluators for evaluation.

        Default evaluators include:
        - IntentResolutionEvaluator: Evaluates how well the agent resolves user intents
        - ToolCallAccuracyEvaluator: Evaluates the accuracy of tool calls made by the agent

        :return: Dictionary of evaluator names to evaluator instances.
        :rtype: Dict
        """
        from azure.ai.evaluation import (
            IntentResolutionEvaluator,
            ToolCallAccuracyEvaluator,
        )

        default_evaluators = [IntentResolutionEvaluator, ToolCallAccuracyEvaluator]
        return {evaluator.__name__: evaluator(model_config=self._model_config) for evaluator in default_evaluators}

    def _evaluate_responses(self, response_file_path: str):
        """Evaluate the generated responses using the provided evaluators.

        :param response_file_path: Path to the file containing generated responses.
        :type response_file_path: str
        :return: Evaluation results.
        :rtype: EvaluationResult
        """
        if not os.path.exists(response_file_path):
            raise FileNotFoundError(f"Response file not found: {response_file_path}")

        # Run evaluations
        results = evaluate(data=response_file_path, evaluators=self._evaluators)

        return results

    def _boost(self, iteration_result: EvaluationResult, prompt_config: _PromptConfiguration) -> _PromptConfiguration:
        """Analyze evaluation results and return an improved prompt configuration.

        :param iteration_result: Results from evaluation containing scores and conversation data.
        :type iteration_result: EvaluationResult
        :param prompt_config: Current prompt configuration.
        :type prompt_config: _PromptConfiguration
        :return: Improved prompt configuration.
        :rtype: _PromptConfiguration
        """
        # Extract evaluation cases from results
        cases = self._extract_evaluation_cases(iteration_result)

        if not cases:
            if self._verbose:
                print("No evaluation cases found. Returning original prompt configuration.")
            return prompt_config

        # Generate and process critiques
        system_prompt = prompt_config["system_prompt"]
        tools = prompt_config["tools"]

        critiques = self._generate_critiques(cases, system_prompt, tools)

        if not critiques:
            if self._verbose:
                print("No critiques generated. Returning original prompt configuration.")
            return prompt_config

        # Create improved prompt using human intent and evaluation data
        improved_prompt = self._create_improved_prompt(system_prompt, critiques, tools)

        # Return new configuration with improved prompt
        new_config = _PromptConfiguration(system_prompt=improved_prompt, tools=tools)

        # Print summary
        if self._verbose:
            self._print_boost_summary(cases, critiques, system_prompt, improved_prompt, tools)

        return new_config

    def _extract_evaluation_cases(self, eval_results: EvaluationResult) -> List[_EvaluationCase]:
        """Extract evaluation cases from results.

        :param eval_results: Evaluation results containing case data.
        :type eval_results: EvaluationResult
        :return: List of extracted evaluation cases.
        :rtype: List[_EvaluationCase]
        """
        cases = []

        for i, row in enumerate(eval_results.get("rows", [])):
            case_id = f"case_{i}"
            case = _EvaluationCase.from_row(row, case_id)

            if case.metrics:  # Only add cases with scores
                cases.append(case)

        return cases

    def _generate_critiques(
        self,
        cases: List[_EvaluationCase],
        system_prompt: str,
        tools: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate critiques for all cases.

        :param cases: List of evaluation cases to critique.
        :type cases: List[_EvaluationCase]
        :param system_prompt: Current system prompt text.
        :type system_prompt: str
        :param tools: List of tool configurations.
        :type tools: List[Dict[str, Any]]
        :return: List of generated critique messages.
        :rtype: List[str]
        """
        critiques = []

        for case in cases:
            critique = self._critique_generator.generate_critique(case, system_prompt, tools)
            critiques.append(critique)
            if self._verbose:
                print(f"Generated critique for {case.case_id}")

        return critiques

    def _create_improved_prompt(self, original_prompt: str, critiques: List[str], tools: List[Dict[str, Any]]) -> str:
        """Create improved prompt from critiques and optional human intent.

        :param original_prompt: The original prompt to improve.
        :type original_prompt: str
        :param critiques: List of critique messages.
        :type critiques: List[str]
        :param tools: List of tool configurations.
        :type tools: List[Dict[str, Any]]
        :return: Improved prompt text.
        :rtype: str
        """

        if self._verbose:
            print("Aggregating critiques into meta-critique...")
        meta_critique = self._critique_generator.aggregate_critiques(critiques)

        if self._verbose:
            print("Generating improved prompt...")

        # Include human intent in the improvement process
        improved = self._prompt_improver.improve_prompt(
            original_prompt,
            meta_critique,
            tools,
            self._config["improvement_intent"],
        )

        return improved

    def _print_boost_summary(
        self,
        cases: List[_EvaluationCase],
        critiques: List[str],
        original_prompt: str,
        improved_prompt: str,
        tools: List[Dict[str, Any]],
    ):
        """Print improvement summary.

        :param cases: List of evaluation cases processed.
        :type cases: List[_EvaluationCase]
        :param critiques: List of critique messages generated.
        :type critiques: List[str]
        :param original_prompt: The original prompt before improvement.
        :type original_prompt: str
        :param improved_prompt: The improved prompt after processing.
        :type improved_prompt: str
        :param tools: List of tool configurations.
        :type tools: List[Dict[str, Any]]
        """

        print("\n" + "=" * 50)
        print("BOOST SUMMARY")
        print("=" * 50)
        print(f"Processed {len(cases)} evaluation cases")
        print(f"Generated {len(critiques)} individual critiques")
        print("Generated meta-critique and improved prompt")
        if tools:
            print(f"Considered {len(tools)} tools in analysis")

        print("\nOriginal Prompt:")
        print("-" * 20)
        print(original_prompt)

        if tools:
            print(f"\nTools Configuration:")
            print("-" * 20)
            print(json.dumps(tools, indent=2))

        print("\nImproved Prompt:")
        print("-" * 20)
        print(improved_prompt)

    def _run_single_iteration(self, prompt_config: _PromptConfiguration, queries: List[str]):
        """Run a single iteration of evaluation and improvement.

        :param prompt_config: Current prompt configuration to use.
        :type prompt_config: _PromptConfiguration
        :param queries: List of queries to process.
        :type queries: List[str]
        :return: Evaluation results from this iteration.
        :rtype: EvaluationResult
        """
        response_file_path = self._generate_responses(queries, prompt_config)
        if self._verbose:
            print(f"Generated responses saved to: {response_file_path}")

        evaluation_results = self._evaluate_responses(response_file_path)
        if self._verbose:
            print(f"Evaluation results: {evaluation_results}")

        return evaluation_results

    def _get_client(self) -> Union[AzureOpenAI, OpenAI]:
        """Construct an appropriate OpenAI client using this grader's model configuration.
        Returns a slightly different client depending on whether or not this grader's model
        configuration is for Azure OpenAI or OpenAI.

        :return: The OpenAI client.
        :rtype: [~openai.OpenAI, ~openai.AzureOpenAI]
        """
        default_headers = {"User-Agent": UserAgentSingleton().value}
        if "azure_endpoint" in self._model_config:
            from openai import AzureOpenAI

            # TODO set default values?
            return AzureOpenAI(
                azure_endpoint=self._model_config["azure_endpoint"],
                api_key=self._model_config.get("api_key", None),  # Default-style access to appease linters.
                api_version=DEFAULT_AOAI_API_VERSION,  # Force a known working version
                azure_deployment=self._model_config.get("azure_deployment", ""),
                default_headers=default_headers,
            )
        from openai import OpenAI

        # TODO add default values for base_url and organization?
        return OpenAI(
            api_key=self._model_config["api_key"],
            base_url=self._model_config.get("base_url", ""),
            organization=self._model_config.get("organization", ""),
            default_headers=default_headers,
        )
