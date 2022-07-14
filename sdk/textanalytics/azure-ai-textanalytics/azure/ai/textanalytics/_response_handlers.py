# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import functools
from collections import defaultdict
from urllib.parse import urlparse, parse_qsl
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ResourceNotFoundError,
    ODataV4Format,
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
    AnalyzeHealthcareEntitiesResult,
    _AnalyzeActionsType,
    RecognizeCustomEntitiesResult,
    ClassifyDocumentResult,
    ActionPointerKind,
)


class CSODataV4Format(ODataV4Format):
    def __init__(self, odata_error):
        try:
            if odata_error["error"]["innererror"]:
                super().__init__(
                    odata_error["error"]["innererror"]
                )
        except KeyError:
            super().__init__(odata_error)


def process_http_response_error(error):
    """Raise detailed error message."""
    raise_error = HttpResponseError
    if error.status_code == 401:
        raise_error = ClientAuthenticationError
    if error.status_code == 404:
        raise_error = ResourceNotFoundError
    raise raise_error(response=error.response, error_format=CSODataV4Format) from error


def order_results(response, combined):
    """Order results in the order the user passed them in.

    :param response: Used to get the original documents in the request
    :param combined: A combined list of the results | errors
    :return: In order list of results | errors (if any)
    """
    try:
        request = json.loads(response.http_response.request.body)["documents"]
    except KeyError:  # language API compat
        request = json.loads(response.http_response.request.body)["analysisInput"]["documents"]
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
    ordered_response = [
        i[1] for i in sorted(mapping, key=lambda m: doc_id_order.index(m[0]))
    ]
    return ordered_response


def prepare_result(func):
    def choose_wrapper(*args, **kwargs):
        def wrapper(
            response, obj, _, ordering_function
        ):
            if hasattr(obj, "results"):
                obj = obj.results  # language API compat

            if obj.errors:
                combined = obj.documents + obj.errors
                results = ordering_function(response, combined)

            else:
                results = obj.documents

            for idx, item in enumerate(results):
                if hasattr(item, "error"):
                    results[idx] = DocumentError(
                        id=item.id,
                        error=TextAnalyticsError._from_generated(  # pylint: disable=protected-access
                            item.error
                        ),
                    )
                else:
                    results[idx] = func(item, results)
            return results

        lro = kwargs.get("lro", False)

        if lro:
            return wrapper(*args, ordering_function=order_lro_results)
        return wrapper(*args, ordering_function=order_results)

    return choose_wrapper


@prepare_result
def language_result(language, results):  # pylint: disable=unused-argument
    return DetectLanguageResult(
        id=language.id,
        primary_language=DetectedLanguage._from_generated(  # pylint: disable=protected-access
            language.detected_language
        ),
        warnings=[
            TextAnalyticsWarning._from_generated(w)  # pylint: disable=protected-access
            for w in language.warnings
        ],
        statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
            language.statistics
        ),
    )


@prepare_result
def entities_result(
    entity, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return RecognizeEntitiesResult(
        id=entity.id,
        entities=[
            CategorizedEntity._from_generated(e)  # pylint: disable=protected-access
            for e in entity.entities
        ],
        warnings=[
            TextAnalyticsWarning._from_generated(w)  # pylint: disable=protected-access
            for w in entity.warnings
        ],
        statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
            entity.statistics
        ),
    )


@prepare_result
def linked_entities_result(
    entity, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return RecognizeLinkedEntitiesResult(
        id=entity.id,
        entities=[
            LinkedEntity._from_generated(e)  # pylint: disable=protected-access
            for e in entity.entities
        ],
        warnings=[
            TextAnalyticsWarning._from_generated(w)  # pylint: disable=protected-access
            for w in entity.warnings
        ],
        statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
            entity.statistics
        ),
    )


@prepare_result
def key_phrases_result(
    phrases, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return ExtractKeyPhrasesResult(
        id=phrases.id,
        key_phrases=phrases.key_phrases,
        warnings=[
            TextAnalyticsWarning._from_generated(w)  # pylint: disable=protected-access
            for w in phrases.warnings
        ],
        statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
            phrases.statistics
        ),
    )


@prepare_result
def sentiment_result(
    sentiment, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return AnalyzeSentimentResult(
        id=sentiment.id,
        sentiment=sentiment.sentiment,
        warnings=[
            TextAnalyticsWarning._from_generated(w)  # pylint: disable=protected-access
            for w in sentiment.warnings
        ],
        statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
            sentiment.statistics
        ),
        confidence_scores=SentimentConfidenceScores._from_generated(  # pylint: disable=protected-access
            sentiment.confidence_scores
        ),
        sentences=[
            SentenceSentiment._from_generated(  # pylint: disable=protected-access
                s, results, sentiment
            )
            for s in sentiment.sentences
        ],
    )


