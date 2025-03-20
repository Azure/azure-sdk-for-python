from typing import Optional, List
from pydantic import BaseModel

from azure.ai.evaluation._common._models._messages import ChatMessage

class InputTokenDetails(BaseModel):
    """
    Represents details about input tokens.

    Attributes:
        cached_tokens (Optional[int]): The number of cached tokens.
    """
    cached_tokens: Optional[int] = None

class OutputTokenDetails(BaseModel):
    """
    Represents details about output tokens.

    Attributes:
        reasoning_tokens (Optional[int]): The number of reasoning tokens.
    """
    reasoning_tokens: Optional[int] = None

class CompletionUsage(BaseModel):
    """
    Represents the usage details of a completion.

    Attributes:
        output_tokens (int): The number of output tokens.
        input_tokens (int): The number of input tokens.
        total_tokens (int): The total number of tokens.
        input_token_details (Optional[InputTokenDetails]): Details about input tokens.
        output_token_details (Optional[OutputTokenDetails]): Details about output tokens.
    """
    output_tokens: int
    input_tokens: int
    total_tokens: int
    input_token_details: Optional[InputTokenDetails] = None
    output_token_details: Optional[OutputTokenDetails] = None

class IncompleteDetails(BaseModel):
    """
    Represents details about incomplete completions.

    Attributes:
        reason (str): The reason for the incomplete status.
    """
    reason: str

class Completion(BaseModel):
    """
    Represents a completion.

    Attributes:
        agent_id (str): The ID of the agent.
        completion_id (str): The ID of the completion.
        created_at (int): The timestamp when the completion was created.
        completed_at (int): The timestamp when the completion was completed.
        status (str): The status of the completion.
        output (List[ChatMessage]): The output messages of the completion.
        thread_id (str): The ID of the thread the completion belongs to.
        usage (CompletionUsage): The usage details of the completion.
        incomplete_details (Optional[IncompleteDetails]): Details about incomplete completions.
    """
    agent_id: str
    completion_id: str
    created_at: int
    completed_at: int
    status: str
    output: List[ChatMessage] = []
    thread_id: str
    usage: CompletionUsage
    incomplete_details: Optional[IncompleteDetails] = None
