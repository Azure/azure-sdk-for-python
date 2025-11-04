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
from typing import Any, Optional, Sequence, Tuple, Union, Mapping as TypingMapping, List, overload

from ._models import MetadataFilter as _GeneratedMetadataFilter
from ._models import MetadataRecord
from ._models import AnswersFromTextOptions as _GeneratedAnswersFromTextOptions
from ._models import TextDocument

__all__: list[str] = ["MetadataFilter", "AnswersFromTextOptions"]

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
            raise ValueError("'metadata' must be an iterable of key/value pairs or MetadataRecord instances.") from exc

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
                raise ValueError("Invalid metadata entry; expected a 2-item tuple but received a string/bytes value.")
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
    """Backward compatible MetadataFilter supporting legacy tuple/dict inputs.

    Supported ``metadata`` input forms (all normalized to ``List[MetadataRecord]``):
      1. ``None`` – leave metadata unset.
      2. ``[("key","value"), ("k2","v2")]`` – list of 2-item tuples.
      3. ``[MetadataRecord(...), ...]`` – list of generated model records.
      4. ``[{"key": "k", "value": "v"}, ...]`` – list of mapping objects with key/value.
      5. ``{"k": "v", "k2": "v2"}`` – single mapping; each item becomes a record.
      6. ``{"key": "k", "value": "v"}`` – single record mapping.
      7. Mixed list: ``[MetadataRecord(...), ("k","v"), {"key":"a","value":"b"}]``.

    Invalid inputs raise ``ValueError`` (e.g. plain string, bytes, malformed iterable).

    The optional ``logical_operation`` parameter is passed through unchanged.
    """

    # Overload stubs to improve type hints and documentation rendering.
    @overload
    def __init__(self, *, metadata: None = ..., logical_operation: Optional[str] = ...) -> None: ...  # noqa: D401,E701
    @overload
    def __init__(
        self, *, metadata: Sequence[Tuple[str, str]], logical_operation: Optional[str] = ...
    ) -> None: ...  # noqa: E701
    @overload
    def __init__(
        self, *, metadata: Sequence[MetadataRecord], logical_operation: Optional[str] = ...
    ) -> None: ...  # noqa: E701
    @overload
    def __init__(
        self, *, metadata: TypingMapping[str, str], logical_operation: Optional[str] = ...
    ) -> None: ...  # noqa: E701
    @overload
    def __init__(
        self,
        *,
        metadata: Sequence[Union[Tuple[str, str], MetadataRecord, TypingMapping[str, str]]],
        logical_operation: Optional[str] = ...,
    ) -> None: ...  # noqa: E701

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


class AnswersFromTextOptions(_GeneratedAnswersFromTextOptions):
    """Convenience wrapper allowing ``text_documents`` to be a list of either ``str`` or ``TextDocument``.

    This subclass accepts mixed inputs and converts plain strings to ``TextDocument`` instances
    with auto-generated incremental string IDs ("0", "1", ...). It also sets ``string_index_type``
    to ``"UnicodeCodePoint"`` for consistent offset interpretation, exposing it as an extra
    serialized field ``stringIndexType``.

    Supported ``text_documents`` forms:
      1. ``["text one", "text two"]``
      2. ``[TextDocument(id="a", text="...")]``
      3. Mixed: ``["plain", TextDocument(id="b", text="...")]``

    :param question: User question to query against the given text records. Required.
    :param text_documents: Text records as list of ``str`` or ``TextDocument``. Required.
    :param language: Optional BCP-47 language code, e.g. "en", "zh-Hans", "es".
    """

    @overload
    def __init__(
        self,
        *,
        question: str,
        text_documents: Sequence[str],
        language: Optional[str] = None,
    ) -> None: ...  # noqa: E701

    @overload
    def __init__(
        self,
        *,
        question: str,
        text_documents: Sequence[TextDocument],
        language: Optional[str] = None,
    ) -> None: ...  # noqa: E701

    @overload
    def __init__(
        self,
        *,
        question: str,
        text_documents: Sequence[Union[str, TextDocument]],
        language: Optional[str] = None,
    ) -> None: ...  # noqa: E701

    def __init__(
        self,
        *,
        question: str,
        text_documents: Sequence[Union[str, TextDocument]],
        language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # Normalize text_documents into List[TextDocument]
        normalized: List[TextDocument] = []
        for idx, doc in enumerate(text_documents):
            if isinstance(doc, TextDocument):
                normalized.append(doc)
            elif isinstance(doc, str):
                normalized.append(TextDocument(id=str(idx), text=doc))
            else:
                raise TypeError(
                    "Each item in 'text_documents' must be either a str or TextDocument; got {}".format(type(doc))
                )
        super().__init__(question=question, text_documents=normalized, language=language, **kwargs)
        # Inject custom string index type attribute/serialization map
        self.string_index_type = "UnicodeCodePoint"
        # _attribute_map may not exist if underlying generator changed; guard accordingly.
        try:  # pragma: no cover - defensive
            self._attribute_map.update({"string_index_type": {"key": "stringIndexType", "type": "str"}})
        except AttributeError:
            pass


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
