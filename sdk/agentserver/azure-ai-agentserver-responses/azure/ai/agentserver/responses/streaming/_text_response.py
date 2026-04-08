# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""TextResponse — high-level convenience for producing text-message responses.

Handles the full SSE lifecycle automatically:
``response.created`` → ``response.in_progress`` → message/content events
→ ``response.completed``.

Use ``create_text`` when the complete text is available (or produced by a
single async call).  Use ``create_text_stream`` when text arrives
incrementally (e.g., token-by-token from an LLM).
"""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import TYPE_CHECKING, Any, AsyncIterator, Awaitable, Callable

from ._event_stream import ResponseEventStream

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import CreateResponse, ResponseObject


class TextResponse:
    """A high-level convenience that produces a complete text-message response stream.

    Implements :class:`AsyncIterable` so it can be returned directly from a
    ``create_handler``.

    Handles the full SSE lifecycle automatically:

    * ``response.created`` → ``response.in_progress``
    * ``response.output_item.added`` (message)
    * ``response.content_part.added`` (text)
    * ``response.output_text.delta`` (one or more)
    * ``response.output_text.done``
    * ``response.content_part.done``
    * ``response.output_item.done``
    * ``response.completed``

    **Complete text mode** — provide ``create_text``::

        return TextResponse(context, request,
            create_text=lambda: "Hello!")

    **Streaming mode** — provide ``create_text_stream``::

        async def tokens():
            for t in ["Hello", ", ", "world!"]:
                yield t

        return TextResponse(context, request,
            create_text_stream=tokens)

    :param context: The response context (provides the response ID).
    :type context: ~azure.ai.agentserver.responses.ResponseContext
    :param request: The incoming create-response request.
    :type request: ~azure.ai.agentserver.responses.models.CreateResponse
    :param create_text: An async or sync callable that returns the complete
        response text. Mutually exclusive with *create_text_stream*.
    :type create_text: Callable[[], str | Awaitable[str]] | None
    :param create_text_stream: A callable returning an async iterable of text
        chunks. Mutually exclusive with *create_text*.
    :type create_text_stream: Callable[[], AsyncIterable[str]] | None
    :param configure: An optional callback to configure the
        :class:`ResponseObject` (e.g. set Temperature, Instructions, Metadata)
        before ``response.created`` is emitted.
    :type configure: Callable[[ResponseObject], None] | None
    :raises ValueError: If neither or both of *create_text* and
        *create_text_stream* are provided.
    """

    def __init__(
        self,
        context: "ResponseContext",
        request: "CreateResponse",
        *,
        create_text: Callable[[], str | Awaitable[str]] | None = None,
        create_text_stream: Callable[[], AsyncIterable[str]] | None = None,
        configure: Callable[["ResponseObject"], None] | None = None,
    ) -> None:
        if create_text is not None and create_text_stream is not None:
            raise ValueError("Provide either create_text or create_text_stream, not both.")
        if create_text is None and create_text_stream is None:
            raise ValueError("Provide either create_text or create_text_stream.")
        self._context = context
        self._request = request
        self._create_text = create_text
        self._create_text_stream = create_text_stream
        self._configure = configure

    def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        return self._generate()

    async def _generate(self) -> AsyncIterator[dict[str, Any]]:
        stream = ResponseEventStream(
            response_id=self._context.response_id,
            request=self._request,
        )

        if self._configure is not None:
            self._configure(stream.response)

        yield stream.emit_created()
        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()

        text = message.add_text_content()
        yield text.emit_added()

        if self._create_text is not None:
            # Complete-text mode: one delta with the full text.
            result = self._create_text()
            if hasattr(result, "__await__"):
                result = await result  # type: ignore[misc]
            yield text.emit_delta(result)  # type: ignore[arg-type]
            yield text.emit_done(result)  # type: ignore[arg-type]
        else:
            # Streaming mode: N deltas, accumulate final text.
            assert self._create_text_stream is not None
            accumulated: list[str] = []
            async for chunk in self._create_text_stream():
                accumulated.append(chunk)
                yield text.emit_delta(chunk)
            yield text.emit_done("".join(accumulated))

        yield message.emit_content_done(text)
        yield message.emit_done()
        yield stream.emit_completed()
