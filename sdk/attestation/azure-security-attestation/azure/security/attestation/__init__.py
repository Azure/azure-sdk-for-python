# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._client import AttestationClient
from ._administration_client import AttestationAdministrationClient
from ._models import (
    AttestationSigner,
    AttestationToken,
    AttestationPolicyResult,
    AttestationResult,
    AttestationTokenValidationException,
    AttestationPolicyCertificateResult,
    PolicyModification,
    CertificateModification,
    AttestationPolicyToken,
)
from ._generated.models import AttestationType
from ._version import VERSION

__version__ = VERSION
__all__ = [
    "AttestationClient",
    "AttestationAdministrationClient",
    "AttestationType",
    "AttestationToken",
    "AttestationSigner",
    "AttestationPolicyResult",
    "AttestationPolicyCertificateResult",
    "AttestationResult",
    "CertificateModification",
    "PolicyModification",
    "AttestationTokenValidationException",
    "AttestationPolicyToken",
]

try:
    from ._patch import patch_sdk  # type: ignore

    patch_sdk()
except ImportError:
    pass
