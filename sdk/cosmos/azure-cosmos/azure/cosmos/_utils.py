# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal Helper functions in the Azure Cosmos database service.
"""

import platform
import re
import base64
import json
import time
import os
from typing import Any, Optional, Tuple
from ._constants import _Constants
from ._version import VERSION

# cspell:ignore ppcb
# pylint: disable=protected-access

def get_user_agent(suffix: Optional[str] = None) -> str:
    os_name = safe_user_agent_header(platform.platform())
    python_version = safe_user_agent_header(platform.python_version())
    user_agent = "azsdk-python-cosmos/{} Python/{} ({})".format(VERSION, python_version, os_name)
    if suffix:
        user_agent += f" {suffix}"
    return user_agent

def get_user_agent_async(suffix: Optional[str] = None) -> str:
    os_name = safe_user_agent_header(platform.platform())
    python_version = safe_user_agent_header(platform.python_version())
    user_agent = "azsdk-python-cosmos-async/{} Python/{} ({})".format(VERSION, python_version, os_name)
    if suffix:
        user_agent += f" {suffix}"
    return user_agent


def safe_user_agent_header(s: Optional[str] = None) -> str:
    if s is None:
        s = "unknown"
    # remove all white spaces
    s = re.sub(r"\s+", "", s)
    if not s:
        s = "unknown"
    return s


def get_index_metrics_info(delimited_string: Optional[str] = None) -> dict[str, Any]:
    if delimited_string is None:
        return {}
    try:
        # Decode the base64 string to bytes
        bytes_string = base64.b64decode(delimited_string)
        # Decode the bytes to a string using UTF-8 encoding
        decoded_string = bytes_string.decode('utf-8')

        # Python's json.loads method is used for deserialization
        result = json.loads(decoded_string) or {}
        return result
    except (json.JSONDecodeError, ValueError):
        return {}

def current_time_millis() -> int:
    return int(round(time.time() * 1000))

def add_args_to_kwargs(
        arg_names: list[str],
        args: Tuple[Any, ...],
        kwargs: dict[str, Any]
    ) -> None:
    """Add positional arguments(args) to keyword argument dictionary(kwargs) using names in arg_names as keys.
    To be backward-compatible, some expected positional arguments has to be allowed. This method will verify number of
    maximum positional arguments and add them to the keyword argument dictionary(kwargs)

    :param list[str] arg_names: The names of positional arguments.
    :param Tuple[Any, ...] args: The tuple of positional arguments.
    :param dict[str, Any] kwargs: The dictionary of keyword arguments as reference. This dictionary will be updated.
    """

    if len(args) > len(arg_names):
        raise ValueError(f"Positional argument is out of range. Expected {len(arg_names)} arguments, "
                         f"but got {len(args)} instead. Please review argument list in API documentation.")

    for name, arg in zip(arg_names, args):
        if name in kwargs:
            raise ValueError(f"{name} cannot be used as positional and keyword argument at the same time.")
        kwargs[name] = arg


def format_list_with_and(items: list[str]) -> str:
    """Format a list of items into a string with commas and 'and' for the last item.

    :param list[str] items: The list of items to format.
    :return: A formatted string with items separated by commas and 'and' before the last item.
    :rtype: str
    """
    formatted_items = ""
    quoted = [f"'{item}'" for item in items]
    if len(quoted) > 2:
        formatted_items = ", ".join(quoted[:-1]) + ", and " + quoted[-1]
    elif len(quoted) == 2:
        formatted_items = " and ".join(quoted)
    elif quoted:
        formatted_items = quoted[0]
    return formatted_items

def verify_exclusive_arguments(
        exclusive_keys: list[str],
        **kwargs: dict[str, Any]) -> None:
    """Verify if exclusive arguments are present in kwargs.
    For some Cosmos SDK APIs, some arguments are exclusive, or cannot be used at the same time. This method will verify
    that and raise an error if exclusive arguments are present.

    :param list[str] exclusive_keys: The names of exclusive arguments.
    """
    keys_in_kwargs = [key for key in exclusive_keys if key in kwargs and kwargs[key] is not None]

    if len(keys_in_kwargs) > 1:
        raise ValueError(f"{format_list_with_and(keys_in_kwargs)} are exclusive parameters, "
                         f"please only set one of them.")

def valid_key_value_exist(
        kwargs: dict[str, Any],
        key: str,
        invalid_value: Any = None) -> bool:
    """Check if a valid key and value exists in kwargs. By default, it checks if the value is not None.

    :param dict[str, Any] kwargs: The dictionary of keyword arguments.
    :param str key: The key to check.
    :param Any invalid_value: The value that is considered invalid. Default is None.
    :return: True if the key exists and its value is not None, False otherwise.
    :rtype: bool
    """
    return key in kwargs and kwargs[key] is not invalid_value


def get_user_agent_features(global_endpoint_manager: Any) -> str:
    """
    Check the account and client configurations in order to add feature flags
    to the user agent using bitmask logic and hex encoding (matching .NET/Java).
    
    :param Any global_endpoint_manager: The GlobalEndpointManager instance.
    :return: A string representing the user agent feature flags.
    :rtype: str
    """
    feature_flag = 0
    # Bitwise OR for feature flags
    if global_endpoint_manager._database_account_cache is not None:
        if global_endpoint_manager._database_account_cache._EnablePerPartitionFailoverBehavior is True:
            feature_flag |= _Constants.UserAgentFeatureFlags.PER_PARTITION_AUTOMATIC_FAILOVER
    ppcb_check = os.environ.get(
        _Constants.CIRCUIT_BREAKER_ENABLED_CONFIG,
        _Constants.CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT
    ).lower()
    if ppcb_check == "true" or feature_flag > 0:
        feature_flag |= _Constants.UserAgentFeatureFlags.PER_PARTITION_CIRCUIT_BREAKER
    return f"| F{feature_flag:X}" if feature_flag > 0 else ""
