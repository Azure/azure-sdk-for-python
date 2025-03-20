import datetime
import json
from enum import Enum

from pydantic import BaseModel

from typing import List, Optional, Union, Dict, Any


class AuthorRole(Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TOOL = "tool"
    DEVELOPER = "developer"

class AIContent(BaseModel):
    """
    Base class for content of a message.

    Attributes:
        type (str): The type of the content.
    """
    type: str

class Annotation(BaseModel):
    """
    Represents an annotation that links a portion of message content to a specific tool result or an external reference.

    Attributes:
        tool_call_id (Optional[str]): The ID of the tool call that produced the result being referenced by this annotation.
                                      Optional if the annotation references an external URL instead.
        json_path (Optional[str]): A JSONPath query into the result object of the tool call.
                                   This path should locate the specific value within the tool result relevant to this annotation.
                                   Optional if referencing an external URL.
        url (Optional[str]): A URL to an external resource that provides additional context or references the annotated content.
                             Optional if referencing a tool call result.
        start (Optional[int]): The start index of the text span in the message content that this annotation applies to.
        end (Optional[int]): The end index of the text span in the message content that this annotation applies to.
    """
    tool_call_id: Optional[str] = None
    json_path: Optional[str] = None
    url: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None

class ContentFilterContent(AIContent):
    """
    Represents content filtered by a content filter.

    Attributes:
        type (str): The type of the content, which is always 'content_filter'.
        content_filter (str): The content filter applied.
        detected (bool): Indicates whether the content was detected by the filter.
    """
    type: str = "content_filter"
    content_filter: str
    detected: bool

class RefusalContent(AIContent):
    """
    Represents refusal content.

    Attributes:
        type (str): The type of the content, which is always 'refusal'.
        refusal (str): The refusal message.
    """
    type: str = "refusal"
    refusal: str

class TextContent(AIContent):
    """
    Represents text content.

    Attributes:
        type (str): The type of the content, which is always 'text'.
        text (str): The text content.
        annotations (List[Annotation]): A list of annotations associated with the text content.
    """
    type: str = "text"
    text: str
    annotations: List[Annotation] = []

class ToolCallContent(AIContent):
    """
    Represents tool call content.

    Attributes:
        type (str): The type of the content, which is always 'tool_call'.
        name (str): The name of the tool.
        tool_call_id (str): The ID of the tool call.
        arguments (Optional[Dict[str, Any]]): The arguments for the tool call.
    """
    type: str = "tool_call"
    name: str
    tool_call_id: str
    arguments: Optional[Dict[str, Any]] = None

class ToolResultContent(AIContent):
    """
    Represents tool result content.

    Attributes:
        type (str): The type of the content, which is always 'tool_result'.
        tool_call_id (str): The ID of the tool call.
        results (Optional[Any]): The results of the tool call.
    """
    type: str = "tool_result"
    tool_call_id: str
    results: Optional[Any] = None

class FileContent(AIContent):
    """
    Represents file content.

    Attributes:
        type (str): The type of the content, which is always 'file'.
        file_name (Optional[str]): The name of the file.
        mime_type (Optional[str]): The MIME type of the file.
        uri (Optional[str]): The URI of the file.
        data_uri (Optional[str]): The data URI of the file.
        data (Optional[bytes]): The binary data of the file.
    """
    type: str = "file"
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    uri: Optional[str] = None
    data_uri: Optional[str] = None
    data: Optional[bytes] = None

class AudioContent(FileContent):
    """
    Represents audio content.

    Attributes:
        type (str): The type of the content, which is always 'audio'.
        duration (Optional[short]): The duration of the audio content.
    """
    type: str = "audio"
    duration: Optional[int] = None

class ImageContent(FileContent):
    """
    Represents image content.

    Attributes:
        type (str): The type of the content, which is always 'image'.
        width (Optional[int]): The width of the image.
        height (Optional[int]): The height of the image.
    """
    type: str = "image"
    width: Optional[int] = None
    height: Optional[int] = None

class VideoContent(FileContent):
    """
    Represents video content.

    Attributes:
        type (str): The type of the content, which is always 'video'.
        duration (Optional[int]): The duration of the video.
        width (Optional[int]): The width of the video.
        height (Optional[int]): The height of the video.
    """
    type: str = "video"
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class ChatMessage(BaseModel):
    """
    Represents a chat message.

    Attributes:
        user_id (Optional[str]): The ID of the user who sent the message.
        agent_id (Optional[str]): The ID of the agent who sent the message.
        message_id (str): The ID of the message.
        completion_id (Optional[str]): The ID of the completion associated with the message.
        thread_id (str): The ID of the thread the message belongs to.
        role (AuthorRole): The role of the message sender.
        content (List[AIContent]): The content of the message.
        author_name (Optional[str]): The name of the author of the message.
        created_at (Optional[int]): The timestamp when the message was created.
        completed_at (Optional[int]): The timestamp when the message was completed.
    """
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    message_id: str
    completion_id: Optional[str] = None
    thread_id: str
    role: AuthorRole
    content: List[AIContent]
    author_name: Optional[str] = None
    created_at: Optional[int] = None
    completed_at: Optional[int] = None




