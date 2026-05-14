# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EmbeddingResult:
    """Represents the result of an embedding generation call.

    :ivar vectors: The generated ``float32`` embedding vectors, one per input string,
        in the same order as the inputs.
    :vartype vectors: List[List[float]]
    :ivar total_tokens: The total number of tokens consumed by the embedding call.
    :vartype total_tokens: Optional[int]
    """

    vectors: List[List[float]]
    total_tokens: Optional[int] = None
