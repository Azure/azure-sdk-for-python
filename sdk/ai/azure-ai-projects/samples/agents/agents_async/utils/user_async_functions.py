# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import os
import sys
import json
import datetime
from typing import Any, Callable, Set, Optional
from azure.ai.agents.telemetry import trace_function


# Add parent directory to sys.path to import user_functions
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from samples.utils.user_functions import fetch_current_datetime, fetch_weather, send_email


async def send_email_async(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email with the specified subject and body to the recipient.

    :param recipient (str): Email address of the recipient.
    :param subject (str): Subject of the email.
    :param body (str): Body content of the email.
    :return: Confirmation message.
    :rtype: str
    """
    await asyncio.sleep(1)
    return send_email(recipient, subject, body)


# The trace_func decorator will trace the function call and enable adding additional attributes
# to the span in the function implementation. Note that this will trace the function parameters and their values.
@trace_function()
async def fetch_current_datetime_async(format: Optional[str] = None) -> str:
    """
    Get the current time as a JSON string, optionally formatted.

    :param format (Optional[str]): The format in which to return the current time. Defaults to None, which uses a standard format.
    :return: The current time in JSON format.
    :rtype: str
    """
    await asyncio.sleep(1)
    current_time = datetime.datetime.now()

    # Use the provided format if available, else use a default format
    if format:
        time_format = format
    else:
        time_format = "%Y-%m-%d %H:%M:%S"

    time_json = json.dumps({"current_time": current_time.strftime(time_format)})
    return time_json


# Statically defined user functions for fast reference with send_email as async but the rest as sync
user_async_functions: Set[Callable[..., Any]] = {
    fetch_current_datetime_async,
    fetch_weather,
    send_email_async,
}
