# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional


class LangGraphMissingConversationIdError(ValueError):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(
            message
            or "conversation.id is required when a LangGraph checkpointer is enabled. "
            "Provide conversation.id or disable the checkpointer."
        )
