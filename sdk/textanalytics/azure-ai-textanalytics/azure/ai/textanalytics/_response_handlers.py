# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ODataV4Format
)
from ._models import (
    RecognizeEntitiesResult,
    CategorizedEntity,
    TextDocumentStatistics,
    RecognizeLinkedEntitiesResult,
    RecognizePiiEntitiesResult,
    LinkedEntity,
    ExtractKeyPhrasesResult,
    AnalyzeSentimentResult,
    SentenceSentiment,
    DetectLanguageResult,
    DetectedLanguage,
    DocumentError,
    SentimentScorePerLabel,
    TextAnalyticsError,
    PiiEntity
)


class CSODataV4Format(ODataV4Format):
    INNERERROR_LABEL = "innerError"  # Service plans to fix casing ("innererror") to reflect ODataV4 error spec

    def __init__(self, odata_error):
        try:
            if odata_error["error"]["innerError"]:
                super(CSODataV4Format, self).__init__(odata_error["error"]["innerError"])
        except KeyError:
            super(CSODataV4Format, self).__init__(odata_error)


def process_batch_error(error):
    """Raise detailed error message.
    """
    raise_error = HttpResponseError
    if error.status_code == 401:
        raise_error = ClientAuthenticationError
    raise raise_error(response=error.response, error_format=CSODataV4Format)


def order_results(response, combined):
    """Order results in the order the user passed them in.

    :param response: Used to get the original documents in the request
    :param combined: A combined list of the results | errors
    :return: In order list of results | errors (if any)
    """
    request = json.loads(response.request.body)["documents"]
    mapping = {item.id: item for item in combined}
    ordered_response = [mapping[item["id"]] for item in request]
    return ordered_response


def prepare_result(func):
    def wrapper(response, obj, response_headers):  # pylint: disable=unused-argument
        if obj.errors:
            combined = obj.documents + obj.errors
            results = order_results(response, combined)
        else:
            results = obj.documents

        for idx, item in enumerate(results):
            if hasattr(item, "error"):
                results[idx] = DocumentError(id=item.id, error=TextAnalyticsError._from_generated(item.error))  # pylint: disable=protected-access
            else:
                results[idx] = func(item)
        return results

    return wrapper


@prepare_result
def language_result(language):
    return DetectLanguageResult(
        id=language.id,
        primary_language=DetectedLanguage._from_generated(language.detected_languages[0]),  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(language.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def entities_result(entity):
    return RecognizeEntitiesResult(
        id=entity.id,
        entities=[CategorizedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def pii_entities_result(entity):
    return RecognizePiiEntitiesResult(
        id=entity.id,
        entities=[PiiEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def linked_entities_result(entity):
    return RecognizeLinkedEntitiesResult(
        id=entity.id,
        entities=[LinkedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def key_phrases_result(phrases):
    return ExtractKeyPhrasesResult(
        id=phrases.id,
        key_phrases=phrases.key_phrases,
        statistics=TextDocumentStatistics._from_generated(phrases.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def sentiment_result(sentiment):
    return AnalyzeSentimentResult(
        id=sentiment.id,
        sentiment=sentiment.sentiment.value,
        statistics=TextDocumentStatistics._from_generated(sentiment.statistics),  # pylint: disable=protected-access
        sentiment_scores=SentimentScorePerLabel._from_generated(sentiment.document_scores),  # pylint: disable=protected-access
        sentences=[SentenceSentiment._from_generated(s) for s in sentiment.sentences],  # pylint: disable=protected-access
    )
