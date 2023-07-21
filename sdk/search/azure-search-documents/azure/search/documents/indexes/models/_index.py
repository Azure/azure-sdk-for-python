# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from .._generated import _serialization
from ._edm import Collection, ComplexType, String
from .._generated.models import (
    SearchField as _SearchField,
    SearchIndex as _SearchIndex,
    PatternTokenizer as _PatternTokenizer,
)
from ._models import (
    pack_analyzer,
    unpack_analyzer,
    PatternTokenizer,
    SearchResourceEncryptionKey,
)

if TYPE_CHECKING:
    from typing import Any, Dict, List

__all__ = ("ComplexField", "SearchableField", "SimpleField")


class SearchField(_serialization.Model):
    # pylint: disable=too-many-instance-attributes
    """Represents a field in an index definition, which describes the name, data type, and search behavior of a field.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :paramtype name: str
    :keyword type: Required. The data type of the field. Possible values include: "Edm.String",
     "Edm.Int32", "Edm.Int64", "Edm.Double", "Edm.Boolean", "Edm.DateTimeOffset",
     "Edm.GeographyPoint", "Edm.ComplexType".
    :paramtype type: str or ~azure.search.documents.indexes.models.SearchFieldDataType
    :keyword key: A value indicating whether the field uniquely identifies documents in the index.
     Exactly one top-level field in each index must be chosen as the key field and it must be of
     type Edm.String. Key fields can be used to look up documents directly and update or delete
     specific documents. Default is false for simple fields and null for complex fields.
    :paramtype key: bool
    :keyword hidden: A value indicating whether the field can be returned in a search result.
     You can enable this option if you want to use a field (for example, margin) as a filter,
     sorting, or scoring mechanism but do not want the field to be visible to the end user. This
     property must be False for key fields, and it must be null for complex fields. This property can
     be changed on existing fields. Enabling this property does not cause any increase in index
     storage requirements. Default is False for simple fields and null for complex fields.
    :paramtype hidden: bool
    :keyword searchable: A value indicating whether the field is full-text searchable. This means it
     will undergo analysis such as word-breaking during indexing. If you set a searchable field to a
     value like "sunny day", internally it will be split into the individual tokens "sunny" and
     "day". This enables full-text searches for these terms. Fields of type Edm.String or
     Collection(Edm.String) are searchable by default. This property must be false for simple fields
     of other non-string data types, and it must be null for complex fields. Note: searchable fields
     consume extra space in your index since Azure Cognitive Search will store an additional
     tokenized version of the field value for full-text searches. If you want to save space in your
     index and you don't need a field to be included in searches, set searchable to false.
    :paramtype searchable: bool
    :keyword filterable: A value indicating whether to enable the field to be referenced in $filter
     queries. filterable differs from searchable in how strings are handled. Fields of type
     Edm.String or Collection(Edm.String) that are filterable do not undergo word-breaking, so
     comparisons are for exact matches only. For example, if you set such a field f to "sunny day",
     $filter=f eq 'sunny' will find no matches, but $filter=f eq 'sunny day' will. This property
     must be null for complex fields. Default is true for simple fields and null for complex fields.
    :paramtype filterable: bool
    :keyword sortable: A value indicating whether to enable the field to be referenced in $orderby
     expressions. By default Azure Cognitive Search sorts results by score, but in many experiences
     users will want to sort by fields in the documents. A simple field can be sortable only if it
     is single-valued (it has a single value in the scope of the parent document). Simple collection
     fields cannot be sortable, since they are multi-valued. Simple sub-fields of complex
     collections are also multi-valued, and therefore cannot be sortable. This is true whether it's
     an immediate parent field, or an ancestor field, that's the complex collection. Complex fields
     cannot be sortable and the sortable property must be null for such fields. The default for
     sortable is true for single-valued simple fields, false for multi-valued simple fields, and
     null for complex fields.
    :paramtype sortable: bool
    :keyword facetable: A value indicating whether to enable the field to be referenced in facet
     queries. Typically used in a presentation of search results that includes hit count by category
     (for example, search for digital cameras and see hits by brand, by megapixels, by price, and so
     on). This property must be null for complex fields. Fields of type Edm.GeographyPoint or
     Collection(Edm.GeographyPoint) cannot be facetable. Default is true for all other simple
     fields.
    :paramtype facetable: bool
    :keyword analyzer_name: The name of the analyzer to use for the field. This option can be used only
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
    :paramtype analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :keyword search_analyzer_name: The name of the analyzer used at search time for the field. This option
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
    :paramtype search_analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :keyword index_analyzer_name: The name of the analyzer used at indexing time for the field. This
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
    :paramtype index_analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :keyword normalizer_name: The name of the normalizer to use for the field. This option can be used
     only with fields with filterable, sortable, or facetable enabled. Once the normalizer is
     chosen, it cannot be changed for the field. Must be null for complex fields. Possible values
     include: "asciifolding", "elision", "lowercase", "standard", "uppercase".
    :paramtype normalizer_name: str or ~azure.search.documents.indexes.models.LexicalNormalizerName
    :keyword synonym_map_names: A list of the names of synonym maps to associate with this field. This
     option can be used only with searchable fields. Currently only one synonym map per field is
     supported. Assigning a synonym map to a field ensures that query terms targeting that field are
     expanded at query-time using the rules in the synonym map. This attribute can be changed on
     existing fields. Must be null or an empty collection for complex fields.
    :paramtype synonym_map_names: list[str]
    :keyword fields: A list of sub-fields if this is a field of type Edm.ComplexType or
     Collection(Edm.ComplexType). Must be null or empty for simple fields.
    :paramtype fields: list[~azure.search.documents.models.SearchField]
    :keyword int vector_search_dimensions: The dimensionality of the vector field.
    :keyword str vector_search_configuration: The name of the vector search algorithm configuration
     that specifies the algorithm and optional parameters for searching the vector field.
    """

    _validation = {
        "name": {"required": True},
        "type": {"required": True},
    }

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "type": {"key": "type", "type": "str"},
        "key": {"key": "key", "type": "bool"},
        "hidden": {"key": "hidden", "type": "bool"},
        "searchable": {"key": "searchable", "type": "bool"},
        "filterable": {"key": "filterable", "type": "bool"},
        "sortable": {"key": "sortable", "type": "bool"},
        "facetable": {"key": "facetable", "type": "bool"},
        "analyzer_name": {"key": "analyzerName", "type": "str"},
        "search_analyzer_name": {"key": "searchAnalyzerName", "type": "str"},
        "index_analyzer_name": {"key": "indexAnalyzerName", "type": "str"},
        "normalizer_name": {"key": "normalizerName", "type": "str"},
        "synonym_map_names": {"key": "synonymMapNames", "type": "[str]"},
        "fields": {"key": "fields", "type": "[SearchField]"},
        "vector_search_dimensions": {"key": "vectorSearchDimensions", "type": "int"},
        "vector_search_configuration": {"key": "vectorSearchConfiguration", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(SearchField, self).__init__(**kwargs)
        self.name = kwargs["name"]
        self.type = kwargs["type"]
        self.key = kwargs.get("key", None)
        self.hidden = kwargs.get("hidden", None)
        self.searchable = kwargs.get("searchable", None)
        self.filterable = kwargs.get("filterable", None)
        self.sortable = kwargs.get("sortable", None)
        self.facetable = kwargs.get("facetable", None)
        self.analyzer_name = kwargs.get("analyzer_name", None)
        self.search_analyzer_name = kwargs.get("search_analyzer_name", None)
        self.index_analyzer_name = kwargs.get("index_analyzer_name", None)
        self.normalizer_name = kwargs.get("normalizer_name", None)
        self.synonym_map_names = kwargs.get("synonym_map_names", None)
        self.fields = kwargs.get("fields", None)
        self.vector_search_dimensions = kwargs.get("vector_search_dimensions", None)
        self.vector_search_configuration = kwargs.get("vector_search_configuration", None)

    def _to_generated(self):
        fields = [pack_search_field(x) for x in self.fields] if self.fields else None
        retrievable = not self.hidden if self.hidden is not None else None
        return _SearchField(
            name=self.name,
            type=self.type,
            key=self.key,
            retrievable=retrievable,
            searchable=self.searchable,
            filterable=self.filterable,
            sortable=self.sortable,
            facetable=self.facetable,
            analyzer=self.analyzer_name,
            search_analyzer=self.search_analyzer_name,
            index_analyzer=self.index_analyzer_name,
            normalizer=self.normalizer_name,
            synonym_maps=self.synonym_map_names,
            fields=fields,
            dimensions=self.vector_search_dimensions,
            vector_search_configuration=self.vector_search_configuration,
        )

    @classmethod
    def _from_generated(cls, search_field):
        if not search_field:
            return None
        # pylint:disable=protected-access
        fields = [SearchField._from_generated(x) for x in search_field.fields] if search_field.fields else None
        hidden = not search_field.retrievable if search_field.retrievable is not None else None
        try:
            normalizer = search_field.normalizer_name
        except AttributeError:
            normalizer = None
        return cls(
            name=search_field.name,
            type=search_field.type,
            key=search_field.key,
            hidden=hidden,
            searchable=search_field.searchable,
            filterable=search_field.filterable,
            sortable=search_field.sortable,
            facetable=search_field.facetable,
            analyzer_name=search_field.analyzer,
            search_analyzer_name=search_field.search_analyzer,
            index_analyzer_name=search_field.index_analyzer,
            normalizer_name=normalizer,
            synonym_map_names=search_field.synonym_maps,
            fields=fields,
            vector_search_dimensions=search_field.dimensions,
            vector_search_configuration=search_field.vector_search_configuration,
        )


def SimpleField(**kw):
    # type: (**Any) -> SearchField
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
    :paramtype analyzer_name: str or ~azure.search.documents.indexes.models.AnalyzerName
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
    :paramtype search_analyzer_name: str or ~azure.search.documents.indexes.models.AnalyzerName
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
    :paramtype index_analyzer_name: str or ~azure.search.documents.indexes.models.AnalyzerName
    :keyword synonym_map_names: A list of the names of synonym maps to associate with this field. Currently
     only one synonym map per field is supported. Assigning a synonym map to a field ensures that
     query terms targeting that field are expanded at query-time using the rules in the synonym map.
     This attribute can be changed on existing fields.
    :paramtype synonym_map_names: list[str]

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

    :keyword name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :paramtype name: str
    :keyword collection: Whether this complex field is a collection (default False)
    :paramtype collection: bool
    :paramtype type: str or ~search_service_client.models.DataType
    :keyword fields: A list of sub-fields
    :paramtype fields: list[~search_service_client.models.Field]

    """
    typ = Collection(ComplexType) if kw.get("collection", False) else ComplexType
    result = {"name": kw.get("name"), "type": typ}  # type: Dict[str, Any]
    result["fields"] = kw.get("fields")
    return SearchField(**result)


class SearchIndex(_serialization.Model):
    # pylint: disable=too-many-instance-attributes
    """Represents a search index definition, which describes the fields and search behavior of an index.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the index.
    :paramtype name: str
    :keyword fields: Required. The fields of the index.
    :paramtype fields: list[~azure.search.documents.indexes.models.SearchField]
    :keyword scoring_profiles: The scoring profiles for the index.
    :paramtype scoring_profiles: list[~azure.search.documents.indexes.models.ScoringProfile]
    :keyword default_scoring_profile: The name of the scoring profile to use if none is specified in
     the query. If this property is not set and no scoring profile is specified in the query, then
     default scoring (tf-idf) will be used.
    :paramtype default_scoring_profile: str
    :keyword cors_options: Options to control Cross-Origin Resource Sharing (CORS) for the index.
    :paramtype cors_options: ~azure.search.documents.indexes.models.CorsOptions
    :keyword suggesters: The suggesters for the index.
    :paramtype suggesters: list[~azure.search.documents.indexes.models.SearchSuggester]
    :keyword analyzers: The analyzers for the index.
    :paramtype analyzers: list[~azure.search.documents.indexes.models.LexicalAnalyzer]
    :keyword tokenizers: The tokenizers for the index.
    :paramtype tokenizers: list[~azure.search.documents.indexes.models.LexicalTokenizer]
    :keyword token_filters: The token filters for the index.
    :paramtype token_filters: list[~azure.search.documents.indexes.models.TokenFilter]
    :keyword char_filters: The character filters for the index.
    :paramtype char_filters: list[~azure.search.documents.indexes.models.CharFilter]
    :keyword normalizers: The normalizers for the index.
    :paramtype normalizers:
     list[~azure.search.documents.indexes.models.LexicalNormalizer]
    :keyword encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your data when you
     want full assurance that no one, not even Microsoft, can decrypt your data in Azure Cognitive
     Search. Once you have encrypted your data, it will always remain encrypted. Azure Cognitive
     Search will ignore attempts to set this property to null. You can change this property as
     needed if you want to rotate your encryption key; Your data will be unaffected. Encryption with
     customer-managed keys is not available for free search services, and is only available for paid
     services created on or after January 1, 2019.
    :paramtype encryption_key: ~azure.search.documents.indexes.models.SearchResourceEncryptionKey
    :keyword similarity: The type of similarity algorithm to be used when scoring and ranking the
     documents matching a search query. The similarity algorithm can only be defined at index
     creation time and cannot be modified on existing indexes. If null, the ClassicSimilarity
     algorithm is used.
    :paramtype similarity: ~azure.search.documents.indexes.models.SimilarityAlgorithm
    :keyword semantic_settings: Defines parameters for a search index that influence semantic capabilities.
    :paramtype semantic_settings: ~azure.search.documents.indexes.models.SemanticSettings
    :keyword e_tag: The ETag of the index.
    :paramtype e_tag: str
    """

    _validation = {
        "name": {"required": True},
        "fields": {"required": True},
    }

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "fields": {"key": "fields", "type": "[SearchField]"},
        "scoring_profiles": {"key": "scoringProfiles", "type": "[ScoringProfile]"},
        "default_scoring_profile": {"key": "defaultScoringProfile", "type": "str"},
        "cors_options": {"key": "corsOptions", "type": "CorsOptions"},
        "suggesters": {"key": "suggesters", "type": "[SearchSuggester]"},
        "analyzers": {"key": "analyzers", "type": "[LexicalAnalyzer]"},
        "tokenizers": {"key": "tokenizers", "type": "[LexicalTokenizer]"},
        "token_filters": {"key": "tokenFilters", "type": "[TokenFilter]"},
        "char_filters": {"key": "charFilters", "type": "[CharFilter]"},
        "normalizers": {"key": "normalizers", "type": "[LexicalNormalizer]"},
        "encryption_key": {
            "key": "encryptionKey",
            "type": "SearchResourceEncryptionKey",
        },
        "similarity": {"key": "similarity", "type": "SimilarityAlgorithm"},
        "semantic_settings": {"key": "semantic", "type": "SemanticSettings"},
        "vector_search": {"key": "vectorSearch", "type": "VectorSearch"},
        "e_tag": {"key": "@odata\\.etag", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(SearchIndex, self).__init__(**kwargs)
        self.name = kwargs["name"]
        self.fields = kwargs["fields"]
        self.scoring_profiles = kwargs.get("scoring_profiles", None)
        self.default_scoring_profile = kwargs.get("default_scoring_profile", None)
        self.cors_options = kwargs.get("cors_options", None)
        self.suggesters = kwargs.get("suggesters", None)
        self.analyzers = kwargs.get("analyzers", None)
        self.tokenizers = kwargs.get("tokenizers", None)
        self.token_filters = kwargs.get("token_filters", None)
        self.char_filters = kwargs.get("char_filters", None)
        self.normalizers = kwargs.get("normalizers", None)
        self.encryption_key = kwargs.get("encryption_key", None)
        self.similarity = kwargs.get("similarity", None)
        self.semantic_settings = kwargs.get("semantic_settings", None)
        self.vector_search = kwargs.get("vector_search", None)
        self.e_tag = kwargs.get("e_tag", None)

    def _to_generated(self):
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
            fields = None
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
            normalizers=self.normalizers,
            # pylint:disable=protected-access
            encryption_key=self.encryption_key._to_generated() if self.encryption_key else None,
            similarity=self.similarity,
            semantic_settings=self.semantic_settings,
            e_tag=self.e_tag,
            vector_search=self.vector_search,
        )

    @classmethod
    def _from_generated(cls, search_index):
        if not search_index:
            return None
        if search_index.analyzers:
            analyzers = [unpack_analyzer(x) for x in search_index.analyzers]  # type: ignore
        else:
            analyzers = None
        if search_index.tokenizers:
            tokenizers = [
                PatternTokenizer._from_generated(x)  # pylint:disable=protected-access
                if isinstance(x, _PatternTokenizer)
                else x
                for x in search_index.tokenizers
            ]
        else:
            tokenizers = None
        if search_index.fields:
            fields = [SearchField._from_generated(x) for x in search_index.fields]  # pylint:disable=protected-access
        else:
            fields = None
        try:
            normalizers = search_index.normalizers
        except AttributeError:
            normalizers = None
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
            normalizers=normalizers,
            # pylint:disable=protected-access
            encryption_key=SearchResourceEncryptionKey._from_generated(search_index.encryption_key),
            similarity=search_index.similarity,
            semantic_settings=search_index.semantic_settings,
            e_tag=search_index.e_tag,
            vector_search=search_index.vector_search,
        )


def pack_search_field(search_field):
    # type: (SearchField) -> _SearchField
    if not search_field:
        return None
    if isinstance(search_field, dict):
        name = search_field.get("name")
        field_type = search_field.get("type")
        key = search_field.get("key")
        hidden = search_field.get("hidden")
        searchable = search_field.get("searchable")
        filterable = search_field.get("filterable")
        sortable = search_field.get("sortable")
        facetable = search_field.get("facetable")
        analyzer_name = search_field.get("analyzer_name")
        search_analyzer_name = search_field.get("search_analyzer_name")
        index_analyzer_name = search_field.get("index_analyzer_name")
        normalizer = search_field.get("normalizer")
        synonym_map_names = search_field.get("synonym_map_names")
        fields = search_field.get("fields")
        fields = [pack_search_field(x) for x in fields] if fields else None
        return _SearchField(
            name=name,
            type=field_type,
            key=key,
            retrievable=not hidden,
            searchable=searchable,
            filterable=filterable,
            sortable=sortable,
            facetable=facetable,
            analyzer=analyzer_name,
            search_analyzer=search_analyzer_name,
            index_analyzer=index_analyzer_name,
            normalizer=normalizer,
            synonym_maps=synonym_map_names,
            fields=fields,
        )
    return search_field._to_generated()  # pylint:disable=protected-access
