# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import TYPE_CHECKING
import six
from azure.core import MatchConditions
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceNotModifiedError,
)
from ._generated.models import (
    AzureActiveDirectoryApplicationCredentials,
    CustomAnalyzer as _CustomAnalyzer,
    DataSourceCredentials,
    SearchIndexerDataSource as _SearchIndexerDataSource,
    SearchResourceEncryptionKey as _SearchResourceEncryptionKey,
    SynonymMap as _SynonymMap,
    SearchField as _SearchField,
    SearchIndex as _SearchIndex,
    PatternAnalyzer as _PatternAnalyzer,
    PatternTokenizer as _PatternTokenizer,
)
from ._models import (
    CustomAnalyzer,
    PatternAnalyzer,
    PatternTokenizer,
    SynonymMap,
    SearchIndexerDataSourceConnection,
    SearchResourceEncryptionKey,
)
from ._index import (
    SearchField,
    SearchIndex,
)

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Optional

DELIMITER = "|"


def quote_etag(etag):
    if not etag or etag == "*":
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'


def prep_if_match(etag, match_condition):
    # type: (str, MatchConditions) -> Optional[str]
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None


def prep_if_none_match(etag, match_condition):
    # type: (str, MatchConditions) -> Optional[str]
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None


def pack_custom_analyzer(custom_analyzer):
    # type: (CustomAnalyzer) -> _CustomAnalyzer
    return _CustomAnalyzer(
        name=custom_analyzer.name,
        odata_type=custom_analyzer.odata_type,
        tokenizer=custom_analyzer.tokenizer_name,
        token_filters=custom_analyzer.token_filters,
        char_filters=custom_analyzer.char_filters
    )


def unpack_custom_analyzer(custom_analyzer):
    # type: (_CustomAnalyzer) -> CustomAnalyzer
    return CustomAnalyzer(
        name=custom_analyzer.name,
        odata_type=custom_analyzer.odata_type,
        tokenizer_name=custom_analyzer.tokenizer,
        token_filters=custom_analyzer.token_filters,
        char_filters=custom_analyzer.char_filters
    )


def pack_pattern_analyzer(pattern_analyzer):
    # type: (PatternAnalyzer) -> _PatternAnalyzer
    if not pattern_analyzer.flags:
        flags = None
    else:
        flags = DELIMITER.join(pattern_analyzer.flags)
    return _PatternAnalyzer(
        name=pattern_analyzer.name,
        lower_case_terms=pattern_analyzer.lower_case_terms,
        pattern=pattern_analyzer.pattern,
        flags=flags,
        stopwords=pattern_analyzer.stopwords,
    )


def unpack_pattern_analyzer(pattern_analyzer):
    # type: (_PatternAnalyzer) -> PatternAnalyzer
    if not pattern_analyzer.flags:
        flags = None
    else:
        flags = pattern_analyzer.flags.split(DELIMITER)
    return PatternAnalyzer(
        name=pattern_analyzer.name,
        lower_case_terms=pattern_analyzer.lower_case_terms,
        pattern=pattern_analyzer.pattern,
        flags=flags,
        stopwords=pattern_analyzer.stopwords,
    )


def pack_analyzer(analyzer):
    if not analyzer:
        return None
    if isinstance(analyzer, PatternAnalyzer):
        return pack_pattern_analyzer(analyzer)
    if isinstance(analyzer, CustomAnalyzer):
        return pack_custom_analyzer(analyzer)
    return analyzer


def unpack_analyzer(analyzer):
    if not analyzer:
        return None
    if isinstance(analyzer, _PatternAnalyzer):
        return unpack_pattern_analyzer(analyzer)
    if isinstance(analyzer, _CustomAnalyzer):
        return unpack_custom_analyzer(analyzer)
    return analyzer


def pack_pattern_tokenizer(pattern_tokenizer):
    # type: (PatternTokenizer) -> _PatternTokenizer
    if not pattern_tokenizer.flags:
        flags = None
    else:
        flags = DELIMITER.join(pattern_tokenizer.flags)
    return _PatternTokenizer(
        name=pattern_tokenizer.name,
        pattern=pattern_tokenizer.pattern,
        flags=flags,
        group=pattern_tokenizer.group,
    )


