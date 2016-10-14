#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

from azure.keyvault import http_bearer_challenge_cache as HttpBearerChallengeCache
from .http_bearer_challenge import HttpBearerChallenge
from .key_vault_client import KeyVaultClient
from .key_vault_authentication import KeyVaultAuthentication
from .key_vault_id import \
    (create_object_id, parse_object_id,
     create_key_id, parse_key_id,
     create_secret_id, parse_secret_id,
     create_certificate_id, parse_certificate_id,
     create_certificate_operation_id, parse_certificate_operation_id,
     create_certificate_issuer_id, parse_certificate_issuer_id)
from azure.keyvault.generated.version import VERSION

__all__ = [
    'HttpBearerChallengeCache',
    'HttpBearerChallenge',
    'KeyVaultClient',
    'KeyVaultAuthentication',
    'create_object_id',
    'parse_object_id',
    'create_key_id',
    'parse_key_id',
    'create_secret_id',
    'parse_secret_id',
    'create_certificate_id',
    'parse_certificate_id',
    'create_certificate_operation_id',
    'parse_certificate_operation_id',
    'create_certificate_issuer_id',
    'parse_certificate_issuer_id'
]

__version__ = VERSION
