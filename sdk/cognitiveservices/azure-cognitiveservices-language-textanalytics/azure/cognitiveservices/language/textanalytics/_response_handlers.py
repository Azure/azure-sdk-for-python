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
    DocumentEntities,
    Entity,
    DocumentStatistics,
    DocumentLinkedEntities,
    LinkedEntity,
    DocumentKeyPhrases,
    DocumentSentiment,
    SentenceSentiment,
    DocumentLanguage,
    DetectedLanguage,
    DocumentError,
)


def process_single_error(error):
    """Configure and raise a DocumentError for single text operation errors.
    """
    error_message = error.error["innerError"]["message"]
    error_code = error.error["code"]
    error_message += "\nErrorCode:{}".format(error_code)
    error = HttpResponseError(message=error_message)
    error.error_code = error_code
    raise error


def process_batch_error(error):
    """Raise detailed error message for HttpResponseErrors
    """
    raise_error = HttpResponseError
    if error.status_code == 401:
        raise_error = ClientAuthenticationError
    error_message = error.message
    error_code = error.status_code
    error_body = None

    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
    except DecodeError:
        pass

    if error_body is not None:
        error_resp = error_body["error"]
        if "innerError" in error_resp:
            error_resp = error_resp["innerError"]

        error_message = error_resp["message"]
        error_code = error_resp["code"]
        error_message += "\nErrorCode:{}".format(error_code)

    error = raise_error(message=error_message, response=error.response)
    error.error_code = error_code
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
                results[idx] = DocumentError(id=item.id, error=item.error)
            else:
                results[idx] = func(item)
        return results

    return wrapper


@prepare_result
def language_result(language):
    return DocumentLanguage(
        id=language.id,
        detected_languages=[DetectedLanguage._from_generated(l) for l in language.detected_languages],  # pylint: disable=protected-access
        statistics=DocumentStatistics._from_generated(language.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def entities_result(entity):
    return DocumentEntities(
        id=entity.id,
        entities=[Entity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        statistics=DocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def linked_entities_result(entity):
    return DocumentLinkedEntities(
        id=entity.id,
        entities=[LinkedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
        statistics=DocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def key_phrases_result(phrases):
    return DocumentKeyPhrases(
        id=phrases.id,
        key_phrases=phrases.key_phrases,
        statistics=DocumentStatistics._from_generated(phrases.statistics),  # pylint: disable=protected-access
    )


@prepare_result
def sentiment_result(sentiment):
    return DocumentSentiment(
        id=sentiment.id,
        sentiment=sentiment.sentiment,
        statistics=DocumentStatistics._from_generated(sentiment.statistics),  # pylint: disable=protected-access
        document_scores=sentiment.document_scores,
        sentences=[SentenceSentiment._from_generated(s) for s in sentiment.sentences],  # pylint: disable=protected-access
    )
