# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from typing import Any, Optional

from ._models import MetadataFilter as _GeneratedMetadataFilter
from ._models import MetadataRecord

__all__: list[str] = ["MetadataFilter"]

_MISSING = object()


def _normalize_metadata_sequence(
    metadata: Any,
) -> Optional[list[MetadataRecord]]:
    """Coerce supported metadata inputs into MetadataRecord objects."""

    if metadata is None:
        return None

    # Single MetadataRecord instance
    if isinstance(metadata, MetadataRecord):
        return [metadata]

    # Mapping inputs:
    if isinstance(metadata, Mapping):
        if "key" in metadata and "value" in metadata and len(metadata) <= 2:
            return [MetadataRecord(key=metadata["key"], value=metadata["value"])]
        metadata_iterable: Iterable[Any] = metadata.items()
    else:
        if isinstance(metadata, (str, bytes)):
            raise ValueError(
                "'metadata' must be provided as key/value pairs, MetadataRecord instances, "
                "or mappings; strings are not supported."
            )
        try:
            metadata_iterable = iter(metadata)
        except TypeError as exc:  # pragma: no cover - defensive guard
            raise ValueError(
                "'metadata' must be an iterable of key/value pairs or MetadataRecord instances."
            ) from exc

    normalized: list[MetadataRecord] = []
    for entry in metadata_iterable:
        if isinstance(entry, MetadataRecord):
            normalized.append(entry)
            continue
        if isinstance(entry, Mapping):
            if "key" in entry and "value" in entry:
                key = entry["key"]
                value = entry["value"]
            elif len(entry) == 1:
                key, value = next(iter(entry.items()))
            else:
                raise ValueError(
                    "Mapping entries for 'metadata' must either contain 'key'/'value' keys "
                    "or represent a single key/value pair."
                )
        else:
            if isinstance(entry, (str, bytes)):
                raise ValueError(
                    "Invalid metadata entry; expected a 2-item tuple but received a string/bytes value."
                )
            try:
                key, value = entry  # type: ignore[assignment]
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "Each metadata entry must be a MetadataRecord, a mapping with 'key'/'value', "
                    "or a 2-item iterable representing (key, value)."
                ) from exc
        normalized.append(MetadataRecord(key=key, value=value))

    return normalized


class MetadataFilter(_GeneratedMetadataFilter):
    """Backward compatible MetadataFilter supporting legacy tuple/dict inputs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        metadata_kwarg = kwargs.pop("metadata", _MISSING)
        args_list = list(args)

        if metadata_kwarg is not _MISSING:
            kwargs["metadata"] = _normalize_metadata_sequence(metadata_kwarg)
        elif args_list and isinstance(args_list[0], MutableMapping):
            first_mapping = dict(args_list[0])
            if "metadata" in first_mapping:
                first_mapping["metadata"] = _normalize_metadata_sequence(first_mapping["metadata"])
                args_list[0] = first_mapping

        super().__init__(*args_list, **kwargs)

        if self.metadata is not None:
            self.metadata = _normalize_metadata_sequence(self.metadata)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
