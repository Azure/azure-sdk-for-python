from azure.ai.inference.prompts._utils import remove_leading_empty_space


def test_success_with_no_changes():
    prompt_str = """First line
Second line"""
    result = remove_leading_empty_space(prompt_str)
    assert result == prompt_str


def test_success_by_remove_leading_empty_space():
    prompt_str = """
    
    First line

      Second line
        Third line
"""
    result = remove_leading_empty_space(prompt_str)
    assert (
        result
        == """First line

  Second line
    Third line"""
    )
