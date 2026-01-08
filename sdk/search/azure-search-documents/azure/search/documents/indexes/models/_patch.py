# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict, List, Optional, Union
from ._models import SearchField as _SearchField
from ._enums import (
    LexicalAnalyzerName,
    SearchFieldDataType as _SearchFieldDataType,
)


class SearchField(_SearchField):
    """Represents a field in an index definition, which describes the name, data type, and search
    behavior of a field.

    This class adds backward compatibility support for the 'hidden' property, which is the inverse
    of 'retrievable'.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Handle 'hidden' kwarg for backward compatibility
        hidden = kwargs.pop("hidden", None)
        super().__init__(*args, **kwargs)
        # If hidden was explicitly provided, set retrievable to its inverse
        if hidden is not None:
            self.retrievable = not hidden

    @property
    def hidden(self) -> Optional[bool]:
        """A value indicating whether the field will be returned in a search result.
        This is the inverse of 'retrievable'. Kept for backward compatibility.

        :return: True if the field is hidden (not retrievable), False otherwise.
        :rtype: bool or None
        """
        if self.retrievable is None:
            return None
        return not self.retrievable

    @hidden.setter
    def hidden(self, value: Optional[bool]) -> None:
        """Set whether the field should be hidden (not retrievable).

        :param value: True to hide the field, False to make it retrievable.
        :type value: bool or None
        """
        if value is None:
            self.retrievable = None
        else:
            self.retrievable = not value

# Re-export SearchFieldDataType and add Collection helper
SearchFieldDataType = _SearchFieldDataType


# Add Collection method to SearchFieldDataType enum
def _collection_helper(typ) -> str:
    """Helper function to create a collection type string.

    :param typ: The type to wrap in a collection. Can be a string or an enum value.
    :type typ: str or Enum
    :return: A collection type string.
    :rtype: str
    """
    # If typ is an enum, get its value; otherwise use it as-is
    if hasattr(typ, "value"):
        typ = typ.value
    return "Collection({})".format(typ)


# Monkey-patch the Collection method onto the enum class
SearchFieldDataType.Collection = staticmethod(_collection_helper)  # type: ignore


def Collection(typ) -> str:
    """Helper function to create a collection type string.

    :param typ: The type to wrap in a collection. Can be a string or an enum value.
    :type typ: str or Enum
    :return: A collection type string.
    :rtype: str
    """
    # If typ is an enum, get its value; otherwise use it as-is
    if hasattr(typ, "value"):
        typ = typ.value
    return "Collection({})".format(typ)


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
    :keyword hidden: A value indicating whether the field will be returned in a search result.
        Setting this to True is equivalent to setting retrievable to False. You can enable this option
        if you want to use a field (for example, margin) as a filter, sorting, or scoring mechanism
        but do not want the field to be visible to the end user. This property must be False for key
        fields. Default is False.
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
    :keyword hidden: A value indicating whether the field will be returned in a search result.
        Setting this to True is equivalent to setting retrievable to False. You can enable this option
        if you want to use a field (for example, margin) as a filter, sorting, or scoring mechanism
        but do not want the field to be visible to the end user. This property must be False for key
        fields. Default is False.
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
    fields: Optional[List[SearchField]] = None,
    **kw  # pylint:disable=unused-argument
) -> SearchField:
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
    return SearchField(**result)


__all__: list[str] = [
    "SearchField",
    "SearchFieldDataType",
    "SimpleField",
    "SearchableField",
    "ComplexField",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
