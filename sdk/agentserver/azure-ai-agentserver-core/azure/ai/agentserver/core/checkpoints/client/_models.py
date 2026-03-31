# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Data models for checkpoint storage API."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


@dataclass
class CheckpointSession:
    """Represents a checkpoint session.

    A session maps to a conversation and groups related checkpoints together.

    :ivar session_id: The session identifier (maps to conversation_id).
    :ivar metadata: Optional metadata for the session.
    """

    session_id: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CheckpointItemId:
    """Identifier for a checkpoint item.

    :ivar session_id: The session identifier this checkpoint belongs to.
    :ivar item_id: The unique checkpoint item identifier.
    :ivar parent_id: Optional parent checkpoint identifier for hierarchical checkpoints.
    """

    session_id: str
    item_id: str
    parent_id: Optional[str] = None


@dataclass
class CheckpointItem:
    """Represents a single checkpoint item.

    Contains the serialized checkpoint data along with identifiers.

    :ivar session_id: The session identifier this checkpoint belongs to.
    :ivar item_id: The unique checkpoint item identifier.
    :ivar data: Serialized checkpoint data as bytes.
    :ivar parent_id: Optional parent checkpoint identifier.
    """

    session_id: str
    item_id: str
    data: bytes
    parent_id: Optional[str] = None

    def to_item_id(self) -> CheckpointItemId:
        """Convert to a CheckpointItemId.

        :return: The checkpoint item identifier.
        :rtype: CheckpointItemId
        """
        return CheckpointItemId(
            session_id=self.session_id,
            item_id=self.item_id,
            parent_id=self.parent_id,
        )


# Pydantic models for API request/response serialization


class CheckpointSessionRequest(BaseModel):
    """Request model for creating/updating a checkpoint session."""

    session_id: str = Field(alias="sessionId")
    metadata: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}

    @classmethod
    def from_session(cls, session: CheckpointSession) -> "CheckpointSessionRequest":
        """Create a request from a CheckpointSession.

        :param session: The checkpoint session.
        :type session: CheckpointSession
        :return: The request model.
        :rtype: CheckpointSessionRequest
        """
        return cls(
            session_id=session.session_id,
            metadata=session.metadata,
        )


class CheckpointSessionResponse(BaseModel):
    """Response model for checkpoint session operations."""

    session_id: str = Field(alias="sessionId")
    metadata: Optional[Dict[str, Any]] = None
    etag: Optional[str] = None

    model_config = {"populate_by_name": True}

    def to_session(self) -> CheckpointSession:
        """Convert to a CheckpointSession.

        :return: The checkpoint session.
        :rtype: CheckpointSession
        """
        return CheckpointSession(
            session_id=self.session_id,
            metadata=self.metadata,
        )


class CheckpointItemIdResponse(BaseModel):
    """Response model for checkpoint item identifiers."""

    session_id: str = Field(alias="sessionId")
    item_id: str = Field(alias="itemId")
    parent_id: Optional[str] = Field(default=None, alias="parentId")

    model_config = {"populate_by_name": True}

    def to_item_id(self) -> CheckpointItemId:
        """Convert to a CheckpointItemId.

        :return: The checkpoint item identifier.
        :rtype: CheckpointItemId
        """
        return CheckpointItemId(
            session_id=self.session_id,
            item_id=self.item_id,
            parent_id=self.parent_id,
        )


class CheckpointItemRequest(BaseModel):
    """Request model for creating checkpoint items."""

    session_id: str = Field(alias="sessionId")
    item_id: str = Field(alias="itemId")
    data: str  # Base64-encoded bytes
    parent_id: Optional[str] = Field(default=None, alias="parentId")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_item(cls, item: CheckpointItem) -> "CheckpointItemRequest":
        """Create a request from a CheckpointItem.

        :param item: The checkpoint item.
        :type item: CheckpointItem
        :return: The request model.
        :rtype: CheckpointItemRequest
        """
        import base64

        return cls(
            session_id=item.session_id,
            item_id=item.item_id,
            data=base64.b64encode(item.data).decode("utf-8"),
            parent_id=item.parent_id,
        )


class CheckpointItemResponse(BaseModel):
    """Response model for checkpoint item operations."""

    session_id: str = Field(alias="sessionId")
    item_id: str = Field(alias="itemId")
    data: str  # Base64-encoded bytes
    parent_id: Optional[str] = Field(default=None, alias="parentId")
    etag: Optional[str] = None

    model_config = {"populate_by_name": True}

    def to_item(self) -> CheckpointItem:
        """Convert to a CheckpointItem.

        :return: The checkpoint item.
        :rtype: CheckpointItem
        """
        import base64

        return CheckpointItem(
            session_id=self.session_id,
            item_id=self.item_id,
            data=base64.b64decode(self.data),
            parent_id=self.parent_id,
        )


class ListCheckpointItemIdsResponse(BaseModel):
    """Response model for listing checkpoint item identifiers."""

    value: List[CheckpointItemIdResponse] = Field(default_factory=list)
    next_link: Optional[str] = Field(default=None, alias="nextLink")

    model_config = {"populate_by_name": True}
