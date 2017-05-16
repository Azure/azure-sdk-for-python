# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# The 'azure.keyvault.generated' namespace has been preserved in this version
# of the SDK for backwards compatibility through the preview, however it may
# be removed in subsequent versions of the SDK.
# ---------------------------------------------------------------------------

from .. import __models_Attributes as Attributes
from .. import __models_JsonWebKey as JsonWebKey
from .. import __models_KeyAttributes as KeyAttributes
from .. import __models_KeyBundle as KeyBundle
from .. import __models_KeyItem as KeyItem
from .. import __models_SecretAttributes as SecretAttributes
from .. import __models_SecretBundle as SecretBundle
from .. import __models_SecretItem as SecretItem
from .. import __models_CertificateAttributes as CertificateAttributes
from .. import __models_CertificateItem as CertificateItem
from .. import __models_CertificateIssuerItem as CertificateIssuerItem
from .. import __models_KeyProperties as KeyProperties
from .. import __models_SecretProperties as SecretProperties
from .. import __models_SubjectAlternativeNames as SubjectAlternativeNames
from .. import __models_X509CertificateProperties as X509CertificateProperties
from .. import __models_Trigger as Trigger
from .. import __models_Action as Action
from .. import __models_LifetimeAction as LifetimeAction
from .. import __models_IssuerParameters as IssuerParameters
from .. import __models_CertificatePolicy as CertificatePolicy
from .. import __models_CertificateBundle as CertificateBundle
from .. import __models_Error as Error
from .. import __models_CertificateOperation as CertificateOperation
from .. import __models_IssuerCredentials as IssuerCredentials
from .. import __models_AdministratorDetails as AdministratorDetails
from .. import __models_OrganizationDetails as OrganizationDetails
from .. import __models_IssuerAttributes as IssuerAttributes
from .. import __models_IssuerBundle as IssuerBundle
from .. import __models_Contact as Contact
from .. import __models_Contacts as Contacts
from .. import __models_KeyCreateParameters as KeyCreateParameters
from .. import __models_KeyImportParameters as KeyImportParameters
from .. import __models_KeyOperationsParameters as KeyOperationsParameters
from .. import __models_KeySignParameters as KeySignParameters
from .. import __models_KeyVerifyParameters as KeyVerifyParameters
from .. import __models_KeyUpdateParameters as KeyUpdateParameters
from .. import __models_KeyRestoreParameters as KeyRestoreParameters
from .. import __models_SecretSetParameters as SecretSetParameters
from .. import __models_SecretUpdateParameters as SecretUpdateParameters
from .. import __models_CertificateCreateParameters as CertificateCreateParameters
from .. import __models_CertificateImportParameters as CertificateImportParameters
from .. import __models_CertificateUpdateParameters as CertificateUpdateParameters
from .. import __models_CertificateMergeParameters as CertificateMergeParameters
from .. import __models_CertificateIssuerSetParameters as CertificateIssuerSetParameters
from .. import __models_CertificateIssuerUpdateParameters as CertificateIssuerUpdateParameters
from .. import __models_CertificateOperationUpdateParameter as CertificateOperationUpdateParameter
from .. import __models_KeyOperationResult as KeyOperationResult
from .. import __models_KeyVerifyResult as KeyVerifyResult
from .. import __models_BackupKeyResult as BackupKeyResult
from .. import __models_PendingCertificateSigningRequestResult as PendingCertificateSigningRequestResult
from .. import __models_KeyVaultError as KeyVaultError
from .. import __models_KeyVaultErrorException as KeyVaultErrorException
from .. import __models_KeyItemPaged as KeyItemPaged
from .. import __models_SecretItemPaged as SecretItemPaged
from .. import __models_CertificateItemPaged as CertificateItemPaged
from .. import __models_CertificateIssuerItemPaged as CertificateIssuerItemPaged
from .. import __models_JsonWebKeyType as JsonWebKeyType
from .. import __models_KeyUsageType as KeyUsageType
from .. import __models_ActionType as ActionType
from .. import __models_JsonWebKeyOperation as JsonWebKeyOperation
from .. import __models_JsonWebKeyEncryptionAlgorithm as JsonWebKeyEncryptionAlgorithm
from .. import __models_JsonWebKeySignatureAlgorithm as JsonWebKeySignatureAlgorithm

import warnings

warnings.warn("The namespace azure.keyvault.generated.models has been deprecated and it's contents moved to azure.keyvault.models", DeprecationWarning)

__all__ = [
    'Attributes',
    'JsonWebKey',
    'KeyAttributes',
    'KeyBundle',
    'KeyItem',
    'SecretAttributes',
    'SecretBundle',
    'SecretItem',
    'CertificateAttributes',
    'CertificateItem',
    'CertificateIssuerItem',
    'KeyProperties',
    'SecretProperties',
    'SubjectAlternativeNames',
    'X509CertificateProperties',
    'Trigger',
    'Action',
    'LifetimeAction',
    'IssuerParameters',
    'CertificatePolicy',
    'CertificateBundle',
    'Error',
    'CertificateOperation',
    'IssuerCredentials',
    'AdministratorDetails',
    'OrganizationDetails',
    'IssuerAttributes',
    'IssuerBundle',
    'Contact',
    'Contacts',
    'KeyCreateParameters',
    'KeyImportParameters',
    'KeyOperationsParameters',
    'KeySignParameters',
    'KeyVerifyParameters',
    'KeyUpdateParameters',
    'KeyRestoreParameters',
    'SecretSetParameters',
    'SecretUpdateParameters',
    'CertificateCreateParameters',
    'CertificateImportParameters',
    'CertificateUpdateParameters',
    'CertificateMergeParameters',
    'CertificateIssuerSetParameters',
    'CertificateIssuerUpdateParameters',
    'CertificateOperationUpdateParameter',
    'KeyOperationResult',
    'KeyVerifyResult',
    'BackupKeyResult',
    'PendingCertificateSigningRequestResult',
    'KeyVaultError', 'KeyVaultErrorException',
    'KeyItemPaged',
    'SecretItemPaged',
    'CertificateItemPaged',
    'CertificateIssuerItemPaged',
    'JsonWebKeyType',
    'KeyUsageType',
    'ActionType',
    'JsonWebKeyOperation',
    'JsonWebKeyEncryptionAlgorithm',
    'JsonWebKeySignatureAlgorithm',
]
