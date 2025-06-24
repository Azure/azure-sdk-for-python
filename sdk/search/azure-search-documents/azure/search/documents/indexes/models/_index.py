# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Union, List, Optional, MutableMapping, Callable, cast
from typing_extensions import Self
from .._generated import _serialization
from ._edm import Collection, ComplexType, String
from .._generated.models import (
    SearchField as _SearchField,
    SearchIndex as _SearchIndex,
    PatternTokenizer as _PatternTokenizer,
    LexicalAnalyzerName,
    VectorEncodingFormat,
    SearchFieldDataType,
    ScoringProfile,
    CorsOptions,
    SearchSuggester,
    LexicalAnalyzer,
    LexicalTokenizer,
    TokenFilter,
    CharFilter,
    SimilarityAlgorithm,
    SemanticSearch,
    VectorSearch,
)
from ._models import (
    pack_analyzer,
    unpack_analyzer,
    PatternTokenizer,
    SearchResourceEncryptionKey,
)


__all__ = ("ComplexField", "SearchableField", "SimpleField")


class SearchField(_serialization.Model):
    # pylint: disable=too-many-instance-attributes
    """Represents a field in an index definition, which describes the name, data type, and search behavior of a field.

    All required parameters must be populated in order to send to Azure.

    :ivar name: The name of the field, which must be unique within the fields collection of the
        index or parent field. Required.
    :vartype name: str
    :ivar type: The data type of the field. Required. Known values are: "Edm.String", "Edm.Int32",
        "Edm.Int64", "Edm.Double", "Edm.Boolean", "Edm.DateTimeOffset", "Edm.GeographyPoint",
        "Edm.ComplexType", "Edm.Single", "Edm.Half", "Edm.Int16", "Edm.SByte", and "Edm.Byte".
    :vartype type: str or ~azure.search.documents.indexes.models.SearchFieldDataType
    :ivar key: A value indicating whether the field uniquely identifies documents in the index.
        Exactly one top-level field in each index must be chosen as the key field and it must be of
        type Edm.String. Key fields can be used to look up documents directly and update or delete
        specific documents. Default is false for simple fields and null for complex fields.
    :vartype key: bool
    :ivar stored: An immutable value indicating whether the field will be persisted separately on
       disk to be returned in a search result. You can disable this option if you don't plan to return
       the field contents in a search response to save on storage overhead. This can only be set
       during index creation and only for vector fields. This property cannot be changed for existing
       fields or set as false for new fields. If this property is set as false, the property
       'hidden' must be set to true. This property must be true or unset for key fields,
       for new fields, and for non-vector fields, and it must be null for complex fields. Disabling
       this property will reduce index storage requirements. The default is true for vector fields.
    :vartype stored: bool
    :ivar searchable: A value indicating whether the field is full-text searchable. This means it
        will undergo analysis such as word-breaking during indexing. If you set a searchable field to a
        value like "sunny day", internally it will be split into the individual tokens "sunny" and
        "day". This enables full-text searches for these terms. Fields of type Edm.String or
        Collection(Edm.String) are searchable by default. This property must be false for simple fields
        of other non-string data types, and it must be null for complex fields. Note: searchable fields
        consume extra space in your index since Azure Cognitive Search will store an additional
        tokenized version of the field value for full-text searches. If you want to save space in your
        index and you don't need a field to be included in searches, set searchable to false.
    :vartype searchable: bool
    :ivar filterable: A value indicating whether to enable the field to be referenced in $filter
        queries. filterable differs from searchable in how strings are handled. Fields of type
        Edm.String or Collection(Edm.String) that are filterable do not undergo word-breaking, so
        comparisons are for exact matches only. For example, if you set such a field f to "sunny day",
        $filter=f eq 'sunny' will find no matches, but $filter=f eq 'sunny day' will. This property
        must be null for complex fields. Default is true for simple fields and null for complex fields.
    :vartype filterable: bool
    :ivar sortable: A value indicating whether to enable the field to be referenced in $orderby
        expressions. By default Azure Cognitive Search sorts results by score, but in many experiences
        users will want to sort by fields in the documents. A simple field can be sortable only if it
        is single-valued (it has a single value in the scope of the parent document). Simple collection
        fields cannot be sortable, since they are multi-valued. Simple sub-fields of complex
        collections are also multi-valued, and therefore cannot be sortable. This is true whether it's
        an immediate parent field, or an ancestor field, that's the complex collection. Complex fields
        cannot be sortable and the sortable property must be null for such fields. The default for
        sortable is true for single-valued simple fields, false for multi-valued simple fields, and
        null for complex fields.
    :vartype sortable: bool
    :ivar facetable: A value indicating whether to enable the field to be referenced in facet
        queries. Typically used in a presentation of search results that includes hit count by category
        (for example, search for digital cameras and see hits by brand, by megapixels, by price, and so
        on). This property must be null for complex fields. Fields of type Edm.GeographyPoint or
        Collection(Edm.GeographyPoint) cannot be facetable. Default is true for all other simple
        fields.
    :vartype facetable: bool
    :ivar analyzer_name: The name of the analyzer to use for the field. This option can be used only
        with searchable fields and it can't be set together with either searchAnalyzer or
        indexAnalyzer. Once the analyzer is chosen, it cannot be changed for the field. Must be null
        for complex fields. Known values are: "ar.microsoft", "ar.lucene", "hy.lucene", "bn.microsoft",
        "eu.lucene", "bg.microsoft", "bg.lucene", "ca.microsoft", "ca.lucene", "zh-Hans.microsoft",
        "zh-Hans.lucene", "zh-Hant.microsoft", "zh-Hant.lucene", "hr.microsoft", "cs.microsoft",
        "cs.lucene", "da.microsoft", "da.lucene", "nl.microsoft", "nl.lucene", "en.microsoft",
        "en.lucene", "et.microsoft", "fi.microsoft", "fi.lucene", "fr.microsoft", "fr.lucene",
        "gl.lucene", "de.microsoft", "de.lucene", "el.microsoft", "el.lucene", "gu.microsoft",
        "he.microsoft", "hi.microsoft", "hi.lucene", "hu.microsoft", "hu.lucene", "is.microsoft",
        "id.microsoft", "id.lucene", "ga.lucene", "it.microsoft", "it.lucene", "ja.microsoft",
        "ja.lucene", "kn.microsoft", "ko.microsoft", "ko.lucene", "lv.microsoft", "lv.lucene",
        "lt.microsoft", "ml.microsoft", "ms.microsoft", "mr.microsoft", "nb.microsoft", "no.lucene",
        "fa.lucene", "pl.microsoft", "pl.lucene", "pt-BR.microsoft", "pt-BR.lucene", "pt-PT.microsoft",
        "pt-PT.lucene", "pa.microsoft", "ro.microsoft", "ro.lucene", "ru.microsoft", "ru.lucene",
        "sr-cyrillic.microsoft", "sr-latin.microsoft", "sk.microsoft", "sl.microsoft", "es.microsoft",
        "es.lucene", "sv.microsoft", "sv.lucene", "ta.microsoft", "te.microsoft", "th.microsoft",
        "th.lucene", "tr.microsoft", "tr.lucene", "uk.microsoft", "ur.microsoft", "vi.microsoft",
        "standard.lucene", "standardasciifolding.lucene", "keyword", "pattern", "simple", "stop", and
        "whitespace".
    :vartype analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :ivar search_analyzer_name: The name of the analyzer used at search time for the field. This option
        can be used only with searchable fields. It must be set together with indexAnalyzer and it
        cannot be set together with the analyzer option. This property cannot be set to the name of a
        language analyzer; use the analyzer property instead if you need a language analyzer. This
        analyzer can be updated on an existing field. Must be null for complex fields. Known values
        are: "ar.microsoft", "ar.lucene", "hy.lucene", "bn.microsoft", "eu.lucene", "bg.microsoft",
        "bg.lucene", "ca.microsoft", "ca.lucene", "zh-Hans.microsoft", "zh-Hans.lucene",
        "zh-Hant.microsoft", "zh-Hant.lucene", "hr.microsoft", "cs.microsoft", "cs.lucene",
        "da.microsoft", "da.lucene", "nl.microsoft", "nl.lucene", "en.microsoft", "en.lucene",
        "et.microsoft", "fi.microsoft", "fi.lucene", "fr.microsoft", "fr.lucene", "gl.lucene",
        "de.microsoft", "de.lucene", "el.microsoft", "el.lucene", "gu.microsoft", "he.microsoft",
        "hi.microsoft", "hi.lucene", "hu.microsoft", "hu.lucene", "is.microsoft", "id.microsoft",
        "id.lucene", "ga.lucene", "it.microsoft", "it.lucene", "ja.microsoft", "ja.lucene",
        "kn.microsoft", "ko.microsoft", "ko.lucene", "lv.microsoft", "lv.lucene", "lt.microsoft",
        "ml.microsoft", "ms.microsoft", "mr.microsoft", "nb.microsoft", "no.lucene", "fa.lucene",
        "pl.microsoft", "pl.lucene", "pt-BR.microsoft", "pt-BR.lucene", "pt-PT.microsoft",
        "pt-PT.lucene", "pa.microsoft", "ro.microsoft", "ro.lucene", "ru.microsoft", "ru.lucene",
        "sr-cyrillic.microsoft", "sr-latin.microsoft", "sk.microsoft", "sl.microsoft", "es.microsoft",
        "es.lucene", "sv.microsoft", "sv.lucene", "ta.microsoft", "te.microsoft", "th.microsoft",
        "th.lucene", "tr.microsoft", "tr.lucene", "uk.microsoft", "ur.microsoft", "vi.microsoft",
        "standard.lucene", "standardasciifolding.lucene", "keyword", "pattern", "simple", "stop", and
        "whitespace".
    :vartype search_analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :ivar index_analyzer_name: The name of the analyzer used at indexing time for the field. This option
        can be used only with searchable fields. It must be set together with searchAnalyzer and it
        cannot be set together with the analyzer option.  This property cannot be set to the name of a
        language analyzer; use the analyzer property instead if you need a language analyzer. Once the
        analyzer is chosen, it cannot be changed for the field. Must be null for complex fields. Known
        values are: "ar.microsoft", "ar.lucene", "hy.lucene", "bn.microsoft", "eu.lucene",
        "bg.microsoft", "bg.lucene", "ca.microsoft", "ca.lucene", "zh-Hans.microsoft",
        "zh-Hans.lucene", "zh-Hant.microsoft", "zh-Hant.lucene", "hr.microsoft", "cs.microsoft",
        "cs.lucene", "da.microsoft", "da.lucene", "nl.microsoft", "nl.lucene", "en.microsoft",
        "en.lucene", "et.microsoft", "fi.microsoft", "fi.lucene", "fr.microsoft", "fr.lucene",
        "gl.lucene", "de.microsoft", "de.lucene", "el.microsoft", "el.lucene", "gu.microsoft",
        "he.microsoft", "hi.microsoft", "hi.lucene", "hu.microsoft", "hu.lucene", "is.microsoft",
        "id.microsoft", "id.lucene", "ga.lucene", "it.microsoft", "it.lucene", "ja.microsoft",
        "ja.lucene", "kn.microsoft", "ko.microsoft", "ko.lucene", "lv.microsoft", "lv.lucene",
        "lt.microsoft", "ml.microsoft", "ms.microsoft", "mr.microsoft", "nb.microsoft", "no.lucene",
        "fa.lucene", "pl.microsoft", "pl.lucene", "pt-BR.microsoft", "pt-BR.lucene", "pt-PT.microsoft",
        "pt-PT.lucene", "pa.microsoft", "ro.microsoft", "ro.lucene", "ru.microsoft", "ru.lucene",
        "sr-cyrillic.microsoft", "sr-latin.microsoft", "sk.microsoft", "sl.microsoft", "es.microsoft",
        "es.lucene", "sv.microsoft", "sv.lucene", "ta.microsoft", "te.microsoft", "th.microsoft",
        "th.lucene", "tr.microsoft", "tr.lucene", "uk.microsoft", "ur.microsoft", "vi.microsoft",
        "standard.lucene", "standardasciifolding.lucene", "keyword", "pattern", "simple", "stop", and
        "whitespace".
    :vartype index_analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :ivar vector_search_dimensions: The dimensionality of the vector field.
    :vartype vector_search_dimensions: int
    :ivar vector_search_profile_name: The name of the vector search profile that specifies the algorithm
        to use when searching the vector field.
    :vartype vector_search_profile_name: str
    :ivar synonym_map_names: A list of the names of synonym maps to associate with this field. This
        option can be used only with searchable fields. Currently only one synonym map per field is
        supported. Assigning a synonym map to a field ensures that query terms targeting that field are
        expanded at query-time using the rules in the synonym map. This attribute can be changed on
        existing fields. Must be null or an empty collection for complex fields.
    :vartype synonym_map_names: list[str]
    :ivar fields: A list of sub-fields if this is a field of type Edm.ComplexType or
        Collection(Edm.ComplexType). Must be null or empty for simple fields.
    :vartype fields: list[~azure.search.documents.indexes.models.SearchField]
    :ivar vector_encoding_format: The encoding format to interpret the field contents. "packedBit"
    :vartype vector_encoding_format: str or ~azure.search.documents.indexes.models.VectorEncodingFormat
    """

    def __init__(
        self,
        *,
        name: str,
        type: Union[str, SearchFieldDataType],
        key: Optional[bool] = None,
        hidden: Optional[bool] = None,
        stored: Optional[bool] = None,
        searchable: Optional[bool] = None,
        filterable: Optional[bool] = None,
        sortable: Optional[bool] = None,
        facetable: Optional[bool] = None,
        analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
        search_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
        index_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
        synonym_map_names: Optional[List[str]] = None,
        fields: Optional[List["SearchField"]] = None,
        vector_search_dimensions: Optional[int] = None,
        vector_search_profile_name: Optional[str] = None,
        vector_encoding_format: Optional[Union[str, VectorEncodingFormat]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.type = type
        self.key = key
        self.hidden = hidden
        self.stored = stored
        self.searchable = searchable
        self.filterable = filterable
        self.sortable = sortable
        self.facetable = facetable
        self.analyzer_name = analyzer_name
        self.search_analyzer_name = search_analyzer_name
        self.index_analyzer_name = index_analyzer_name
        self.synonym_map_names = synonym_map_names
        self.fields = fields
        self.vector_search_dimensions = vector_search_dimensions
        self.vector_search_profile_name = vector_search_profile_name
        self.vector_encoding_format = vector_encoding_format

    def _to_generated(self) -> _SearchField:
        fields = [pack_search_field(x) for x in self.fields] if self.fields else None
        retrievable = not self.hidden if self.hidden is not None else None
        return _SearchField(
            name=self.name,
            type=self.type,
            key=self.key,
            retrievable=retrievable,
            stored=self.stored,
            searchable=self.searchable,
            filterable=self.filterable,
            sortable=self.sortable,
            facetable=self.facetable,
            analyzer=self.analyzer_name,
            search_analyzer=self.search_analyzer_name,
            index_analyzer=self.index_analyzer_name,
            synonym_maps=self.synonym_map_names,
            fields=fields,
            vector_search_dimensions=self.vector_search_dimensions,
            vector_search_profile_name=self.vector_search_profile_name,
            vector_encoding_format=self.vector_encoding_format,
        )

    @classmethod
    def _from_generated(cls, search_field) -> Optional[Self]:
        if not search_field:
            return None
        # pylint:disable=protected-access
        fields = (
            [cast(SearchField, SearchField._from_generated(x)) for x in search_field.fields]
            if search_field.fields
            else None
        )
        hidden = not search_field.retrievable if search_field.retrievable is not None else None
        return cls(
            name=search_field.name,
            type=search_field.type,
            key=search_field.key,
            hidden=hidden,
            stored=search_field.stored,
            searchable=search_field.searchable,
            filterable=search_field.filterable,
            sortable=search_field.sortable,
            facetable=search_field.facetable,
            analyzer_name=search_field.analyzer,
            search_analyzer_name=search_field.search_analyzer,
            index_analyzer_name=search_field.index_analyzer,
            synonym_map_names=search_field.synonym_maps,
            fields=fields,
            vector_search_dimensions=search_field.vector_search_dimensions,
            vector_search_profile_name=search_field.vector_search_profile_name,
            vector_encoding_format=search_field.vector_encoding_format,
        )

    def serialize(self, keep_readonly: bool = False, **kwargs: Any) -> MutableMapping[str, Any]:
        """Return the JSON that would be sent to server from this model.
        :param bool keep_readonly: If you want to serialize the readonly attributes
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        return self._to_generated().serialize(keep_readonly=keep_readonly, **kwargs)

    @classmethod
    def deserialize(cls, data: Any, content_type: Optional[str] = None) -> Optional[Self]:  # type: ignore
        """Parse a str using the RestAPI syntax and return a SearchField instance.

        :param str data: A str using RestAPI structure. JSON by default.
        :param str content_type: JSON by default, set application/xml if XML.
        :returns: A SearchField instance
        :raises: DeserializationError if something went wrong
        """
        return cls._from_generated(_SearchField.deserialize(data, content_type=content_type))

    def as_dict(
        self,
        keep_readonly: bool = True,
        key_transformer: Callable[[str, Dict[str, Any], Any], Any] = _serialization.attribute_transformer,
        **kwargs: Any
    ) -> MutableMapping[str, Any]:
        """Return a dict that can be serialized using json.dump.

        :param bool keep_readonly: If you want to serialize the readonly attributes
        :param Callable key_transformer: A callable that will transform the key of the dict
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        return self._to_generated().as_dict(  # type: ignore
            keep_readonly=keep_readonly, key_transformer=key_transformer, **kwargs
        )

    @classmethod
    def from_dict(  # type: ignore
        cls,
        data: Any,
        key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None,
        content_type: Optional[str] = None,
    ) -> Optional["SearchField"]:
        """Parse a dict using given key extractor return a model.

        By default consider key
        extractors (rest_key_case_insensitive_extractor, attribute_key_case_insensitive_extractor
        and last_rest_key_case_insensitive_extractor)

        :param dict data: A dict using RestAPI structure
        :param Callable key_extractors: A callable that will extract a key from a dict
        :param str content_type: JSON by default, set application/xml if XML.
        :returns: A SearchField instance
        :rtype: SearchField
        :raises: DeserializationError if something went wrong
        """
        return cls._from_generated(
            _SearchField.from_dict(data, content_type=content_type, key_extractors=key_extractors)
        )


def SimpleField(
    *,
    name: str,
    type: str,
    key: bool = False,
    hidden: bool = False,
    filterable: bool = False,
    sortable: bool = False,
    facetable: bool = False,
    **kw  # pylint:disable=unused-argument
) -> SearchField:
    """Configure a simple field for an Azure Search Index

    :keyword name: Required. The name of the field, which must be unique within the fields collection
        of the index or parent field.
    :paramtype name: str
    :keyword type: Required. The data type of the field. Possible values include: SearchFieldDataType.String,
        SearchFieldDataType.Int32, SearchFieldDataType.Int64, SearchFieldDataType.Double, SearchFieldDataType.Boolean,
        SearchFieldDataType.DateTimeOffset, SearchFieldDataType.GeographyPoint, SearchFieldDataType.ComplexType,
        from `azure.search.documents.SearchFieldDataType`.
    :paramtype type: str
    :keyword key: A value indicating whether the field uniquely identifies documents in the index.
        Exactly one top-level field in each index must be chosen as the key field and it must be of
        type SearchFieldDataType.String. Key fields can be used to look up documents directly and
        update or delete specific documents. Default is False
    :paramtype key: bool
    :keyword hidden: A value indicating whether the field can be returned in a search result.
        You can enable this option if you want to use a field (for example, margin) as a filter,
        sorting, or scoring mechanism but do not want the field to be visible to the end user. This
        property must be False for key fields. This property can be changed on existing fields.
        Enabling this property does not cause any increase in index storage requirements. Default is
        False.
    :paramtype hidden: bool
    :keyword filterable: A value indicating whether to enable the field to be referenced in $filter
        queries. filterable differs from searchable in how strings are handled. Fields of type
        SearchFieldDataType.String or Collection(SearchFieldDataType.String) that are filterable do
        not undergo word-breaking, so comparisons are for exact matches only. For example, if you
        set such a field f to "sunny day", $filter=f eq 'sunny' will find no matches, but
        $filter=f eq 'sunny day' will. This property must be null for complex fields. Default is False
    :paramtype filterable: bool
    :keyword sortable: A value indicating whether to enable the field to be referenced in $orderby
        expressions. By default Azure Cognitive Search sorts results by score, but in many experiences
        users will want to sort by fields in the documents. A simple field can be sortable only if it
        is single-valued (it has a single value in the scope of the parent document). Simple collection
        fields cannot be sortable, since they are multi-valued. Simple sub-fields of complex
        collections are also multi-valued, and therefore cannot be sortable. This is true whether it's
        an immediate parent field, or an ancestor field, that's the complex collection. The default is
        False.
    :paramtype sortable: bool
    :keyword facetable: A value indicating whether to enable the field to be referenced in facet
        queries. Typically used in a presentation of search results that includes hit count by category
        (for example, search for digital cameras and see hits by brand, by megapixels, by price, and so
        on). Fields of type SearchFieldDataType.GeographyPoint or
        Collection(SearchFieldDataType.GeographyPoint) cannot be facetable. Default is False.
    :paramtype facetable: bool
    :return: The search field object.
    :rtype:  SearchField
    """
    result: Dict[str, Any] = {
        "name": name,
        "type": type,
        "key": key,
        "searchable": False,
        "filterable": filterable,
        "facetable": facetable,
        "sortable": sortable,
        "hidden": hidden,
    }
    return SearchField(**result)


def SearchableField(
    *,
    name: str,
    collection: bool = False,
    key: bool = False,
    hidden: bool = False,
    searchable: bool = True,
    filterable: bool = False,
    sortable: bool = False,
    facetable: bool = False,
    analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
    search_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
    index_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
    synonym_map_names: Optional[List[str]] = None,
    **kw  # pylint:disable=unused-argument
) -> SearchField:
    """Configure a searchable text field for an Azure Search Index

    :keyword name: Required. The name of the field, which must be unique within the fields collection
        of the index or parent field.
    :paramtype name: str
    :keyword collection: Whether this search field is a collection (default False)
    :paramtype collection: bool
    :keyword key: A value indicating whether the field uniquely identifies documents in the index.
        Exactly one top-level field in each index must be chosen as the key field and it must be of
        type SearchFieldDataType.String. Key fields can be used to look up documents directly and update or delete
        specific documents. Default is False
    :paramtype key: bool
    :keyword hidden: A value indicating whether the field can be returned in a search result.
        You can enable this option if you want to use a field (for example, margin) as a filter,
        sorting, or scoring mechanism but do not want the field to be visible to the end user. This
        property must be False for key fields. This property can be changed on existing fields.
        Enabling this property does not cause any increase in index storage requirements. Default is
        False.
    :paramtype hidden: bool
    :keyword searchable: A value indicating whether the field is full-text searchable. This means it
        will undergo analysis such as word-breaking during indexing. If you set a searchable field to a
        value like "sunny day", internally it will be split into the individual tokens "sunny" and
        "day". This enables full-text searches for these terms. Note: searchable fields
        consume extra space in your index since Azure Cognitive Search will store an additional
        tokenized version of the field value for full-text searches. If you want to save space in your
        index and you don't need a field to be included in searches, set searchable to false. Default
        is True.
    :paramtype searchable: bool
    :keyword filterable: A value indicating whether to enable the field to be referenced in $filter
        queries. filterable differs from searchable in how strings are handled. Fields that are
        filterable do not undergo word-breaking, so comparisons are for exact matches only. For example,
        if you set such a field f to "sunny day", $filter=f eq 'sunny' will find no matches, but
        $filter=f eq 'sunny day' will. Default is False.
    :paramtype filterable: bool
    :keyword sortable: A value indicating whether to enable the field to be referenced in $orderby
        expressions. By default Azure Cognitive Search sorts results by score, but in many experiences
        users will want to sort by fields in the documents.  The default is False.
    :paramtype sortable: bool
    :keyword facetable: A value indicating whether to enable the field to be referenced in facet
        queries. Typically used in a presentation of search results that includes hit count by category
        (for example, search for digital cameras and see hits by brand, by megapixels, by price, and so
        on). Default is False.
    :paramtype facetable: bool
    :keyword analyzer_name: The name of the analyzer to use for the field. This option can't be set together
        with either searchAnalyzer or indexAnalyzer. Once the analyzer is chosen, it cannot be changed
        for the field. Possible values include: 'ar.microsoft', 'ar.lucene', 'hy.lucene',
        'bn.microsoft', 'eu.lucene', 'bg.microsoft', 'bg.lucene', 'ca.microsoft', 'ca.lucene', 'zh-
        Hans.microsoft', 'zh-Hans.lucene', 'zh-Hant.microsoft', 'zh-Hant.lucene', 'hr.microsoft',
        'cs.microsoft', 'cs.lucene', 'da.microsoft', 'da.lucene', 'nl.microsoft', 'nl.lucene',
        'en.microsoft', 'en.lucene', 'et.microsoft', 'fi.microsoft', 'fi.lucene', 'fr.microsoft',
        'fr.lucene', 'gl.lucene', 'de.microsoft', 'de.lucene', 'el.microsoft', 'el.lucene',
        'gu.microsoft', 'he.microsoft', 'hi.microsoft', 'hi.lucene', 'hu.microsoft', 'hu.lucene',
        'is.microsoft', 'id.microsoft', 'id.lucene', 'ga.lucene', 'it.microsoft', 'it.lucene',
        'ja.microsoft', 'ja.lucene', 'kn.microsoft', 'ko.microsoft', 'ko.lucene', 'lv.microsoft',
        'lv.lucene', 'lt.microsoft', 'ml.microsoft', 'ms.microsoft', 'mr.microsoft', 'nb.microsoft',
        'no.lucene', 'fa.lucene', 'pl.microsoft', 'pl.lucene', 'pt-BR.microsoft', 'pt-BR.lucene', 'pt-
        PT.microsoft', 'pt-PT.lucene', 'pa.microsoft', 'ro.microsoft', 'ro.lucene', 'ru.microsoft',
        'ru.lucene', 'sr-cyrillic.microsoft', 'sr-latin.microsoft', 'sk.microsoft', 'sl.microsoft',
        'es.microsoft', 'es.lucene', 'sv.microsoft', 'sv.lucene', 'ta.microsoft', 'te.microsoft',
        'th.microsoft', 'th.lucene', 'tr.microsoft', 'tr.lucene', 'uk.microsoft', 'ur.microsoft',
        'vi.microsoft', 'standard.lucene', 'standardasciifolding.lucene', 'keyword', 'pattern',
        'simple', 'stop', 'whitespace'.
    :paramtype analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :keyword search_analyzer_name: The name of the analyzer used at search time for the field. It must be
        set together with indexAnalyzer and it cannot be set together with the analyzer option. This
        property cannot be set to the name of a language analyzer; use the analyzer property instead
        if you need a language analyzer. This analyzer can be updated on an existing field. Possible
        values include:
        'ar.microsoft', 'ar.lucene', 'hy.lucene', 'bn.microsoft', 'eu.lucene', 'bg.microsoft',
        'bg.lucene', 'ca.microsoft', 'ca.lucene', 'zh-Hans.microsoft', 'zh-Hans.lucene', 'zh-
        Hant.microsoft', 'zh-Hant.lucene', 'hr.microsoft', 'cs.microsoft', 'cs.lucene', 'da.microsoft',
        'da.lucene', 'nl.microsoft', 'nl.lucene', 'en.microsoft', 'en.lucene', 'et.microsoft',
        'fi.microsoft', 'fi.lucene', 'fr.microsoft', 'fr.lucene', 'gl.lucene', 'de.microsoft',
        'de.lucene', 'el.microsoft', 'el.lucene', 'gu.microsoft', 'he.microsoft', 'hi.microsoft',
        'hi.lucene', 'hu.microsoft', 'hu.lucene', 'is.microsoft', 'id.microsoft', 'id.lucene',
        'ga.lucene', 'it.microsoft', 'it.lucene', 'ja.microsoft', 'ja.lucene', 'kn.microsoft',
        'ko.microsoft', 'ko.lucene', 'lv.microsoft', 'lv.lucene', 'lt.microsoft', 'ml.microsoft',
        'ms.microsoft', 'mr.microsoft', 'nb.microsoft', 'no.lucene', 'fa.lucene', 'pl.microsoft',
        'pl.lucene', 'pt-BR.microsoft', 'pt-BR.lucene', 'pt-PT.microsoft', 'pt-PT.lucene',
        'pa.microsoft', 'ro.microsoft', 'ro.lucene', 'ru.microsoft', 'ru.lucene', 'sr-
        cyrillic.microsoft', 'sr-latin.microsoft', 'sk.microsoft', 'sl.microsoft', 'es.microsoft',
        'es.lucene', 'sv.microsoft', 'sv.lucene', 'ta.microsoft', 'te.microsoft', 'th.microsoft',
        'th.lucene', 'tr.microsoft', 'tr.lucene', 'uk.microsoft', 'ur.microsoft', 'vi.microsoft',
        'standard.lucene', 'standardasciifolding.lucene', 'keyword', 'pattern', 'simple', 'stop',
        'whitespace'.
    :paramtype search_analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :keyword index_analyzer_name: The name of the analyzer used at indexing time for the field.
        It must be set together with searchAnalyzer and it cannot be set together with the analyzer
        option.  This property cannot be set to the name of a language analyzer; use the analyzer
        property instead if you need a language analyzer. Once the analyzer is chosen, it cannot be
        changed for the field. Possible values include:
        'ar.microsoft', 'ar.lucene', 'hy.lucene', 'bn.microsoft', 'eu.lucene',
        'bg.microsoft', 'bg.lucene', 'ca.microsoft', 'ca.lucene', 'zh-Hans.microsoft', 'zh-
        Hans.lucene', 'zh-Hant.microsoft', 'zh-Hant.lucene', 'hr.microsoft', 'cs.microsoft',
        'cs.lucene', 'da.microsoft', 'da.lucene', 'nl.microsoft', 'nl.lucene', 'en.microsoft',
        'en.lucene', 'et.microsoft', 'fi.microsoft', 'fi.lucene', 'fr.microsoft', 'fr.lucene',
        'gl.lucene', 'de.microsoft', 'de.lucene', 'el.microsoft', 'el.lucene', 'gu.microsoft',
        'he.microsoft', 'hi.microsoft', 'hi.lucene', 'hu.microsoft', 'hu.lucene', 'is.microsoft',
        'id.microsoft', 'id.lucene', 'ga.lucene', 'it.microsoft', 'it.lucene', 'ja.microsoft',
        'ja.lucene', 'kn.microsoft', 'ko.microsoft', 'ko.lucene', 'lv.microsoft', 'lv.lucene',
        'lt.microsoft', 'ml.microsoft', 'ms.microsoft', 'mr.microsoft', 'nb.microsoft', 'no.lucene',
        'fa.lucene', 'pl.microsoft', 'pl.lucene', 'pt-BR.microsoft', 'pt-BR.lucene', 'pt-PT.microsoft',
        'pt-PT.lucene', 'pa.microsoft', 'ro.microsoft', 'ro.lucene', 'ru.microsoft', 'ru.lucene', 'sr-
        cyrillic.microsoft', 'sr-latin.microsoft', 'sk.microsoft', 'sl.microsoft', 'es.microsoft',
        'es.lucene', 'sv.microsoft', 'sv.lucene', 'ta.microsoft', 'te.microsoft', 'th.microsoft',
        'th.lucene', 'tr.microsoft', 'tr.lucene', 'uk.microsoft', 'ur.microsoft', 'vi.microsoft',
        'standard.lucene', 'standardasciifolding.lucene', 'keyword', 'pattern', 'simple', 'stop',
        'whitespace'.
    :paramtype index_analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :keyword synonym_map_names: A list of the names of synonym maps to associate with this field. Currently
        only one synonym map per field is supported. Assigning a synonym map to a field ensures that
        query terms targeting that field are expanded at query-time using the rules in the synonym map.
        This attribute can be changed on existing fields.
    :paramtype synonym_map_names: list[str]
    :return: The search field object.
    :rtype:  SearchField
    """
    typ = Collection(String) if collection else String
    result: Dict[str, Any] = {
        "name": name,
        "type": typ,
        "key": key,
        "searchable": searchable,
        "filterable": filterable,
        "facetable": facetable,
        "sortable": sortable,
        "hidden": hidden,
    }
    if analyzer_name:
        result["analyzer_name"] = analyzer_name
    if search_analyzer_name:
        result["search_analyzer_name"] = search_analyzer_name
    if index_analyzer_name:
        result["index_analyzer_name"] = index_analyzer_name
    if synonym_map_names:
        result["synonym_map_names"] = synonym_map_names
    return SearchField(**result)


def ComplexField(
    *,
    name: str,
    collection: bool = False,
    fields: Optional[List[SearchField]] = None,
    **kw  # pylint:disable=unused-argument
) -> SearchField:
    """Configure a Complex or Complex collection field for an Azure Search
    Index

    :keyword name: Required. The name of the field, which must be unique within the fields collection
        of the index or parent field.
    :paramtype name: str
    :keyword collection: Whether this complex field is a collection (default False)
    :paramtype collection: bool
    :keyword fields: A list of sub-fields
    :paramtype fields: list[~azure.search.documents.indexes.models.SearchField]
    :return: The search field object.
    :rtype:  SearchField
    """
    typ = Collection(ComplexType) if collection else ComplexType
    result: Dict[str, Any] = {"name": name, "type": typ, "fields": fields}
    return SearchField(**result)


class SearchIndex(_serialization.Model):
    # pylint: disable=too-many-instance-attributes
    """Represents a search index definition, which describes the fields and search behavior of an index.

    All required parameters must be populated in order to send to Azure.

    :ivar name: Required. The name of the index.
    :vartype name: str
    :ivar fields: Required. The fields of the index.
    :vartype fields: list[~azure.search.documents.indexes.models.SearchField]
    :ivar scoring_profiles: The scoring profiles for the index.
    :vartype scoring_profiles: list[~azure.search.documents.indexes.models.ScoringProfile]
    :ivar default_scoring_profile: The name of the scoring profile to use if none is specified in
        the query. If this property is not set and no scoring profile is specified in the query, then
        default scoring (tf-idf) will be used.
    :vartype default_scoring_profile: str
    :ivar cors_options: Options to control Cross-Origin Resource Sharing (CORS) for the index.
    :vartype cors_options: ~azure.search.documents.indexes.models.CorsOptions
    :ivar suggesters: The suggesters for the index.
    :vartype suggesters: list[~azure.search.documents.indexes.models.SearchSuggester]
    :ivar analyzers: The analyzers for the index.
    :vartype analyzers: list[~azure.search.documents.indexes.models.LexicalAnalyzer]
    :ivar tokenizers: The tokenizers for the index.
    :vartype tokenizers: list[~azure.search.documents.indexes.models.LexicalTokenizer]
    :ivar token_filters: The token filters for the index.
    :vartype token_filters: list[~azure.search.documents.indexes.models.TokenFilter]
    :ivar char_filters: The character filters for the index.
    :vartype char_filters: list[~azure.search.documents.indexes.models.CharFilter]
    :ivar encryption_key: A description of an encryption key that you create in Azure Key Vault.
        This key is used to provide an additional level of encryption-at-rest for your data when you
        want full assurance that no one, not even Microsoft, can decrypt your data in Azure Cognitive
        Search. Once you have encrypted your data, it will always remain encrypted. Azure Cognitive
        Search will ignore attempts to set this property to null. You can change this property as
        needed if you want to rotate your encryption key; Your data will be unaffected. Encryption with
        customer-managed keys is not available for free search services, and is only available for paid
        services created on or after January 1, 2019.
    :vartype encryption_key: ~azure.search.documents.indexes.models.SearchResourceEncryptionKey
    :ivar similarity: The type of similarity algorithm to be used when scoring and ranking the
        documents matching a search query. The similarity algorithm can only be defined at index
        creation time and cannot be modified on existing indexes. If null, the ClassicSimilarity
        algorithm is used.
    :vartype similarity: ~azure.search.documents.indexes.models.SimilarityAlgorithm
    :ivar semantic_search: Defines parameters for a search index that influence semantic capabilities.
    :vartype semantic_search: ~azure.search.documents.indexes.models.SemanticSearch
    :ivar vector_search: Defines parameters for a search index that influence scoring in a vector space.
    :vartype vector_search: ~azure.search.documents.indexes.models.VectorSearch
    :ivar e_tag: The ETag of the index.
    :vartype e_tag: str
    """

    def __init__(
        self,
        *,
        name: str,
        fields: List[SearchField],
        scoring_profiles: Optional[List[ScoringProfile]] = None,
        default_scoring_profile: Optional[str] = None,
        cors_options: Optional[CorsOptions] = None,
        suggesters: Optional[List[SearchSuggester]] = None,
        analyzers: Optional[List[LexicalAnalyzer]] = None,
        tokenizers: Optional[List[LexicalTokenizer]] = None,
        token_filters: Optional[List[TokenFilter]] = None,
        char_filters: Optional[List[CharFilter]] = None,
        encryption_key: Optional[SearchResourceEncryptionKey] = None,
        similarity: Optional[SimilarityAlgorithm] = None,
        semantic_search: Optional[SemanticSearch] = None,
        vector_search: Optional[VectorSearch] = None,
        e_tag: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.fields = fields
        self.scoring_profiles = scoring_profiles
        self.default_scoring_profile = default_scoring_profile
        self.cors_options = cors_options
        self.suggesters = suggesters
        self.analyzers = analyzers
        self.tokenizers = tokenizers
        self.token_filters = token_filters
        self.char_filters = char_filters
        self.encryption_key = encryption_key
        self.similarity = similarity
        self.semantic_search = semantic_search
        self.vector_search = vector_search
        self.e_tag = e_tag

    def _to_generated(self) -> _SearchIndex:
        if self.analyzers:
            analyzers = [pack_analyzer(x) for x in self.analyzers]  # type: ignore  # mypy: ignore
        else:
            analyzers = None
        if self.tokenizers:
            tokenizers = [
                x._to_generated() if isinstance(x, PatternTokenizer) else x  # pylint:disable=protected-access
                for x in self.tokenizers
            ]
        else:
            tokenizers = None
        if self.fields:
            fields = [pack_search_field(x) for x in self.fields]
        else:
            fields = []
        return _SearchIndex(
            name=self.name,
            fields=fields,
            scoring_profiles=self.scoring_profiles,
            default_scoring_profile=self.default_scoring_profile,
            cors_options=self.cors_options,
            suggesters=self.suggesters,
            analyzers=analyzers,
            tokenizers=tokenizers,
            token_filters=self.token_filters,
            char_filters=self.char_filters,
            # pylint:disable=protected-access
            encryption_key=self.encryption_key._to_generated() if self.encryption_key else None,
            similarity=self.similarity,
            semantic_search=self.semantic_search,
            e_tag=self.e_tag,
            vector_search=self.vector_search,
        )

    @classmethod
    def _from_generated(cls, search_index) -> Optional[Self]:
        if not search_index:
            return None
        if search_index.analyzers:
            analyzers = [unpack_analyzer(x) for x in search_index.analyzers]  # type: ignore
        else:
            analyzers = None
        if search_index.tokenizers:
            tokenizers = [
                (
                    PatternTokenizer._from_generated(x)  # pylint:disable=protected-access
                    if isinstance(x, _PatternTokenizer)
                    else x
                )
                for x in search_index.tokenizers
            ]
        else:
            tokenizers = None
        if search_index.fields:
            # pylint:disable=protected-access
            fields = [cast(SearchField, SearchField._from_generated(x)) for x in search_index.fields]
        else:
            fields = []
        return cls(
            name=search_index.name,
            fields=fields,
            scoring_profiles=search_index.scoring_profiles,
            default_scoring_profile=search_index.default_scoring_profile,
            cors_options=search_index.cors_options,
            suggesters=search_index.suggesters,
            analyzers=analyzers,
            tokenizers=tokenizers,
            token_filters=search_index.token_filters,
            char_filters=search_index.char_filters,
            # pylint:disable=protected-access
            encryption_key=SearchResourceEncryptionKey._from_generated(search_index.encryption_key),
            similarity=search_index.similarity,
            semantic_search=search_index.semantic_search,
            e_tag=search_index.e_tag,
            vector_search=search_index.vector_search,
        )

    def serialize(self, keep_readonly: bool = False, **kwargs: Any) -> MutableMapping[str, Any]:
        """Return the JSON that would be sent to server from this model.
        :param bool keep_readonly: If you want to serialize the readonly attributes
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        return self._to_generated().serialize(keep_readonly=keep_readonly, **kwargs)

    @classmethod
    def deserialize(cls, data: Any, content_type: Optional[str] = None) -> Optional[Self]:  # type: ignore
        """Parse a str using the RestAPI syntax and return a SearchIndex instance.

        :param str data: A str using RestAPI structure. JSON by default.
        :param str content_type: JSON by default, set application/xml if XML.
        :returns: A SearchIndex instance
        :rtype: SearchIndex
        :raises: DeserializationError if something went wrong
        """
        return cls._from_generated(_SearchIndex.deserialize(data, content_type=content_type))

    def as_dict(
        self,
        keep_readonly: bool = True,
        key_transformer: Callable[[str, Dict[str, Any], Any], Any] = _serialization.attribute_transformer,
        **kwargs: Any
    ) -> MutableMapping[str, Any]:
        """Return a dict that can be serialized using json.dump.

        :param bool keep_readonly: If you want to serialize the readonly attributes
        :param Callable key_transformer: A callable that will transform the key of the dict
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        return self._to_generated().as_dict(
            keep_readonly=keep_readonly, key_transformer=key_transformer, **kwargs
        )  # type: ignore

    @classmethod
    def from_dict(  # type: ignore
        cls,
        data: Any,
        key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None,
        content_type: Optional[str] = None,
    ) -> Optional[Self]:
        """Parse a dict using given key extractor return a model.

        By default consider key
        extractors (rest_key_case_insensitive_extractor, attribute_key_case_insensitive_extractor
        and last_rest_key_case_insensitive_extractor)

        :param dict data: A dict using RestAPI structure
        :param Callable key_extractors: A callable that will extract a key from a dict
        :param str content_type: JSON by default, set application/xml if XML.
        :returns: A SearchIndex instance
        :rtype: SearchIndex
        :raises: DeserializationError if something went wrong
        """
        return cls._from_generated(
            _SearchIndex.from_dict(data, content_type=content_type, key_extractors=key_extractors)
        )


def pack_search_field(search_field: SearchField) -> _SearchField:
    if isinstance(search_field, dict):
        name = search_field.get("name")
        assert name is not None  # Hint for mypy
        field_type = search_field.get("type")
        assert field_type is not None  # Hint for mypy
        key = search_field.get("key")
        hidden = search_field.get("hidden")
        retrievable = not hidden if hidden is not None else None
        searchable = search_field.get("searchable")
        filterable = search_field.get("filterable")
        sortable = search_field.get("sortable")
        facetable = search_field.get("facetable")
        analyzer_name = search_field.get("analyzer_name")
        search_analyzer_name = search_field.get("search_analyzer_name")
        index_analyzer_name = search_field.get("index_analyzer_name")
        synonym_map_names = search_field.get("synonym_map_names")
        fields = search_field.get("fields")
        fields = [pack_search_field(x) for x in fields] if fields else None
        vector_search_dimensions = search_field.get("vector_search_dimensions")
        vector_search_profile_name = search_field.get("vector_search_profile_name")
        return _SearchField(
            name=name,
            type=field_type,
            key=key,
            retrievable=retrievable,
            searchable=searchable,
            filterable=filterable,
            sortable=sortable,
            facetable=facetable,
            analyzer=analyzer_name,
            search_analyzer=search_analyzer_name,
            index_analyzer=index_analyzer_name,
            synonym_maps=synonym_map_names,
            fields=fields,
            vector_search_dimensions=vector_search_dimensions,
            vector_search_profile_name=vector_search_profile_name,
        )
    return search_field._to_generated()  # pylint:disable=protected-access
