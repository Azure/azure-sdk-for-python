# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextvars import ContextVar
from abc import ABC, abstractmethod
from typing import ClassVar, Optional

from ..client._models import UserInfo


class UserProvider(ABC):
    """Base class for user providers."""

    @abstractmethod
    async def get_user(self) -> Optional[UserInfo]:
        """Get the user information."""
        raise NotImplementedError


class ContextVarUserProvider(UserProvider):
    user_info_context: ClassVar[ContextVar] = ContextVar("user_info_context", default=None)
