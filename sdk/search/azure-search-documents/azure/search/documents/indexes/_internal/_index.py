# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

import msrest.serialization
from ._edm import Collection, ComplexType, String

if TYPE_CHECKING:
    from typing import Any, Dict, List

__all__ = ("ComplexField", "SearchableField", "SimpleField")


class SearchField(msrest.serialization.Model):
    # pylint: disable=too-many-instance-attributes
    """Represents a field in an index definition, which describes the name, data type, and search behavior of a field.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :type name: str
    :param type: Required. The data type of the field. Possible values include: "Edm.String",
     "Edm.Int32", "Edm.Int64", "Edm.Double", "Edm.Boolean", "Edm.DateTimeOffset",
     "Edm.GeographyPoint", "Edm.ComplexType".
    :type type: str or ~azure.search.documents.models.SearchFieldDataType
    :param key: A value indicating whether the field uniquely identifies documents in the index.
     Exactly one top-level field in each index must be chosen as the key field and it must be of
     type Edm.String. Key fields can be used to look up documents directly and update or delete
     specific documents. Default is false for simple fields and null for complex fields.
    :type key: bool
    :param hidden: A value indicating whether the field can be returned in a search result.
     You can enable this option if you want to use a field (for example, margin) as a filter,
     sorting, or scoring mechanism but do not want the field to be visible to the end user. This
     property must be False for key fields, and it must be null for complex fields. This property can
     be changed on existing fields. Enabling this property does not cause any increase in index
     storage requirements. Default is False for simple fields and null for complex fields.
    :type hidden: bool
    :param searchable: A value indicating whether the field is full-text searchable. This means it
     will undergo analysis such as word-breaking during indexing. If you set a searchable field to a
     value like "sunny day", internally it will be split into the individual tokens "sunny" and
     "day". This enables full-text searches for these terms. Fields of type Edm.String or
     Collection(Edm.String) are searchable by default. This property must be false for simple fields
     of other non-string data types, and it must be null for complex fields. Note: searchable fields
     consume extra space in your index since Azure Cognitive Search will store an additional
     tokenized version of the field value for full-text searches. If you want to save space in your
     index and you don't need a field to be included in searches, set searchable to false.
    :type searchable: bool
    :param filterable: A value indicating whether to enable the field to be referenced in $filter
     queries. filterable differs from searchable in how strings are handled. Fields of type
     Edm.String or Collection(Edm.String) that are filterable do not undergo word-breaking, so
     comparisons are for exact matches only. For example, if you set such a field f to "sunny day",
     $filter=f eq 'sunny' will find no matches, but $filter=f eq 'sunny day' will. This property
     must be null for complex fields. Default is true for simple fields and null for complex fields.
    :type filterable: bool
    :param sortable: A value indicating whether to enable the field to be referenced in $orderby
     expressions. By default Azure Cognitive Search sorts results by score, but in many experiences
     users will want to sort by fields in the documents. A simple field can be sortable only if it
     is single-valued (it has a single value in the scope of the parent document). Simple collection
     fields cannot be sortable, since they are multi-valued. Simple sub-fields of complex
     collections are also multi-valued, and therefore cannot be sortable. This is true whether it's
     an immediate parent field, or an ancestor field, that's the complex collection. Complex fields
     cannot be sortable and the sortable property must be null for such fields. The default for
     sortable is true for single-valued simple fields, false for multi-valued simple fields, and
     null for complex fields.
    :type sortable: bool
    :param facetable: A value indicating whether to enable the field to be referenced in facet
     queries. Typically used in a presentation of search results that includes hit count by category
     (for example, search for digital cameras and see hits by brand, by megapixels, by price, and so
     on). This property must be null for complex fields. Fields of type Edm.GeographyPoint or
     Collection(Edm.GeographyPoint) cannot be facetable. Default is true for all other simple
     fields.
    :type facetable: bool
    :param analyzer_name: The name of the analyzer to use for the field. This option can be used only
     with searchable fields and it can't be set together with either searchAnalyzer or
     indexAnalyzer. Once the analyzer is chosen, it cannot be changed for the field. Must be null
     for complex fields. Possible values include: "ar.microsoft", "ar.lucene", "hy.lucene",
     "bn.microsoft", "eu.lucene", "bg.microsoft", "bg.lucene", "ca.microsoft", "ca.lucene", "zh-
     Hans.microsoft", "zh-Hans.lucene", "zh-Hant.microsoft", "zh-Hant.lucene", "hr.microsoft",
     "cs.microsoft", "cs.lucene", "da.microsoft", "da.lucene", "nl.microsoft", "nl.lucene",
     "en.microsoft", "en.lucene", "et.microsoft", "fi.microsoft", "fi.lucene", "fr.microsoft",
     "fr.lucene", "gl.lucene", "de.microsoft", "de.lucene", "el.microsoft", "el.lucene",
     "gu.microsoft", "he.microsoft", "hi.microsoft", "hi.lucene", "hu.microsoft", "hu.lucene",
     "is.microsoft", "id.microsoft", "id.lucene", "ga.lucene", "it.microsoft", "it.lucene",
     "ja.microsoft", "ja.lucene", "kn.microsoft", "ko.microsoft", "ko.lucene", "lv.microsoft",
     "lv.lucene", "lt.microsoft", "ml.microsoft", "ms.microsoft", "mr.microsoft", "nb.microsoft",
     "no.lucene", "fa.lucene", "pl.microsoft", "pl.lucene", "pt-BR.microsoft", "pt-BR.lucene", "pt-
     PT.microsoft", "pt-PT.lucene", "pa.microsoft", "ro.microsoft", "ro.lucene", "ru.microsoft",
     "ru.lucene", "sr-cyrillic.microsoft", "sr-latin.microsoft", "sk.microsoft", "sl.microsoft",
     "es.microsoft", "es.lucene", "sv.microsoft", "sv.lucene", "ta.microsoft", "te.microsoft",
     "th.microsoft", "th.lucene", "tr.microsoft", "tr.lucene", "uk.microsoft", "ur.microsoft",
     "vi.microsoft", "standard.lucene", "standardasciifolding.lucene", "keyword", "pattern",
     "simple", "stop", "whitespace".
    :type analyzer_name: str or ~azure.search.documents.models.LexicalAnalyzerName
    :param search_analyzer_name: The name of the analyzer used at search time for the field. This option
     can be used only with searchable fields. It must be set together with indexAnalyzer and it
     cannot be set together with the analyzer option. This property cannot be set to the name of a
     language analyzer; use the analyzer property instead if you need a language analyzer. This
     analyzer can be updated on an existing field. Must be null for complex fields. Possible values
     include: "ar.microsoft", "ar.lucene", "hy.lucene", "bn.microsoft", "eu.lucene", "bg.microsoft",
     "bg.lucene", "ca.microsoft", "ca.lucene", "zh-Hans.microsoft", "zh-Hans.lucene", "zh-
     Hant.microsoft", "zh-Hant.lucene", "hr.microsoft", "cs.microsoft", "cs.lucene", "da.microsoft",
     "da.lucene", "nl.microsoft", "nl.lucene", "en.microsoft", "en.lucene", "et.microsoft",
     "fi.microsoft", "fi.lucene", "fr.microsoft", "fr.lucene", "gl.lucene", "de.microsoft",
     "de.lucene", "el.microsoft", "el.lucene", "gu.microsoft", "he.microsoft", "hi.microsoft",
     "hi.lucene", "hu.microsoft", "hu.lucene", "is.microsoft", "id.microsoft", "id.lucene",
     "ga.lucene", "it.microsoft", "it.lucene", "ja.microsoft", "ja.lucene", "kn.microsoft",
     "ko.microsoft", "ko.lucene", "lv.microsoft", "lv.lucene", "lt.microsoft", "ml.microsoft",
     "ms.microsoft", "mr.microsoft", "nb.microsoft", "no.lucene", "fa.lucene", "pl.microsoft",
     "pl.lucene", "pt-BR.microsoft", "pt-BR.lucene", "pt-PT.microsoft", "pt-PT.lucene",
     "pa.microsoft", "ro.microsoft", "ro.lucene", "ru.microsoft", "ru.lucene", "sr-
     cyrillic.microsoft", "sr-latin.microsoft", "sk.microsoft", "sl.microsoft", "es.microsoft",
     "es.lucene", "sv.microsoft", "sv.lucene", "ta.microsoft", "te.microsoft", "th.microsoft",
     "th.lucene", "tr.microsoft", "tr.lucene", "uk.microsoft", "ur.microsoft", "vi.microsoft",
     "standard.lucene", "standardasciifolding.lucene", "keyword", "pattern", "simple", "stop",
     "whitespace".
    :type search_analyzer_name: str or ~azure.search.documents.models.LexicalAnalyzerName
    :param index_analyzer_name: The name of the analyzer used at indexing time for the field. This
     option can be used only with searchable fields. It must be set together with searchAnalyzer and
     it cannot be set together with the analyzer option.  This property cannot be set to the name of
     a language analyzer; use the analyzer property instead if you need a language analyzer. Once
     the analyzer is chosen, it cannot be changed for the field. Must be null for complex fields.
     Possible values include: "ar.microsoft", "ar.lucene", "hy.lucene", "bn.microsoft", "eu.lucene",
     "bg.microsoft", "bg.lucene", "ca.microsoft", "ca.lucene", "zh-Hans.microsoft", "zh-
     Hans.lucene", "zh-Hant.microsoft", "zh-Hant.lucene", "hr.microsoft", "cs.microsoft",
     "cs.lucene", "da.microsoft", "da.lucene", "nl.microsoft", "nl.lucene", "en.microsoft",
     "en.lucene", "et.microsoft", "fi.microsoft", "fi.lucene", "fr.microsoft", "fr.lucene",
     "gl.lucene", "de.microsoft", "de.lucene", "el.microsoft", "el.lucene", "gu.microsoft",
     "he.microsoft", "hi.microsoft", "hi.lucene", "hu.microsoft", "hu.lucene", "is.microsoft",
     "id.microsoft", "id.lucene", "ga.lucene", "it.microsoft", "it.lucene", "ja.microsoft",
     "ja.lucene", "kn.microsoft", "ko.microsoft", "ko.lucene", "lv.microsoft", "lv.lucene",
     "lt.microsoft", "ml.microsoft", "ms.microsoft", "mr.microsoft", "nb.microsoft", "no.lucene",
     "fa.lucene", "pl.microsoft", "pl.lucene", "pt-BR.microsoft", "pt-BR.lucene", "pt-PT.microsoft",
     "pt-PT.lucene", "pa.microsoft", "ro.microsoft", "ro.lucene", "ru.microsoft", "ru.lucene", "sr-
     cyrillic.microsoft", "sr-latin.microsoft", "sk.microsoft", "sl.microsoft", "es.microsoft",
     "es.lucene", "sv.microsoft", "sv.lucene", "ta.microsoft", "te.microsoft", "th.microsoft",
     "th.lucene", "tr.microsoft", "tr.lucene", "uk.microsoft", "ur.microsoft", "vi.microsoft",
     "standard.lucene", "standardasciifolding.lucene", "keyword", "pattern", "simple", "stop",
     "whitespace".
    :type index_analyzer_name: str or ~azure.search.documents.models.LexicalAnalyzerName
    :param synonym_map_names: A list of the names of synonym maps to associate with this field. This
     option can be used only with searchable fields. Currently only one synonym map per field is
     supported. Assigning a synonym map to a field ensures that query terms targeting that field are
     expanded at query-time using the rules in the synonym map. This attribute can be changed on
     existing fields. Must be null or an empty collection for complex fields.
    :type synonym_map_names: list[str]
    :param fields: A list of sub-fields if this is a field of type Edm.ComplexType or
     Collection(Edm.ComplexType). Must be null or empty for simple fields.
    :type fields: list[~azure.search.documents.models.SearchField]
    """

    _validation = {
        'name': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'key': {'key': 'key', 'type': 'bool'},
        'hidden': {'key': 'hidden', 'type': 'bool'},
        'searchable': {'key': 'searchable', 'type': 'bool'},
        'filterable': {'key': 'filterable', 'type': 'bool'},
        'sortable': {'key': 'sortable', 'type': 'bool'},
        'facetable': {'key': 'facetable', 'type': 'bool'},
        'analyzer_name': {'key': 'analyzerName', 'type': 'str'},
        'search_analyzer_name': {'key': 'searchAnalyzerName', 'type': 'str'},
        'index_analyzer_name': {'key': 'indexAnalyzerName', 'type': 'str'},
        'synonym_map_names': {'key': 'synonymMapNames', 'type': '[str]'},
        'fields': {'key': 'fields', 'type': '[SearchField]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SearchField, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.type = kwargs['type']
        self.key = kwargs.get('key', None)
        self.hidden = kwargs.get('hidden', None)
        self.searchable = kwargs.get('searchable', None)
        self.filterable = kwargs.get('filterable', None)
        self.sortable = kwargs.get('sortable', None)
        self.facetable = kwargs.get('facetable', None)
        self.analyzer_name = kwargs.get('analyzer_name', None)
        self.search_analyzer_name = kwargs.get('search_analyzer_name', None)
        self.index_analyzer_name = kwargs.get('index_analyzer_name', None)
        self.synonym_map_names = kwargs.get('synonym_map_names', None)
        self.fields = kwargs.get('fields', None)


def SimpleField(**kw):
    # type: (**Any) -> SearchField
    """Configure a simple field for an Azure Search Index

    :param name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :type name: str
    :param type: Required. The data type of the field. Possible values include: SearchFieldDataType.String,
     SearchFieldDataType.Int32, SearchFieldDataType.Int64, SearchFieldDataType.Double, SearchFieldDataType.Boolean,
     SearchFieldDataType.DateTimeOffset, SearchFieldDataType.GeographyPoint, SearchFieldDataType.ComplexType,
     from `azure.search.documents.SearchFieldDataType`.
     :type type: str
    :param key: A value indicating whether the field uniquely identifies documents in the index.
     Exactly one top-level field in each index must be chosen as the key field and it must be of
     type SearchFieldDataType.String. Key fields can be used to look up documents directly and
     update or delete specific documents. Default is False
    :type key: bool
    :param hidden: A value indicating whether the field can be returned in a search result.
     You can enable this option if you want to use a field (for example, margin) as a filter,
     sorting, or scoring mechanism but do not want the field to be visible to the end user. This
     property must be False for key fields. This property can be changed on existing fields.
     Enabling this property does not cause any increase in index storage requirements. Default is
     False.
    :type hidden: bool
    :param filterable: A value indicating whether to enable the field to be referenced in $filter
     queries. filterable differs from searchable in how strings are handled. Fields of type
     SearchFieldDataType.String or Collection(SearchFieldDataType.String) that are filterable do
     not undergo word-breaking, so comparisons are for exact matches only. For example, if you
     set such a field f to "sunny day", $filter=f eq 'sunny' will find no matches, but
     $filter=f eq 'sunny day' will. This property must be null for complex fields. Default is False
    :type filterable: bool
    :param sortable: A value indicating whether to enable the field to be referenced in $orderby
     expressions. By default Azure Cognitive Search sorts results by score, but in many experiences
     users will want to sort by fields in the documents. A simple field can be sortable only if it
     is single-valued (it has a single value in the scope of the parent document). Simple collection
     fields cannot be sortable, since they are multi-valued. Simple sub-fields of complex
     collections are also multi-valued, and therefore cannot be sortable. This is true whether it's
     an immediate parent field, or an ancestor field, that's the complex collection. The default is
     False.
    :type sortable: bool
    :param facetable: A value indicating whether to enable the field to be referenced in facet
     queries. Typically used in a presentation of search results that includes hit count by category
     (for example, search for digital cameras and see hits by brand, by megapixels, by price, and so
     on). Fields of type SearchFieldDataType.GeographyPoint or
     Collection(SearchFieldDataType.GeographyPoint) cannot be facetable. Default is False.
    :type facetable: bool
    """
    result = {"name": kw.get("name"), "type": kw.get("type")}  # type: Dict[str, Any]
    result["key"] = kw.get("key", False)
    result["searchable"] = False
    result["filterable"] = kw.get("filterable", False)
    result["facetable"] = kw.get("facetable", False)
    result["sortable"] = kw.get("sortable", False)
    result["hidden"] = kw.get("hidden", False)
    return SearchField(**result)


def SearchableField(**kw):
    # type: (**Any) -> SearchField
    """Configure a searchable text field for an Azure Search Index

    :param name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :type name: str
    :param collection: Whether this search field is a collection (default False)
    :type collection: bool
    :param key: A value indicating whether the field uniquely identifies documents in the index.
     Exactly one top-level field in each index must be chosen as the key field and it must be of
     type SearchFieldDataType.String. Key fields can be used to look up documents directly and update or delete
     specific documents. Default is False
    :type key: bool
    :param hidden: A value indicating whether the field can be returned in a search result.
     You can enable this option if you want to use a field (for example, margin) as a filter,
     sorting, or scoring mechanism but do not want the field to be visible to the end user. This
     property must be False for key fields. This property can be changed on existing fields.
     Enabling this property does not cause any increase in index storage requirements. Default is
     False.
    :type hidden: bool
    :param searchable: A value indicating whether the field is full-text searchable. This means it
     will undergo analysis such as word-breaking during indexing. If you set a searchable field to a
     value like "sunny day", internally it will be split into the individual tokens "sunny" and
     "day". This enables full-text searches for these terms. Note: searchable fields
     consume extra space in your index since Azure Cognitive Search will store an additional
     tokenized version of the field value for full-text searches. If you want to save space in your
     index and you don't need a field to be included in searches, set searchable to false. Default
     is True.
    :type searchable: bool
    :param filterable: A value indicating whether to enable the field to be referenced in $filter
     queries. filterable differs from searchable in how strings are handled. Fields that are
     filterable do not undergo word-breaking, so comparisons are for exact matches only. For example,
     if you set such a field f to "sunny day", $filter=f eq 'sunny' will find no matches, but
     $filter=f eq 'sunny day' will. Default is False.
    :type filterable: bool
    :param sortable: A value indicating whether to enable the field to be referenced in $orderby
     expressions. By default Azure Cognitive Search sorts results by score, but in many experiences
     users will want to sort by fields in the documents.  The default is true False.
    :type sortable: bool
    :param facetable: A value indicating whether to enable the field to be referenced in facet
     queries. Typically used in a presentation of search results that includes hit count by category
     (for example, search for digital cameras and see hits by brand, by megapixels, by price, and so
     on). Default is False.
    :type facetable: bool
    :param analyzer_name: The name of the analyzer to use for the field. This option can't be set together
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
    :type analyzer_name: str or ~search_service_client.models.AnalyzerName
    :param search_analyzer_name: The name of the analyzer used at search time for the field. It must be
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
    :type search_analyzer_name: str or ~search_service_client.models.AnalyzerName
    :param index_analyzer_name: The name of the analyzer used at indexing time for the field.
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
    :type index_analyzer_name: str or ~search_service_client.models.AnalyzerName
    :param synonym_map_names: A list of the names of synonym maps to associate with this field. Currently
     only one synonym map per field is supported. Assigning a synonym map to a field ensures that
     query terms targeting that field are expanded at query-time using the rules in the synonym map.
     This attribute can be changed on existing fields.
    :type synonym_map_names: list[str]

    """
    typ = Collection(String) if kw.get("collection", False) else String
    result = {"name": kw.get("name"), "type": typ}  # type: Dict[str, Any]
    result["key"] = kw.get("key", False)
    result["searchable"] = kw.get("searchable", True)
    result["filterable"] = kw.get("filterable", False)
    result["facetable"] = kw.get("facetable", False)
    result["sortable"] = kw.get("sortable", False)
    result["hidden"] = kw.get("hidden", False)
    if "analyzer_name" in kw:
        result["analyzer_name"] = kw["analyzer_name"]
    if "search_analyzer_name" in kw:
        result["search_analyzer_name"] = kw["search_analyzer_name"]
    if "index_analyzer_name" in kw:
        result["index_analyzer_name"] = kw["index_analyzer_name"]
    if "synonym_map_names" in kw:
        result["synonym_map_names"] = kw["synonym_map_names"]
    return SearchField(**result)


def ComplexField(**kw):
    # type: (**Any) -> SearchField
    """Configure a Complex or Complex collection field for an Azure Search
    Index

    :param name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :type name: str
    :param collection: Whether this complex field is a collection (default False)
    :type collection: bool
    :type type: str or ~search_service_client.models.DataType
    :param fields: A list of sub-fields
    :type fields: list[~search_service_client.models.Field]

    """
    typ = Collection(ComplexType) if kw.get("collection", False) else ComplexType
    result = {"name": kw.get("name"), "type": typ}  # type: Dict[str, Any]
    result["fields"] = kw.get("fields")
    return SearchField(**result)


class SearchIndex(msrest.serialization.Model):
    # pylint: disable=too-many-instance-attributes
    """Represents a search index definition, which describes the fields and search behavior of an index.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the index.
    :type name: str
    :param fields: Required. The fields of the index.
    :type fields: list[~azure.search.documents.models.SearchField]
    :param scoring_profiles: The scoring profiles for the index.
    :type scoring_profiles: list[~azure.search.documents.models.ScoringProfile]
    :param default_scoring_profile: The name of the scoring profile to use if none is specified in
     the query. If this property is not set and no scoring profile is specified in the query, then
     default scoring (tf-idf) will be used.
    :type default_scoring_profile: str
    :param cors_options: Options to control Cross-Origin Resource Sharing (CORS) for the index.
    :type cors_options: ~azure.search.documents.models.CorsOptions
    :param suggesters: The suggesters for the index.
    :type suggesters: list[~azure.search.documents.models.Suggester]
    :param analyzers: The analyzers for the index.
    :type analyzers: list[~azure.search.documents.models.LexicalAnalyzer]
    :param tokenizers: The tokenizers for the index.
    :type tokenizers: list[~azure.search.documents.models.LexicalTokenizer]
    :param token_filters: The token filters for the index.
    :type token_filters: list[~azure.search.documents.models.TokenFilter]
    :param char_filters: The character filters for the index.
    :type char_filters: list[~azure.search.documents.models.CharFilter]
    :param encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your data when you
     want full assurance that no one, not even Microsoft, can decrypt your data in Azure Cognitive
     Search. Once you have encrypted your data, it will always remain encrypted. Azure Cognitive
     Search will ignore attempts to set this property to null. You can change this property as
     needed if you want to rotate your encryption key; Your data will be unaffected. Encryption with
     customer-managed keys is not available for free search services, and is only available for paid
     services created on or after January 1, 2019.
    :type encryption_key: ~azure.search.documents.models.SearchResourceEncryptionKey
    :param similarity: The type of similarity algorithm to be used when scoring and ranking the
     documents matching a search query. The similarity algorithm can only be defined at index
     creation time and cannot be modified on existing indexes. If null, the ClassicSimilarity
     algorithm is used.
    :type similarity: ~azure.search.documents.models.Similarity
    :param e_tag: The ETag of the index.
    :type e_tag: str
    """

    _validation = {
        'name': {'required': True},
        'fields': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'fields': {'key': 'fields', 'type': '[SearchField]'},
        'scoring_profiles': {'key': 'scoringProfiles', 'type': '[ScoringProfile]'},
        'default_scoring_profile': {'key': 'defaultScoringProfile', 'type': 'str'},
        'cors_options': {'key': 'corsOptions', 'type': 'CorsOptions'},
        'suggesters': {'key': 'suggesters', 'type': '[SearchSuggester]'},
        'analyzers': {'key': 'analyzers', 'type': '[LexicalAnalyzer]'},
        'tokenizers': {'key': 'tokenizers', 'type': '[LexicalTokenizer]'},
        'token_filters': {'key': 'tokenFilters', 'type': '[TokenFilter]'},
        'char_filters': {'key': 'charFilters', 'type': '[CharFilter]'},
        'encryption_key': {'key': 'encryptionKey', 'type': 'SearchResourceEncryptionKey'},
        'similarity': {'key': 'similarity', 'type': 'SimilarityAlgorithm'},
        'e_tag': {'key': '@odata\\.etag', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SearchIndex, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.fields = kwargs['fields']
        self.scoring_profiles = kwargs.get('scoring_profiles', None)
        self.default_scoring_profile = kwargs.get('default_scoring_profile', None)
        self.cors_options = kwargs.get('cors_options', None)
        self.suggesters = kwargs.get('suggesters', None)
        self.analyzers = kwargs.get('analyzers', None)
        self.tokenizers = kwargs.get('tokenizers', None)
        self.token_filters = kwargs.get('token_filters', None)
        self.char_filters = kwargs.get('char_filters', None)
        self.encryption_key = kwargs.get('encryption_key', None)
        self.similarity = kwargs.get('similarity', None)
        self.e_tag = kwargs.get('e_tag', None)
