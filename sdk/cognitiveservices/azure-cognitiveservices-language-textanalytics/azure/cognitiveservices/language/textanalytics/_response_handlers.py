# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import six
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    DecodeError,
)
from ._models import (
    LanguageInput,
    MultiLanguageInput,
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
    Error
)


# TODO: remove this method after service bug fix
def process_entities_error(error):
    """This should be removed after the bug with entities APIs is fixed.
    """
    raise_error = HttpResponseError
    error_message = error.message
    error_code = error.code
    error_message += "\nErrorCode:{}".format(error_code)
    error = raise_error(message=error_message)
    error.error_code = error_code
    raise error


def process_single_error(error):
    """We actually raise the DocumentError for single text operations.
    """
    raise_error = HttpResponseError
    error_message = error.error["innerError"]["message"]
    error_code = error.error["code"]
    error_message += "\nErrorCode:{}".format(error_code)
    error = raise_error(message=error_message)
    error.error_code = error_code
    raise error


# TODO: refactor this function
def process_batch_error(error):
    """Raise and return detailed error message for HttpResponseErrors
    """
    try:
        raise_error = HttpResponseError
        if error.status_code == 401:
            raise_error = ClientAuthenticationError
        error_message = error.message

        try:
            error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
            if error_body is None:
                error = raise_error(message=error_message, response=error.response)
                error.error_code = error.status_code
                raise error
            try:
                error_message = error_body["error"]["message"]
            except KeyError:
                error_message = error_body["innerError"]["message"]
            error_message += "\nErrorCode:{}".format(error.status_code)
        except DecodeError:
            pass

        error = raise_error(message=error_message, response=error.response)
        error.error_code = error.status_code
        raise error
    except Exception:
        raise error


def whole_batch_error(err):
    """500 status code error for batch.
    """
    return Error(
        code=err.code,
        message=err.message,
        target=err.target,
        innererror=err.innererror,
        details=err.details
    )


def _validate_single_input(text, hint, hint_value):
    """Validate text input is string. Let service handle
    validity of hint and hint value.

    :param str text: A single text document.
    :param str hint: Could be country_hint or language
    :param str hint_value: The user passed country_hint or language
    :return: A LanguageInput or MultiLanguageInput
    """
    if isinstance(text, six.text_type):
        return [{"id": "0", "text": text, hint: hint_value}]
    else:
        raise TypeError("Text parameter must be string.")


def _validate_batch_input(documents):
    """Validate that batch input has either all string docs
    or dict/LanguageInput/MultiLanguageInput, not a mix of both.

    :param list documents: The input documents.
    :return: A list of LanguageInput or MultiLanguageInput
    """
    string_input = False
    for idx, doc in enumerate(documents):
        if isinstance(doc, six.text_type):
            documents[idx] = {"id": str(idx), "text": doc}
            string_input = True
        if isinstance(doc, (dict, MultiLanguageInput, LanguageInput)):
            if string_input:
                raise TypeError("Mixing string and dictionary input unsupported.")
    return documents


def order_results(response, combined):
    """Order results in the order the user passed them in.

    :param response: Used to get the original documents in the request
    :param combined: A combined list of the results | errors
    :return: In order list of results | errors (if any)
    """
    request = json.loads(response.request.body)["documents"]
    mapping = {}
    for item in combined:
        mapping[item.id] = item

    ordered_response = []
    for item in request:
        ordered_response.append(mapping[item["id"]])
    return ordered_response


def language_result(response, obj, response_headers):
    if hasattr(obj, "innererror"):
        return whole_batch_error(obj)

    if obj.errors:
        combined = obj.documents + obj.errors
        results = order_results(response, combined)
    else:
        results = obj.documents

    for idx, language in enumerate(results):
        if hasattr(language, "error"):
            results[idx] = DocumentError(id=language.id, error=language.error)
        else:
            results[idx] = DocumentLanguage(
                id=language.id,
                detected_languages=[DetectedLanguage._from_generated(l) for l in language.detected_languages],
                statistics=DocumentStatistics._from_generated(language.statistics),
            )
    return results


def entities_result(response, obj, response_headers):
    if hasattr(obj, "innererror"):
        return whole_batch_error(obj)

    if obj.errors:
        combined = obj.documents + obj.errors
        results = order_results(response, combined)
    else:
        results = obj.documents

    for idx, entity in enumerate(results):
        if hasattr(entity, "error"):
            results[idx] = DocumentError(id=entity.id, error=entity.error)
        else:
            results[idx] = DocumentEntities(
                id=entity.id,
                entities=[Entity._from_generated(e) for e in entity.entities],
                statistics=DocumentStatistics._from_generated(entity.statistics),
            )
    return results


def linked_entities_result(response, obj, response_headers):
    if hasattr(obj, "innererror"):
        return whole_batch_error(obj)

    if obj.errors:
        combined = obj.documents + obj.errors
        results = order_results(response, combined)
    else:
        results = obj.documents

    for idx, entity in enumerate(results):
        if hasattr(entity, "error"):
            results[idx] = DocumentError(id=entity.id, error=entity.error)
        else:
            results[idx] = DocumentLinkedEntities(
                id=entity.id,
                entities=[LinkedEntity._from_generated(e) for e in entity.entities],
                statistics=DocumentStatistics._from_generated(entity.statistics),
            )
    return results


def key_phrases_result(response, obj, response_headers):
    if hasattr(obj, "innererror"):
        return whole_batch_error(obj)

    if obj.errors:
        combined = obj.documents + obj.errors
        results = order_results(response, combined)
    else:
        results = obj.documents

    for idx, phrases in enumerate(results):
        if hasattr(phrases, "error"):
            results[idx] = DocumentError(id=phrases.id, error=phrases.error)
        else:
            results[idx] = DocumentKeyPhrases(
                id=phrases.id,
                key_phrases=phrases.key_phrases,
                statistics=DocumentStatistics._from_generated(phrases.statistics),
            )
    return results


def sentiment_result(response, obj, response_headers):
    if hasattr(obj, "innererror"):
        return whole_batch_error(obj)

    if obj.errors:
        combined = obj.documents + obj.errors
        results = order_results(response, combined)
    else:
        results = obj.documents

    for idx, sentiment in enumerate(results):
        if hasattr(sentiment, "error"):
            results[idx] = DocumentError(id=sentiment.id, error=sentiment.error)
        else:
            results[idx] = DocumentSentiment(
                id=sentiment.id,
                sentiment=sentiment.sentiment,
                statistics=DocumentStatistics._from_generated(sentiment.statistics),
                document_scores=sentiment.document_scores,
                sentences=[SentenceSentiment._from_generated(s) for s in sentiment.sentences],
            )
    return results
