

class DocumentEntities(object):
    """DocumentEntities.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. Unique, non-empty document identifier.
    :type id: str
    :param entities: Required. Recognized entities in the document.
    :type entities: list[~textanalytics.models.Entity]
    :param statistics: if showStats=true was specified in the request this
     field will contain information about the document payload.
    :type statistics: ~textanalytics.models.DocumentStatistics
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.entities = kwargs.get('entities', None)
        self.statistics = kwargs.get('statistics', None)


class Entity(object):
    """Entity.

    All required parameters must be populated in order to send to Azure.

    :param text: Required. Entity text as appears in the request.
    :type text: str
    :param type: Required. Entity type, such as Person/Location/Org/SSN etc
    :type type: str
    :param sub_type: Entity sub type, such as Age/Year/TimeRange etc
    :type sub_type: str
    :param offset: Required. Start position (in Unicode characters) for the
     entity text.
    :type offset: int
    :param length: Required. Length (in Unicode characters) for the entity
     text.
    :type length: int
    :param score: Required. Confidence score between 0 and 1 of the extracted
     entity.
    :type score: float
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.type = kwargs.get('type', None)
        self.sub_type = kwargs.get('sub_type', None)
        self.offset = kwargs.get('offset', None)
        self.length = kwargs.get('length', None)
        self.score = kwargs.get('score', None)

    @classmethod
    def _from_generated(cls, entity):
        return cls(
            text=entity.text,
            type=entity.type,
            sub_type=entity.sub_type,
            offset=entity.offset,
            length=entity.length,
            score=entity.score
        )


class DocumentStatistics(object):
    """if showStats=true was specified in the request this field will contain
    information about the document payload.

    All required parameters must be populated in order to send to Azure.

    :param characters_count: Required. Number of text elements recognized in
     the document.
    :type characters_count: int
    :param transactions_count: Required. Number of transactions for the
     document.
    :type transactions_count: int
    """

    def __init__(self, **kwargs):
        self.characters_count = kwargs.get('characters_count', None)
        self.transactions_count = kwargs.get('transactions_count', None)

    @classmethod
    def _from_generated(cls, stats):
        if stats is None:
            return None
        return cls(
            characters_count=stats.characters_count,
            transactions_count=stats.transactions_count
        )