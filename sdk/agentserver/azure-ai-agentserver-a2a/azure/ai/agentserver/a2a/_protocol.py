# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Protocol selection shared by native request dispatch and tracing."""

from a2a.server.context import ServerCallContext
from a2a.server.routes import DefaultServerCallContextBuilder, ServerCallContextBuilder
from a2a.utils.errors import InvalidParamsError, VersionNotSupportedError
from starlette.requests import Request

_SUPPORTED_VERSION = "1.0"
_VERSION_HEADER = "a2a-version"


def resolve_protocol_version(request: Request) -> str:
    versions = {
        value.strip()
        for value in [
            *request.headers.getlist(_VERSION_HEADER),
            *(value for key, value in request.query_params.multi_items() if key.lower() == _VERSION_HEADER),
        ]
        if value.strip()
    }
    if len(versions) > 1:
        raise InvalidParamsError(message="Conflicting A2A-Version selectors")
    selected = next(iter(versions), "0.3")
    if selected != _SUPPORTED_VERSION:
        raise VersionNotSupportedError(message=f"A2A version '{selected}' is not supported. Expected '1.0'.")
    return _SUPPORTED_VERSION


class ProtocolContextBuilder(ServerCallContextBuilder):
    """Validate selection and supply the effective version to native dispatch."""

    def __init__(self, builder: ServerCallContextBuilder | None) -> None:
        self._builder = builder if builder is not None else DefaultServerCallContextBuilder()

    def build(self, request: Request) -> ServerCallContext:
        version = resolve_protocol_version(request)
        context = self._builder.build(request)
        headers = {
            key: value for key, value in context.state.get("headers", {}).items() if key.lower() != _VERSION_HEADER
        }
        headers[_VERSION_HEADER] = version
        context.state["headers"] = headers
        return context
