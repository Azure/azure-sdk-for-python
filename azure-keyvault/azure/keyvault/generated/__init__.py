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

from .. import KeyVaultClient
from .. import VERSION
from ..models import Attributes as __models_Attributes
from ..models import JsonWebKey as __models_JsonWebKey
from ..models import KeyAttributes as __models_KeyAttributes
from ..models import KeyBundle as __models_KeyBundle
from ..models import KeyItem as __models_KeyItem
from ..models import SecretAttributes as __models_SecretAttributes
from ..models import SecretBundle as __models_SecretBundle
from ..models import SecretItem as __models_SecretItem
from ..models import CertificateAttributes as __models_CertificateAttributes
from ..models import CertificateItem as __models_CertificateItem
from ..models import CertificateIssuerItem as __models_CertificateIssuerItem
from ..models import KeyProperties as __models_KeyProperties
from ..models import SecretProperties as __models_SecretProperties
from ..models import SubjectAlternativeNames as __models_SubjectAlternativeNames
from ..models import X509CertificateProperties as __models_X509CertificateProperties
from ..models import Trigger as __models_Trigger
from ..models import Action as __models_Action
from ..models import LifetimeAction as __models_LifetimeAction
from ..models import IssuerParameters as __models_IssuerParameters
from ..models import CertificatePolicy as __models_CertificatePolicy
from ..models import CertificateBundle as __models_CertificateBundle
from ..models import Error as __models_Error
from ..models import CertificateOperation as __models_CertificateOperation
from ..models import IssuerCredentials as __models_IssuerCredentials
from ..models import AdministratorDetails as __models_AdministratorDetails
from ..models import OrganizationDetails as __models_OrganizationDetails
from ..models import IssuerAttributes as __models_IssuerAttributes
from ..models import IssuerBundle as __models_IssuerBundle
from ..models import Contact as __models_Contact
from ..models import Contacts as __models_Contacts
from ..models import KeyCreateParameters as __models_KeyCreateParameters
from ..models import KeyImportParameters as __models_KeyImportParameters
from ..models import KeyOperationsParameters as __models_KeyOperationsParameters
from ..models import KeySignParameters as __models_KeySignParameters
from ..models import KeyVerifyParameters as __models_KeyVerifyParameters
from ..models import KeyUpdateParameters as __models_KeyUpdateParameters
from ..models import KeyRestoreParameters as __models_KeyRestoreParameters
from ..models import SecretSetParameters as __models_SecretSetParameters
from ..models import SecretUpdateParameters as __models_SecretUpdateParameters
from ..models import CertificateCreateParameters as __models_CertificateCreateParameters
from ..models import CertificateImportParameters as __models_CertificateImportParameters
from ..models import CertificateUpdateParameters as __models_CertificateUpdateParameters
from ..models import CertificateMergeParameters as __models_CertificateMergeParameters
from ..models import CertificateIssuerSetParameters as __models_CertificateIssuerSetParameters
from ..models import CertificateIssuerUpdateParameters as __models_CertificateIssuerUpdateParameters
from ..models import CertificateOperationUpdateParameter as __models_CertificateOperationUpdateParameter
from ..models import KeyOperationResult as __models_KeyOperationResult
from ..models import KeyVerifyResult as __models_KeyVerifyResult
from ..models import BackupKeyResult as __models_BackupKeyResult
from ..models import PendingCertificateSigningRequestResult as __models_PendingCertificateSigningRequestResult
from ..models import KeyVaultError as __models_KeyVaultError
from ..models import KeyVaultErrorException as __models_KeyVaultErrorException
from ..models import KeyItemPaged as __models_KeyItemPaged
from ..models import SecretItemPaged as __models_SecretItemPaged
from ..models import CertificateItemPaged as __models_CertificateItemPaged
from ..models import CertificateIssuerItemPaged as __models_CertificateIssuerItemPaged
from ..models import JsonWebKeyType as __models_JsonWebKeyType
from ..models import KeyUsageType as __models_KeyUsageType
from ..models import ActionType as __models_ActionType
from ..models import JsonWebKeyOperation as __models_JsonWebKeyOperation
from ..models import JsonWebKeyEncryptionAlgorithm as __models_JsonWebKeyEncryptionAlgorithm
from ..models import JsonWebKeySignatureAlgorithm as __models_JsonWebKeySignatureAlgorithm

import warnings

warnings.warn("The namespace azure.keyvault.generated has been deprecated and it's contents moved to azure.keyvault", DeprecationWarning)

__all__ = ['KeyVaultClient',
           '__models_Attributes',
           '__models_JsonWebKey',
           '__models_KeyAttributes',
           '__models_KeyBundle',
           '__models_KeyItem',
           '__models_SecretAttributes',
           '__models_SecretBundle',
           '__models_SecretItem',
           '__models_CertificateAttributes',
           '__models_CertificateItem',
           '__models_CertificateIssuerItem',
           '__models_KeyProperties',
           '__models_SecretProperties',
           '__models_SubjectAlternativeNames',
           '__models_X509CertificateProperties',
           '__models_Trigger',
           '__models_Action',
           '__models_LifetimeAction',
           '__models_IssuerParameters',
           '__models_CertificatePolicy',
           '__models_CertificateBundle',
           '__models_Error',
           '__models_CertificateOperation',
           '__models_IssuerCredentials',
           '__models_AdministratorDetails',
           '__models_OrganizationDetails',
           '__models_IssuerAttributes',
           '__models_IssuerBundle',
           '__models_Contact',
           '__models_Contacts',
           '__models_KeyCreateParameters',
           '__models_KeyImportParameters',
           '__models_KeyOperationsParameters',
           '__models_KeySignParameters',
           '__models_KeyVerifyParameters',
           '__models_KeyUpdateParameters',
           '__models_KeyRestoreParameters',
           '__models_SecretSetParameters',
           '__models_SecretUpdateParameters',
           '__models_CertificateCreateParameters',
           '__models_CertificateImportParameters',
           '__models_CertificateUpdateParameters',
           '__models_CertificateMergeParameters',
           '__models_CertificateIssuerSetParameters',
           '__models_CertificateIssuerUpdateParameters',
           '__models_CertificateOperationUpdateParameter',
           '__models_KeyOperationResult',
           '__models_KeyVerifyResult',
           '__models_BackupKeyResult',
           '__models_PendingCertificateSigningRequestResult',
           '__models_KeyVaultError',
           '__models_KeyVaultErrorException',
           '__models_KeyItemPaged',
           '__models_SecretItemPaged',
           '__models_CertificateItemPaged',
           '__models_CertificateIssuerItemPaged',
           '__models_JsonWebKeyType',
           '__models_KeyUsageType',
           '__models_ActionType',
           '__models_JsonWebKeyOperation',
           '__models_JsonWebKeyEncryptionAlgorithm',
           '__models_JsonWebKeySignatureAlgorithm',]

__version__ = VERSION



