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
    LinkedEntity,
    ExtractKeyPhrasesResult,
    AnalyzeSentimentResult,
    SentenceSentiment,
    DetectLanguageResult,
    DetectedLanguage,
    DocumentError,
    SentimentConfidenceScores,
    TextAnalyticsError,
    TextAnalyticsWarning
)

class CSODataV4Format(ODataV4Format):

    def __init__(self, odata_error):
        try:
            if odata_error["error"]["innererror"]:
                super(CSODataV4Format, self).__init__(odata_error["error"]["innererror"])
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
    request = json.loads(response.http_response.request.body)["documents"]
    mapping = {item.id: item for item in combined}
    ordered_response = [mapping[item["id"]] for item in request]
    return ordered_response


def prepare_result(func):
    def _get_error_code_and_message(error):
        if hasattr(error.error, 'innererror') and error.error.innererror:
            return error.error.innererror.code, error.error.innererror.message
        return error.error.code, error.error.message

    def _deal_with_too_many_documents(response, obj):
        # special case for now if there are too many documents in the request
        too_many_documents_errors = [
            error for error in obj.errors if error.id == ""
        ]
        if too_many_documents_errors:
            too_many_documents_error = too_many_documents_errors[0]
            response.status_code = 400
            response.reason = "Bad Request"
            code, message = _get_error_code_and_message(too_many_documents_error)
            raise HttpResponseError(
                message="({}) {}".format(code, message),
                response=response
            )

    def wrapper(response, obj, response_headers):  # pylint: disable=unused-argument
        if obj.errors:
            _deal_with_too_many_documents(response.http_response, obj)
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
        primary_language=DetectedLanguage._from_generated(language.detected_language),  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in language.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(language.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def entities_result(entity):
    return RecognizeEntitiesResult(
        id=entity.id,
        entities=[CategorizedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def linked_entities_result(entity):
    return RecognizeLinkedEntitiesResult(
        id=entity.id,
        entities=[LinkedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def key_phrases_result(phrases):
    return ExtractKeyPhrasesResult(
        id=phrases.id,
        key_phrases=phrases.key_phrases,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in phrases.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(phrases.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def sentiment_result(sentiment):
    return AnalyzeSentimentResult(
        id=sentiment.id,
        sentiment=sentiment.sentiment,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in sentiment.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(sentiment.statistics),  # pylint: disable=protected-access
        confidence_scores=SentimentConfidenceScores._from_generated(sentiment.confidence_scores),  # pylint: disable=protected-access
        sentences=[SentenceSentiment._from_generated(s) for s in sentiment.sentences],  # pylint: disable=protected-access
    )
