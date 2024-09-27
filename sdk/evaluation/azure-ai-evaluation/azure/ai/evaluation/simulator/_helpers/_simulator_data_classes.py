# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=C0103,C0114,C0116
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from azure.ai.evaluation.simulator._conversation.constants import ConversationRole


@dataclass
class Turn:
    """
    Represents a conversation turn,
    keeping track of the role, content,
    and context of a turn in a conversation.
    """

    role: Union[str, ConversationRole]
    content: str
    context: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Convert the conversation turn to a dictionary.

        :returns: A dictionary representation of the conversation turn.
        :rtype: Dict[str, Optional[str]]
        """
        return {
            "role": self.role.value if isinstance(self.role, ConversationRole) else self.role,
            "content": self.content,
            "context": self.context,
        }

    def __repr__(self):
        return f"Turn(role={self.role}, content={self.content})"


class ConversationHistory:
    """
    Conversation history class to keep track of the conversation turns in a conversation.
    """

    def __init__(self):
        """
        Initializes the conversation history with an empty list of turns.
        """
        self.history: List[Turn] = []

    def add_to_history(self, turn: Turn):
        """
        Adds a turn to the conversation history.

        :param turn: The conversation turn to add.
        :type turn: Turn
        """
        self.history.append(turn)

    def to_list(self) -> List[Dict[str, str]]:
        """
        Converts the conversation history to a list of dictionaries.

        :returns: A list of dictionaries representing the conversation turns.
        :rtype: List[Dict[str, str]]
        """
        return [turn.to_dict() for turn in self.history]

    def __len__(self) -> int:
        return len(self.history)

    def __repr__(self):
        for turn in self.history:
            print(turn)
        return ""
