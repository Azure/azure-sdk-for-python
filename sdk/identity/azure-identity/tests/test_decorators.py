# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from unittest.mock import patch

from azure.identity._internal.decorators import log_get_token
from azure.identity.aio._internal.decorators import log_get_token_async
import pytest


@log_get_token
def fake_method(*_, **__):
    return "token"


@log_get_token_async
async def fake_method_async(*_, **__):
    return "token"


def test_log_get_token():
    with patch("azure.identity._internal.decorators._LOGGER") as mock_logger:
        assert fake_method() == "token"
        mock_logger.log.assert_called_once_with(logging.INFO, "%s succeeded", "fake_method")


@pytest.mark.asyncio
async def test_log_get_token_async():
    with patch("azure.identity.aio._internal.decorators._LOGGER") as mock_logger:
        assert await fake_method_async() == "token"
        mock_logger.log.assert_called_once_with(logging.INFO, "%s succeeded", "fake_method_async")
