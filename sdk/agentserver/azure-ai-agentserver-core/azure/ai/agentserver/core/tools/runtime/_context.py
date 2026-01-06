# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod

from ..client._models import UserInfo


class UserProvider(ABC):
    """Base class for user providers."""

    @abstractmethod
    async def get_user(self) -> UserInfo:
        """Get the user information."""
        raise NotImplementedError
