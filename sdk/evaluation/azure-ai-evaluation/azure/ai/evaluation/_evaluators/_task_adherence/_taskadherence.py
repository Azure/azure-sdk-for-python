import os
from typing import Dict, Union, List
from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase

class Content:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value

class FunctionToolCall:
    def __init__(self, tool_name: str, type: str, parameters: dict, function_name: str, output: str):
        self.tool_name = tool_name
        self.type = type
        self.parameters = parameters
        self.function_name = function_name
        self.output = output

class FileSearchToolCall:
    def __init__(self, tool_name: str, type: str, results: List[str]):
        self.tool_name = tool_name
        self.type = type
        self.results = results

class Message:
    def __init__(self, type: str, content: Union[str, List[Content]], tool_calls: Union[List[FunctionToolCall], List[FileSearchToolCall]] = []):
        self.type = type
        self.content = content
        self.tool_calls = tool_calls

class Tool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class TaskAdherenceEvaluator(PromptyEvaluatorBase):

    _PROMPTY_FILE = "taskadherence.prompty"
    _RESULT_KEY = "taskadherence"

    id = "taskadherence"

    @override
    def __init__(self, model_config):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)

    @overload
    def __call__(
        self, 
        *, 
        instructions: str,
        query: Union[str, List[Message]],
        response: Union[str, List[Message]],
        conversation_history: List[Message],
        tool_definitions: List[Tool],
        threshold: float
    ) -> Dict[str, Union[bool, float, str]]:
        ...

    @override
    def __call__(self, *args, **kwargs) -> Dict[str, Union[bool, float, str]]:
        task_adherence_result = super().__call__(*args, **kwargs)

        if not isinstance(task_adherence_result, dict) or not "task_adherence" in task_adherence_result:
            raise Exception("task adherence Result is invalid") 
        threshold = kwargs.get("threshold", 3.0)
        task_adherence_score = task_adherence_result.get("score")
        explanation = task_adherence_result.get("explanation")
        is_task_adherent = task_adherence_score >= threshold

        return {
            "is_task_adherent": is_task_adherent,
            "task_adherence_score": task_adherence_score,
            "explanation": explanation
        }
