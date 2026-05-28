# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from __future__ import annotations


class AzurePgEntraError(Exception):
    """Base class for all custom exceptions in the project."""


class TokenDecodeError(AzurePgEntraError):
    """Raised when a token value is invalid."""


class UsernameExtractionError(AzurePgEntraError):
    """Raised when username cannot be extracted from token."""


class CredentialValueError(AzurePgEntraError):
    """Raised when token credential is invalid."""


class EntraConnectionValueError(AzurePgEntraError):
    """Raised when Entra connection credentials are invalid."""


class ScopePermissionError(AzurePgEntraError):
    """Raised when the provided scope does not have sufficient permissions."""
