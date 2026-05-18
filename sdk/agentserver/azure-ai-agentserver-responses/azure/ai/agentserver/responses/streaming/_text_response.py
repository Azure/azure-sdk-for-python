# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""TextResponse — high-level convenience for producing text-message responses.

Handles the full SSE lifecycle automatically:
``response.created`` → ``response.in_progress`` → message/content events
→ ``response.completed``.

Pass any text source to ``text=``:

* **Plain string** — single delta, immediate completion.
* **Sync/async callable** — called once, result emitted as one delta.
* **Async iterable** — streamed token-by-token.
"""

from __future__ import annotations

import inspect
from collections.abc import AsyncIterable
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Callable, Union

from ..models import _generated as generated_models
from ._event_stream import ResponseEventStream

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import CreateResponse, ResponseObject

#: Union of all accepted text sources.
TextSource = Union[str, Callable[[], Union[str, Awaitable[str]]], AsyncIterable[str]]


class TextResponse:
    """A high-level convenience that produces a complete text-message response stream.

    Implements :class:`AsyncIterable` so it can be returned directly from a
    ``response_handler``.

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

    **Async iterable (token streaming)**::

        async def tokens():
            for t in ["Hello", ", ", "world!"]:
                yield t

        return TextResponse(context, request, text=tokens())

    :param context: The response context (provides the response ID).
    :param request: The incoming create-response request.
    :param text: The text source — a plain string, a sync/async callable
        returning a string, or an async iterable of string chunks for
        token-by-token streaming.
    :param configure: An optional callback to configure the
        :class:`ResponseObject` before ``response.created`` is emitted.
    """

    def __init__(
        self,
        context: "ResponseContext",
        request: "CreateResponse",
        *,
        text: TextSource,
        configure: Callable[["ResponseObject"], None] | None = None,
    ) -> None:
        self._context = context
        self._request = request
        self._text = text
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

        text_content = message.add_text_content()
        yield text_content.emit_added()

        source = self._text

        if isinstance(source, str):
            # Plain string — single delta.
            yield text_content.emit_delta(source)
            yield text_content.emit_text_done(source)
        elif isinstance(source, AsyncIterable):
            # Async iterable — stream token-by-token.
            accumulated: list[str] = []
            async for chunk in source:
                accumulated.append(chunk)
                yield text_content.emit_delta(chunk)
            yield text_content.emit_text_done("".join(accumulated))
        elif callable(source):
            # Sync or async callable — call once.
            result = source()
            if inspect.isawaitable(result):
                result = await result
            yield text_content.emit_delta(result)  # type: ignore[arg-type]
            yield text_content.emit_text_done(result)  # type: ignore[arg-type]
        else:
            raise TypeError(f"text must be str, callable, or AsyncIterable, got {type(source).__name__}")

        yield text_content.emit_done()
        yield message.emit_done()
        yield stream.emit_completed()
