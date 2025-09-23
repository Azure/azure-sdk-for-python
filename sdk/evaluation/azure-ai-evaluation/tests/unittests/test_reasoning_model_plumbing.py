import os
from unittest.mock import patch, MagicMock

import pytest


def _openai_model_config():
    # Minimal OpenAI config used in unit tests
    return {"model": "gpt-4o-mini"}


def _azure_openai_model_config():
    # Minimal Azure OpenAI config used in unit tests
    return {
        "azure_deployment": "fake-deployment",
        "azure_endpoint": "https://example.openai.azure.com/",
    }


@pytest.mark.unittest
def test_is_reasoning_model_plumbed_to_asyncprompty_load():
    # Patch the AsyncPrompty symbol in base_prompty_eval module before evaluator init
    with patch("azure.ai.evaluation._evaluators._common._base_prompty_eval.AsyncPrompty") as mock_async_prompty:
        mock_async_prompty.load = MagicMock(return_value=MagicMock())

        # Import after patch so Evaluator uses patched symbol
        from azure.ai.evaluation._evaluators._fluency._fluency import FluencyEvaluator

        evalr = FluencyEvaluator(_openai_model_config(), is_reasoning_model=True)
        assert evalr is not None

        # Assert that AsyncPrompty.load was called once with is_reasoning_model=True
        assert mock_async_prompty.load.call_count == 1
        kwargs = mock_async_prompty.load.call_args.kwargs
        assert kwargs.get("is_reasoning_model") is True

        # Also ensure we passed a prompty source path for fluency
        source_path = kwargs.get("source")
        assert isinstance(source_path, str) and source_path.endswith("fluency.prompty")

        # Ensure we do not override prompty temperature/max_tokens in model parameters
        # Only extra_headers should be present in parameters added by code
        model_cfg = kwargs.get("model")
        assert isinstance(model_cfg, dict)
        params = model_cfg.get("parameters", {})
        # Our code only sets extra_headers inside parameters; temperature/max_tokens come from prompty
        assert "extra_headers" in params
        assert "temperature" not in params
        assert "max_tokens" not in params


@pytest.mark.unittest
def test_is_reasoning_model_plumbed_for_azure_sets_api_version_and_headers():
    # Patch the AsyncPrompty symbol in base_prompty_eval module before evaluator init
    with patch("azure.ai.evaluation._evaluators._common._base_prompty_eval.AsyncPrompty") as mock_async_prompty:
        mock_async_prompty.load = MagicMock(return_value=MagicMock())

        from azure.ai.evaluation._evaluators._fluency._fluency import FluencyEvaluator

        evalr = FluencyEvaluator(_azure_openai_model_config(), is_reasoning_model=True)
        assert evalr is not None

        # Verify AsyncPrompty.load is called and receives expected prompty model tweaks
        assert mock_async_prompty.load.call_count == 1
        kwargs = mock_async_prompty.load.call_args.kwargs
        assert kwargs.get("is_reasoning_model") is True

        model_cfg = kwargs.get("model")
        assert isinstance(model_cfg, dict)
        configuration = model_cfg.get("configuration", {})
        # api_version should be populated for Azure OpenAI configuration
        assert configuration.get("api_version")
        # Ensure extra headers include user agent for AOAI calls
        extra_headers = model_cfg.get("parameters", {}).get("extra_headers", {})
        assert "x-ms-useragent" in extra_headers


@pytest.mark.unittest
@pytest.mark.parametrize(
    "import_path, class_name, prompty_filename",
    [
        ("azure.ai.evaluation._evaluators._coherence._coherence", "CoherenceEvaluator", "coherence.prompty"),
        ("azure.ai.evaluation._evaluators._similarity._similarity", "SimilarityEvaluator", "similarity.prompty"),
        ("azure.ai.evaluation._evaluators._relevance._relevance", "RelevanceEvaluator", "relevance.prompty"),
        ("azure.ai.evaluation._evaluators._retrieval._retrieval", "RetrievalEvaluator", "retrieval.prompty"),
        (
            "azure.ai.evaluation._evaluators._response_completeness._response_completeness",
            "ResponseCompletenessEvaluator",
            "response_completeness.prompty",
        ),
    ],
)
def test_reasoning_flag_plumbed_across_prompty_evaluators(import_path, class_name, prompty_filename):
    # Patch base prompty evaluator AsyncPrompty symbol once for all prompty-based evaluators
    with patch("azure.ai.evaluation._evaluators._common._base_prompty_eval.AsyncPrompty") as mock_async_prompty:
        mock_async_prompty.load = MagicMock(return_value=MagicMock())

        module = __import__(import_path, fromlist=[class_name])
        Evaluator = getattr(module, class_name)

        evalr = Evaluator(_openai_model_config(), is_reasoning_model=True)
        assert evalr is not None

        assert mock_async_prompty.load.call_count == 1
        kwargs = mock_async_prompty.load.call_args.kwargs
        assert kwargs.get("is_reasoning_model") is True

        source = kwargs.get("source")
        assert isinstance(source, str) and source.endswith(prompty_filename)


