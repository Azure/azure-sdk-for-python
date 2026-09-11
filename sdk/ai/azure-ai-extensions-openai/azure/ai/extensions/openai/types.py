# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""OpenAI SDK type re-exports used by Azure AI packages."""

try:
    from openai.types.responses import *  # type: ignore # noqa: F401,F403
    from openai.types.responses.response_input_param import ResponseInputParam
except ImportError:
    pass

__all__ = [
    name
    for name in list(globals())
    if not name.startswith("_") and name not in {"annotations"}
]
