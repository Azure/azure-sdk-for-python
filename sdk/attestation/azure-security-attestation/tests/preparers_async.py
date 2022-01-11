# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Awaitable, List
from azure.security.attestation import AttestationType

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

from typing import Awaitable, Callable, Dict, Optional, Any, TypeVar, overload

T = TypeVar("T")


def AllAttestationTypes(func: Callable[..., Awaitable[T]] = None, **kwargs: Any):
    """Decorator to apply to function to add attestation_type kwarg for each attestation type."""

    async def wrapper(*args, **kwargs) -> Callable[..., Awaitable[T]]:
        for attestation_type in [
            AttestationType.SGX_ENCLAVE,
            AttestationType.OPEN_ENCLAVE,
            AttestationType.TPM,
        ]:
            await func(*args, attestation_type=attestation_type, **kwargs)

    return wrapper


def AllInstanceTypes(
    func: Callable[..., Awaitable[T]] = None, include_shared: bool = True, **kwargs: Any
):
    """Decorator to apply to function to add instance_url kwarg for each instance type."""

    async def wrapper(*args, **kwargs) -> Callable[..., Awaitable[T]]:
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

        for instance_url in instances:
            await func(*args, instance_url=instance_url, **kwargs)

    return wrapper
