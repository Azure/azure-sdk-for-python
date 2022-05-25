# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


from ._models import (
    DetectLanguageInput,
    TextDocumentInput,
    _AnalyzeActionsType,
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

    if isinstance(documents, str):
        raise TypeError("Input documents cannot be a string.")

    if isinstance(documents, dict):
        raise TypeError("Input documents cannot be a dict")

    if not all(isinstance(x, str) for x in documents):
        if not all(
            isinstance(x, (dict, TextDocumentInput, DetectLanguageInput))
            for x in documents
        ):
            raise TypeError(
                "Mixing string and dictionary/object document input unsupported."
            )

    request_batch = []
    for idx, doc in enumerate(documents):
        if isinstance(doc, str):
            if hint == "country_hint" and whole_input_hint.lower() == "none":
                whole_input_hint = ""
            document = {"id": str(idx), hint: whole_input_hint, "text": doc}
            request_batch.append(document)
        if isinstance(doc, dict):
            item_hint = doc.get(hint, None)
            if item_hint is None:
                doc = {
                    "id": doc.get("id", None),
                    hint: whole_input_hint,
                    "text": doc.get("text", None),
                }
            elif item_hint.lower() == "none":
                doc = {
                    "id": doc.get("id", None),
                    hint: "",
                    "text": doc.get("text", None),
                }
            request_batch.append(doc)
        if isinstance(doc, TextDocumentInput):
            item_hint = doc.language
            if item_hint is None:
                doc = TextDocumentInput(
                    id=doc.id, language=whole_input_hint, text=doc.text
                )
            request_batch.append(doc)
        if isinstance(doc, DetectLanguageInput):
            item_hint = doc.country_hint
            if item_hint is None:
                doc = DetectLanguageInput(
                    id=doc.id, country_hint=whole_input_hint, text=doc.text
                )
            elif item_hint.lower() == "none":
                doc = DetectLanguageInput(id=doc.id, country_hint="", text=doc.text)
            request_batch.append(doc)

    return request_batch


def _determine_action_type(action):  # pylint: disable=too-many-return-statements
    if action.__class__.__name__ in ["EntitiesTask", "EntitiesLROTask"]:
        return _AnalyzeActionsType.RECOGNIZE_ENTITIES
    if action.__class__.__name__ in ["PiiTask", "PiiLROTask"]:
        return _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES
    if action.__class__.__name__ in ["EntityLinkingTask", "EntityLinkingLROTask"]:
        return _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES
    if action.__class__.__name__ in ["SentimentAnalysisTask", "SentimentAnalysisLROTask"]:
        return _AnalyzeActionsType.ANALYZE_SENTIMENT
    if action.__class__.__name__ == "ExtractiveSummarizationLROTask":
        return _AnalyzeActionsType.EXTRACT_SUMMARY
    if action.__class__.__name__ == "CustomEntitiesLROTask":
        return _AnalyzeActionsType.RECOGNIZE_CUSTOM_ENTITIES
    if action.__class__.__name__ == "CustomSingleLabelClassificationLROTask":
        return _AnalyzeActionsType.SINGLE_CATEGORY_CLASSIFY
    if action.__class__.__name__ == "CustomMultiLabelClassificationLROTask":
        return _AnalyzeActionsType.MULTI_CATEGORY_CLASSIFY
    if action.__class__.__name__ == "HealthcareLROTask":
        return _AnalyzeActionsType.ANALYZE_HEALTHCARE_ENTITIES
    return _AnalyzeActionsType.EXTRACT_KEY_PHRASES
