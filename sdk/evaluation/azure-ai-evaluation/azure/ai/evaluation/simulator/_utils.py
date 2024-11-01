# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
This module contains a utility class for managing a list of JSON lines.
"""
import json


class JsonLineList(list):
    """
    A util to manage a list of JSON lines.
    """

    def to_json_lines(self):
        """
        Converts the list to a string of JSON lines.
        Each item in the list is converted to a JSON string
        and appended to the result string with a newline.

        :returns: A string of JSON lines, where each line is a JSON representation of an item in the list.
        :rtype: str
        """
        json_lines = ""
        for item in self:
            json_lines += json.dumps(item) + "\n"
        return json_lines

    def to_eval_qr_json_lines(self):
        """
        Converts the list to a string of JSON lines suitable for evaluation in a query & response format.
        Each item in the list is expected to be a dictionary with
        'messages' key. The 'messages' value is a list of
        dictionaries, each with a 'role' key and a 'content' key.
        The 'role' value should be either 'user' or 'assistant',
        and the 'content' value should be a string.
        If a 'context' key is present in the message, its value is also included
        in the output.

        :returns: A string of JSON lines.
        :rtype: str
        """
        json_lines = ""
        for item in self:
            user_message = None
            assistant_message = None
            user_context = None
            assistant_context = None
            template_parameters = item.get("template_parameters", {})
            category = template_parameters.get("category", None)
            for message in item["messages"]:
                if message["role"] == "user":
                    user_message = message["content"]
                    user_context = message.get("context", "")
                elif message["role"] == "assistant":
                    assistant_message = message["content"]
                    assistant_context = message.get("context", "")
                if user_message and assistant_message:
                    if user_context or assistant_context:
                        json_lines += (
                            json.dumps(
                                {
                                    "query": user_message,
                                    "response": assistant_message,
                                    "context": str(
                                        {
                                            "user_context": user_context,
                                            "assistant_context": assistant_context,
                                        }
                                    ),
                                    "category": category,
                                }
                            )
                            + "\n"
                        )
                        user_message = assistant_message = None
                    else:
                        json_lines += (
                            json.dumps({"query": user_message, "response": assistant_message, "category": category})
                            + "\n"
                        )
                        user_message = assistant_message = None

        return json_lines


class JsonLineChatProtocol(dict):
    """
    A util to manage a JSON object that follows the chat protocol.
    """

    def to_json(self):
        """
        Converts the object to a JSON string.

        :returns: A JSON representation of the object.
        :rtype: str
        """
        return json.dumps(self)

    def to_eval_qr_json_lines(self) -> str:
        """
        Converts the object to a string of JSON lines suitable for evaluation in a query and response format.
        The object is expected to be a dictionary with 'messages' key.

        :returns: A json lines document
        :rtype: str
        """
        user_message = None
        assistant_message = None
        if "context" in self:
            context = self["context"]
        else:
            context = None
        json_lines = ""
        for message in self["messages"]:
            if message["role"] == "user":
                user_message = message["content"]
            elif message["role"] == "assistant":
                assistant_message = message["content"]
            if "context" in message and message["context"] is not None:
                context = message.get("context", context)
            if user_message and assistant_message:
                if context:
                    json_lines += (
                        json.dumps({"query": user_message, "response": assistant_message, "context": context}) + "\n"
                    )
                    user_message = assistant_message = None
                else:
                    json_lines += json.dumps({"query": user_message, "response": assistant_message}) + "\n"
                    user_message = assistant_message = None
        return json_lines