def unpack_pattern_tokenizer(pattern_tokenizer):
    # type: (PatternTokenizer) -> PatternTokenizer
    if not pattern_tokenizer.flags:
        flags = None
    else:
        flags = pattern_tokenizer.flags.split(DELIMITER)
    return PatternTokenizer(
        name=pattern_tokenizer.name,
        pattern=pattern_tokenizer.pattern,
        flags=flags,
        group=pattern_tokenizer.group,
    )


def pack_search_index(search_index):
    # type: (SearchIndex) -> _SearchIndex
    if not search_index:
        return None
    if search_index.analyzers:
        analyzers = [
            pack_analyzer(x)  # type: ignore
            for x in search_index.analyzers
        ]  # mypy: ignore
    else:
        analyzers = None
    if search_index.tokenizers:
        tokenizers = [
            pack_pattern_tokenizer(x)  # type: ignore
            if isinstance(x, PatternTokenizer)
            else x
            for x in search_index.tokenizers
        ]
    else:
        tokenizers = None
    if search_index.fields:
        fields = [pack_search_field(x) for x in search_index.fields]
    else:
        fields = None
    return _SearchIndex(
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
        encryption_key=unpack_search_resource_encryption_key(search_index.encryption_key),
        similarity=search_index.similarity,
        e_tag=search_index.e_tag
    )


def unpack_search_index(search_index):
    # type: (_SearchIndex) -> SearchIndex
    if not search_index:
        return None
    if search_index.analyzers:
        analyzers = [
            unpack_analyzer(x)  # type: ignore
            for x in search_index.analyzers
        ]
    else:
        analyzers = None
    if search_index.tokenizers:
        tokenizers = [
            unpack_pattern_tokenizer(x)  # type: ignore
            if isinstance(x, _PatternTokenizer)
            else x
            for x in search_index.tokenizers
        ]
    else:
        tokenizers = None
    if search_index.fields:
        fields = [unpack_search_field(x) for x in search_index.fields]
    else:
        fields = None
    return SearchIndex(
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
        encryption_key=unpack_search_resource_encryption_key(search_index.encryption_key),
        similarity=search_index.similarity,
        e_tag=search_index.e_tag
    )


def pack_synonym_map(synonym_map):
    # type: (SynonymMap) -> _SynonymMap
    return _SynonymMap(
        name=synonym_map.name,
        synonyms="\n".join(synonym_map.synonyms),
        encryption_key=pack_search_resource_encryption_key(synonym_map.encryption_key),
        e_tag=synonym_map.e_tag
    )


def unpack_synonym_map(synonym_map):
    # type: (_SynonymMap) -> SynonymMap
    return SynonymMap(
        name=synonym_map.name,
        synonyms=synonym_map.synonyms.split("\n"),
        encryption_key=unpack_search_resource_encryption_key(synonym_map.encryption_key),
        e_tag=synonym_map.e_tag
    )


def pack_search_resource_encryption_key(search_resource_encryption_key):
    # type: (SearchResourceEncryptionKey) -> _SearchResourceEncryptionKey
    if not search_resource_encryption_key:
        return None
    if search_resource_encryption_key.application_id and search_resource_encryption_key.application_secret:
        access_credentials = AzureActiveDirectoryApplicationCredentials(
            application_id=search_resource_encryption_key.application_id,
            application_secret=search_resource_encryption_key.application_secret
        )
    else:
        access_credentials = None
    return _SearchResourceEncryptionKey(
        key_name=search_resource_encryption_key.key_name,
        key_version=search_resource_encryption_key.key_version,
        vault_uri=search_resource_encryption_key.vault_uri,
        access_credentials=access_credentials
    )


def unpack_search_resource_encryption_key(search_resource_encryption_key):
    # type: (_SearchResourceEncryptionKey) -> SearchResourceEncryptionKey
    if not search_resource_encryption_key:
        return None
    if search_resource_encryption_key.access_credentials:
        application_id = search_resource_encryption_key.access_credentials.application_id
        application_secret = search_resource_encryption_key.access_credentials.application_secret
    else:
        application_id = None
        application_secret = None
    return SearchResourceEncryptionKey(
        key_name=search_resource_encryption_key.key_name,
        key_version=search_resource_encryption_key.key_version,
        vault_uri=search_resource_encryption_key.vault_uri,
        application_id=application_id,
        application_secret=application_secret
    )


