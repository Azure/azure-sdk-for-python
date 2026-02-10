# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""JSON Lines (JSONL) decoder for streaming responses."""
import json
from typing import Any, Optional


class JSONLEvent:
    """Represents a JSON Lines event.

    :param data: The JSON data as a string.
    :type data: Optional[str]
    """

    def __init__(
        self,
        *,
        data: Optional[str] = None,
    ) -> None:
        self.data = data

    def json(self) -> Any:
        """Parse the event data as JSON.

        :return: The parsed JSON data.
        :rtype: Any
        :raises ValueError: If the data is not valid JSON.
        """
        if not self.data:
            return None
        return json.loads(self.data)

    def __repr__(self) -> str:
        return f"JSONLEvent(data={self.data!r})"


class JSONLDecoder:
    """Decoder for JSON Lines (JSONL) stream.

    Each line in a JSONL stream is a separate JSON object.
    """

    def __init__(self) -> None:
        self.data: list[str] = []

    def decode(self, line: str) -> None:
        """Decode a single line from the JSONL stream.

        :param line: A line from the JSONL stream.
        :type line: str
        """
        if line.strip():  # Only process non-empty lines
            self.data.append(line)

    def event(self) -> JSONLEvent:
        """Create and return a JSONLEvent from accumulated data.

        :return: The constructed JSONLEvent.
        :rtype: JSONLEvent
        """
        jsonl = JSONLEvent(data="\n".join(self.data))
        self.data = []
        return jsonl
