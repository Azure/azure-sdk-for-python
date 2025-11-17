# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=line-too-long
"""
Protocol definitions for OpenAI Response Input parameters.
These protocols define the interface for response input items without requiring
direct dependencies on the OpenAI SDK types.
"""

# TODO : Replace Protocols with accurate info

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ResponseInputItemParam(Protocol):
    """
    Protocol for response input item parameters.
    
    This protocol describes the interface for any item that can be used as input
    to a response, such as messages, function calls, and function call outputs.
    It acts as a dict-like interface allowing .get() access to item properties.
    """
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the item by key.
        
        :param key: The key to retrieve.
        :type key: str
        :param default: The default value if key is not found.
        :type default: Any
        :return: The value associated with the key, or default if not found.
        :rtype: Any
        """
        ...


@runtime_checkable
class ResponseFunctionToolCallParam(Protocol):
    """
    Protocol for function tool call parameters.
    
    This protocol describes the interface for function tool calls, typically
    containing fields like call_id, name, and arguments.
    """
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the function tool call by key.
        
        :param key: The key to retrieve.
        :type key: str
        :param default: The default value if key is not found.
        :type default: Any
        :return: The value associated with the key, or default if not found.
        :rtype: Any
        """
        ...


@runtime_checkable
class FunctionCallOutput(Protocol):
    """
    Protocol for function call output parameters.
    
    This protocol describes the interface for function call outputs, typically
    containing fields like call_id and output.
    """
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the function call output by key.
        
        :param key: The key to retrieve.
        :type key: str
        :param default: The default value if key is not found.
        :type default: Any
        :return: The value associated with the key, or default if not found.
        :rtype: Any
        """
        ...


__all__ = [
    "ResponseInputItemParam",
    "ResponseFunctionToolCallParam",
    "FunctionCallOutput",
]
