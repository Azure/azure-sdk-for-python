# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._generated.models import LexicalAnalyzer, LexicalTokenizer
import msrest.serialization


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
    :type synonyms: str
    :param encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your data when you
     want full assurance that no one, not even Microsoft, can decrypt your data in Azure Cognitive
     Search. Once you have encrypted your data, it will always remain encrypted. Azure Cognitive
     Search will ignore attempts to set this property to null. You can change this property as
     needed if you want to rotate your encryption key; Your data will be unaffected. Encryption with
     customer-managed keys is not available for free search services, and is only available for paid
     services created on or after January 1, 2019.
    :type encryption_key: ~azure.search.documents.models.SearchResourceEncryptionKey
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