# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Model-level convenience extensions.

Adds tuple -> MetadataRecord conversion, logical_operation validation, string list -> TextDocument
normalization, and backward-compatible aliases. Kept in patch to preserve across regeneration.
"""
from typing import List, Optional, Tuple, Union, Any
from ._models import (
    MetadataFilter as MetadataFilterGenerated,
    MetadataRecord,
    AnswersFromTextOptions as AnswersFromTextOptionsGenerated,
    TextDocument,
    KnowledgeBaseAnswerContext as KnowledgeBaseAnswerContextGenerated,
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
        self,
        *,
        metadata: Optional[List[Tuple[str, str]]] = None,
        logical_operation: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword metadata:
        :paramtype metadata: list[tuple[str, str]]
        :keyword logical_operation: Operation used to join metadata filters. Possible values include:
         "AND", "OR".
        :paramtype logical_operation: str
        """
        # Convert convenience tuples to generated MetadataRecord models.
        metadata_records: Optional[List[MetadataRecord]] = None
        if metadata is not None:
            if len(metadata) == 0:
                metadata_records = []
            else:
                # Expecting list of (key, value) tuples
                metadata_records = [MetadataRecord(key=k, value=v) for (k, v) in metadata]

        # Standardize logical_operation to upper (service enum values are AND/OR)
        if logical_operation is not None:
            up = logical_operation.upper()
            if up not in ("AND", "OR"):
                raise ValueError("logical_operation must be 'AND' or 'OR' (case-insensitive)")
            logical_operation = up

        super().__init__(metadata=metadata_records, logical_operation=logical_operation, **kwargs)


class AnswersFromTextOptions(AnswersFromTextOptionsGenerated):
    """The question and text record parameters to answer.

    All required parameters must be populated in order to send to Azure.

    :ivar question: Required. User question to query against the given text records.
    :vartype question: str
    :ivar text_documents: Required. Text records to be searched for given question.
    :vartype text_documents: list[str or ~azure.ai.language.questionanswering.models.TextDocument]
    :ivar language: Language of the text records (BCP-47, e.g. "en", "es"). If omitted the service
     default is applied (no client-side forced default).
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
    :keyword language: Language of the text records (BCP-47). If not provided, no implicit 'en'
     is injected; the service decides the default.
        :paramtype language: str
        """
        # Normalize text_documents: allow passing plain strings for convenience
        # by converting them to TextDocument(id=str(index), text=value).
        normalized_docs: List[TextDocument] = []
        for idx, doc in enumerate(text_documents):
            if isinstance(doc, TextDocument):
                normalized_docs.append(doc)
            elif isinstance(doc, str):
                normalized_docs.append(TextDocument(id=str(idx), text=doc))
            else:
                raise TypeError(
                    "text_documents[{idx}] must be str or TextDocument; got {t}".format(
                        idx=idx, t=type(doc).__name__
                    )
                )
        AnswersFromTextOptionsGenerated.__init__(
            self, question=question, text_documents=normalized_docs, language=language, **kwargs
        )


class KnowledgeBaseAnswerContext(KnowledgeBaseAnswerContextGenerated):
    """Context object with previous QnA's information.

    Accepts previous_user_query as an alias of previous_question for backward compatibility.
    """

    def __init__(
        self,
        *,
        previous_qna_id: int,
        previous_question: Optional[str] = None,
        previous_user_query: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if previous_question is None and previous_user_query is not None:
            previous_question = previous_user_query
        KnowledgeBaseAnswerContextGenerated.__init__(
            self,
            previous_qna_id=previous_qna_id,
            previous_question=previous_question,
            **kwargs,
        )


__all__: List[str] = [
    "MetadataFilter",
    "AnswersFromTextOptions",
    "KnowledgeBaseAnswerContext",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
