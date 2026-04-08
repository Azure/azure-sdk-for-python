# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

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

"""Optimized JSON serialization/deserialization for the Azure Cosmos database service.

Uses orjson when available for significantly faster encoding/decoding of float-heavy
payloads (e.g., vector search queries with 768-float embeddings). Falls back to
stdlib json when orjson is not installed.
"""

import json as _json

try:
    import orjson as _orjson
except ImportError:
    _orjson = None  # type: ignore[assignment]


def dumps(data, **kwargs):
    """Serialize data to a JSON string.

    Uses orjson when available for better performance.
    Produces compact output (no extra whitespace) to match the existing
    ``json.dumps(data, separators=(",", ":"))`` behavior.

    :param data: The data to serialize.
    :returns: JSON string.
    :rtype: str
    """
    if _orjson is not None:
        # orjson.dumps returns bytes; decode to str for compatibility
        return _orjson.dumps(data).decode("utf-8")
    return _json.dumps(data, separators=(",", ":"))


def loads(data):
    """Deserialize a JSON string to Python objects.

    Uses orjson when available for better performance.

    :param data: JSON string or bytes.
    :returns: Deserialized Python object.
    """
    if _orjson is not None:
        return _orjson.loads(data)
    return _json.loads(data)
