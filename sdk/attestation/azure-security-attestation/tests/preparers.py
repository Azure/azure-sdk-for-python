# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List
import pytest
import functools
from devtools_testutils import PowerShellPreparer

from azure.security.attestation import AttestationType

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Callable, Dict, Optional, Any, TypeVar

    T = TypeVar("T")


AttestationPreparer = functools.partial(
    PowerShellPreparer,
    "attestation",
    #            attestation_azure_authority_host='xxx',
    #            attestation_resource_group='yyyy',
    #            attestation_subscription_id='xxx',
    #            attestation_environment='AzureCloud',
    attestation_policy_signing_key0="keyvalue",
    attestation_policy_signing_key1="keyvalue",
    attestation_policy_signing_key2="keyvalue",
    attestation_policy_signing_certificate0="more junk",
    attestation_policy_signing_certificate1="more junk",
    attestation_policy_signing_certificate2="more junk",
    attestation_serialized_policy_signing_key0="junk",
    attestation_serialized_policy_signing_key1="junk",
    attestation_serialized_policy_signing_key2="junk",
    attestation_serialized_isolated_signing_key="yyyy",
    attestation_isolated_signing_key="xxxx",
    attestation_isolated_signing_certificate="xxxx",
    attestation_service_management_url="https://management.core.windows.net/",
    attestation_location_short_name="wus",  # Note: This must match the short name in the fake resources.
    attestation_client_id="xxxx",
    attestation_client_secret="secret",
    attestation_tenant_id="tenant",
    attestation_isolated_url="https://fakeresource.wus.attest.azure.net",
    attestation_aad_url="https://fakeresource.wus.attest.azure.net",
    #            attestation_resource_manager_url='https://resourcemanager/zzz'
)


def AllAttestationTypes(
    __func=None,  # type: Callable[..., T]
    **kwargs  # type: Any
):
    """Decorator to apply to function to add attestation_type kwarg for each attestation type."""

    def decorator(func):
        # type: (Callable[..., T]) -> Callable[..., T]

        @functools.wraps(func)
        def wrapper_use_attestationtype(*args, **kwargs):
            # type: (*Any, **Any) -> T

            for attestation_type in [
                AttestationType.SGX_ENCLAVE,
                AttestationType.OPEN_ENCLAVE,
                AttestationType.TPM,
            ]:
                func(*args, attestation_type=attestation_type, **kwargs)

        return wrapper_use_attestationtype

    return decorator if __func is None else decorator(__func)


def AllInstanceTypes(
    __func=None,  # type: Callable[..., T]
    include_shared=True,  # type: bool
    **kwargs  # type: Any
):
    """Decorator to apply to function to add instance_url kwarg for each instance type."""

    def decorator(func):
        # type: (Callable[..., T]) -> Callable[..., T]

        @functools.wraps(func)
        def wrapper_use_instance(*args, **kwargs):
            # type: (*Any, **Any) -> T

            instances = []  # type:List[str]
            instances.append(kwargs.get("attestation_aad_url"))
            instances.append(kwargs.get("attestation_isolated_url"))
            if include_shared:
                instances.append(
                    "https://shared"
                    + kwargs.get("attestation_location_short_name")
                    + "."
                    + kwargs.get("attestation_location_short_name")
                    + ".attest.azure.net"
                )

            for attestation_type in instances:
                func(*args, instance_url=attestation_type, **kwargs)

        return wrapper_use_instance

    return decorator if __func is None else decorator(__func)
