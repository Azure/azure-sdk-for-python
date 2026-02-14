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
        """Get the user information.

        :return: The user information or None if not found.
        :rtype: Optional[UserInfo]
        """
        raise NotImplementedError


class ContextVarUserProvider(UserProvider):
    """User provider that retrieves user information from a ContextVar."""
    default_user_info_context: ClassVar[ContextVar[UserInfo]] = ContextVar("user_info_context")

    def __init__(self, context: Optional[ContextVar[UserInfo]] = None):
        self.context = context or self.default_user_info_context

    async def get_user(self) -> Optional[UserInfo]:
        """Get the user information from the context variable.

        :return: The user information or None if not found.
        :rtype: Optional[UserInfo]
        """
        return self.context.get(None)


def resolve_user_from_headers(headers: Mapping[str, str],
                              object_id_header: str = "x-aml-oid",
                              tenant_id_header: str = "x-aml-tid") -> Optional[UserInfo]:
    """Resolve user information from HTTP headers.

    :param headers: The HTTP headers.
    :type headers: Mapping[str, str]
    :param object_id_header: The header name for the object ID.
    :type object_id_header: str
    :param tenant_id_header: The header name for the tenant ID.
    :type tenant_id_header: str
    :return: The user information or None if not found.
    :rtype: Optional[UserInfo]
    """
    object_id = headers.get(object_id_header, "")
    tenant_id = headers.get(tenant_id_header, "")

    if not object_id or not tenant_id:
        return None

    return UserInfo(object_id=object_id, tenant_id=tenant_id)
