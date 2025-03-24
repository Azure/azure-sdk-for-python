# Add test case for task_adherence evaluator
from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation import TaskAdherenceEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


async def task_adherence_mock():
    return """<S0>Let's think step by step: The query asks for the weather today, which requires a specific and detailed response about 
        the current weather conditions. The response provided is 'The weather is sunny,' which partially answers the query but lacks critical 
        details such as location, temperature, or any additional weather conditions (e.g., wind, humidity). This makes the response overly 
        vague and incomplete.</S0>  
        <S1>The response partially aligns with the query but has significant gaps in detail, making it barely adherent.</S1>  
        <S2>2</S2>"""



@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestTaskAdherenceEvaluator:
    def test_task_adherence_evaluator(self, mock_model_config):
        task_adherence = TaskAdherenceEvaluator(model_config=mock_model_config)
        task_adherence._flow = MagicMock(return_value=task_adherence_mock())
        # Test with query and response as strings
        result = task_adherence(
            query="How is the weather today? ?",
            response="The weather is sunny.",
        )
        assert isinstance(result, dict)
        assert "task_adherence" in result
        assert result["task_adherence"] == 2.0
        assert result["task_adherence_result"] == "fail"
        assert result["task_adherence_threshold"] == TaskAdherenceEvaluator.DEFAULT_TASK_ADHERENCE_SCORE
        assert "The response partially aligns with the query but has significant gaps in detail, making it barely adherent." in result[
            "task_adherence_reason"
        ]

    def test_task_adherence_evaluator_with_tool_definitions(self, mock_model_config):
        task_adherence = TaskAdherenceEvaluator(model_config=mock_model_config)
        task_adherence._flow = MagicMock(return_value=task_adherence_mock())
        # Test with query and response as strings
        result = task_adherence(
            query="How is the weather today?",
            response="The weather is sunny.",
            tool_definitions={
                "name": "fetch_weather",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to fetch weather for."
                        }
                    }
                }
            }
        )
        assert isinstance(result, dict)
        assert "task_adherence" in result
        assert result["task_adherence"] == 2.0
        assert result["task_adherence_result"] == "fail"
        assert result["task_adherence_threshold"] == TaskAdherenceEvaluator.DEFAULT_TASK_ADHERENCE_SCORE
        assert "The response partially aligns with the query but has significant gaps in detail, making it barely adherent." in result[
            "task_adherence_reason"
        ]
    

    def test_task_adherence_evaluator_missing_query(self, mock_model_config):
        task_adherence = TaskAdherenceEvaluator(model_config=mock_model_config)
        task_adherence._flow = MagicMock(return_value=task_adherence_mock())
        with pytest.raises(EvaluationException) as exc_info:
            task_adherence(response="The weather is sunny.")
        print(exc_info)
        assert ("Either 'conversation' or individual inputs must be provided." in str(exc_info.value))
            
