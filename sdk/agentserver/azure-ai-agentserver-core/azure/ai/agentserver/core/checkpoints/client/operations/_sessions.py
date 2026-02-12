# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Operations for checkpoint sessions."""

from typing import Any, ClassVar, Dict, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async

from ....tools.client.operations._base import BaseOperations
from .._models import (
    CheckpointSession,
    CheckpointSessionRequest,
    CheckpointSessionResponse,
)


class CheckpointSessionOperations(BaseOperations):
    """Operations for managing checkpoint sessions."""

    _API_VERSION: ClassVar[str] = "2025-11-15-preview"

    _HEADERS: ClassVar[Dict[str, str]] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    _QUERY_PARAMS: ClassVar[Dict[str, Any]] = {"api-version": _API_VERSION}

    def _session_path(self, session_id: Optional[str] = None) -> str:
        """Get the API path for session operations.

        :param session_id: Optional session identifier.
        :type session_id: Optional[str]
        :return: The API path.
        :rtype: str
        """
        base = "/checkpoints/sessions"
        return f"{base}/{session_id}" if session_id else base

    def _build_upsert_request(self, session: CheckpointSession) -> HttpRequest:
        """Build the HTTP request for upserting a session.

        :param session: The checkpoint session.
        :type session: CheckpointSession
        :return: The HTTP request.
        :rtype: HttpRequest
        """
        request_model = CheckpointSessionRequest.from_session(session)
        return self._client.put(
            self._session_path(session.session_id),
            params=self._QUERY_PARAMS,
            headers=self._HEADERS,
            content=request_model.model_dump(by_alias=True),
        )

    def _build_read_request(self, session_id: str) -> HttpRequest:
        """Build the HTTP request for reading a session.

        :param session_id: The session identifier.
        :type session_id: str
        :return: The HTTP request.
        :rtype: HttpRequest
        """
        return self._client.get(
            self._session_path(session_id),
            params=self._QUERY_PARAMS,
            headers=self._HEADERS,
        )

    def _build_delete_request(self, session_id: str) -> HttpRequest:
        """Build the HTTP request for deleting a session.

        :param session_id: The session identifier.
        :type session_id: str
        :return: The HTTP request.
        :rtype: HttpRequest
        """
        return self._client.delete(
            self._session_path(session_id),
            params=self._QUERY_PARAMS,
            headers=self._HEADERS,
        )

    @distributed_trace_async
    async def upsert(self, session: CheckpointSession) -> CheckpointSession:
        """Create or update a checkpoint session.

        :param session: The checkpoint session to upsert.
        :type session: CheckpointSession
        :return: The upserted checkpoint session.
        :rtype: CheckpointSession
        """
        request = self._build_upsert_request(session)
        response = await self._send_request(request)
        async with response:
            json_response = self._extract_response_json(response)
            session_response = CheckpointSessionResponse.model_validate(json_response)
        return session_response.to_session()

    @distributed_trace_async
    async def read(self, session_id: str) -> Optional[CheckpointSession]:
        """Read a checkpoint session by ID.

        :param session_id: The session identifier.
        :type session_id: str
        :return: The checkpoint session if found, None otherwise.
        :rtype: Optional[CheckpointSession]
        """
        request = self._build_read_request(session_id)
        try:
            response = await self._send_request(request)
            async with response:
                json_response = self._extract_response_json(response)
                session_response = CheckpointSessionResponse.model_validate(json_response)
            return session_response.to_session()
        except ResourceNotFoundError:
            return None

    @distributed_trace_async
    async def delete(self, session_id: str) -> None:
        """Delete a checkpoint session.

        :param session_id: The session identifier.
        :type session_id: str
        """
        request = self._build_delete_request(session_id)
        response = await self._send_request(request)
        async with response:
            pass  # No response body expected
