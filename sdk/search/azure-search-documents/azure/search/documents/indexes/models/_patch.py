# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict, List, Optional, Union
from ._models import (
    SearchField as _SearchField,
    SearchIndexerDataSourceConnection as _SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchIndexerDataIdentity,
    SearchResourceEncryptionKey,
    DataChangeDetectionPolicy,
    DataDeletionDetectionPolicy,
    DataSourceCredentials,
)
from ._enums import (
    LexicalAnalyzerName,
    IndexerPermissionOption,
    SearchFieldDataType as _SearchFieldDataType,
    PermissionFilter,
    VectorEncodingFormat,
)

# Re-export SearchFieldDataType and add Collection helper
SearchFieldDataType = _SearchFieldDataType

# Add Collection method to SearchFieldDataType enum
def _collection_helper(typ) -> str:
    """Helper function to create a collection type string.
    
    :param typ: The type to wrap in a collection. Can be a string or an enum value.
    :return: A collection type string.
    """
    # If typ is an enum, get its value; otherwise use it as-is
    if hasattr(typ, 'value'):
        typ = typ.value
    return "Collection({})".format(typ)

# Monkey-patch the Collection method onto the enum class
SearchFieldDataType.Collection = staticmethod(_collection_helper)

def Collection(typ) -> str:
    """Helper function to create a collection type string.
    
    :param typ: The type to wrap in a collection. Can be a string or an enum value.
    :return: A collection type string.
    """
    # If typ is an enum, get its value; otherwise use it as-is
    if hasattr(typ, 'value'):
        typ = typ.value
    return "Collection({})".format(typ)


