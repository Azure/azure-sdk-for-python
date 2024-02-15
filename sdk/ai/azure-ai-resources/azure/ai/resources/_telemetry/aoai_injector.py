# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import functools
import importlib
import logging
import os
from importlib.metadata import version

from azure.ai.resources.constants._common import USER_AGENT_HEADER
from azure.ai.resources._user_agent import USER_AGENT

IS_LEGACY_OPENAI = version("openai").startswith("0.")


"""Code modified from promptflow SDK openai_injector.py to inject telemetry headers into OpenAI API requests. """


def get_aoai_telemetry_headers() -> dict:
    """Get the http headers for AOAI request.

    The header, whose name starts with "ms-azure-ai-" or "x-ms-", is used to track the request in AOAI. The
    value in this dict will be recorded as telemetry, so please do not put any sensitive information in it.

    Returns:
        A dictionary of http headers.
    """
    return {USER_AGENT_HEADER: USER_AGENT}


def inject_openai_headers(f):
    def inject_headers(kwargs):
        # Inject headers from operation context, overwrite injected header with headers from kwargs.
        injected_headers = get_aoai_telemetry_headers()
        original_headers = kwargs.get("headers" if IS_LEGACY_OPENAI else "extra_headers")
        if original_headers and isinstance(original_headers, dict):
            injected_headers.update(original_headers)
        kwargs["headers" if IS_LEGACY_OPENAI else "extra_headers"] = injected_headers

    if asyncio.iscoroutinefunction(f):

        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            inject_headers(kwargs)
            return await f(*args, **kwargs)

    else:

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            inject_headers(kwargs)
            return f(*args, **kwargs)

    return wrapper
