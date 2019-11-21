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
)


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


def process_batch_error(error):
    """Raise and return detailed error message for HttpResponseErrors
    """
    raise_error = HttpResponseError
    if error.status_code == 401:
        raise_error = ClientAuthenticationError
    error_message = error.message
    error_body = None

    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
    except DecodeError:
        pass

    if error_body is not None:
        error_resp = error_body["error"]
        try:
            error_message = error_resp["innerError"]["message"]
        except KeyError:
            error_message = error_resp["message"]

        error_message += "\nErrorCode:{}".format(error.status_code)

    error = raise_error(message=error_message, response=error.response)
    error.error_code = error.status_code
    raise error


def _validate_single_input(text, hint, hint_value):
    """Validate text input is string. Let service handle
    validity of hint and hint value.

    :param str text: A single text document.
    :param str hint: Could be country_hint or language
    :param str hint_value: The user passed country_hint or language
    :return: A LanguageInput or MultiLanguageInput
    """
    if isinstance(text, six.string_types):
        if hint_value:
            return [{"id": "0", "text": text, hint: hint_value}]
        return [{"id": "0", "text": text}]
    raise TypeError("Text parameter must be string.")


def _validate_batch_input(documents, hint, hint_value):
    """Validate that batch input has either all string docs
    or dict/LanguageInput/MultiLanguageInput, not a mix of both.

    :param list documents: The input documents.
    :return: A list of LanguageInput or MultiLanguageInput
    """
    if not isinstance(documents, list):
        raise TypeError("Documents parameter must be a list.")

    string_input, nonstring_input = False, False
    string_batch = []
    for idx, doc in enumerate(documents):
        if isinstance(doc, six.string_types):
            if hint_value:
                string_batch.append({"id": str(idx), hint: hint_value, "text": doc})
            else:
                string_batch.append({"id": str(idx), "text": doc})
            string_input = True
        if isinstance(doc, (dict, MultiLanguageInput, LanguageInput)):
            nonstring_input = True

    if string_input and nonstring_input:
        raise TypeError("Mixing string and dictionary/object input unsupported.")
    return string_batch if string_batch != [] else documents


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


def language_result(response, obj, response_headers):  # pylint: disable=unused-argument
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
                detected_language=DetectedLanguage._from_generated(language.detected_languages[0]),  # pylint: disable=protected-access
                statistics=DocumentStatistics._from_generated(language.statistics),  # pylint: disable=protected-access
            )
    return results


def entities_result(response, obj, response_headers):  # pylint: disable=unused-argument
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
                entities=[Entity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
                statistics=DocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
            )
    return results


def linked_entities_result(response, obj, response_headers):  # pylint: disable=unused-argument
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
                entities=[LinkedEntity._from_generated(e) for e in entity.entities],  # pylint: disable=protected-access
                statistics=DocumentStatistics._from_generated(entity.statistics),  # pylint: disable=protected-access
            )
    return results


def key_phrases_result(response, obj, response_headers):  # pylint: disable=unused-argument
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
                statistics=DocumentStatistics._from_generated(phrases.statistics),  # pylint: disable=protected-access
            )
    return results


def sentiment_result(response, obj, response_headers):  # pylint: disable=unused-argument
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
                statistics=DocumentStatistics._from_generated(sentiment.statistics),  # pylint: disable=protected-access
                document_scores=sentiment.document_scores,
                sentences=[SentenceSentiment._from_generated(s) for s in sentiment.sentences],  # pylint: disable=protected-access
            )
    return results
