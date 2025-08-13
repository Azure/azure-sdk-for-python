import json
import os
import pathlib
import tempfile
import openai
import pytest
from devtools_testutils import is_live
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.evaluation._boost._agent_booster import _AgentBooster


@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestAgentBooster:
    @pytest.fixture
    def project_client(self, project_scope_onedp):
        """Create an AIProjectClient from project scope."""
        if is_live():
            return AIProjectClient(
                endpoint=project_scope_onedp,
                credential=DefaultAzureCredential(),
            )
        else:
            from unittest.mock import Mock

            mock_client = Mock(spec=AIProjectClient)

            # Create mock agents manager
            mock_agents = Mock()
            mock_client.agents = mock_agents

            # Create mock agent
            mock_agent = Mock()
            mock_agent.id = "test_agent"
            mock_agent.instructions = "You are a helpful assistant. Answer questions clearly and concisely."
            mock_agents.get_agent.return_value = mock_agent

            return mock_client

    @pytest.fixture
    def auto_cleanup_agent(self, project_client):
        """Create an agent and automatically delete it after the test is finished."""
        agent = None
        agent_id = None

        try:
            if is_live():
                # Create a real agent for live tests
                agent = project_client.agents.create_agent(
                    model="gpt-4o",
                    name="test-agent-auto-cleanup",
                    instructions="You are a helpful assistant. Answer questions clearly and concisely.",
                )
                agent_id = agent.id
                print(f"Created agent with ID: {agent_id}")
            else:
                # For recorded tests, create a mock agent
                from unittest.mock import Mock

                agent = Mock()
                agent.id = "test_agent_auto_cleanup"
                agent.instructions = "You are a helpful assistant. Answer questions clearly and concisely."
                agent_id = agent.id

            yield agent

        finally:
            # Cleanup: Delete the agent if it was created
            if agent_id and is_live():
                try:
                    project_client.agents.delete_agent(agent_id)
                    print(f"Deleted agent with ID: {agent_id}")
                except Exception as e:
                    print(f"Warning: Failed to delete agent {agent_id}: {e}")

    @pytest.fixture
    def test_queries_file(self):
        """Create a temporary JSONL file with test queries."""
        test_queries = [
            {"query": "What is the weather like today?"},
            {"query": "How do I reset my password?"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for query in test_queries:
                f.write(json.dumps(query) + "\n")
            temp_file_path = f.name

        yield temp_file_path

        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

    @pytest.fixture
    def static_test_queries_file(self):
        """Get path to static test queries file."""
        data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
        return os.path.join(data_path, "agent_booster_test_queries.jsonl")

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_initialization(self, model_config, project_client, auto_cleanup_agent):
        """Test that AgentBooster can be initialized with required parameters."""
        agent_booster = _AgentBooster(
            project_client=project_client,
            model_config=model_config,
            agent_id=auto_cleanup_agent.id,
            sample_size=3,
            max_iterations=1,
            improvement_intent="Make responses more helpful and concise",
            verbose=True,
        )

        assert agent_booster is not None
        assert agent_booster._config["sample_size"] == 3
        assert agent_booster._config["max_iterations"] == 1
        assert agent_booster._config["improvement_intent"] == "Make responses more helpful and concise"

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_refine_with_custom_evaluators(
        self, model_config, project_client, test_queries_file, auto_cleanup_agent
    ):
        """Test the refine method with custom evaluators."""
        from azure.ai.evaluation import FluencyEvaluator, CoherenceEvaluator

        custom_evaluators = {
            "fluency": FluencyEvaluator(model_config=model_config),
            "coherence": CoherenceEvaluator(model_config=model_config),
        }

        agent_booster = _AgentBooster(
            project_client=project_client,
            model_config=model_config,
            agent_id=auto_cleanup_agent.id,
            evaluators=custom_evaluators,
            sample_size=2,
            max_iterations=1,
            verbose=True,
        )

        # Create a temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_booster._output_dir = temp_dir

            try:
                result = agent_booster.refine(data_file=test_queries_file, max_iterations=1)
            except openai.BadRequestError as e:
                pytest.skip(f"Request was filtered by OpenAI, skipping test: {e}")

            # Verify the result structure
            assert "final_prompt_config" in result
            assert "refinement_history" in result
            assert "best_iteration" in result
            assert "best_scores" in result
            assert "history_file_path" in result

            # Verify refinement history structure
            assert len(result["refinement_history"]) == 1
            iteration_data = result["refinement_history"][0]
            assert "iteration" in iteration_data
            assert "prompt_config" in iteration_data
            assert "results" in iteration_data
            assert iteration_data["iteration"] == 1

            # Verify final prompt config has required fields
            final_config = result["final_prompt_config"]
            assert "system_prompt" in final_config
            assert "tools" in final_config

            # Verify history file was created
            assert os.path.exists(result["history_file_path"])

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_boost_single_iteration(self, model_config, project_client, auto_cleanup_agent):
        """Test the boost method with a single evaluation result."""
        from azure.ai.evaluation import EvaluationResult

        agent_booster = _AgentBooster(
            project_client=project_client, model_config=model_config, agent_id=auto_cleanup_agent.id, verbose=True
        )

        # Create a mock evaluation result as a dictionary (EvaluationResult is a TypedDict)
        mock_eval_result: EvaluationResult = {
            "metrics": {"fluency": 4.0, "coherence": 3.5},
            "rows": [
                {
                    "inputs.query": "What is the weather?",
                    "outputs.response": "I can help with weather information.",
                    "outputs.fluency": 4.0,
                    "outputs.coherence": 3.5,
                }
            ],
        }

        try:
            result_config = agent_booster.boost(mock_eval_result)
        except openai.BadRequestError as e:
            pytest.skip(f"Request was filtered by OpenAI, skipping test: {e}")

        # Verify the result is a prompt configuration
        assert "system_prompt" in result_config
        assert "tools" in result_config

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_load_queries(self, model_config, project_client, test_queries_file, auto_cleanup_agent):
        """Test loading queries from JSONL file."""
        agent_booster = _AgentBooster(
            project_client=project_client, model_config=model_config, agent_id=auto_cleanup_agent.id
        )

        queries = agent_booster._load_queries(test_queries_file)

        # Verify queries were loaded correctly
        assert len(queries) == 2
        assert "What is the weather like today?" in queries
        assert "How do I reset my password?" in queries

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_load_queries_from_static_file(
        self, model_config, project_client, static_test_queries_file, auto_cleanup_agent
    ):
        """Test loading queries from static test data file."""
        agent_booster = _AgentBooster(
            project_client=project_client, model_config=model_config, agent_id=auto_cleanup_agent.id
        )

        queries = agent_booster._load_queries(static_test_queries_file)

        # Verify queries were loaded correctly from static file
        assert len(queries) == 2
        assert "What is the weather like today?" in queries
        assert "How do I reset my password?" in queries

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_invalid_data_file(self, model_config, project_client, auto_cleanup_agent):
        """Test error handling for invalid data file."""
        agent_booster = _AgentBooster(
            project_client=project_client, model_config=model_config, agent_id=auto_cleanup_agent.id
        )

        with pytest.raises(FileNotFoundError, match="Data file not found"):
            agent_booster._load_queries("nonexistent_file.jsonl")

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_with_default_evaluators(
        self, model_config, project_client, test_queries_file, auto_cleanup_agent
    ):
        """Test agent booster with default evaluators."""
        agent_booster = _AgentBooster(
            project_client=project_client,
            model_config=model_config,
            agent_id=auto_cleanup_agent.id,
            sample_size=2,
            max_iterations=1,
            verbose=True,
        )

        # Verify default evaluators are set
        assert agent_booster._evaluators is not None
        assert len(agent_booster._evaluators) > 0

        # Test with minimal iteration
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_booster._output_dir = temp_dir

            try:
                result = agent_booster.refine(data_file=test_queries_file, max_iterations=1)
            except openai.BadRequestError as e:
                pytest.skip(f"Request was filtered by OpenAI, skipping test: {e}")

            assert result is not None
            assert "final_prompt_config" in result

    @pytest.mark.skipif(not is_live(), reason="AOAI recordings have bad recording scrubbing")
    def test_agent_booster_multiple_iterations(
        self, model_config, project_client, static_test_queries_file, auto_cleanup_agent
    ):
        """Test agent booster with multiple iterations."""
        agent_booster = _AgentBooster(
            project_client=project_client,
            model_config=model_config,
            agent_id=auto_cleanup_agent.id,
            sample_size=3,
            max_iterations=2,
            improvement_intent="Make responses more detailed and informative",
            verbose=True,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            agent_booster._output_dir = temp_dir

            try:
                result = agent_booster.refine(data_file=static_test_queries_file, max_iterations=2)
            except openai.BadRequestError as e:
                pytest.skip(f"Request was filtered by OpenAI, skipping test: {e}")

            # Verify multiple iterations were completed
            assert len(result["refinement_history"]) == 2

            # Verify each iteration has the expected structure
            for i, iteration_data in enumerate(result["refinement_history"]):
                assert iteration_data["iteration"] == i + 1
                assert "prompt_config" in iteration_data
                assert "results" in iteration_data

            # Verify final configuration is returned
            assert "final_prompt_config" in result
            assert "system_prompt" in result["final_prompt_config"]
