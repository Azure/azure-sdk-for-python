# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List
import functools

from azure.security.attestation import AttestationType

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Callable, Dict, Optional, Any, TypeVar

    T = TypeVar("T")


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
