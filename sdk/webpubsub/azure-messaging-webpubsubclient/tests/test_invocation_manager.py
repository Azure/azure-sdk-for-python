# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.messaging.webpubsubclient.models._models import (
    InvokeResponseMessage,
    InvocationManager,
    InvocationError,
)
from azure.messaging.webpubsubclient.models import WebPubSubDataType


class TestInvocationManager:
    """Test InvocationManager functionality"""

    def test_register_and_resolve(self):
        """Test registering and resolving invocations"""
        inv_mgr = InvocationManager()
        inv_id, entry = inv_mgr.register()

        assert inv_id == "1"
        assert entry is not None
        assert inv_mgr._entries.get(inv_id) is not None

        response = InvokeResponseMessage(
            invocation_id=inv_id,
            success=True,
            data_type=WebPubSubDataType.TEXT,
            data="result",
        )

        resolved = inv_mgr.resolve(response)
        assert resolved is True
        assert entry.result == response

    def test_register_custom_id(self):
        """Test registering with custom invocation ID"""
        inv_mgr = InvocationManager()
        inv_id, entry = inv_mgr.register("custom-id")

        assert inv_id == "custom-id"
        assert inv_mgr._entries.get("custom-id") is not None

    def test_register_duplicate_raises(self):
        """Test that registering duplicate ID raises InvocationError"""
        inv_mgr = InvocationManager()
        inv_mgr.register("same-id")

        with pytest.raises(InvocationError) as exc_info:
            inv_mgr.register("same-id")

        assert exc_info.value.invocation_id == "same-id"

    def test_reject(self):
        """Test rejecting an invocation"""
        inv_mgr = InvocationManager()
        inv_id, entry = inv_mgr.register()

        error = Exception("test error")
        rejected = inv_mgr.reject(inv_id, error)

        assert rejected is True
        assert entry.error == error

    def test_discard(self):
        """Test discarding an invocation"""
        inv_mgr = InvocationManager()
        inv_id, _ = inv_mgr.register()

        assert inv_mgr._entries.get(inv_id) is not None
        inv_mgr.discard(inv_id)
        assert inv_mgr._entries.get(inv_id) is None

    def test_reject_all(self):
        """Test rejecting all pending invocations"""
        inv_mgr = InvocationManager()
        inv_id1, entry1 = inv_mgr.register()
        inv_id2, entry2 = inv_mgr.register()

        inv_mgr.reject_all(lambda inv_id: InvocationError("disconnected", invocation_id=inv_id))

        assert entry1.error is not None
        assert entry2.error is not None
        assert len(inv_mgr._entries) == 0
