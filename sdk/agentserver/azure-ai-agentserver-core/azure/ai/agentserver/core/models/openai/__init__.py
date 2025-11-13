# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Re-exports of OpenAI SDK response types.

This module re-exports types from the OpenAI SDK for convenience.
These types are fully documented in the OpenAI SDK documentation.

.. note::
   This module re-exports OpenAI SDK types. For detailed documentation,
   please refer to the `OpenAI Python SDK documentation <https://github.com/openai/openai-python>`_.
"""

# TODO: WE DONT WANT THIS
from openai.types.responses import *  # pylint: disable=unused-wildcard-import

__all__ = [name for name in globals() if not name.startswith("_")]  # type: ignore[var-annotated]
