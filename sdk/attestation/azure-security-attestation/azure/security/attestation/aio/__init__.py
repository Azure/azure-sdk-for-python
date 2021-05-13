# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from .._generated.models import AttestationType

from ._client_async import AttestationClient
from ._administration_client_async import AttestationAdministrationClient
from .._models import (AttestationResponse,
    AttestationSigner,
    AttestationToken, 
    AttestationSigningKey, 
    AttestationData, 
    PolicyResult, 
    AttestationResult, 
    TpmAttestationResponse, 
    TpmAttestationRequest, 
    AttestationTokenValidationException,
    PolicyCertificatesModificationResult,
    AttestationType,
    PolicyModification,
    StoredAttestationPolicy,
    CertificateModification)
from .._configuration import TokenValidationOptions
from .._version import VERSION

__version__ = VERSION
__all__ = [
    'AttestationClient',
    'AttestationAdministrationClient',
    'AttestationType',
    'AttestationToken',
    'AttestationSigner',
    'AttestationResponse',
    'AttestationResult',
    'AttestationData',
    'TokenValidationOptions',
    'StoredAttestationPolicy',
    'PolicyResult',
    'CertificateModification',
    'AttestationSigningKey',
    'TpmAttestationRequest',
    'TpmAttestationResponse',
    'PolicyModification',
    'PolicyCertificatesModificationResult',
    'AttestationTokenValidationException',
]


try:
    from ._patch import patch_sdk  # type: ignore
    patch_sdk()
except ImportError:
    pass
