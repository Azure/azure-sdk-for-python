# # ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import copy
import datetime
import pytest

from azure.ai.agents.models._models import ThreadRun, RunStep, ThreadMessage
from azure.ai.agents.models._patch import _safe_instantiate, _filter_parameters


class TestDeserialization:
    """Tests for deserialization of sse responses."""

    @pytest.mark.parametrize(
        "valid_params,model_cls",
        [
            (
                {
                    "id": "12345",
                    "object": "thread.run",
                    "thread_id": "6789",
                    "agent_id": "101112",
                    "status": "in_progress",
                    "required_action": "test",
                    "last_error": "none",
                    "model": "gpt-4",
                    "instructions": "Test instruction",
                    "tools": "Test function",
                    "created_at": datetime.datetime(2024, 11, 14),
                    "expires_at": datetime.datetime(2024, 11, 17),
                    "started_at": datetime.datetime(2024, 11, 15),
                    "completed_at": datetime.datetime(2024, 11, 16),
                    "cancelled_at": datetime.datetime(2024, 11, 16),
                    "failed_at": datetime.datetime(2024, 11, 16),
                    "incomplete_details": "max_completion_tokens",
                    "usage": "in_progress",
                    "temperature": 1.0,
                    "top_p": 1.0,
                    "max_completion_tokens": 1000,
                    "truncation_strategy": "test",
                    "tool_choice": "tool name",
                    "response_format": "json",
                    "metadata": {"foo": "bar"},
                    "tool_resources": "test",
                    "parallel_tool_calls": True,
                },
                ThreadRun,
            ),
            (
                {
                    "id": "1233",
                    "object": "thread.message",
                    "created_at": datetime.datetime(2024, 11, 14),
                    "thread_id": "5678",
                    "status": "incomplete",
                    "incomplete_details": "test",
                    "completed_at": datetime.datetime(2024, 11, 16),
                    "incomplete_at": datetime.datetime(2024, 11, 16),
                    "role": "assistant",
                    "content": "Test",
                    "agent_id": "9911",
                    "run_id": "11",
                    "attachments": ["4", "8", "15", "16", "23", "42"],
                    "metadata": {"foo", "bar"},
                },
                ThreadMessage,
            ),
        ],
    )
    def test_correct_thread_params(self, valid_params, model_cls):
        """Test that if service returned extra parameter in SSE response, it does not create issues."""

        bad_params = {"foo": "bar"}
        params = copy.deepcopy(valid_params)
        params.update(bad_params)
        # We should bot e able to create Thread Run with bad parameters.
        with pytest.raises(TypeError):
            model_cls(**params)
        filtered_params = _filter_parameters(model_cls, params)
        for k in valid_params:
            assert k in filtered_params, f"{k} not in {list(filtered_params.keys())}"
        for k in bad_params:
            assert k not in filtered_params
        # Implicitly check that we can create object with the filtered parameters.
        model_cls(**filtered_params)
        # Check safe initialization.
        assert isinstance(_safe_instantiate(model_cls, params), model_cls)

    def test_safe_instantiate_non_dict(self):
        """Test that safe_instantiate method when user supplies not a dictionary."""
        assert _safe_instantiate(RunStep, 42) == 42
