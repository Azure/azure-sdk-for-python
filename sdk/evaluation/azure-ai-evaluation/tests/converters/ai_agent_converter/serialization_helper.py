# Serialization and deserialization helper functions to make test-writing easier

import json
from datetime import datetime

from azure.ai.evaluation._converters._models import ToolCall


# Breaking changes introduced in newer version of the agents SDK
# Models have been moved, so try a few different locations
try:
    from azure.ai.projects.models import (
        RunStepCodeInterpreterToolCall,
        RunStepCodeInterpreterToolCallDetails,
        RunStepFileSearchToolCall,
        RunStepFileSearchToolCallResults,
        RunStepFileSearchToolCallResult,
        FileSearchRankingOptions,
        RunStepBingGroundingToolCall,
        ThreadRun,
    )
except ImportError:
    pass
try:
    from azure.ai.agents.models import (
        RunStepCodeInterpreterToolCall,
        RunStepCodeInterpreterToolCallDetails,
        RunStepFileSearchToolCall,
        RunStepFileSearchToolCallResults,
        RunStepFileSearchToolCallResult,
        FileSearchRankingOptions,
        RunStepBingGroundingToolCall,
        ThreadRun,
    )
except ImportError:
    pass



class ToolDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'completed' in obj and 'created' in obj and 'details' in obj:
            return ToolCall(
                created=datetime.fromisoformat(obj['created']),
                completed=datetime.fromisoformat(obj['completed']),
                details=self.decode_details(obj['details'])
            )
        return obj

    def decode_details(self, details):
        if 'id' in details and 'type' in details:
            if details['type'] == 'code_interpreter':
                return RunStepCodeInterpreterToolCall(
                    id=details['id'],
                    code_interpreter=RunStepCodeInterpreterToolCallDetails(
                        input=details['code_interpreter']['input'],
                        outputs=details['code_interpreter']['outputs']
                    )
                )
            elif details['type'] == 'file_search':
                return RunStepFileSearchToolCall(
                    id=details['id'],
                    file_search=RunStepFileSearchToolCallResults(
                        results=[
                            RunStepFileSearchToolCallResult(
                                file_name=result['file_name'],
                                file_id=result['file_id'],
                                score=result['score'],
                                content=result['content']
                            ) for result in details['file_search']['results']
                        ],
                        ranking_options=FileSearchRankingOptions(
                            ranker=details['file_search']['ranking_options']['ranker'],
                            score_threshold=details['file_search']['ranking_options']['score_threshold']
                        )
                    )
                )
            elif details['type'] == 'bing_grounding':
                return RunStepBingGroundingToolCall(
                    id=details['id'],
                    bing_grounding=details['bing_grounding']
                )
        return details

class ToolEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ToolCall):
            return {
                "completed": obj.completed,
                "created": obj.created,
                "details": obj.details
            }
        if isinstance(obj, RunStepCodeInterpreterToolCall):
            return {
                "id": obj.id,
                # "type": obj.type,
                "code_interpreter": obj.code_interpreter
            }
        if isinstance(obj, RunStepCodeInterpreterToolCallDetails):
            return {
                "input": obj.input,
                "outputs": obj.outputs
            }
        if isinstance(obj, RunStepFileSearchToolCall):
            return {
                "id": obj.id,
                # "type": obj.type,
                "file_search": obj.file_search
            }
        if isinstance(obj, RunStepFileSearchToolCallResults):
            return {
                "results": obj.results,
                "ranking_options": obj.ranking_options
            }
        if isinstance(obj, RunStepFileSearchToolCallResult):
            return {
                "file_name": obj.file_name,
                "file_id": obj.file_id,
                "score": obj.score,
                "content": obj.content
            }
        if isinstance(obj, FileSearchRankingOptions):
            return {
                "ranker": obj.ranker,
                "score_threshold": obj.score_threshold
            }
        if isinstance(obj, RunStepBingGroundingToolCall):
            return {
                "id": obj.id,
                # "type": obj.type,
                "bing_grounding": obj.bing_grounding
            }
        return super().default(obj)

class ThreadRunDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "id" in obj and "thread_id" in obj:
            return ThreadRun(
                id=obj["id"],
                thread_id=obj["thread_id"],
                agent_id=obj["assistant_id"],
                status=obj["status"],
                required_action=obj.get("required_action"),
                last_error=obj.get("last_error"),
                model=obj["model"],
                instructions=obj["instructions"],
                tools=obj["tools"],
                created_at=datetime.fromtimestamp(obj["created_at"]),
                expires_at=datetime.fromtimestamp(obj["expires_at"]) if obj.get("expires_at") else None,
                started_at=datetime.fromtimestamp(obj["started_at"]) if obj.get("started_at") else None,
                completed_at=datetime.fromtimestamp(obj["completed_at"]) if obj.get("completed_at") else None,
                cancelled_at=datetime.fromtimestamp(obj["cancelled_at"]) if obj.get("cancelled_at") else None,
                failed_at=datetime.fromtimestamp(obj["failed_at"]) if obj.get("failed_at") else None,
                incomplete_details=obj.get("incomplete_details"),
                usage=obj.get("usage"),
                temperature=obj.get("temperature"),
                top_p=obj.get("top_p"),
                max_prompt_tokens=obj["max_prompt_tokens"],
                max_completion_tokens=obj["max_completion_tokens"],
                truncation_strategy=obj["truncation_strategy"],
                tool_choice=obj["tool_choice"],
                response_format=obj["response_format"],
                metadata=obj["metadata"],
                tool_resources=obj.get("tool_resources"),
                parallel_tool_calls=obj["parallel_tool_calls"],
            )
        return obj


class ThreadRunEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ThreadRun):
            return {
                "id": obj.id,
                "object": obj.object,
                "thread_id": obj.thread_id,
                "assistant_id": obj.assistant_id,
                "status": obj.status,
                "required_action": obj.required_action,
                "last_error": obj.last_error,
                "model": obj.model,
                "instructions": obj.instructions,
                "tools": obj.tools,
                "created_at": int(obj.created_at.timestamp()),
                "expires_at": int(obj.expires_at.timestamp()) if obj.expires_at else None,
                "started_at": int(obj.started_at.timestamp()) if obj.started_at else None,
                "completed_at": int(obj.completed_at.timestamp()) if obj.completed_at else None,
                "cancelled_at": int(obj.cancelled_at.timestamp()) if obj.cancelled_at else None,
                "failed_at": int(obj.failed_at.timestamp()) if obj.failed_at else None,
                "incomplete_details": obj.incomplete_details,
                "usage": obj.usage,
                "temperature": obj.temperature,
                "top_p": obj.top_p,
                "max_prompt_tokens": obj.max_prompt_tokens,
                "max_completion_tokens": obj.max_completion_tokens,
                "truncation_strategy": obj.truncation_strategy,
                "tool_choice": obj.tool_choice,
                "response_format": obj.response_format,
                "metadata": obj.metadata,
                "tool_resources": obj.tool_resources,
                "parallel_tool_calls": obj.parallel_tool_calls,
            }
        return super().default(obj)