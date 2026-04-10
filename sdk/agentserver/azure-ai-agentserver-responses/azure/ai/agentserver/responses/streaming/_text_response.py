# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""TextResponse — high-level convenience for producing text-message responses.

Handles the full SSE lifecycle automatically:
``response.created`` → ``response.in_progress`` → message/content events
→ ``response.completed``.

Use ``text`` when the complete text is available (a plain string, a sync
callable, or an async callable).  Use ``text_stream`` when text arrives
incrementally (e.g., token-by-token from an LLM).
"""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import TYPE_CHECKING, Any, AsyncIterator, Awaitable, Callable, Union

from ..models import _generated as generated_models
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

    **Plain string**::

        return TextResponse(context, request, text="Hello!")

    **Callable (sync or async)**::

        return TextResponse(context, request,
            text=lambda: "Hello!")

    **Streaming mode** — provide ``text_stream``::

        async def tokens():
            for t in ["Hello", ", ", "world!"]:
                yield t

        return TextResponse(context, request,
            text_stream=tokens)

    :param context: The response context (provides the response ID).
    :type context: ~azure.ai.agentserver.responses.ResponseContext
    :param request: The incoming create-response request.
    :type request: ~azure.ai.agentserver.responses.models.CreateResponse
    :param text: A plain string, or a sync/async callable that returns the
        complete response text. Mutually exclusive with *text_stream*.
    :type text: str | Callable[[], str | Awaitable[str]] | None
    :param text_stream: A callable returning an async iterable of text
        chunks. Mutually exclusive with *text*.
    :type text_stream: Callable[[], AsyncIterable[str]] | None
    :param configure: An optional callback to configure the
        :class:`ResponseObject` (e.g. set Temperature, Instructions, Metadata)
        before ``response.created`` is emitted.
    :type configure: Callable[[ResponseObject], None] | None
    :raises ValueError: If neither or both of *text* and
        *text_stream* are provided.
    """

    def __init__(
        self,
        context: "ResponseContext",
        request: "CreateResponse",
        *,
        text: Union[str, Callable[[], Union[str, Awaitable[str]]], None] = None,
        text_stream: Callable[[], AsyncIterable[str]] | None = None,
        # Deprecated aliases — kept for backward compatibility
        create_text: Union[str, Callable[[], Union[str, Awaitable[str]]], None] = None,
        create_text_stream: Callable[[], AsyncIterable[str]] | None = None,
        configure: Callable[["ResponseObject"], None] | None = None,
    ) -> None:
        # Merge deprecated aliases into the new parameters
        if create_text is not None:
            if text is not None:
                raise ValueError("Use 'text' or 'create_text', not both.")
            text = create_text
        if create_text_stream is not None:
            if text_stream is not None:
                raise ValueError("Use 'text_stream' or 'create_text_stream', not both.")
            text_stream = create_text_stream

        if text is not None and text_stream is not None:
            raise ValueError("Provide either text or text_stream, not both.")
        if text is None and text_stream is None:
            raise ValueError("Provide either text or text_stream.")

        # Normalise: if text is a plain str, wrap it in a lambda so the
        # rest of the pipeline always deals with a callable.
        if isinstance(text, str):
            _literal = text
            text = lambda: _literal  # noqa: E731

        self._context = context
        self._request = request
        self._create_text = text
        self._create_text_stream = text_stream
        self._configure = configure

    def __aiter__(self) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        return self._generate()

    async def _generate(self) -> AsyncIterator[generated_models.ResponseStreamEvent]:
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