@pytest.mark.unittest
def test_groundedness_reasoning_flag_plumbed_via_module_asyncprompty():
    # Groundedness does its own AsyncPrompty.load internally depending on constructor kwargs
    with patch("azure.ai.evaluation._evaluators._groundedness._groundedness.AsyncPrompty") as mock_async_prompty:
        mock_async_prompty.load = MagicMock(return_value=MagicMock())

        from azure.ai.evaluation._evaluators._groundedness._groundedness import GroundednessEvaluator

        # Also patch base __call__ to avoid executing real evaluation; we only want to trigger the re-load path
        with patch(
            "azure.ai.evaluation._evaluators._common._base_prompty_eval.PromptyEvaluatorBase.__call__",
            return_value={},
        ):
            evalr = GroundednessEvaluator(_openai_model_config(), is_reasoning_model=True)
            assert evalr is not None
            # Trigger the __call__ path that switches prompty when query is provided
            evalr(query="q", response="r", context="c")

        # It should call module-level AsyncPrompty.load with is_reasoning_model once during switching
        assert mock_async_prompty.load.call_count == 1
        kwargs = mock_async_prompty.load.call_args.kwargs
        assert kwargs.get("is_reasoning_model") is True
        source = kwargs.get("source")
        # When query is present, groundedness switches to the "with_query" prompty
        assert isinstance(source, str) and source.endswith("groundedness_with_query.prompty")


@pytest.mark.unittest
def test_qa_evaluator_propagates_is_reasoning_model_to_components():
    # Patch base prompty AsyncPrompty to ensure each component evaluator attempts to load
    with patch("azure.ai.evaluation._evaluators._common._base_prompty_eval.AsyncPrompty") as mock_async_prompty:
        mock_async_prompty.load = MagicMock(return_value=MagicMock())

        from azure.ai.evaluation._evaluators._qa._qa import QAEvaluator

        qa = QAEvaluator(_openai_model_config(), is_reasoning_model=True)
        assert qa is not None

        # Call QA evaluator to drive child evaluators
        with patch(
            "azure.ai.evaluation._evaluators._common._base_prompty_eval.PromptyEvaluatorBase.__call__",
            return_value={"coherence": 5.0},
        ):
            qa(query="q", response="r", context="c", ground_truth="gt")

        # Multiple child evaluators should have loaded prompty with reasoning flag; at least one call expected
        assert mock_async_prompty.load.call_count >= 1
        # Inspect last call to ensure flag is present
        kwargs = mock_async_prompty.load.call_args.kwargs
        assert kwargs.get("is_reasoning_model") is True


@pytest.mark.unittest
@pytest.mark.parametrize(
    "prompty_rel_path, expected_temp_key, expected_temp_val, expected_max_tokens",
    [
        ("_evaluators/_fluency/fluency.prompty", "temperature", 0.0, 800),
        ("_evaluators/_task_success/task_success.prompty", "temperature", 0.0, 1500),
    ],
)
def test_prompty_yaml_contains_expected_parameters(
    prompty_rel_path, expected_temp_key, expected_temp_val, expected_max_tokens
):
    # Validate that prompty files define temperature and max_tokens in YAML
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    prompty_path = os.path.join(base_dir, "azure", "ai", "evaluation", prompty_rel_path)
    assert os.path.exists(prompty_path), f"Prompty file not found: {prompty_path}"

    # Read a small chunk of the file and look for parameter lines
    with open(prompty_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Simple checks to ensure YAML front matter includes expected parameters
    assert f"{expected_temp_key}: {expected_temp_val}" in content
    assert f"max_tokens: {expected_max_tokens}" in content
