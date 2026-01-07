# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextvars import ContextVar
from typing import Awaitable, Callable, Optional

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

from ._user import ContextVarUserProvider, resolve_user_from_headers
from ..client._models import UserInfo

_UserContextType = ContextVar[Optional[UserInfo]]
_ResolverType = Callable[[Request], Awaitable[Optional[UserInfo]]]

class UserInfoContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, user_info_var: _UserContextType, user_resolver: _ResolverType):
        super().__init__(app)
        self._user_info_var = user_info_var
        self._user_resolver = user_resolver

    @classmethod
    def install(cls,
                app: Starlette,
                user_context: Optional[_UserContextType] = None,
                user_resolver: Optional[_ResolverType] = None):
        app.add_middleware(UserInfoContextMiddleware,
                           user_info_var=user_context or ContextVarUserProvider.default_user_info_context,
                           user_resolver=user_resolver or cls._default_user_resolver)

    @staticmethod
    async def _default_user_resolver(request: Request) -> Optional[UserInfo]:
        return resolve_user_from_headers(request.headers)

    async def dispatch(self, request: Request, call_next):
        user = await self._user_resolver(request)
        token = self._user_info_var.set(user)
        try:
            return await call_next(request)
        finally:
            self._user_info_var.reset(token)
