# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

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

"""Test fixtures for azure-cosmos-ai.

Until ``azure-cosmos`` 4.16.0b3 (PR #46902) is released, ``EmbeddingResult``
isn't available from ``azure.cosmos`` in our checkout. Inject a minimal stub
on import so the provider modules — which ``from azure.cosmos import
EmbeddingResult`` at module load — work in CI/local dev. Once the dependency
ships, this stub becomes a no-op (the real class wins).
"""

from dataclasses import dataclass
from typing import List, Optional

import azure.cosmos as _cosmos

if not hasattr(_cosmos, "EmbeddingResult"):

    @dataclass
    class EmbeddingResult:  # pylint: disable=too-few-public-methods
        vectors: List[List[float]]
        total_tokens: Optional[int] = None

    _cosmos.EmbeddingResult = EmbeddingResult  # type: ignore[attr-defined]
