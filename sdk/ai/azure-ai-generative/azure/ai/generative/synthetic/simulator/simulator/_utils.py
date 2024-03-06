# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json


class JsonLineList(list):
    def to_json_lines(self):
        json_lines = ""
        for item in self:
            json_lines += json.dumps(item) + "\n"
        return json_lines

    def to_eval_qa_json_lines(self):
        json_lines = ""
        for item in self:
            user_message = None
            assistant_message = None
            for message in item["messages"]:
                if message["role"] == "user":
                    user_message = message["content"]
                elif message["role"] == "assistant":
                    assistant_message = message["content"]
            if user_message and assistant_message:
                json_lines += json.dumps({"question": user_message, "answer": assistant_message}) + "\n"
        return json_lines
