# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _starlette.py - testing public methods of UserInfoContextMiddleware."""
import pytest
from contextvars import ContextVar
from unittest.mock import AsyncMock, MagicMock

from azure.ai.agentserver.core.tools.client._models import UserInfo


class TestUserInfoContextMiddlewareInstall:
    """Tests for UserInfoContextMiddleware.install class method."""

    def test_install_adds_middleware_to_starlette_app(self):
        """Test install adds middleware to Starlette application."""
        # Import here to avoid requiring starlette when not needed
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        mock_app = MagicMock()

        UserInfoContextMiddleware.install(mock_app)

        mock_app.add_middleware.assert_called_once()
        call_args = mock_app.add_middleware.call_args
        assert call_args[0][0] == UserInfoContextMiddleware

    def test_install_uses_default_context_when_none_provided(self):
        """Test install uses default user context when none is provided."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware
        from azure.ai.agentserver.core.tools.runtime._user import ContextVarUserProvider

        mock_app = MagicMock()

        UserInfoContextMiddleware.install(mock_app)

        call_kwargs = mock_app.add_middleware.call_args[1]
        assert call_kwargs["user_info_var"] is ContextVarUserProvider.default_user_info_context

    def test_install_uses_custom_context(self):
        """Test install uses custom user context when provided."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        mock_app = MagicMock()
        custom_context = ContextVar("custom_context")

        UserInfoContextMiddleware.install(mock_app, user_context=custom_context)

        call_kwargs = mock_app.add_middleware.call_args[1]
        assert call_kwargs["user_info_var"] is custom_context

    def test_install_uses_custom_resolver(self):
        """Test install uses custom user resolver when provided."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        mock_app = MagicMock()

        async def custom_resolver(request):
            return UserInfo(object_id="custom-oid", tenant_id="custom-tid")

        UserInfoContextMiddleware.install(mock_app, user_resolver=custom_resolver)

        call_kwargs = mock_app.add_middleware.call_args[1]
        assert call_kwargs["user_resolver"] is custom_resolver


class TestUserInfoContextMiddlewareDispatch:
    """Tests for UserInfoContextMiddleware.dispatch method."""

    @pytest.mark.asyncio
    async def test_dispatch_sets_user_in_context(self):
        """Test dispatch sets user info in context variable."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        user_context = ContextVar("test_context")
        user_info = UserInfo(object_id="test-oid", tenant_id="test-tid")

        async def mock_resolver(request):
            return user_info

        # Create a simple mock app
        mock_app = AsyncMock()

        middleware = UserInfoContextMiddleware(
            app=mock_app,
            user_info_var=user_context,
            user_resolver=mock_resolver
        )

        mock_request = MagicMock()
        captured_user = None

        async def call_next(request):
            nonlocal captured_user
            captured_user = user_context.get(None)
            return MagicMock()

        await middleware.dispatch(mock_request, call_next)

        assert captured_user is user_info

    @pytest.mark.asyncio
    async def test_dispatch_resets_context_after_request(self):
        """Test dispatch resets context variable after request completes."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        user_context = ContextVar("test_context")
        original_user = UserInfo(object_id="original-oid", tenant_id="original-tid")
        user_context.set(original_user)

        new_user = UserInfo(object_id="new-oid", tenant_id="new-tid")

        async def mock_resolver(request):
            return new_user

        mock_app = AsyncMock()

        middleware = UserInfoContextMiddleware(
            app=mock_app,
            user_info_var=user_context,
            user_resolver=mock_resolver
        )

        mock_request = MagicMock()

        async def call_next(request):
            # During request, should have new_user
            assert user_context.get(None) is new_user
            return MagicMock()

        await middleware.dispatch(mock_request, call_next)

        # After request, context should be reset to original value
        assert user_context.get(None) is original_user

    @pytest.mark.asyncio
    async def test_dispatch_resets_context_on_exception(self):
        """Test dispatch resets context even when call_next raises exception."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        user_context = ContextVar("test_context")
        original_user = UserInfo(object_id="original-oid", tenant_id="original-tid")
        user_context.set(original_user)

        new_user = UserInfo(object_id="new-oid", tenant_id="new-tid")

        async def mock_resolver(request):
            return new_user

        mock_app = AsyncMock()

        middleware = UserInfoContextMiddleware(
            app=mock_app,
            user_info_var=user_context,
            user_resolver=mock_resolver
        )

        mock_request = MagicMock()

        async def call_next(request):
            raise RuntimeError("Request failed")

        with pytest.raises(RuntimeError, match="Request failed"):
            await middleware.dispatch(mock_request, call_next)

        # Context should still be reset to original
        assert user_context.get(None) is original_user

    @pytest.mark.asyncio
    async def test_dispatch_handles_none_user(self):
        """Test dispatch handles None user from resolver."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        user_context = ContextVar("test_context")

        async def mock_resolver(request):
            return None

        mock_app = AsyncMock()

        middleware = UserInfoContextMiddleware(
            app=mock_app,
            user_info_var=user_context,
            user_resolver=mock_resolver
        )

        mock_request = MagicMock()
        captured_user = "not_set"

        async def call_next(request):
            nonlocal captured_user
            captured_user = user_context.get("default")
            return MagicMock()

        await middleware.dispatch(mock_request, call_next)

        assert captured_user is None

    @pytest.mark.asyncio
    async def test_dispatch_calls_resolver_with_request(self):
        """Test dispatch calls user resolver with the request object."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        user_context = ContextVar("test_context")
        captured_request = None

        async def mock_resolver(request):
            nonlocal captured_request
            captured_request = request
            return UserInfo(object_id="oid", tenant_id="tid")

        mock_app = AsyncMock()

        middleware = UserInfoContextMiddleware(
            app=mock_app,
            user_info_var=user_context,
            user_resolver=mock_resolver
        )

        mock_request = MagicMock()
        mock_request.url = "https://test.com/api"

        async def call_next(request):
            return MagicMock()

        await middleware.dispatch(mock_request, call_next)

        assert captured_request is mock_request


class TestUserInfoContextMiddlewareDefaultResolver:
    """Tests for UserInfoContextMiddleware default resolver."""

    @pytest.mark.asyncio
    async def test_default_resolver_extracts_user_from_headers(self):
        """Test default resolver extracts user info from request headers."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        mock_request = MagicMock()
        mock_request.headers = {
            "x-aml-oid": "header-object-id",
            "x-aml-tid": "header-tenant-id"
        }

        result = await UserInfoContextMiddleware._default_user_resolver(mock_request)

        assert result is not None
        assert result.object_id == "header-object-id"
        assert result.tenant_id == "header-tenant-id"

    @pytest.mark.asyncio
    async def test_default_resolver_returns_none_when_headers_missing(self):
        """Test default resolver returns None when required headers are missing."""
        from azure.ai.agentserver.core.tools.runtime._starlette import UserInfoContextMiddleware

        mock_request = MagicMock()
        mock_request.headers = {}

        result = await UserInfoContextMiddleware._default_user_resolver(mock_request)

        assert result is None