def pack_search_indexer_data_source(search_indexer_data_source):
    # type: (SearchIndexerDataSourceConnection) -> _SearchIndexerDataSource
    if not search_indexer_data_source:
        return None
    if search_indexer_data_source.connection_string is None or search_indexer_data_source.connection_string == "":
        connection_string = "<unchanged>"
    else:
        connection_string = search_indexer_data_source.connection_string
    credentials = DataSourceCredentials(
        connection_string=connection_string
    )
    return _SearchIndexerDataSource(
        name=search_indexer_data_source.name,
        description=search_indexer_data_source.description,
        type=search_indexer_data_source.type,
        credentials=credentials,
        container=search_indexer_data_source.container,
        data_change_detection_policy=search_indexer_data_source.data_change_detection_policy,
        data_deletion_detection_policy=search_indexer_data_source.data_deletion_detection_policy,
        e_tag=search_indexer_data_source.e_tag
    )


def unpack_search_indexer_data_source(search_indexer_data_source):
    # type: (_SearchIndexerDataSource) -> SearchIndexerDataSourceConnection
    if not search_indexer_data_source:
        return None
    connection_string = search_indexer_data_source.credentials.connection_string \
            if search_indexer_data_source.credentials else None
    return SearchIndexerDataSourceConnection(
        name=search_indexer_data_source.name,
        description=search_indexer_data_source.description,
        type=search_indexer_data_source.type,
        connection_string=connection_string,
        container=search_indexer_data_source.container,
        data_change_detection_policy=search_indexer_data_source.data_change_detection_policy,
        data_deletion_detection_policy=search_indexer_data_source.data_deletion_detection_policy,
        e_tag=search_indexer_data_source.e_tag
    )


def get_access_conditions(model, match_condition=MatchConditions.Unconditionally):
    # type: (Any, MatchConditions) -> Tuple[Dict[int, Any], Dict[str, bool]]
    error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError}

    if isinstance(model, six.string_types):
        if match_condition is not MatchConditions.Unconditionally:
            raise ValueError("A model must be passed to use access conditions")
        return (error_map, {})

    try:
        if_match = prep_if_match(model.e_tag, match_condition)
        if_none_match = prep_if_none_match(model.e_tag, match_condition)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[304] = ResourceNotModifiedError
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        return (error_map, dict(if_match=if_match, if_none_match=if_none_match))
    except AttributeError:
        raise ValueError("Unable to get e_tag from the model")


def normalize_endpoint(endpoint):
    try:
        if not endpoint.lower().startswith('http'):
            endpoint = "https://" + endpoint
        elif not endpoint.lower().startswith('https'):
            raise ValueError("Bearer token authentication is not permitted for non-TLS protected (non-https) URLs.")
        return endpoint
    except AttributeError:
        raise ValueError("Endpoint must be a string.")


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
            synonym_maps=synonym_map_names,
            fields=fields
        )
    fields = [pack_search_field(x) for x in search_field.fields] \
        if search_field.fields else None
    retrievable = not search_field.hidden if search_field.hidden is not None else None
    return _SearchField(
        name=search_field.name,
        type=search_field.type,
        key=search_field.key,
        retrievable=retrievable,
        searchable=search_field.searchable,
        filterable=search_field.filterable,
        sortable=search_field.sortable,
        facetable=search_field.facetable,
        analyzer=search_field.analyzer_name,
        search_analyzer=search_field.search_analyzer_name,
        index_analyzer=search_field.index_analyzer_name,
        synonym_maps=search_field.synonym_map_names,
        fields=fields
    )


def unpack_search_field(search_field):
    # type: (_SearchField) -> SearchField
    if not search_field:
        return None
    fields = [unpack_search_field(x) for x in search_field.fields] \
        if search_field.fields else None
    hidden = not search_field.retrievable if search_field.retrievable is not None else None
    return SearchField(
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
        synonym_map_names=search_field.synonym_maps,
        fields=fields
    )
