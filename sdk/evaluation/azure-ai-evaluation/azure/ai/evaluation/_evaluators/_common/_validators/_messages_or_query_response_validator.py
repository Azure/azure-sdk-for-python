# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Validator that supports either messages or query/response input."""

from typing import Any, Dict
from typing_extensions import override

from ._conversation_validator import ConversationValidator


class MessagesOrQueryResponseInputValidator(ConversationValidator):
    """Validate either ``messages`` or standard ``query``/``response`` inputs."""

    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        messages = eval_input.get("messages")
        if messages is not None:
            messages_validation_exception = self._validate_input_messages_list(messages, "Messages")
            if messages_validation_exception:
                raise messages_validation_exception
            return True
        return super().validate_eval_input(eval_input)
