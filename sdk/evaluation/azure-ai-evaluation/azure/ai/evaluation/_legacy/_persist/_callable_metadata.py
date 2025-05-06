# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TypedDict, Dict, Any
from typing_extensions import NotRequired


class CallableArgMetadata(TypedDict):
    """Metadata for a callable argument, or output."""
    type: str
    """The type of the argument."""
    default: NotRequired[str]
    """Default value of the argument (optional)."""


class CallableMetadata(TypedDict):
    """Metadata for a callable."""
    entry: str
    """The entry point of the callable. This is typically the function name, or ClassName:FunctionName."""
    inputs: NotRequired[Dict[str, CallableArgMetadata]]
    """The input arguments for the callable."""
    outputs: NotRequired[Dict[str, CallableArgMetadata]]
    """The outputs for the callable."""
    init: NotRequired[Dict[str, CallableArgMetadata]]
    """The arguments for the callable's constructor (if applicable)."""
    environment: NotRequired[Dict[str, Any]]
    """Any environment variables or settings for the callable."""