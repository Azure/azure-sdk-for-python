# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmbeddingResult:
    """Represents the result of an embedding generation call.

    :ivar vectors: The generated embedding vectors, one per input string, in
        the same order as the inputs. Each inner list holds the floating-point
        components of one vector as returned by the embedding service.
    :vartype vectors: List[List[float]]
    :ivar total_tokens: The total number of tokens consumed by the embedding call,
        if reported by the provider.
    :vartype total_tokens: Optional[int]
    :ivar latency: The end-to-end latency of the embedding call, in seconds,
        as measured by the provider. ``None`` if the provider does not report it.
    :vartype latency: Optional[float]
    """

    vectors: List[List[float]]
    total_tokens: Optional[int] = None
    latency: Optional[float] = None
