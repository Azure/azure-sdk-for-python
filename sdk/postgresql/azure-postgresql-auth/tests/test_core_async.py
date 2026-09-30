# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Async unit tests for the core authentication module."""

from __future__ import annotations

import pytest

from azure_postgresql_auth.core import get_entra_conninfo_async
from azure_postgresql_auth.errors import TokenDecodeError

from utils import (
    TEST_USERS,
    MockAsyncTokenCredential,
    create_jwt_token_with_xms_mirid,
    create_valid_jwt_token,
)


class TestGetEntraConninfoAsync:
    """Tests for get_entra_conninfo_async function."""

    @pytest.mark.asyncio
    async def test_async_conninfo_with_upn_claim(self):
        """Test async: UPN claim extracted as username."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockAsyncTokenCredential(token)
        result = await get_entra_conninfo_async(credential)
        assert result["user"] == TEST_USERS["ENTRA_USER"]
        assert result["password"] == token

    @pytest.mark.asyncio
    async def test_async_conninfo_with_managed_identity(self):
        """Test async: managed identity xms_mirid claim parsed for username."""
        token = create_jwt_token_with_xms_mirid(TEST_USERS["MANAGED_IDENTITY_PATH"])
        credential = MockAsyncTokenCredential(token)
        result = await get_entra_conninfo_async(credential)
        assert result["user"] == TEST_USERS["MANAGED_IDENTITY_NAME"]

    @pytest.mark.asyncio
    async def test_async_conninfo_invalid_token_raises_error(self):
        """Test async: invalid token raises TokenDecodeError."""
        credential = MockAsyncTokenCredential("invalid-token")
        with pytest.raises(TokenDecodeError):
            await get_entra_conninfo_async(credential)
