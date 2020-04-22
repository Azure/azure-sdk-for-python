# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._generated.models import (
    Analyzer,
    Tokenizer,
    DataSource as _DataSource
)


class PatternAnalyzer(Analyzer):
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


class PatternTokenizer(Tokenizer):
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


class DataSource(_DataSource):
    """Represents a datasource definition, which can be used to configure an indexer.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the datasource.
    :type name: str
    :param description: The description of the datasource.
    :type description: str
    :param type: Required. The type of the datasource. Possible values include: 'azuresql',
     'cosmosdb', 'azureblob', 'azuretable', 'mysql'.
    :type type: str or ~search_service_client.models.DataSourceType
    :param credentials: Required. Credentials for the datasource.
    :type credentials: ~search_service_client.models.DataSourceCredentials
    :param container: Required. The data container for the datasource.
    :type container: ~search_service_client.models.DataContainer
    :param data_change_detection_policy: The data change detection policy for the datasource.
    :type data_change_detection_policy: ~search_service_client.models.DataChangeDetectionPolicy
    :param data_deletion_detection_policy: The data deletion detection policy for the datasource.
    :type data_deletion_detection_policy: ~search_service_client.models.DataDeletionDetectionPolicy
    :param e_tag: The ETag of the DataSource.
    :type e_tag: str
    """

    _validation = {
        'name': {'required': True},
        'type': {'required': True},
        'credentials': {'required': True},
        'container': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'credentials': {'key': 'credentials', 'type': 'DataSourceCredentials'},
        'container': {'key': 'container', 'type': 'DataContainer'},
        'data_change_detection_policy': {'key': 'dataChangeDetectionPolicy', 'type': 'DataChangeDetectionPolicy'},
        'data_deletion_detection_policy': {'key': 'dataDeletionDetectionPolicy', 'type': 'DataDeletionDetectionPolicy'},
        'e_tag': {'key': '@odata\\.etag', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(DataSource, self).__init__(**kwargs)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('description', None)
        self.type = kwargs.get('type', None)
        self.credentials = kwargs.get('credentials', None)
        self.container = kwargs.get('container', None)
        self.data_change_detection_policy = kwargs.get('data_change_detection_policy', None)
        self.data_deletion_detection_policy = kwargs.get('data_deletion_detection_policy', None)
        self.e_tag = kwargs.get('e_tag', None)