class SearchField(_SearchField):
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
    :ivar permission_filter: A value indicating whether the field should be used as a permission
        filter. Known values are: "userIds", "groupIds", and "rbacScope".
    :vartype permission_filter: str or ~azure.search.documents.indexes.models.PermissionFilter
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
    :ivar normalizer_name: The name of the normalizer to use for the field. This option can be used only
        with fields with filterable, sortable, or facetable enabled. Once the normalizer is chosen, it
        cannot be changed for the field. Must be null for complex fields. Known values are:
        "asciifolding", "elision", "lowercase", "standard", and "uppercase".
    :vartype normalizer_name: str or ~azure.search.documents.indexes.models.LexicalNormalizerName
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
        permission_filter: Optional[Union[str, PermissionFilter]] = None,
        analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
        search_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
        index_analyzer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
        synonym_map_names: Optional[List[str]] = None,
        fields: Optional[List["SearchField"]] = None,
        normalizer_name: Optional[Union[str, LexicalAnalyzerName]] = None,
        vector_search_dimensions: Optional[int] = None,
        vector_search_profile_name: Optional[str] = None,
        vector_encoding_format: Optional[Union[str, VectorEncodingFormat]] = None,
        **kwargs
    ):
        retrievable = not hidden if hidden is not None else None
        super().__init__(
            name=name,
            type=type,
            key=key,
            retrievable=retrievable,
            stored=stored,
            searchable=searchable,
            filterable=filterable,
            sortable=sortable,
            facetable=facetable,
            permission_filter=permission_filter,
            analyzer_name=analyzer_name,
            search_analyzer_name=search_analyzer_name,
            index_analyzer_name=index_analyzer_name,
            synonym_map_names=synonym_map_names,
            fields=fields,
            normalizer_name=normalizer_name,
            vector_search_dimensions=vector_search_dimensions,
            vector_search_profile_name=vector_search_profile_name,
            vector_encoding_format=vector_encoding_format,
            **kwargs
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
) -> _SearchField:
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
    typ = Collection(SearchFieldDataType.String) if collection else SearchFieldDataType.String
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
    fields: Optional[List[_SearchField]] = None,
    **kw  # pylint:disable=unused-argument
) -> _SearchField:
    """Configure a Complex or Complex collection field for an Azure Search Index

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
    typ = Collection(SearchFieldDataType.COMPLEX) if collection else SearchFieldDataType.COMPLEX
    result: Dict[str, Any] = {"name": name, "type": typ, "fields": fields}
    return _SearchField(**result)


class SearchIndexerDataSourceConnection(_SearchIndexerDataSourceConnection):
    """Represents a datasource connection definition, which can be used to configure an indexer.

    All required parameters must be populated in order to send to Azure.

    :ivar name: Required. The name of the datasource connection.
    :vartype name: str
    :ivar description: The description of the datasource connection.
    :vartype description: str
    :ivar type: Required. The type of the datasource connection. Possible values include: "azuresql",
     "cosmosdb", "azureblob", "azuretable", "mysql", "adlsgen2".
    :vartype type: str or ~azure.search.documents.indexes.models.SearchIndexerDataSourceType
    :ivar connection_string: The connection string for the datasource connection.
    :vartype connection_string: str
    :ivar container: Required. The data container for the datasource connection.
    :vartype container: ~azure.search.documents.indexes.models.SearchIndexerDataContainer
    :ivar identity: An explicit managed identity to use for this datasource. If not specified and
     the connection string is a managed identity, the system-assigned managed identity is used. If
     not specified, the value remains unchanged. If "none" is specified, the value of this property
     is cleared.
    :vartype identity: ~azure.search.documents.indexes.models.SearchIndexerDataIdentity
    :ivar indexer_permission_options: Ingestion options with various types of permission data.
    :vartype indexer_permission_options: list[str or
     ~azure.search.documents.indexes.models.IndexerPermissionOption]
    :ivar data_change_detection_policy: The data change detection policy for the datasource connection.
    :vartype data_change_detection_policy: ~azure.search.documents.models.DataChangeDetectionPolicy
    :ivar data_deletion_detection_policy: The data deletion detection policy for the datasource connection.
    :vartype data_deletion_detection_policy:
     ~azure.search.documents.models.DataDeletionDetectionPolicy
    :ivar e_tag: The ETag of the data source.
    :vartype e_tag: str
    :ivar encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your datasource
     definition when you want full assurance that no one, not even Microsoft, can decrypt your data
     source definition in Azure Cognitive Search. Once you have encrypted your data source
     definition, it will always remain encrypted. Azure Cognitive Search will ignore attempts to set
     this property to null. You can change this property as needed if you want to rotate your
     encryption key; Your datasource definition will be unaffected. Encryption with customer-managed
     keys is not available for free search services, and is only available for paid services created
     on or after January 1, 2019.
    :vartype encryption_key: ~azure.search.documents.indexes.models.SearchResourceEncryptionKey
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        type: str,
        connection_string: str,
        container: SearchIndexerDataContainer,
        identity: Optional[SearchIndexerDataIdentity] = None,
        indexer_permission_options: Optional[List[Union[str, IndexerPermissionOption]]] = None,
        data_change_detection_policy: Optional[DataChangeDetectionPolicy] = None,
        data_deletion_detection_policy: Optional[DataDeletionDetectionPolicy] = None,
        e_tag: Optional[str] = None,
        encryption_key: Optional[SearchResourceEncryptionKey] = None,
        **kwargs
    ):
        credentials = DataSourceCredentials(connection_string=connection_string)
        super().__init__(
            name=name,
            description=description,
            type=type,
            credentials=credentials,
            container=container,
            data_change_detection_policy=data_change_detection_policy,
            data_deletion_detection_policy=data_deletion_detection_policy,
            e_tag=e_tag,
            encryption_key=encryption_key,
            identity=identity,
            indexer_permission_options=indexer_permission_options,
            **kwargs
        )


__all__: list[str] = [
    "SearchField",
    "SearchFieldDataType",
    "SimpleField",
    "SearchableField",
    "ComplexField",
    "SearchIndexerDataSourceConnection",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
