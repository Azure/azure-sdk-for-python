# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, ClassVar, Optional


def _required_string(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be empty")
    return value


def _mapping(name: str, value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    return MappingProxyType(dict(value))


def _string_sequence(name: str, value: Sequence[str]) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{name} must be a sequence of strings")
    return tuple(
        _required_string(f"{name}[{index}]", item) for index, item in enumerate(value)
    )


@dataclass(frozen=True)
class DiskImage:
    """A VHD image used by an execution plan storage profile."""

    source_vhd_uri: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_vhd_uri",
            _required_string("source_vhd_uri", self.source_vhd_uri),
        )

    def _to_dict(self) -> dict[str, Any]:
        return {"sourceVhdUri": self.source_vhd_uri}


@dataclass(frozen=True)
class StorageProfile:
    """OS and data disk images supplied to certification tests."""

    os_disk_image: DiskImage
    data_disk_images: Sequence[DiskImage] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.os_disk_image, DiskImage):
            raise TypeError("os_disk_image must be a DiskImage")
        if isinstance(self.data_disk_images, (str, bytes)) or not isinstance(
            self.data_disk_images, Sequence
        ):
            raise TypeError("data_disk_images must be a sequence of DiskImage objects")
        data_disk_images = tuple(self.data_disk_images)
        if any(not isinstance(image, DiskImage) for image in data_disk_images):
            raise TypeError("data_disk_images must contain only DiskImage objects")
        object.__setattr__(self, "data_disk_images", data_disk_images)

    def _to_dict(self) -> dict[str, Any]:
        return {
            "osDiskImage": self.os_disk_image._to_dict(),
            "dataDiskImages": [image._to_dict() for image in self.data_disk_images],
        }


@dataclass(frozen=True)
class CertificationPackageReference:
    """Certification package details consumed by an execution plan."""

    os_type: str
    vm_generation_type: str
    architecture_type: str
    recommended_vm_sizes: Sequence[str]
    storage_profile: StorageProfile
    additional_properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "os_type", _required_string("os_type", self.os_type))
        object.__setattr__(
            self,
            "vm_generation_type",
            _required_string("vm_generation_type", self.vm_generation_type),
        )
        object.__setattr__(
            self,
            "architecture_type",
            _required_string("architecture_type", self.architecture_type),
        )
        object.__setattr__(
            self,
            "recommended_vm_sizes",
            _string_sequence("recommended_vm_sizes", self.recommended_vm_sizes),
        )
        if not self.recommended_vm_sizes:
            raise ValueError("recommended_vm_sizes must contain at least one value")
        if not isinstance(self.storage_profile, StorageProfile):
            raise TypeError("storage_profile must be a StorageProfile")
        object.__setattr__(
            self,
            "additional_properties",
            _mapping("additional_properties", self.additional_properties),
        )

    def _to_dict(self) -> dict[str, Any]:
        return {
            "osType": self.os_type,
            "vmGenerationType": self.vm_generation_type,
            "architectureType": self.architecture_type,
            "recommendedVMSizes": list(self.recommended_vm_sizes),
            "storageProfile": self.storage_profile._to_dict(),
            "additionalProperties": dict(self.additional_properties),
        }


@dataclass(frozen=True)
class ValidationStep:
    """A test step in an execution plan."""

    name: str
    test_ref: str
    inputs: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_string("name", self.name))
        object.__setattr__(
            self, "test_ref", _required_string("test_ref", self.test_ref)
        )
        if self.inputs is not None:
            object.__setattr__(self, "inputs", _mapping("inputs", self.inputs))

    @classmethod
    def test(
        cls,
        *,
        name: str,
        test_ref: str,
        inputs: Optional[Mapping[str, Any]] = None,
    ) -> "ValidationStep":
        """Create a test step using the complete service test reference unchanged."""
        return cls(name=name, test_ref=test_ref, inputs=inputs)

    def _to_dict(self) -> dict[str, Any]:
        result = {"name": self.name, "type": "test", "testRef": self.test_ref}
        if self.inputs is not None:
            result["inputs"] = dict(self.inputs)
        return result


@dataclass(frozen=True)
class ExecutionPlanConfiguration:
    """A serializable PlatformValidation execution plan configuration."""

    API_VERSION: ClassVar[str] = "microsoft.validate/executionPlan.v0"
    KIND: ClassVar[str] = "ExecutionPlan"

    name: str
    certification_package_reference: CertificationPackageReference
    steps: Sequence[ValidationStep]

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_string("name", self.name))
        if not isinstance(
            self.certification_package_reference, CertificationPackageReference
        ):
            raise TypeError(
                "certification_package_reference must be a CertificationPackageReference"
            )
        if isinstance(self.steps, (str, bytes)) or not isinstance(self.steps, Sequence):
            raise TypeError("steps must be a sequence of ValidationStep objects")
        steps = tuple(self.steps)
        if not steps:
            raise ValueError("steps must contain at least one ValidationStep")
        if any(not isinstance(step, ValidationStep) for step in steps):
            raise TypeError("steps must contain only ValidationStep objects")
        object.__setattr__(self, "steps", steps)

    def to_json(self) -> str:
        """Return compact JSON suitable for ``plan_configuration_json``."""
        document = {
            "apiVersion": self.API_VERSION,
            "kind": self.KIND,
            "metadata": {"name": self.name},
            "parameters": {
                "certificationPackageReference": self.certification_package_reference._to_dict()
            },
            "authoring": {"steps": [step._to_dict() for step in self.steps]},
        }
        try:
            return json.dumps(
                document, separators=(",", ":"), ensure_ascii=False, allow_nan=False
            )
        except (TypeError, ValueError) as error:
            raise TypeError(
                "execution plan values must be JSON serializable"
            ) from error


__all__: list[str] = [
    "CertificationPackageReference",
    "DiskImage",
    "ExecutionPlanConfiguration",
    "StorageProfile",
    "ValidationStep",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
