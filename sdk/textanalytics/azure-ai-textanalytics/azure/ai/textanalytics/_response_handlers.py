# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import functools
from urllib.parse import urlparse, parse_qsl
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ODataV4Format
)
from azure.core.paging import ItemPaged
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
    TextAnalyticsWarning,
    RecognizePiiEntitiesResult,
    PiiEntity,
    RecognizeHealthcareEntitiesResult,
    HealthcareEntity,
    HealthcareRelation,
    TextAnalysisResult
)

class CSODataV4Format(ODataV4Format):

    def __init__(self, odata_error):
        try:
            if odata_error["error"]["innererror"]:
                super(CSODataV4Format, self).__init__(odata_error["error"]["innererror"])
        except KeyError:
            super(CSODataV4Format, self).__init__(odata_error)


def process_http_response_error(error):
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
    def wrapper(response, obj, response_headers, lro=False):  # pylint: disable=unused-argument
        if obj.errors:
            combined = obj.documents + obj.errors
            if lro:
                results = combined
            else:
                results = order_results(response, combined)
        else:
            results = obj.documents

        for idx, item in enumerate(results):
            if hasattr(item, "error"):
                results[idx] = DocumentError(id=item.id, error=TextAnalyticsError._from_generated(item.error))  # pylint: disable=protected-access
            else:
                results[idx] = func(item, results)
        return results

    return wrapper


@prepare_result
def language_result(language, results):  # pylint: disable=unused-argument
    return DetectLanguageResult(
        id=language.id,
        primary_language=DetectedLanguage._from_generated(language.detected_language),  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in language.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(language.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def entities_result(entity, results):  # pylint: disable=unused-argument
    return RecognizeEntitiesResult(
        id=entity.id,
        entities=[CategorizedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def linked_entities_result(entity, results):  # pylint: disable=unused-argument
    return RecognizeLinkedEntitiesResult(
        id=entity.id,
        entities=[LinkedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def key_phrases_result(phrases, results):  # pylint: disable=unused-argument
    return ExtractKeyPhrasesResult(
        id=phrases.id,
        key_phrases=phrases.key_phrases,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in phrases.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(phrases.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def sentiment_result(sentiment, results):
    return AnalyzeSentimentResult(
        id=sentiment.id,
        sentiment=sentiment.sentiment,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in sentiment.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(sentiment.statistics),  # pylint: disable=protected-access
        confidence_scores=SentimentConfidenceScores._from_generated(sentiment.confidence_scores),  # pylint: disable=protected-access
        sentences=[SentenceSentiment._from_generated(s, results, sentiment) for s in sentiment.sentences],  # pylint: disable=protected-access
    )

@prepare_result
def pii_entities_result(entity, results):  # pylint: disable=unused-argument
    return RecognizePiiEntitiesResult(
        id=entity.id,
        entities=[PiiEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        redacted_text=entity.redacted_text if hasattr(entity, "redacted_text") else None,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def healthcare_result(health_result):
    return RecognizeHealthcareEntitiesResult._from_generated(health_result)


def healthcare_extract_page_data(response, obj, response_headers, health_job_state):
    return health_job_state.next_link, [healthcare_result(response, result, response_headers, lro=True) for result in health_job_state.results]


def lro_get_next_page(lro_status_callback, continuation_token):
    parsed_url = urlparse(continuation_token)
    job_id = parsed_url.path.split("/")[-1]
    query_params = dict(parse_qsl(parsed_url.query.replace("$", "")))
    return lro_status_callback(job_id, **query_params)
    

def healthcare_paged_result(health_status_callback, response, obj, response_headers):
    return ItemPaged(
        functools.partial(lro_get_next_page, health_status_callback),
        functools.partial(healthcare_extract_page_data, response, obj, response_headers),
        None
    )