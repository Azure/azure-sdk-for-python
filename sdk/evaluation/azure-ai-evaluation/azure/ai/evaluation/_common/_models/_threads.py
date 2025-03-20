from typing import List
from pydantic import BaseModel

from azure.ai.evaluation._common._models._messages import ChatMessage


class ActivityThread(BaseModel):
    """
    Represents an activity thread.

    Attributes:
        thread_id (str): The ID of the thread.
        messages (List[ChatMessage]): The list of chat messages in the thread.
    """
    thread_id: str
    messages: List[ChatMessage] = []