@prepare_result
def pii_entities_result(
    entity, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return RecognizePiiEntitiesResult(
        id=entity.id,
        entities=[
            PiiEntity._from_generated(e)  # pylint: disable=protected-access
            for e in entity.entities
        ],
        redacted_text=entity.redacted_text
        if hasattr(entity, "redacted_text")
        else None,
        warnings=[
            TextAnalyticsWarning._from_generated(w)  # pylint: disable=protected-access
            for w in entity.warnings
        ],
        statistics=TextDocumentStatistics._from_generated(  # pylint: disable=protected-access
            entity.statistics
        ),
    )


@prepare_result
def healthcare_result(
    health_result, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return AnalyzeHealthcareEntitiesResult._from_generated(  # pylint: disable=protected-access
        health_result
    )


@prepare_result
def custom_entities_result(
    custom_entities, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return RecognizeCustomEntitiesResult._from_generated(  # pylint: disable=protected-access
        custom_entities
    )


@prepare_result
def classify_document_result(
    custom_categories, results, *args, **kwargs
):  # pylint: disable=unused-argument
    return ClassifyDocumentResult._from_generated(  # pylint: disable=protected-access
        custom_categories
    )


def healthcare_extract_page_data(
    doc_id_order, obj, health_job_state
):  # pylint: disable=unused-argument
    return (
        health_job_state.next_link,
        healthcare_result(
            doc_id_order,
            health_job_state.results
            if hasattr(health_job_state, "results")
            else health_job_state.tasks.items[0].results,
            {},
            lro=True
        ),
    )


def _get_deserialization_callback_from_task_type(task_type):  # pylint: disable=too-many-return-statements
    if task_type == _AnalyzeActionsType.RECOGNIZE_ENTITIES:
        return entities_result
    if task_type == _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES:
        return pii_entities_result
    if task_type == _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES:
        return linked_entities_result
    if task_type == _AnalyzeActionsType.ANALYZE_SENTIMENT:
        return sentiment_result
    if task_type == _AnalyzeActionsType.RECOGNIZE_CUSTOM_ENTITIES:
        return custom_entities_result
    if task_type == _AnalyzeActionsType.SINGLE_LABEL_CLASSIFY:
        return classify_document_result
    if task_type == _AnalyzeActionsType.MULTI_CATEGORY_CLASSIFY:
        return classify_document_result
    if task_type == _AnalyzeActionsType.ANALYZE_HEALTHCARE_ENTITIES:
        return healthcare_result
    return key_phrases_result


def _get_property_name_from_task_type(task_type):  # pylint: disable=too-many-return-statements
    """v3.1 only"""
    if task_type == _AnalyzeActionsType.RECOGNIZE_ENTITIES:
        return "entity_recognition_tasks"
    if task_type == _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES:
        return "entity_recognition_pii_tasks"
    if task_type == _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES:
        return "entity_linking_tasks"
    if task_type == _AnalyzeActionsType.ANALYZE_SENTIMENT:
        return "sentiment_analysis_tasks"
    return "key_phrase_extraction_tasks"


def get_task_from_pointer(task_type):  # pylint: disable=too-many-return-statements
    """v3.1 only"""
    if task_type == ActionPointerKind.RECOGNIZE_ENTITIES:
        return "entity_recognition_tasks"
    if task_type == ActionPointerKind.RECOGNIZE_PII_ENTITIES:
        return "entity_recognition_pii_tasks"
    if task_type == ActionPointerKind.RECOGNIZE_LINKED_ENTITIES:
        return "entity_linking_tasks"
    if task_type == ActionPointerKind.ANALYZE_SENTIMENT:
        return "sentiment_analysis_tasks"
    return "key_phrase_extraction_tasks"


def resolve_action_pointer(pointer):
    import re
    pointer_union = "|".join(value for value in ActionPointerKind)
    found = re.search(fr"#/tasks/({pointer_union})/\d+", pointer)
    if found:
        index = int(pointer[-1])
        task = pointer.split("#/tasks/")[1].split("/")[0]
        property_name = get_task_from_pointer(task)
        return property_name, index
    raise ValueError(
        f"Unexpected response from service - action pointer '{pointer}' is not a valid action pointer."
    )


def pad_result(tasks_obj, doc_id_order):
    return [
        DocumentError(
            id=doc_id,
            error=TextAnalyticsError(message=f"No result for document. Action returned status '{tasks_obj.status}'.")
        ) for doc_id in doc_id_order
    ]


def get_ordered_errors(tasks_obj, task_name, doc_id_order):
    # throw exception if error missing a target
    missing_target = any([error for error in tasks_obj.errors if error.target is None])
    if missing_target:
        message = "".join([f"({err.code}) {err.message}" for err in tasks_obj.errors])
        raise HttpResponseError(message=message)

    # create a DocumentError per input doc with the action error details
    for err in tasks_obj.errors:
        # language API compat
        if err.target.find("items") != -1:
            action = tasks_obj.tasks.items[int(err.target.split("/")[-1])]
        else:
            property_name, index = resolve_action_pointer(err.target)
            actions = getattr(tasks_obj.tasks, property_name)
            action = actions[index]
        if action.task_name == task_name:
            errors = [
                DocumentError(
                    id=doc_id,
                    error=TextAnalyticsError(code=err.code, message=err.message)
                ) for doc_id in doc_id_order
            ]
            return errors
    raise ValueError("Unexpected response from service - no errors for missing action results.")


def _get_doc_results(task, doc_id_order, returned_tasks_object):
    returned_tasks = returned_tasks_object.tasks
    current_task_type, task_name = task
    deserialization_callback = _get_deserialization_callback_from_task_type(
        current_task_type
    )
    # language api compat
    property_name = \
        "items" if hasattr(returned_tasks, "items") else _get_property_name_from_task_type(current_task_type)
    try:
        response_task_to_deserialize = \
            next(task for task in getattr(returned_tasks, property_name) if task.task_name == task_name)
    except StopIteration:
        raise ValueError("Unexpected response from service - unable to deserialize result.")

    # if no results present, check for action errors
    if response_task_to_deserialize.results is None:
        return get_ordered_errors(returned_tasks_object, task_name, doc_id_order)

    # if results obj present, but no document results (likely a canceled scenario)
    if not response_task_to_deserialize.results.documents:
        return pad_result(returned_tasks_object, doc_id_order)
    return deserialization_callback(
        doc_id_order, response_task_to_deserialize.results, {}, lro=True
    )


def get_iter_items(doc_id_order, task_order, bespoke, analyze_job_state):
    iter_items = defaultdict(list)  # map doc id to action results
    returned_tasks_object = analyze_job_state

    if bespoke:
        return _get_doc_results(
            task_order[0],
            doc_id_order,
            returned_tasks_object,
        )

    for task in task_order:
        results = _get_doc_results(
            task,
            doc_id_order,
            returned_tasks_object,
        )
        for result in results:
            iter_items[result.id].append(result)

    return [iter_items[doc_id] for doc_id in doc_id_order if doc_id in iter_items]


def analyze_extract_page_data(
    doc_id_order, task_order, bespoke, analyze_job_state
):
    # return next link, list of
    iter_items = get_iter_items(
        doc_id_order, task_order, bespoke, analyze_job_state
    )
    return analyze_job_state.next_link, iter_items


def lro_get_next_page(
    lro_status_callback, first_page, continuation_token, show_stats=False
):
    if continuation_token is None:
        return first_page

    try:
        continuation_token = continuation_token.decode("utf-8")

    except AttributeError:
        pass

    parsed_url = urlparse(continuation_token)
    job_id = parsed_url.path.split("/")[-1]
    query_params = dict(parse_qsl(parsed_url.query.replace("$", "")))
    if "showStats" in query_params:
        query_params.pop("showStats")
    if "api-version" in query_params:  # language api compat
        query_params.pop("api-version")
    query_params["show_stats"] = show_stats

    return lro_status_callback(job_id, **query_params)


def healthcare_paged_result(
    doc_id_order, health_status_callback, _, obj, show_stats=False
):
    return ItemPaged(
        functools.partial(
            lro_get_next_page, health_status_callback, obj, show_stats=show_stats
        ),
        functools.partial(
            healthcare_extract_page_data, doc_id_order, obj
        ),
    )


def analyze_paged_result(
    doc_id_order,
    task_order,
    analyze_status_callback,
    _,
    obj,
    show_stats=False,
    bespoke=False
):
    return ItemPaged(
        functools.partial(
            lro_get_next_page, analyze_status_callback, obj, show_stats=show_stats
        ),
        functools.partial(
            analyze_extract_page_data, doc_id_order, task_order, bespoke
        ),
    )


def _get_result_from_continuation_token(
    client, continuation_token, poller_type, polling_method, callback, bespoke=False
):
    def result_callback(initial_response, pipeline_response):
        doc_id_order = initial_response.context.options["doc_id_order"]
        show_stats = initial_response.context.options["show_stats"]
        task_id_order = initial_response.context.options.get("task_id_order")
        return callback(
            pipeline_response,
            None,
            doc_id_order,
            task_id_order=task_id_order,
            show_stats=show_stats,
            bespoke=bespoke
        )

    return poller_type.from_continuation_token(
            polling_method=polling_method,
            client=client,
            deserialization_callback=result_callback,
            continuation_token=continuation_token
        )
