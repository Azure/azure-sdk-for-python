# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import functools
from collections import defaultdict
from six.moves.urllib.parse import urlparse, parse_qsl
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
    TextAnalyticsWarning,
    RecognizePiiEntitiesResult,
    PiiEntity,
    AnalyzeHealthcareEntitiesResultItem,
    AnalyzeBatchActionsResult,
    RequestStatistics,
    AnalyzeBatchActionsType,
    AnalyzeBatchActionsError,
    _get_indices,
)
from ._paging import AnalyzeHealthcareEntitiesResult, AnalyzeResult

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


def order_lro_results(doc_id_order, combined):
    """Order results in the order the user passed them in.
    For long running operations, we need to explicitly pass in the
    document ids since the initial request will no longer be available.

    :param doc_id_order: A list of document IDs from the original request.
    :param combined: A combined list of the results | errors
    :return: In order list of results | errors (if any)
    """

    mapping = [(item.id, item) for item in combined]
    ordered_response = [i[1] for i in sorted(mapping, key=lambda m: doc_id_order.index(m[0]))]
    return ordered_response


def prepare_result(func):
    def choose_wrapper(*args, **kwargs):
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
                    results[idx] = func(item, results)
            return results

        def lro_wrapper(doc_id_order, obj, response_headers):  # pylint: disable=unused-argument
            if obj.errors:
                combined = obj.documents + obj.errors

                results = order_lro_results(doc_id_order, combined)
            else:
                results = obj.documents

            for idx, item in enumerate(results):
                if hasattr(item, "error"):
                    results[idx] = DocumentError(id=item.id, error=TextAnalyticsError._from_generated(item.error))  # pylint: disable=protected-access
                else:
                    results[idx] = func(item, results)
            return results

        lro = kwargs.get("lro", False)

        if lro:
            return lro_wrapper(*args)

        return wrapper(*args)

    return choose_wrapper


