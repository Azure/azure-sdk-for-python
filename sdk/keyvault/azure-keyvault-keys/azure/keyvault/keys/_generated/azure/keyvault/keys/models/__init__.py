# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    BackupKeyResult,
    DeletedKeyBundle,
    DeletedKeyItem,
    GetRandomBytesRequest,
    JsonWebKey,
    KeyAttestation,
    KeyAttributes,
    KeyBundle,
    KeyCreateParameters,
    KeyImportParameters,
    KeyItem,
    KeyOperationResult,
    KeyOperationsParameters,
    KeyReleaseParameters,
    KeyReleasePolicy,
    KeyReleaseResult,
    KeyRestoreParameters,
    KeyRotationPolicy,
    KeyRotationPolicyAttributes,
    KeySignParameters,
    KeyUpdateParameters,
    KeyVaultError,
    KeyVaultErrorError,
    KeyVerifyParameters,
    KeyVerifyResult,
    LifetimeActions,
    LifetimeActionsTrigger,
    LifetimeActionsType,
    RandomBytes,
)

from ._enums import (  # type: ignore
    DeletionRecoveryLevel,
    JsonWebKeyCurveName,
    JsonWebKeyEncryptionAlgorithm,
    JsonWebKeyOperation,
    JsonWebKeySignatureAlgorithm,
    JsonWebKeyType,
    KeyEncryptionAlgorithm,
    KeyRotationPolicyAction,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "BackupKeyResult",
    "DeletedKeyBundle",
    "DeletedKeyItem",
    "GetRandomBytesRequest",
    "JsonWebKey",
    "KeyAttestation",
    "KeyAttributes",
    "KeyBundle",
    "KeyCreateParameters",
    "KeyImportParameters",
    "KeyItem",
    "KeyOperationResult",
    "KeyOperationsParameters",
    "KeyReleaseParameters",
    "KeyReleasePolicy",
    "KeyReleaseResult",
    "KeyRestoreParameters",
    "KeyRotationPolicy",
    "KeyRotationPolicyAttributes",
    "KeySignParameters",
    "KeyUpdateParameters",
    "KeyVaultError",
    "KeyVaultErrorError",
    "KeyVerifyParameters",
    "KeyVerifyResult",
    "LifetimeActions",
    "LifetimeActionsTrigger",
    "LifetimeActionsType",
    "RandomBytes",
    "DeletionRecoveryLevel",
    "JsonWebKeyCurveName",
    "JsonWebKeyEncryptionAlgorithm",
    "JsonWebKeyOperation",
    "JsonWebKeySignatureAlgorithm",
    "JsonWebKeyType",
    "KeyEncryptionAlgorithm",
    "KeyRotationPolicyAction",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
