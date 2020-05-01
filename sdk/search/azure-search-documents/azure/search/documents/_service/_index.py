# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from .edm import Collection, ComplexType
from ._generated.models import Field

if TYPE_CHECKING:
    from typing import Any, Dict, List

__all__ = ("ComplexField", "SearchableField", "SimpleField")


def SimpleField(
    name,
    type,  # pylint:disable=redefined-builtin
    key=False,
    filterable=False,
    facetable=False,
    sortable=False,
    hidden=False,
):
    # type: (str, str, bool, bool, bool, bool, bool) -> Dict[str, Any]
    """Configure a simple field for an Azure Search Index

    :param name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :type name: str
    :param type: Required. The data type of the field. Possible values include: edm.String,
     edm.Int32, edm.Int64, edm.Double, edm.Boolean, edm.DateTimeOffset,
     edm.GeographyPoint, edm.ComplexType, from `azure.search.documents.edm`.
    :type type: str
    :param key: A value indicating whether the field uniquely identifies documents in the index.
     Exactly one top-level field in each index must be chosen as the key field and it must be of
     type Edm.String. Key fields can be used to look up documents directly and update or delete
     specific documents. Default is False
    :type key: bool
    :param hidden: A value indicating whether the field can be returned in a search result.
     You can enable this option if you want to use a field (for example, margin) as a filter,
     sorting, or scoring mechanism but do not want the field to be visible to the end user. This
     property must be False for key fields. This property can be changed on existing fields.
     Enabling this property does not cause any increase in index storage requirements. Default is
     False.
    :type retrievable: bool
    :param filterable: A value indicating whether to enable the field to be referenced in $filter
     queries. filterable differs from searchable in how strings are handled. Fields of type
     Edm.String or Collection(Edm.String) that are filterable do not undergo word-breaking, so
     comparisons are for exact matches only. For example, if you set such a field f to "sunny day",
     $filter=f eq 'sunny' will find no matches, but $filter=f eq 'sunny day' will. This property
     must be null for complex fields. Default is False
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
     on). Fields of type edm.GeographyPoint or Collection(edm.GeographyPoint) cannot be facetable.
     Default is False.
    :type facetable: bool
    """
    result = {"name": name, "type": type}  # type: Dict[str, Any]
    result["key"] = key
    result["searchable"] = False
    result["filterable"] = filterable
    result["facetable"] = facetable
    result["sortable"] = sortable
    result["retrievable"] = not hidden
    return Field(**result)


def SearchableField(
    name,
    type,  # pylint:disable=redefined-builtin
    key=False,
    searchable=True,
    filterable=False,
    facetable=False,
    sortable=False,
    hidden=False,
    analyzer=None,
    search_analyzer=None,
    index_analyzer=None,
    synonym_maps=None,
):
    # type: (str, str, bool, bool, bool, bool, bool, str, str, str, List[str]) -> Dict[str, Any]
    """Configure a searchable text field for an Azure Search Index

    :param name: Required. The name of the field, which must be unique within the fields collection
     of the index or parent field.
    :type name: str
    :param type: Required. The data type of the field. Possible values include: edm.String
     and Collection(edm.String), from `azure.search.documents.edm`.
    :type type: str
    :param key: A value indicating whether the field uniquely identifies documents in the index.
     Exactly one top-level field in each index must be chosen as the key field and it must be of
     type Edm.String. Key fields can be used to look up documents directly and update or delete
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
    :param analyzer: The name of the analyzer to use for the field. This option can't be set together
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
    :type analyzer: str or ~search_service_client.models.AnalyzerName
    :param search_analyzer: The name of the analyzer used at search time for the field. It must be
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
    :type search_analyzer: str or ~search_service_client.models.AnalyzerName
    :param index_analyzer: The name of the analyzer used at indexing time for the field.
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
    :type index_analyzer: str or ~search_service_client.models.AnalyzerName
    :param synonym_maps: A list of the names of synonym maps to associate with this field. Currently
     only one synonym map per field is supported. Assigning a synonym map to a field ensures that
     query terms targeting that field are expanded at query-time using the rules in the synonym map.
     This attribute can be changed on existing fields.
    :type synonym_maps: list[str]

    """
    result = {"name": name, "type": type}  # type: Dict[str, Any]
    result["key"] = key
    result["searchable"] = searchable
    result["filterable"] = filterable
    result["facetable"] = facetable
    result["sortable"] = sortable
    result["retrievable"] = not hidden
    if analyzer:
        result["analyzer"] = analyzer
    if search_analyzer:
        result["search_analyzer"] = search_analyzer
    if index_analyzer:
        result["index_analyzer"] = index_analyzer
    if synonym_maps:
        result["synonym_maps"] = synonym_maps
    return Field(**result)


def ComplexField(name, fields, collection=False):
    # type: (str, List[Dict[str, Any]], bool) -> Dict[str, Any]
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
    typ = Collection(ComplexType) if collection else ComplexType
    result = {"name": name, "type": typ}  # type: Dict[str, Any]
    result["fields"] = fields
    return Field(**result)
