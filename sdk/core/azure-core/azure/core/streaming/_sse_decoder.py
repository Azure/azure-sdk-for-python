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
"""Server-Sent Events (SSE) decoder for streaming responses."""
import json
from typing import Any, Optional


class ServerSentEvent:
    """Represents a Server-Sent Event.

    :param data: The event data payload.
    :type data: Optional[str]
    :param event: The event type.
    :type event: Optional[str]
    :param id: The event ID for reconnection.
    :type id: Optional[str]
    :param retry: Reconnection time in milliseconds.
    :type retry: Optional[int]
    """

    def __init__(
        self,
        *,
        data: Optional[str] = None,
        event: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None,
    ) -> None:
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry

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
        return f"ServerSentEvent(event={self.event!r}, data={self.data!r}, id={self.id!r}, retry={self.retry})"


class SSEDecoder:
    """Decoder for Server-Sent Events (SSE) stream.

    Implements the SSE parsing specification from:
    https://html.spec.whatwg.org/multipage/server-sent-events.html
    """

    def __init__(self) -> None:
        self.data: list[str] = []
        self.last_event_id: Optional[str] = None
        self.event: Optional[str] = None
        self.retry: Optional[int] = None

    def decode(self, line: str) -> None:
        """Decode a single line from the SSE stream.

        :param line: A line from the SSE stream.
        :type line: str
        """
        # Ignore comments (lines starting with colon)
        if line.startswith(":"):
            return

        # Parse field and value
        if ":" in line:
            field, _, value = line.partition(":")
            # Remove leading space from value (per SSE spec)
            if value.startswith(" "):
                value = value[1:]
        else:
            field = line
            value = ""

        # Process the field
        if field == "data":
            self.data.append(value)
        elif field == "event":
            self.event = value
        elif field == "id":
            # Ignore IDs containing null character (per SSE spec)
            if "\0" not in value:
                self.last_event_id = value
        elif field == "retry":
            try:
                self.retry = int(value)
            except (TypeError, ValueError):
                pass  # Ignore invalid retry values

        # Other fields are ignored per SSE spec

    def event(self) -> ServerSentEvent:
        """Create and return a ServerSentEvent from accumulated data.

        This method should be called after processing an empty line,
        which signals the end of an event.

        :return: The constructed ServerSentEvent.
        :rtype: ServerSentEvent
        """
        sse = ServerSentEvent(
            event=self.event,
            data="\n".join(self.data),
            id=self.last_event_id,
            retry=self.retry,
        )

        # Reset event-specific fields (but preserve last_event_id)
        self.data = []
        self.event = None
        self.retry = None

        return sse
