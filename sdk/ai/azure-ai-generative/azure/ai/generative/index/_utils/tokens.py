# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tools for estimating the number of tokens in a string."""
import contextlib
import os
from functools import lru_cache
from pathlib import Path
from typing import Callable, Optional

utils_path = Path(__file__).parent
tiktoken_encodings_path = utils_path / "encodings"


@contextlib.contextmanager
def tiktoken_cache_dir(cache_dir: Optional[Path] = "default"):
    """
    Set TikToken cache directory in environment while in context.

    Default cache_dir is the encodings cached in `azure.ai.generative.index._utils.encodings`.
    cl100k_base and gpt2 encodings are cached.
    """
    if cache_dir == "default":
        cache_dir = tiktoken_encodings_path

    old_cache = os.environ.get("TIKTOKEN_CACHE_DIR")
    old_data_dym_cache = os.environ.get("DATA_GYM_CACHE_DIR")

    if cache_dir is None:
        del os.environ["TIKTOKEN_CACHE_DIR"]
        del os.environ["DATA_GYM_CACHE_DIR"]
    else:
        os.environ["TIKTOKEN_CACHE_DIR"] = str(cache_dir)
        os.environ["DATA_GYM_CACHE_DIR"] = str(cache_dir)

    try:
        yield
    finally:
        if old_cache is None:
            del os.environ["TIKTOKEN_CACHE_DIR"]
        else:
            os.environ["TIKTOKEN_CACHE_DIR"] = old_cache
        if old_data_dym_cache is None:
            del os.environ["DATA_GYM_CACHE_DIR"]
        else:
            os.environ["DATA_GYM_CACHE_DIR"] = old_data_dym_cache


class TikTokenEstimator:
    """TikToken Estimator."""

    def __init__(self, encoding: str = "cl100k_base"):
        """Initialize TikTokenEstimator."""
        import tiktoken

        with tiktoken_cache_dir():
            self.encoder = tiktoken.get_encoding(encoding)

    def estimate(self, text: str) -> int:
        """Estimate the number of tokens in the text."""
        return len(self.encoder.encode(text, disallowed_special=(), allowed_special="all"))

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate the text to the max number of tokens."""
        return self.encoder.decode(self.encoder.encode(text, disallowed_special=(), allowed_special="all")[:max_tokens])


@lru_cache(maxsize=1)
def token_length_function(encoding: str = "cl100k_base") -> Callable[[str], int]:
    """Get the token length function."""
    return TikTokenEstimator(encoding).estimate
