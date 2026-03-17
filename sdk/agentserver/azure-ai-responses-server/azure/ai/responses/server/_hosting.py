"""Starlette hosting integration for the Responses server package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._options import ResponsesServerOptions

if TYPE_CHECKING:
    from starlette.applications import Starlette

    from ._handlers import ResponseHandler


def map_responses_server(
    app: "Starlette",
    handler: "ResponseHandler",
    *,
    prefix: str = "",
    options: ResponsesServerOptions | None = None,
) -> None:
    """Register Responses API routes on a Starlette application.

    :param app: Starlette application instance to configure.
    :param handler: User-provided response handler implementation.
    :param prefix: Optional route prefix.
    :param options: Optional server runtime options.
    """
    raise NotImplementedError("Route registration will be implemented in Phase 2/3.")
