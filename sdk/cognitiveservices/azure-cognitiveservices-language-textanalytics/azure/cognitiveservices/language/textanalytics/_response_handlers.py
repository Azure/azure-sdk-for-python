

import json
import six
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.exceptions import (
    HttpResponseError,
    DecodeError
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


def process_text_analytics_error(error):
    raise_error = HttpResponseError
    error_message = error.message

    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
    except DecodeError:
        pass

    try:
        error_message = error_body['error']['message']
        error_message += "\nErrorCode:{}".format(error.status_code)
    except AttributeError:
        error_message += "\nErrorCode:{}".format(error.status_code)

    error = raise_error(message=error_message, response=error.response)
    error.error_code = error.status_code
    raise error


def _validate_single_input(text, hint, hint_value):
    if isinstance(text, six.text_type):
        return [{"id": 0, "text": text, hint: hint_value}]
    else:
        raise TypeError("Text parameter should be string.")


def _validate_batch_input(documents):
    strings = False
    for idx, item in enumerate(documents):
        if type(item) == str:
            documents[idx] = {"id": idx, "text": item}
            strings = True
        if type(item) == dict or isinstance(item, MultiLanguageInput) or isinstance(item, LanguageInput):
            if strings:
                raise TypeError("Mixing string and dictionary input unsupported.")
    return documents


def get_index(err, resp):
    response = json.loads(resp.request.body)
    docs = response['documents']
    for idx, item in enumerate(docs):
        if item["id"] == err.id:
            return idx


def add_response_errors(obj, resp, result):
    error_map = {}
    if obj.errors:
        for idx, err in enumerate(obj.errors):
            index = get_index(err, resp)
            error_map[index] = err

        for idx, error in error_map.items():
            result.insert(idx, DocumentError(id=error.id, error=error.error))
    return result


def deserialize_language_result(response, obj, response_headers):
    doc_entities = []
    if hasattr(obj, "innererror"):
        return obj
    if obj.documents:
        for language in obj.documents:
            doc_entities.append(
                DocumentLanguage(
                    id=language.id,
                    detected_languages=[DetectedLanguage._from_generated(l) for l in language.detected_languages],
                    statistics=DocumentStatistics._from_generated(language.statistics)
                )
            )
    return add_response_errors(obj, response, doc_entities)


def deserialize_entities_result(response, obj, response_headers):
    doc_entities = []
    if hasattr(obj, "innererror"):
        return obj
    if obj.documents:
        for entity in obj.documents:
            doc_entities.append(
                DocumentEntities(
                    id=entity.id,
                    entities=[Entity._from_generated(e) for e in entity.entities],
                    statistics=DocumentStatistics._from_generated(entity.statistics)
                )
            )
    return add_response_errors(obj, response, doc_entities)


def deserialize_linked_entities_result(response, obj, response_headers):
    linked_entities = []
    if hasattr(obj, "innererror"):
        return obj
    if obj.documents:
        for entity in obj.documents:
            linked_entities.append(
                DocumentLinkedEntities(
                    id=entity.id,
                    entities=[LinkedEntity._from_generated(e) for e in entity.entities],
                    statistics=DocumentStatistics._from_generated(entity.statistics)
                )
            )

    return add_response_errors(obj, response, linked_entities)


def deserialize_key_phrases_result(response, obj, response_headers):
    key_phrases = []
    if hasattr(obj, "innererror"):
        return obj
    if obj.documents:
        for phrases in obj.documents:
            key_phrases.append(
                DocumentKeyPhrases(
                    id=phrases.id,
                    key_phrases=phrases.key_phrases,
                    statistics=DocumentStatistics._from_generated(phrases.statistics)
                )
            )
    return add_response_errors(obj, response, key_phrases)


def deserialize_sentiment_result(response, obj, response_headers):
    sentiments = []
    if hasattr(obj, "innererror"):
        return obj
    if obj.documents:
        for sentiment in obj.documents:
            sentiments.append(
                DocumentSentiment(
                    id=sentiment.id,
                    sentiment=sentiment.sentiment,
                    statistics=DocumentStatistics._from_generated(sentiment.statistics),
                    document_scores=sentiment.document_scores,
                    sentences=[SentenceSentiment._from_generated(s) for s in sentiment.sentences]
                )
            )

    return add_response_errors(obj, response, sentiments)
