# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Tuple, Union, cast, Any, MutableMapping, overload, Mapping
from ._models import (
    MetadataFilter as MetadataFilterGenerated,
    AnswersFromTextOptions as AnswersFromTextOptionsGenerated,
    TextDocument,
    MetadataRecord
)

JSON = MutableMapping[str, Any]


class MetadataFilter(MetadataFilterGenerated):
    """Find QnAs that are associated with the given list of metadata.

    :ivar metadata:
    :vartype metadata: list[tuple[str, str]] or list[~azure.ai.language.questionanswering.models.MetadataRecord]
    :ivar logical_operation: Operation used to join metadata filters. Possible values include:
     "AND", "OR".
    :vartype logical_operation: str
    """
    @overload
    def __init__(
        self,
        *,
        metadata: Optional[List[Tuple[str, str]]] = None,
        logical_operation: Optional[str] = None,
        **kwargs: Any
    ) -> None:  # pragma: no cover - overload definition
        """Overload accepting list of (key, value) tuples."""

    @overload
    def __init__(
        self,
        *,
        metadata: Optional[List[MetadataRecord]] = None,
        logical_operation: Optional[str] = None,
        **kwargs: Any
    ) -> None:  # pragma: no cover - overload definition
        """Overload accepting list of MetadataRecord objects."""

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:  # pragma: no cover - overload definition
        """Overload accepting raw JSON mapping used during deserialization."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - docstring covered by overloads
        """Create a MetadataFilter.

        Accepts either keyword-only parameters (``metadata``/``logical_operation``) or a single
        raw JSON ``mapping`` positional argument used internally for deserialization.
        """
        # Mapping form: pass straight through to generated model
        if args and isinstance(args[0], Mapping):
            super().__init__(*args, **kwargs)
            return

        metadata = kwargs.pop("metadata", None)
        logical_operation = kwargs.pop("logical_operation", None)

        converted: Optional[List[MetadataRecord]]
        if metadata is not None:
            converted = []
            for item in metadata:
                if isinstance(item, tuple):
                    converted.append(MetadataRecord(key=item[0], value=item[1]))
                elif isinstance(item, MetadataRecord):
                    converted.append(item)
                else:
                    raise TypeError(
                        f"metadata items must be tuples or MetadataRecord objects, got {type(item)}"
                    )
        else:
            converted = None
        super().__init__(metadata=converted, logical_operation=logical_operation, **kwargs)

class AnswersFromTextOptions(AnswersFromTextOptionsGenerated):
    """The question and text record parameters to answer.

    All required parameters must be populated in order to send to Azure.

    :ivar question: Required. User question to query against the given text records.
    :vartype question: str
    :ivar text_documents: Required. Text records to be searched for given question.
    :vartype text_documents: list[str or ~azure.ai.language.questionanswering.models.TextDocument]
    :ivar language: Language of the text records. This is BCP-47 representation of a language. For
     example, use "en" for English; "es" for Spanish etc. If not set, use "en" for English as
     default.
    :vartype language: str
    """

    def __init__(
        self,
        *,
        question: str,
        text_documents: List[Union[str, TextDocument]],
        language: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword question: Required. User question to query against the given text records.
        :paramtype question: str
        :keyword text_documents: Required. Text records to be searched for given question.
        :paramtype text_documents: list[str or ~azure.ai.language.questionanswering.models.TextDocument]
        :keyword language: Language of the text records. This is BCP-47 representation of a language.
         For example, use "en" for English; "es" for Spanish etc. If not set, use "en" for English as
         default.
        :paramtype language: str
        """
        super().__init__(
            question=question,
            text_documents=cast(List[TextDocument], text_documents),
            language=language,
            string_index_type="UnicodeCodePoint",
            **kwargs
        )


__all__: List[str] = [
    "MetadataFilter",
    "AnswersFromTextOptions",
]

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
