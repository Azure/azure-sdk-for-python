# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from __future__ import annotations

import base64
import json
from typing import Any, cast, Optional

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import ClientAuthenticationError

from azure_postgresql_auth.errors import (
    ScopePermissionError,
    TokenDecodeError,
    UsernameExtractionError,
)

AZURE_DB_FOR_POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"
AZURE_MANAGEMENT_SCOPE = "https://management.azure.com/.default"


def get_entra_token(credential: TokenCredential, scope: str) -> str:
    """Acquires an Entra authentication token for Azure PostgreSQL synchronously.

    :param credential: Credential object used to obtain the token.
    :type credential: ~azure.core.credentials.TokenCredential
    :param scope: The scope for the token request.
    :type scope: str
    :return: The acquired authentication token to be used as the database password.
    :rtype: str
    """
    cred = credential.get_token(scope)
    return cred.token


async def get_entra_token_async(credential: AsyncTokenCredential, scope: str) -> str:
    """Asynchronously acquires an Entra authentication token for Azure PostgreSQL.

    :param credential: Asynchronous credential used to obtain the token.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param scope: The scope for the token request.
    :type scope: str
    :return: The acquired authentication token to be used as the database password.
    :rtype: str
    """
    cred = await credential.get_token(scope)
    return cred.token


def decode_jwt(token: str) -> dict[str, Any]:
    """Decodes a JWT token to extract its payload claims.

    :param token: The JWT token string in the standard three-part format.
    :type token: str
    :return: A dictionary containing the claims extracted from the token payload.
    :rtype: dict[str, Any]
    :raises ~azure_postgresql_auth.TokenDecodeError: If the token format is invalid or cannot be decoded.
    """
    try:
        payload = token.split(".")[1]
        padding = "=" * (-len(payload) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload + padding)
        return cast(dict[str, Any], json.loads(decoded_payload))
    except Exception as e:
        raise TokenDecodeError("Invalid JWT token format") from e


def parse_principal_name(xms_mirid: str) -> Optional[str]:
    """Parses the principal name from an Azure resource path.

    :param xms_mirid: The xms_mirid claim value containing the Azure resource path.
    :type xms_mirid: str
    :return: The extracted principal name, or None if parsing fails.
    :rtype: str or None
    """
    if not xms_mirid:
        return None

    last_slash_index = xms_mirid.rfind("/")
    if last_slash_index == -1:
        return None

    beginning = xms_mirid[:last_slash_index]
    principal_name = xms_mirid[last_slash_index + 1 :]

    if not principal_name or not beginning.lower().endswith(
        "providers/microsoft.managedidentity/userassignedidentities"
    ):
        return None

    return principal_name


def get_entra_conninfo(credential: TokenCredential) -> dict[str, str]:
    """Synchronously obtains connection information from Entra authentication for Azure PostgreSQL.

    This function acquires an access token from Microsoft Entra ID and extracts the username
    from the token claims. It tries multiple claim sources to determine the username.

    :param credential: The credential used for token acquisition.
    :type credential: ~azure.core.credentials.TokenCredential
    :return: A dictionary with 'user' and 'password' keys for database authentication.
    :rtype: dict[str, str]
    :raises ~azure_postgresql_auth.TokenDecodeError: If the JWT token cannot be decoded.
    :raises ~azure_postgresql_auth.UsernameExtractionError: If the username cannot be extracted.
    :raises ~azure_postgresql_auth.ScopePermissionError: If the management scope token cannot be acquired.
    """
    db_token = get_entra_token(credential, AZURE_DB_FOR_POSTGRES_SCOPE)
    db_claims = decode_jwt(db_token)
    xms_mirid = db_claims.get("xms_mirid")
    username = (
        parse_principal_name(xms_mirid)
        if isinstance(xms_mirid, str)
        else None or db_claims.get("upn") or db_claims.get("preferred_username") or db_claims.get("unique_name")
    )

    if not username:
        try:
            mgmt_token = get_entra_token(credential, AZURE_MANAGEMENT_SCOPE)
        except ClientAuthenticationError as e:
            raise ScopePermissionError("Failed to acquire token from management scope") from e
        mgmt_claims = decode_jwt(mgmt_token)
        xms_mirid = mgmt_claims.get("xms_mirid")
        username = (
            parse_principal_name(xms_mirid)
            if isinstance(xms_mirid, str)
            else None
            or mgmt_claims.get("upn")
            or mgmt_claims.get("preferred_username")
            or mgmt_claims.get("unique_name")
        )

    if not username:
        raise UsernameExtractionError(
            "Could not determine username from token claims. Ensure the identity has the proper Entra ID attributes."
        )

    return {"user": username, "password": db_token}


async def get_entra_conninfo_async(
    credential: AsyncTokenCredential,
) -> dict[str, str]:
    """Asynchronously obtains connection information from Entra authentication for Azure PostgreSQL.

    This function acquires an access token from Microsoft Entra ID and extracts the username
    from the token claims. It tries multiple claim sources to determine the username.

    :param credential: The async credential used for token acquisition.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :return: A dictionary with 'user' and 'password' keys for database authentication.
    :rtype: dict[str, str]
    :raises ~azure_postgresql_auth.TokenDecodeError: If the JWT token cannot be decoded.
    :raises ~azure_postgresql_auth.UsernameExtractionError: If the username cannot be extracted.
    :raises ~azure_postgresql_auth.ScopePermissionError: If the management scope token cannot be acquired.
    """
    db_token = await get_entra_token_async(credential, AZURE_DB_FOR_POSTGRES_SCOPE)
    db_claims = decode_jwt(db_token)
    xms_mirid = db_claims.get("xms_mirid")
    username = (
        parse_principal_name(xms_mirid)
        if isinstance(xms_mirid, str)
        else None or db_claims.get("upn") or db_claims.get("preferred_username") or db_claims.get("unique_name")
    )

    if not username:
        try:
            mgmt_token = await get_entra_token_async(credential, AZURE_MANAGEMENT_SCOPE)
        except ClientAuthenticationError as e:
            raise ScopePermissionError("Failed to acquire token from management scope") from e
        mgmt_claims = decode_jwt(mgmt_token)
        xms_mirid = mgmt_claims.get("xms_mirid")
        username = (
            parse_principal_name(xms_mirid)
            if isinstance(xms_mirid, str)
            else None
            or mgmt_claims.get("upn")
            or mgmt_claims.get("preferred_username")
            or mgmt_claims.get("unique_name")
        )

    if not username:
        raise UsernameExtractionError(
            "Could not determine username from token claims. Ensure the identity has the proper Entra ID attributes."
        )

    return {"user": username, "password": db_token}
