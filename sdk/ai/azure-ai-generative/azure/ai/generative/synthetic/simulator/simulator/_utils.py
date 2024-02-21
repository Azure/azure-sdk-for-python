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
