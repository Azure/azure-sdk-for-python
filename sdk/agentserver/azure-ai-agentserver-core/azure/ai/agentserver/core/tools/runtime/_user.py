# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextvars import ContextVar
from abc import ABC, abstractmethod
from typing import ClassVar, Mapping, Optional

from ..client._models import UserInfo


class UserProvider(ABC):
    """Base class for user providers."""

    @abstractmethod
    async def get_user(self) -> Optional[UserInfo]:
        """Get the user information."""
        raise NotImplementedError


class ContextVarUserProvider(UserProvider):
    default_user_info_context: ClassVar[ContextVar[UserInfo]] = ContextVar("user_info_context")

    def __init__(self, context: Optional[ContextVar[UserInfo]] = None):
        self.context = context or self.default_user_info_context

    async def get_user(self) -> Optional[UserInfo]:
        return self.context.get(None)


def resolve_user_from_headers(headers: Mapping[str, str],
                              object_id_header: str = "x-aml-oid",
                              tenant_id_header: str = "x-aml-tid") -> Optional[UserInfo]:
    object_id = headers.get(object_id_header, "")
    tenant_id = headers.get(tenant_id_header, "")

    if not object_id or not tenant_id:
        return None

    return UserInfo(object_id=object_id, tenant_id=tenant_id)
