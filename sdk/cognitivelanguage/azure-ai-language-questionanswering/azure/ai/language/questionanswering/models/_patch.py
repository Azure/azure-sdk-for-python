# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Tuple, Union
from ._models import (
    MetadataFilter as MetadataFilterGenerated,
    AnswersFromTextOptions as AnswersFromTextOptionsGenerated,
    TextDocument,
)


class MetadataFilter(MetadataFilterGenerated):
    """Find QnAs that are associated with the given list of metadata.

    :ivar metadata:
    :vartype metadata: list[tuple[str, str]]
    :ivar logical_operation: Operation used to join metadata filters. Possible values include:
     "AND", "OR".
    :vartype logical_operation: str
    """

    def __init__(
        self, *, metadata: Optional[List[Tuple[str, str]]] = None, logical_operation: Optional[str] = None, **kwargs
    ):
        """
        :keyword metadata:
        :paramtype metadata: list[tuple[str, str]]
        :keyword logical_operation: Operation used to join metadata filters. Possible values include:
         "AND", "OR".
        :paramtype logical_operation: str
        """
        super().__init__(metadata=metadata, logical_operation=logical_operation, **kwargs)


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
        self, *, question: str, text_documents: List[Union[str, TextDocument]], language: Optional[str] = None, **kwargs
    ):
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
        super().__init__(question=question, text_documents=text_documents, language=language, **kwargs)
        self.string_index_type = "UnicodeCodePoint"
        self._attribute_map.update({"string_index_type": {"key": "stringIndexType", "type": "str"}})


__all__: List[str] = [
    "MetadataFilter",
    "AnswersFromTextOptions",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
