# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Internal utilities for azure-keyvault-secrets."""

from .._shared.challenge_auth_policy import ChallengeAuthPolicy
from .._shared._polling import DeleteRecoverPollingMethod, KeyVaultOperationPoller
from .._shared import parse_key_vault_id

__all__ = [
    "ChallengeAuthPolicy",
    "DeleteRecoverPollingMethod",
    "KeyVaultOperationPoller",
    "parse_key_vault_id",
]

try:
    from .._shared.async_challenge_auth_policy import AsyncChallengeAuthPolicy
    from .._shared._polling_async import AsyncKeyVaultOperationPoller, AsyncDeleteRecoverPollingMethod

    __all__.extend([
        "AsyncChallengeAuthPolicy",
        "AsyncKeyVaultOperationPoller",
        "AsyncDeleteRecoverPollingMethod",
    ])
except (SyntaxError, ImportError):
    pass
