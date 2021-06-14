# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import msrest.serialization
from .._generated.models import (
    LexicalAnalyzer,
    LexicalTokenizer,
    AnalyzeRequest,
    CustomAnalyzer as _CustomAnalyzer,
    PatternAnalyzer as _PatternAnalyzer,
    PatternTokenizer as _PatternTokenizer,
    SearchResourceEncryptionKey as _SearchResourceEncryptionKey,
    SearchIndexerDataSource as _SearchIndexerDataSource,
    SynonymMap as _SynonymMap,
    DataSourceCredentials,
    AzureActiveDirectoryApplicationCredentials
)

DELIMITER = "|"

class AnalyzeTextOptions(msrest.serialization.Model):
    """Specifies some text and analysis components used to break that text into tokens.

    All required parameters must be populated in order to send to Azure.

    :param text: Required. The text to break into tokens.
    :type text: str
    :param analyzer_name: The name of the analyzer to use to break the given text. If this parameter is
     not specified, you must specify a tokenizer instead. The tokenizer and analyzer parameters are
     mutually exclusive. Possible values include: "ar.microsoft", "ar.lucene", "hy.lucene",
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
    :type analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :param tokenizer_name: The name of the tokenizer to use to break the given text. If this parameter
     is not specified, you must specify an analyzer instead. The tokenizer and analyzer parameters
     are mutually exclusive. Possible values include: "classic", "edgeNGram", "keyword_v2",
     "letter", "lowercase", "microsoft_language_tokenizer", "microsoft_language_stemming_tokenizer",
     "nGram", "path_hierarchy_v2", "pattern", "standard_v2", "uax_url_email", "whitespace".
    :type tokenizer_name: str or ~azure.search.documents.indexes.models.LexicalTokenizerName
    :param token_filters: An optional list of token filters to use when breaking the given text.
     This parameter can only be set when using the tokenizer parameter.
    :type token_filters: list[str or ~azure.search.documents.indexes.models.TokenFilterName]
    :param char_filters: An optional list of character filters to use when breaking the given text.
     This parameter can only be set when using the tokenizer parameter.
    :type char_filters: list[str]
    """

    _validation = {
        'text': {'required': True},
    }

    _attribute_map = {
        'text': {'key': 'text', 'type': 'str'},
        'analyzer_name': {'key': 'analyzerName', 'type': 'str'},
        'tokenizer_name': {'key': 'tokenizerName', 'type': 'str'},
        'token_filters': {'key': 'tokenFilters', 'type': '[str]'},
        'char_filters': {'key': 'charFilters', 'type': '[str]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(AnalyzeTextOptions, self).__init__(**kwargs)
        self.text = kwargs['text']
        self.analyzer_name = kwargs.get('analyzer_name', None)
        self.tokenizer_name = kwargs.get('tokenizer_name', None)
        self.token_filters = kwargs.get('token_filters', None)
        self.char_filters = kwargs.get('char_filters', None)

    def _to_analyze_request(self):
        return AnalyzeRequest(
            text=self.text,
            analyzer=self.analyzer_name,
            tokenizer=self.tokenizer_name,
            token_filters=self.token_filters,
            char_filters=self.char_filters
        )


class CustomAnalyzer(LexicalAnalyzer):
    """Allows you to take control over the process of converting text into indexable/searchable tokens.
    It's a user-defined configuration consisting of a single predefined tokenizer and one or more filters.
    The tokenizer is responsible for breaking text into tokens, and the filters for modifying tokens
    emitted by the tokenizer.

    All required parameters must be populated in order to send to Azure.

    :param odata_type: Required. Identifies the concrete type of the analyzer.Constant filled by
     server.
    :type odata_type: str
    :param name: Required. The name of the analyzer. It must only contain letters, digits, spaces,
     dashes or underscores, can only start and end with alphanumeric characters, and is limited to
     128 characters.
    :type name: str
    :param tokenizer_name: Required. The name of the tokenizer to use to divide continuous text into a
     sequence of tokens, such as breaking a sentence into words. Possible values include: "classic",
     "edgeNGram", "keyword_v2", "letter", "lowercase", "microsoft_language_tokenizer",
     "microsoft_language_stemming_tokenizer", "nGram", "path_hierarchy_v2", "pattern",
     "standard_v2", "uax_url_email", "whitespace".
    :type tokenizer_name: str or ~azure.search.documents.indexes.models.LexicalTokenizerName
    :param token_filters: A list of token filters used to filter out or modify the tokens generated
     by a tokenizer. For example, you can specify a lowercase filter that converts all characters to
     lowercase. The filters are run in the order in which they are listed.
    :type token_filters: list[str or ~azure.search.documents.indexes.models.TokenFilterName]
    :param char_filters: A list of character filters used to prepare input text before it is
     processed by the tokenizer. For instance, they can replace certain characters or symbols. The
     filters are run in the order in which they are listed.
    :type char_filters: list[str]
    """

    _validation = {
        'odata_type': {'required': True},
        'name': {'required': True},
        'tokenizer_name': {'required': True},
    }

    _attribute_map = {
        'odata_type': {'key': '@odata\\.type', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'tokenizer_name': {'key': 'tokenizerName', 'type': 'str'},
        'token_filters': {'key': 'tokenFilters', 'type': '[str]'},
        'char_filters': {'key': 'charFilters', 'type': '[str]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CustomAnalyzer, self).__init__(**kwargs)
        self.odata_type = '#Microsoft.Azure.Search.CustomAnalyzer'
        self.tokenizer_name = kwargs['tokenizer_name']
        self.token_filters = kwargs.get('token_filters', None)
        self.char_filters = kwargs.get('char_filters', None)

    def _to_generated(self):
        return _CustomAnalyzer(
            name=self.name,
            odata_type=self.odata_type,
            tokenizer=self.tokenizer_name,
            token_filters=self.token_filters,
            char_filters=self.char_filters
        )

    @classmethod
    def _from_generated(cls, custom_analyzer):
        if not custom_analyzer:
            return None
        return cls(
            name=custom_analyzer.name,
            odata_type=custom_analyzer.odata_type,
            tokenizer_name=custom_analyzer.tokenizer,
            token_filters=custom_analyzer.token_filters,
            char_filters=custom_analyzer.char_filters
        )

class PatternAnalyzer(LexicalAnalyzer):
    """Flexibly separates text into terms via a regular expression.
    This analyzer is implemented using Apache Lucene.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the analyzer. It must only contain letters, digits, spaces,
     dashes or underscores, can only start and end with alphanumeric characters, and is limited to
     128 characters.
    :type name: str
    :param lower_case_terms: A value indicating whether terms should be lower-cased. Default is
     true.
    :type lower_case_terms: bool
    :param pattern: A regular expression to match token separators. Default is an
     expression that matches one or more white space characters.
    :type pattern: str
    :param flags: List of regular expression flags. Possible values of each flag include: 'CANON_EQ',
     'CASE_INSENSITIVE', 'COMMENTS', 'DOTALL', 'LITERAL', 'MULTILINE', 'UNICODE_CASE', 'UNIX_LINES'.
    :type flags: list[str] or list[~search_service_client.models.RegexFlags]
    :param stopwords: A list of stopwords.
    :type stopwords: list[str]
    """

    _validation = {"odata_type": {"required": True}, "name": {"required": True}}

    _attribute_map = {
        "odata_type": {"key": "@odata\\.type", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "lower_case_terms": {"key": "lowercase", "type": "bool"},
        "pattern": {"key": "pattern", "type": "str"},
        "flags": {"key": "flags", "type": "[str]"},
        "stopwords": {"key": "stopwords", "type": "[str]"},
    }

    def __init__(self, **kwargs):
        super(PatternAnalyzer, self).__init__(**kwargs)
        self.odata_type = "#Microsoft.Azure.Search.PatternAnalyzer"
        self.lower_case_terms = kwargs.get("lower_case_terms", True)
        self.pattern = kwargs.get("pattern", r"\W+")
        self.flags = kwargs.get("flags", None)
        self.stopwords = kwargs.get("stopwords", None)

    def _to_generated(self):
        if not self.flags:
            flags = None
        else:
            flags = DELIMITER.join(self.flags)
        return _PatternAnalyzer(
            name=self.name,
            lower_case_terms=self.lower_case_terms,
            pattern=self.pattern,
            flags=flags,
            stopwords=self.stopwords,
        )

    @classmethod
    def _from_generated(cls, pattern_analyzer):
        if not pattern_analyzer:
            return None
        if not pattern_analyzer.flags:
            flags = None
        else:
            flags = pattern_analyzer.flags.split(DELIMITER)
        return cls(
            name=pattern_analyzer.name,
            lower_case_terms=pattern_analyzer.lower_case_terms,
            pattern=pattern_analyzer.pattern,
            flags=flags,
            stopwords=pattern_analyzer.stopwords,
        )

class PatternTokenizer(LexicalTokenizer):
    """Tokenizer that uses regex pattern matching to construct distinct tokens.
    This tokenizer is implemented using Apache Lucene.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the tokenizer. It must only contain letters, digits, spaces,
     dashes or underscores, can only start and end with alphanumeric characters, and is limited to
     128 characters.
    :type name: str
    :param pattern: A regular expression to match token separators. Default is an
     expression that matches one or more white space characters.
    :type pattern: str
    :param flags: List of regular expression flags. Possible values of each flag include: 'CANON_EQ',
     'CASE_INSENSITIVE', 'COMMENTS', 'DOTALL', 'LITERAL', 'MULTILINE', 'UNICODE_CASE', 'UNIX_LINES'.
    :type flags: list[str] or list[~search_service_client.models.RegexFlags]
    :param group: The zero-based ordinal of the matching group in the regular expression to
     extract into tokens. Use -1 if you want to use the entire pattern to split the input into
     tokens, irrespective of matching groups. Default is -1.
    :type group: int
    """

    _validation = {"odata_type": {"required": True}, "name": {"required": True}}

    _attribute_map = {
        "odata_type": {"key": "@odata\\.type", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "pattern": {"key": "pattern", "type": "str"},
        "flags": {"key": "flags", "type": "[str]"},
        "group": {"key": "group", "type": "int"},
    }

    def __init__(self, **kwargs):
        super(PatternTokenizer, self).__init__(**kwargs)
        self.odata_type = "#Microsoft.Azure.Search.PatternTokenizer"
        self.pattern = kwargs.get("pattern", r"\W+")
        self.flags = kwargs.get("flags", None)
        self.group = kwargs.get("group", -1)

    def _to_generated(self):
        if not self.flags:
            flags = None
        else:
            flags = DELIMITER.join(self.flags)
        return _PatternTokenizer(
            name=self.name,
            pattern=self.pattern,
            flags=flags,
            group=self.group,
        )

    @classmethod
    def _from_generated(cls, pattern_tokenizer):
        if not pattern_tokenizer:
            return None
        if not pattern_tokenizer.flags:
            flags = None
        else:
            flags = pattern_tokenizer.flags.split(DELIMITER)
        return cls(
            name=pattern_tokenizer.name,
            pattern=pattern_tokenizer.pattern,
            flags=flags,
            group=pattern_tokenizer.group,
        )

class SearchResourceEncryptionKey(msrest.serialization.Model):
    """A customer-managed encryption key in Azure Key Vault. Keys that you create and manage can be
    used to encrypt or decrypt data-at-rest in Azure Cognitive Search, such as indexes and synonym maps.

    All required parameters must be populated in order to send to Azure.

    :param key_name: Required. The name of your Azure Key Vault key to be used to encrypt your data
     at rest.
    :type key_name: str
    :param key_version: Required. The version of your Azure Key Vault key to be used to encrypt
     your data at rest.
    :type key_version: str
    :param vault_uri: Required. The URI of your Azure Key Vault, also referred to as DNS name, that
     contains the key to be used to encrypt your data at rest. An example URI might be https://my-
     keyvault-name.vault.azure.net.
    :type vault_uri: str
    :param application_id: Required. An AAD Application ID that was granted the required access
     permissions to the Azure Key Vault that is to be used when encrypting your data at rest. The
     Application ID should not be confused with the Object ID for your AAD Application.
    :type application_id: str
    :param application_secret: The authentication key of the specified AAD application.
    :type application_secret: str
    """

    _validation = {
        'key_name': {'required': True},
        'key_version': {'required': True},
        'vault_uri': {'required': True},
    }

    _attribute_map = {
        'key_name': {'key': 'keyVaultKeyName', 'type': 'str'},
        'key_version': {'key': 'keyVaultKeyVersion', 'type': 'str'},
        'vault_uri': {'key': 'keyVaultUri', 'type': 'str'},
        'application_id': {'key': 'applicationId', 'type': 'str'},
        'application_secret': {'key': 'applicationSecret', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SearchResourceEncryptionKey, self).__init__(**kwargs)
        self.key_name = kwargs['key_name']
        self.key_version = kwargs['key_version']
        self.vault_uri = kwargs['vault_uri']
        self.application_id = kwargs.get('application_id', None)
        self.application_secret = kwargs.get('application_secret', None)

    def _to_generated(self):
        if self.application_id and self.application_secret:
            access_credentials = AzureActiveDirectoryApplicationCredentials(
                application_id=self.application_id,
                application_secret=self.application_secret
            )
        else:
            access_credentials = None
        return _SearchResourceEncryptionKey(
            key_name=self.key_name,
            key_version=self.key_version,
            vault_uri=self.vault_uri,
            access_credentials=access_credentials
        )

    @classmethod
    def _from_generated(cls, search_resource_encryption_key):
        if not search_resource_encryption_key:
            return None
        if search_resource_encryption_key.access_credentials:
            application_id = search_resource_encryption_key.access_credentials.application_id
            application_secret = search_resource_encryption_key.access_credentials.application_secret
        else:
            application_id = None
            application_secret = None
        return cls(
            key_name=search_resource_encryption_key.key_name,
            key_version=search_resource_encryption_key.key_version,
            vault_uri=search_resource_encryption_key.vault_uri,
            application_id=application_id,
            application_secret=application_secret
        )

class SynonymMap(msrest.serialization.Model):
    """Represents a synonym map definition.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the synonym map.
    :type name: str
    :ivar format: Required. The format of the synonym map. Only the 'solr' format is currently
     supported. Default value: "solr".
    :vartype format: str
    :param synonyms: Required. A series of synonym rules in the specified synonym map format. The
     rules must be separated by newlines.
    :type synonyms: list[str]
    :param encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your data when you
     want full assurance that no one, not even Microsoft, can decrypt your data in Azure Cognitive
     Search. Once you have encrypted your data, it will always remain encrypted. Azure Cognitive
     Search will ignore attempts to set this property to null. You can change this property as
     needed if you want to rotate your encryption key; Your data will be unaffected. Encryption with
     customer-managed keys is not available for free search services, and is only available for paid
     services created on or after January 1, 2019.
    :type encryption_key: ~azure.search.documents.indexes.models.SearchResourceEncryptionKey
    :param e_tag: The ETag of the synonym map.
    :type e_tag: str
    """

    _validation = {
        'name': {'required': True},
        'format': {'required': True, 'constant': True},
        'synonyms': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'format': {'key': 'format', 'type': 'str'},
        'synonyms': {'key': 'synonyms', 'type': '[str]'},
        'encryption_key': {'key': 'encryptionKey', 'type': 'SearchResourceEncryptionKey'},
        'e_tag': {'key': '@odata\\.etag', 'type': 'str'},
    }

    format = "solr"

    def __init__(
        self,
        **kwargs
    ):
        super(SynonymMap, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.synonyms = kwargs['synonyms']
        self.encryption_key = kwargs.get('encryption_key', None)
        self.e_tag = kwargs.get('e_tag', None)

    def _to_generated(self):
        return _SynonymMap(
            name=self.name,
            synonyms="\n".join(self.synonyms),
            encryption_key=self.encryption_key._to_generated() if self.encryption_key else None, # pylint:disable=protected-access
            e_tag=self.e_tag
        )

    @classmethod
    def _from_generated(cls, synonym_map):
        if not synonym_map:
            return None
        return cls(
            name=synonym_map.name,
            synonyms=synonym_map.synonyms.split("\n"),
            # pylint:disable=protected-access
            encryption_key=SearchResourceEncryptionKey._from_generated(synonym_map.encryption_key),
            e_tag=synonym_map.e_tag
        )

class SearchIndexerDataSourceConnection(msrest.serialization.Model):
    """Represents a datasource connection definition, which can be used to configure an indexer.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the datasource connection.
    :type name: str
    :param description: The description of the datasource connection.
    :type description: str
    :param type: Required. The type of the datasource connection. Possible values include: "azuresql",
     "cosmosdb", "azureblob", "azuretable", "mysql", "adlsgen2".
    :type type: str or ~azure.search.documents.indexes.models.SearchIndexerDataSourceType
    :param connection_string: The connection string for the datasource connection.
    :type connection_string: str
    :param container: Required. The data container for the datasource connection.
    :type container: ~azure.search.documents.indexes.models.SearchIndexerDataContainer
    :param data_change_detection_policy: The data change detection policy for the datasource connection.
    :type data_change_detection_policy: ~azure.search.documents.models.DataChangeDetectionPolicy
    :param data_deletion_detection_policy: The data deletion detection policy for the datasource connection.
    :type data_deletion_detection_policy:
     ~azure.search.documents.models.DataDeletionDetectionPolicy
    :param e_tag: The ETag of the data source.
    :type e_tag: str
    """

    _validation = {
        'name': {'required': True},
        'type': {'required': True},
        'connection_string': {'required': True},
        'container': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'connection_string': {'key': 'connectionString', 'type': 'str'},
        'container': {'key': 'container', 'type': 'SearchIndexerDataContainer'},
        'data_change_detection_policy': {'key': 'dataChangeDetectionPolicy', 'type': 'DataChangeDetectionPolicy'},
        'data_deletion_detection_policy': {'key': 'dataDeletionDetectionPolicy', 'type': 'DataDeletionDetectionPolicy'},
        'e_tag': {'key': '@odata\\.etag', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SearchIndexerDataSourceConnection, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.description = kwargs.get('description', None)
        self.type = kwargs['type']
        self.connection_string = kwargs['connection_string']
        self.container = kwargs['container']
        self.data_change_detection_policy = kwargs.get('data_change_detection_policy', None)
        self.data_deletion_detection_policy = kwargs.get('data_deletion_detection_policy', None)
        self.e_tag = kwargs.get('e_tag', None)

    def _to_generated(self):
        if self.connection_string is None or self.connection_string == "":
            connection_string = "<unchanged>"
        else:
            connection_string = self.connection_string
        credentials = DataSourceCredentials(
            connection_string=connection_string
        )
        return _SearchIndexerDataSource(
            name=self.name,
            description=self.description,
            type=self.type,
            credentials=credentials,
            container=self.container,
            data_change_detection_policy=self.data_change_detection_policy,
            data_deletion_detection_policy=self.data_deletion_detection_policy,
            e_tag=self.e_tag
        )

    @classmethod
    def _from_generated(cls, search_indexer_data_source):
        if not search_indexer_data_source:
            return None
        connection_string = search_indexer_data_source.credentials.connection_string \
            if search_indexer_data_source.credentials else None
        return cls(
            name=search_indexer_data_source.name,
            description=search_indexer_data_source.description,
            type=search_indexer_data_source.type,
            connection_string=connection_string,
            container=search_indexer_data_source.container,
            data_change_detection_policy=search_indexer_data_source.data_change_detection_policy,
            data_deletion_detection_policy=search_indexer_data_source.data_deletion_detection_policy,
            e_tag=search_indexer_data_source.e_tag
        )


def pack_analyzer(analyzer):
    if not analyzer:
        return None
    if isinstance(analyzer, (PatternAnalyzer, CustomAnalyzer)):
        return analyzer._to_generated() # pylint:disable=protected-access
    return analyzer


def unpack_analyzer(analyzer):
    if not analyzer:
        return None
    if isinstance(analyzer, _PatternAnalyzer):
        return PatternAnalyzer._from_generated(analyzer)    # pylint:disable=protected-access
    if isinstance(analyzer, _CustomAnalyzer):
        return CustomAnalyzer._from_generated(analyzer) # pylint:disable=protected-access
    return analyzer
