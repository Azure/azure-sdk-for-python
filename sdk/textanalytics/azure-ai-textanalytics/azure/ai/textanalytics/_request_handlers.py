# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


import six

from ._models import (
    DetectLanguageInput,
    TextDocumentInput,
    RecognizeEntitiesAction,
    RecognizePiiEntitiesAction,
    RecognizeLinkedEntitiesAction,
    AnalyzeBatchActionsType,
)

def _validate_input(documents, hint, whole_input_hint):
    """Validate that batch input has either all string docs
    or dict/DetectLanguageInput/TextDocumentInput, not a mix of both.
    Assign country and language hints on a whole batch or per-item
    basis.

    :param list documents: The input documents.
    :return: A list of DetectLanguageInput or TextDocumentInput
    """
    if not documents:
        raise ValueError("Input documents can not be empty or None")

    if isinstance(documents, six.string_types):
        raise TypeError("Input documents cannot be a string.")

    if isinstance(documents, dict):
        raise TypeError("Input documents cannot be a dict")

    if not all(isinstance(x, six.string_types) for x in documents):
        if not all(isinstance(x, (dict, TextDocumentInput, DetectLanguageInput)) for x in documents):
            raise TypeError("Mixing string and dictionary/object document input unsupported.")


    request_batch = []
    for idx, doc in enumerate(documents):
        if isinstance(doc, six.string_types):
            if hint == "country_hint" and whole_input_hint.lower() == "none":
                whole_input_hint = ""
            document = {"id": str(idx), hint: whole_input_hint, "text": doc}
            request_batch.append(document)
        if isinstance(doc, dict):
            item_hint = doc.get(hint, None)
            if item_hint is None:
                doc = {"id": doc.get("id", None), hint: whole_input_hint, "text": doc.get("text", None)}
            elif item_hint.lower() == "none":
                doc = {"id": doc.get("id", None), hint: "", "text": doc.get("text", None)}
            request_batch.append(doc)
        if isinstance(doc, TextDocumentInput):
            item_hint = doc.language
            if item_hint is None:
                doc = TextDocumentInput(id=doc.id, language=whole_input_hint, text=doc.text)
            request_batch.append(doc)
        if isinstance(doc, DetectLanguageInput):
            item_hint = doc.country_hint
            if item_hint is None:
                doc = DetectLanguageInput(id=doc.id, country_hint=whole_input_hint, text=doc.text)
            elif item_hint.lower() == "none":
                doc = DetectLanguageInput(id=doc.id, country_hint="", text=doc.text)
            request_batch.append(doc)

    return request_batch

def _determine_action_type(action):
    if isinstance(action, RecognizeEntitiesAction):
        return AnalyzeBatchActionsType.RECOGNIZE_ENTITIES
    if isinstance(action, RecognizePiiEntitiesAction):
        return AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES
    if isinstance(action, RecognizeLinkedEntitiesAction):
        return AnalyzeBatchActionsType.RECOGNIZE_LINKED_ENTITIES
    return AnalyzeBatchActionsType.EXTRACT_KEY_PHRASES

def _check_string_index_type_arg(string_index_type_arg, api_version, string_index_type_default="UnicodeCodePoint"):
    string_index_type = None

    if api_version == "v3.0":
        if string_index_type_arg is not None:
            raise ValueError(
                "'string_index_type' is only available for API version V3_1_PREVIEW and up"
            )

    else:
        if string_index_type_arg is None:
            string_index_type = string_index_type_default

        else:
            string_index_type = string_index_type_arg

    return string_index_type
