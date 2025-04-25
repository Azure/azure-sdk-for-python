# Serialization and deserialization helper functions to make test-writing easier

import json
from datetime import datetime

from azure.ai.evaluation._converters._models import ToolCall
from azure.ai.projects.models import RunStepCodeInterpreterToolCall, RunStepCodeInterpreterToolCallDetails, \
    RunStepFileSearchToolCall, RunStepFileSearchToolCallResults, RunStepFileSearchToolCallResult, \
    FileSearchRankingOptions, RunStepBingGroundingToolCall


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