# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _user.py - testing public methods of ContextVarUserProvider and resolve_user_from_headers."""
import pytest
from contextvars import ContextVar

from azure.ai.agentserver.core.tools.runtime._user import (
    ContextVarUserProvider,
    resolve_user_from_headers,
)
from azure.ai.agentserver.core.tools.client._models import UserInfo


class TestContextVarUserProvider:
    """Tests for ContextVarUserProvider public methods."""

    @pytest.mark.asyncio
    async def test_get_user_returns_none_when_context_not_set(self):
        """Test get_user returns None when context variable is not set."""
        custom_context = ContextVar("test_user_context")
        provider = ContextVarUserProvider(context=custom_context)

        result = await provider.get_user()

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_returns_user_when_context_is_set(self, sample_user_info):
        """Test get_user returns UserInfo when context variable is set."""
        custom_context = ContextVar("test_user_context")
        custom_context.set(sample_user_info)
        provider = ContextVarUserProvider(context=custom_context)

        result = await provider.get_user()

        assert result is sample_user_info
        assert result.object_id == "test-object-id"
        assert result.tenant_id == "test-tenant-id"

    @pytest.mark.asyncio
    async def test_uses_default_context_when_none_provided(self, sample_user_info):
        """Test that default context is used when no context is provided."""
        # Set value in default context
        ContextVarUserProvider.default_user_info_context.set(sample_user_info)
        provider = ContextVarUserProvider()

        result = await provider.get_user()

        assert result is sample_user_info

    @pytest.mark.asyncio
    async def test_different_providers_share_same_default_context(self, sample_user_info):
        """Test that different providers using default context share the same value."""
        ContextVarUserProvider.default_user_info_context.set(sample_user_info)
        provider1 = ContextVarUserProvider()
        provider2 = ContextVarUserProvider()

        result1 = await provider1.get_user()
        result2 = await provider2.get_user()

        assert result1 is result2 is sample_user_info

    @pytest.mark.asyncio
    async def test_custom_context_isolation(self, sample_user_info):
        """Test that custom contexts are isolated from each other."""
        context1 = ContextVar("context1")
        context2 = ContextVar("context2")
        user2 = UserInfo(object_id="other-oid", tenant_id="other-tid")

        context1.set(sample_user_info)
        context2.set(user2)

        provider1 = ContextVarUserProvider(context=context1)
        provider2 = ContextVarUserProvider(context=context2)

        result1 = await provider1.get_user()
        result2 = await provider2.get_user()

        assert result1 is sample_user_info
        assert result2 is user2
        assert result1 is not result2


class TestResolveUserFromHeaders:
    """Tests for resolve_user_from_headers public function."""

    def test_returns_user_info_when_both_headers_present(self):
        """Test returns UserInfo when both object_id and tenant_id headers are present."""
        headers = {
            "x-aml-oid": "user-object-id",
            "x-aml-tid": "user-tenant-id"
        }

        result = resolve_user_from_headers(headers)

        assert result is not None
        assert isinstance(result, UserInfo)
        assert result.object_id == "user-object-id"
        assert result.tenant_id == "user-tenant-id"

    def test_returns_none_when_object_id_missing(self):
        """Test returns None when object_id header is missing."""
        headers = {"x-aml-tid": "user-tenant-id"}

        result = resolve_user_from_headers(headers)

        assert result is None

    def test_returns_none_when_tenant_id_missing(self):
        """Test returns None when tenant_id header is missing."""
        headers = {"x-aml-oid": "user-object-id"}

        result = resolve_user_from_headers(headers)

        assert result is None

    def test_returns_none_when_both_headers_missing(self):
        """Test returns None when both headers are missing."""
        headers = {}

        result = resolve_user_from_headers(headers)

        assert result is None

    def test_returns_none_when_object_id_is_empty(self):
        """Test returns None when object_id is empty string."""
        headers = {
            "x-aml-oid": "",
            "x-aml-tid": "user-tenant-id"
        }

        result = resolve_user_from_headers(headers)

        assert result is None

    def test_returns_none_when_tenant_id_is_empty(self):
        """Test returns None when tenant_id is empty string."""
        headers = {
            "x-aml-oid": "user-object-id",
            "x-aml-tid": ""
        }

        result = resolve_user_from_headers(headers)

        assert result is None

    def test_custom_header_names(self):
        """Test using custom header names for object_id and tenant_id."""
        headers = {
            "custom-oid-header": "custom-object-id",
            "custom-tid-header": "custom-tenant-id"
        }

        result = resolve_user_from_headers(
            headers,
            object_id_header="custom-oid-header",
            tenant_id_header="custom-tid-header"
        )

        assert result is not None
        assert result.object_id == "custom-object-id"
        assert result.tenant_id == "custom-tenant-id"

    def test_default_headers_not_matched_with_custom_headers(self):
        """Test that default headers are not matched when custom headers are specified."""
        headers = {
            "x-aml-oid": "default-object-id",
            "x-aml-tid": "default-tenant-id"
        }

        result = resolve_user_from_headers(
            headers,
            object_id_header="custom-oid",
            tenant_id_header="custom-tid"
        )

        assert result is None

    def test_case_sensitive_header_matching(self):
        """Test that header matching is case-sensitive."""
        headers = {
            "X-AML-OID": "user-object-id",
            "X-AML-TID": "user-tenant-id"
        }

        # Default headers are lowercase, so these should not match
        result = resolve_user_from_headers(headers)

        assert result is None

    def test_with_mapping_like_object(self):
        """Test with a mapping-like object that supports .get()."""
        class HeadersMapping:
            def __init__(self, data):
                self._data = data

            def get(self, key, default=""):
                return self._data.get(key, default)

        headers = HeadersMapping({
            "x-aml-oid": "mapping-object-id",
            "x-aml-tid": "mapping-tenant-id"
        })

        result = resolve_user_from_headers(headers)

        assert result is not None
        assert result.object_id == "mapping-object-id"
        assert result.tenant_id == "mapping-tenant-id"
