# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    Action,
    AdministratorDetails,
    BackupCertificateResult,
    CertificateAttributes,
    CertificateBundle,
    CertificateCreateParameters,
    CertificateImportParameters,
    CertificateIssuerItem,
    CertificateIssuerSetParameters,
    CertificateIssuerUpdateParameters,
    CertificateItem,
    CertificateMergeParameters,
    CertificateOperation,
    CertificateOperationUpdateParameter,
    CertificatePolicy,
    CertificateRestoreParameters,
    CertificateUpdateParameters,
    Contact,
    Contacts,
    DeletedCertificateBundle,
    DeletedCertificateItem,
    IssuerAttributes,
    IssuerBundle,
    IssuerCredentials,
    IssuerParameters,
    KeyProperties,
    KeyVaultError,
    KeyVaultErrorError,
    LifetimeAction,
    OrganizationDetails,
    SecretProperties,
    SubjectAlternativeNames,
    Trigger,
    X509CertificateProperties,
)

from ._enums import (  # type: ignore
    CertificatePolicyAction,
    DeletionRecoveryLevel,
    JsonWebKeyCurveName,
    JsonWebKeyType,
    KeyUsageType,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "Action",
    "AdministratorDetails",
    "BackupCertificateResult",
    "CertificateAttributes",
    "CertificateBundle",
    "CertificateCreateParameters",
    "CertificateImportParameters",
    "CertificateIssuerItem",
    "CertificateIssuerSetParameters",
    "CertificateIssuerUpdateParameters",
    "CertificateItem",
    "CertificateMergeParameters",
    "CertificateOperation",
    "CertificateOperationUpdateParameter",
    "CertificatePolicy",
    "CertificateRestoreParameters",
    "CertificateUpdateParameters",
    "Contact",
    "Contacts",
    "DeletedCertificateBundle",
    "DeletedCertificateItem",
    "IssuerAttributes",
    "IssuerBundle",
    "IssuerCredentials",
    "IssuerParameters",
    "KeyProperties",
    "KeyVaultError",
    "KeyVaultErrorError",
    "LifetimeAction",
    "OrganizationDetails",
    "SecretProperties",
    "SubjectAlternativeNames",
    "Trigger",
    "X509CertificateProperties",
    "CertificatePolicyAction",
    "DeletionRecoveryLevel",
    "JsonWebKeyCurveName",
    "JsonWebKeyType",
    "KeyUsageType",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
