import json
from ._models import (
    DocumentEntities,
    Entity,
    DocumentStatistics,
    DocumentLinkedEntities,
    LinkedEntity,
    DocumentKeyPhrases,
    DocumentSentiment,
    SentenceSentiment,
    DocumentError
)


def get_index(err, resp):
    response = json.loads(resp.request.body)
    docs = response['documents']
    for idx, item in enumerate(docs):
        if item["id"] == err.id:
            return idx


def deserialize_entities_result(response, obj, response_headers):
    doc_entities = []
    error_map = {}
    combined_response = [*obj.documents, *obj.errors]
    if obj.errors:
        for error in obj.errors:
            index = get_index(error, response)
            error_map[index] = error
    for idx, entity in enumerate(combined_response):
        if idx in error_map:
            doc_entities.append(
                DocumentError(
                    id=error_map[idx].id,
                    error=error_map[idx].error
                )
            )
            error_map.pop(idx)
        if not hasattr(entity, "error"):
            doc_entities.append(
                DocumentEntities(
                    id=entity.id,
                    entities=[Entity._from_generated(e) for e in entity.entities],
                    statistics=DocumentStatistics._from_generated(entity.statistics)
                )
            )
    return doc_entities


def deserialize_linked_entities_result(response, obj, response_headers):
    if obj.errors:
        print(obj.errors)
    linked_entities = []
    for entity in obj.documents:
        linked_entities.append(
            DocumentLinkedEntities(
                id=entity.id,
                entities=[LinkedEntity._from_generated(e) for e in entity.entities],
                statistics=DocumentStatistics._from_generated(entity.statistics)
            )
        )
    return linked_entities


def deserialize_key_phrases_result(response, obj, response_headers):
    if obj.errors:
        print(obj.errors)
    key_phrases = []
    for phrases in obj.documents:
        key_phrases.append(
            DocumentKeyPhrases(
                id=phrases.id,
                key_phrases=phrases.key_phrases,
                statistics=DocumentStatistics._from_generated(phrases.statistics)
            )
        )
    return key_phrases


def deserialize_sentiment_result(response, obj, response_headers):
    if obj.errors:
        print(obj.errors)
    sentiments = []
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
    return sentiments
