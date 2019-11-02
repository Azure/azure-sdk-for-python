from ._models import DocumentEntities, Entity, DocumentStatistics


def deserialize_entities_result(response, obj, response_headers):
    if obj.errors:
        print(obj.errors)
    doc_entities = []
    for entity in obj.documents:
        doc_entities.append(
            DocumentEntities(
                id=entity.id,
                entities=[Entity._from_generated(e) for e in entity.entities],
                statistics=DocumentStatistics._from_generated(entity.statistics)
            )
        )
    return doc_entities