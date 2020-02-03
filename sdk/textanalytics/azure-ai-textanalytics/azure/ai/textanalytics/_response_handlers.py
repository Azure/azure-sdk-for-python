# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    DecodeError,
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


def process_batch_error(error):
    """Raise detailed error message for HttpResponseErrors
    """
    raise_error = HttpResponseError
    if error.status_code == 401:
        raise_error = ClientAuthenticationError
    error_message = error.message
    error_code = error.status_code
    error_body, error_target = None, None

    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
    except DecodeError:
        pass

    try:
        if error_body is not None:
            error_resp = error_body["error"]
            if "innerError" in error_resp:
                error_resp = error_resp["innerError"]

            error_message = error_resp["message"]
            error_code = error_resp["code"]
            error_target = error_resp.get("target", None)
            if error_target:
                error_message += "\nErrorCode:{}\nTarget:{}".format(error_code, error_target)
            else:
                error_message += "\nErrorCode:{}".format(error_code)
    except KeyError:
        raise HttpResponseError(message="There was an unknown error with the request.")

    error = raise_error(message=error_message, response=error.response)
    error.error_code = error_code
    error.target = error_target
    raise error


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
