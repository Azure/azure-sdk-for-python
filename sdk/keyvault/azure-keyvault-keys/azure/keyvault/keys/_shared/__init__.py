# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
__all__ = []  # type: ignore
try:
    from .async_auth_challenge_policy import AsyncAuthChallengePolicy

    __all__.append("AsyncAuthChallengePolicy")
except (SyntaxError, ImportError):
    pass
