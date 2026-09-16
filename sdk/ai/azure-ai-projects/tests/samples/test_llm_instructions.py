from llm_instructions import (
    agent_tools_instructions,
    agents_instructions,
    default_instructions,
    get_instructions_for_sample_path,
)


def test_get_instructions_uses_specific_folder_mapping():
    sample_path = "/repo/samples/agents/sample_agent_basic.py"

    assert get_instructions_for_sample_path(sample_path) == agents_instructions


def test_get_instructions_uses_longest_folder_mapping():
    sample_path = "/repo/samples/agents/tools/sample_tool.py"

    assert get_instructions_for_sample_path(sample_path) == agent_tools_instructions


def test_get_instructions_supports_windows_paths():
    sample_path = r"C:\repo\samples\agents\tools\sample_tool.py"

    assert get_instructions_for_sample_path(sample_path) == agent_tools_instructions


def test_get_instructions_falls_back_for_unmapped_folder():
    sample_path = "/repo/samples/responses/sample_responses_basic.py"

    instructions = get_instructions_for_sample_path(sample_path)

    assert instructions == default_instructions
    assert "HTTP 404 or resource-not-found responses are acceptable" in instructions


def test_get_instructions_falls_back_for_nested_unmapped_folder():
    sample_path = "/repo/samples/new_feature/nested/sample_basic.py"

    assert get_instructions_for_sample_path(sample_path) == default_instructions