@prepare_result
def language_result(language, results):  # pylint: disable=unused-argument
    return DetectLanguageResult(
        id=language.id,
        primary_language=DetectedLanguage._from_generated(language.detected_language),  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in language.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(language.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def entities_result(entity, results, *args, **kwargs):  # pylint: disable=unused-argument
    return RecognizeEntitiesResult(
        id=entity.id,
        entities=[CategorizedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def linked_entities_result(entity, results, *args, **kwargs):  # pylint: disable=unused-argument
    return RecognizeLinkedEntitiesResult(
        id=entity.id,
        entities=[LinkedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def key_phrases_result(phrases, results, *args, **kwargs):  # pylint: disable=unused-argument
    return ExtractKeyPhrasesResult(
        id=phrases.id,
        key_phrases=phrases.key_phrases,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in phrases.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(phrases.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def sentiment_result(sentiment, results, *args, **kwargs): # pylint: disable=unused-argument
    return AnalyzeSentimentResult(
        id=sentiment.id,
        sentiment=sentiment.sentiment,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in sentiment.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(sentiment.statistics),  # pylint: disable=protected-access
        confidence_scores=SentimentConfidenceScores._from_generated(sentiment.confidence_scores),  # pylint: disable=protected-access
        sentences=[SentenceSentiment._from_generated(s, results, sentiment) for s in sentiment.sentences],  # pylint: disable=protected-access
    )

@prepare_result
def pii_entities_result(entity, results, *args, **kwargs):  # pylint: disable=unused-argument
    return RecognizePiiEntitiesResult(
        id=entity.id,
        entities=[PiiEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        redacted_text=entity.redacted_text if hasattr(entity, "redacted_text") else None,
        warnings=[TextAnalyticsWarning._from_generated(w) for w in entity.warnings],  # pylint: disable=protected-access
        statistics=TextDocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def healthcare_result(health_result, results, *args, **kwargs): # pylint: disable=unused-argument
    return AnalyzeHealthcareEntitiesResultItem._from_generated(health_result) # pylint: disable=protected-access


def healthcare_extract_page_data(doc_id_order, obj, response_headers, health_job_state): # pylint: disable=unused-argument
    return (health_job_state.next_link,
        healthcare_result(doc_id_order, health_job_state.results, response_headers, lro=True))

def _get_deserialization_callback_from_task_type(task_type):
    if task_type == AnalyzeBatchActionsType.RECOGNIZE_ENTITIES:
        return entities_result
    if task_type == AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES:
        return pii_entities_result
    if task_type == AnalyzeBatchActionsType.RECOGNIZE_LINKED_ENTITIES:
        return linked_entities_result
    return key_phrases_result

def _get_property_name_from_task_type(task_type):
    if task_type == AnalyzeBatchActionsType.RECOGNIZE_ENTITIES:
        return "entity_recognition_tasks"
    if task_type == AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES:
        return "entity_recognition_pii_tasks"
    if task_type == AnalyzeBatchActionsType.RECOGNIZE_LINKED_ENTITIES:
        return "entity_linking_tasks"
    return "key_phrase_extraction_tasks"

def _num_tasks_in_current_page(returned_tasks_object):
    return (
        len(returned_tasks_object.entity_recognition_tasks or []) +
        len(returned_tasks_object.entity_recognition_pii_tasks or []) +
        len(returned_tasks_object.key_phrase_extraction_tasks or []) +
        len(returned_tasks_object.entity_linking_tasks or [])
    )

def _get_task_type_from_error(error):
    if "pii" in error.target.lower():
        return AnalyzeBatchActionsType.RECOGNIZE_PII_ENTITIES
    if "entityrecognition" in error.target.lower():
        return AnalyzeBatchActionsType.RECOGNIZE_ENTITIES
    if "entitylinking" in error.target.lower():
        return AnalyzeBatchActionsType.RECOGNIZE_LINKED_ENTITIES
    return AnalyzeBatchActionsType.EXTRACT_KEY_PHRASES

def _get_mapped_errors(analyze_job_state):
    """
    """
    mapped_errors = defaultdict(list)
    if not analyze_job_state.errors:
        return mapped_errors
    for error in analyze_job_state.errors:
        mapped_errors[_get_task_type_from_error(error)].append((_get_error_index(error), error))
    return mapped_errors

def _get_error_index(error):
    return _get_indices(error.target)[-1]

def _get_good_result(current_task_type, index_of_task_result, doc_id_order, response_headers, returned_tasks_object):
    deserialization_callback = _get_deserialization_callback_from_task_type(current_task_type)
    property_name = _get_property_name_from_task_type(current_task_type)
    response_task_to_deserialize = getattr(returned_tasks_object, property_name)[index_of_task_result]
    document_results = deserialization_callback(
        doc_id_order, response_task_to_deserialize.results, response_headers, lro=True
    )
    return AnalyzeBatchActionsResult(
        document_results=document_results,
        statistics=RequestStatistics._from_generated( # pylint: disable=protected-access
            response_task_to_deserialize.results.statistics
        ) if response_task_to_deserialize.results.statistics else None,
        action_type=current_task_type,
        completed_on=response_task_to_deserialize.last_update_date_time,
    )

def get_iter_items(doc_id_order, task_order, response_headers, analyze_job_state):
    iter_items = []
    task_type_to_index = defaultdict(int)  # need to keep track of how many of each type of tasks we've seen
    returned_tasks_object = analyze_job_state.tasks
    mapped_errors = _get_mapped_errors(analyze_job_state)
    for current_task_type in task_order:
        index_of_task_result = task_type_to_index[current_task_type]

        try:
            # try to deserailize as error. If fails, we know it's good
            # kind of a weird way to order things, but we can fail when deserializing
            # the curr response as an error, not when deserializing as a good response.

            current_task_type_errors = mapped_errors[current_task_type]
            error = next(err for err in current_task_type_errors if err[0] == index_of_task_result)
            result = AnalyzeBatchActionsError._from_generated(error[1])  # pylint: disable=protected-access
        except StopIteration:
            result = _get_good_result(
                current_task_type, index_of_task_result, doc_id_order, response_headers, returned_tasks_object
            )
        iter_items.append(result)
        task_type_to_index[current_task_type] += 1
    return iter_items

def analyze_extract_page_data(doc_id_order, task_order, response_headers, analyze_job_state):
    # return next link, list of
    iter_items = get_iter_items(doc_id_order, task_order, response_headers, analyze_job_state)
    return analyze_job_state.next_link, iter_items


def lro_get_next_page(lro_status_callback, first_page, continuation_token, show_stats=False):
    if continuation_token is None:
        return first_page

    try:
        continuation_token = continuation_token.decode("utf-8")

    except AttributeError:
        pass

    parsed_url = urlparse(continuation_token)
    job_id = parsed_url.path.split("/")[-1]
    query_params = dict(parse_qsl(parsed_url.query.replace("$", "")))
    query_params["show_stats"] = show_stats

    return lro_status_callback(job_id, **query_params)


def healthcare_paged_result(doc_id_order, health_status_callback, _, obj, response_headers, show_stats=False): # pylint: disable=unused-argument
    return AnalyzeHealthcareEntitiesResult(
        functools.partial(lro_get_next_page, health_status_callback, obj, show_stats=show_stats),
        functools.partial(healthcare_extract_page_data, doc_id_order, obj, response_headers),
        model_version=obj.results.model_version,
        statistics=RequestStatistics._from_generated(obj.results.statistics) if show_stats else None # pylint: disable=protected-access
    )

def analyze_paged_result(doc_id_order, task_order, analyze_status_callback, _, obj, response_headers, show_stats=False): # pylint: disable=unused-argument
    return AnalyzeResult(
        functools.partial(lro_get_next_page, analyze_status_callback, obj, show_stats=show_stats),
        functools.partial(analyze_extract_page_data, doc_id_order, task_order, response_headers)
    )

def _get_deserialize():
    from ._generated.v3_1_preview_4 import TextAnalyticsClient
    return TextAnalyticsClient("dummy", "dummy")._deserialize  # pylint: disable=protected-access
