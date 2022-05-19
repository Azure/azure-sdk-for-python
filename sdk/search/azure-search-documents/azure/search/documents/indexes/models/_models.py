# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
import msrest.serialization
from azure.core import CaseInsensitiveEnumMeta
from .._generated.models import (
    LexicalAnalyzer,
    LexicalTokenizer,
    AnalyzeRequest,
    CustomAnalyzer as _CustomAnalyzer,
    EntityRecognitionSkill as _EntityRecognitionSkillV1,
    EntityRecognitionSkillV3 as _EntityRecognitionSkillV3,
    PatternAnalyzer as _PatternAnalyzer,
    PatternTokenizer as _PatternTokenizer,
    SearchResourceEncryptionKey as _SearchResourceEncryptionKey,
    SearchIndexerDataSource as _SearchIndexerDataSource,
    SearchIndexerSkill,
    SearchIndexerSkillset as _SearchIndexerSkillset,
    SentimentSkill as _SentimentSkillV1,
    SentimentSkillV3 as _SentimentSkillV3,
    SynonymMap as _SynonymMap,
    DataSourceCredentials,
    AzureActiveDirectoryApplicationCredentials,
)


DELIMITER = "|"


class SearchIndexerSkillset(_SearchIndexerSkillset):
    """A list of skills.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the skillset.
    :paramtype name: str
    :keyword description: The description of the skillset.
    :paramtype description: str
    :keyword skills: Required. A list of skills in the skillset.
    :paramtype skills: list[~azure.search.documents.indexes.models.SearchIndexerSkill]
    :keyword cognitive_services_account: Details about cognitive services to be used when running
     skills.
    :paramtype cognitive_services_account:
     ~azure.search.documents.indexes.models.CognitiveServicesAccount
    :keyword knowledge_store: Definition of additional projections to azure blob, table, or files, of
     enriched data.
    :paramtype knowledge_store: ~azure.search.documents.indexes.models.SearchIndexerKnowledgeStore
    :keyword e_tag: The ETag of the skillset.
    :paramtype e_tag: str
    :keyword encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your skillset
     definition when you want full assurance that no one, not even Microsoft, can decrypt your
     skillset definition in Azure Cognitive Search. Once you have encrypted your skillset
     definition, it will always remain encrypted. Azure Cognitive Search will ignore attempts to set
     this property to null. You can change this property as needed if you want to rotate your
     encryption key; Your skillset definition will be unaffected. Encryption with customer-managed
     keys is not available for free search services, and is only available for paid services created
     on or after January 1, 2019.
    :paramtype encryption_key: ~azure.search.documents.indexes.models.SearchResourceEncryptionKey
    """

    def __init__(
        self,
        **kwargs
    ):
        super(SearchIndexerSkillset, self).__init__(**kwargs)

    def _to_generated(self):
        generated_skills = []
        for skill in self.skills:
            if hasattr(skill, '_to_generated'):
                generated_skills.append(skill._to_generated()) # pylint:disable=protected-access
            else:
                generated_skills.append(skill)
        assert len(generated_skills) == len(self.skills)
        return _SearchIndexerSkillset(
            name=getattr(self, 'name', None),
            description=getattr(self, 'description', None),
            skills=generated_skills,
            cognitive_services_account=getattr(self, 'cognitive_services_account', None),
            knowledge_store=getattr(self, 'knowledge_store', None),
            e_tag=getattr(self, 'e_tag', None),
            encryption_key=getattr(self, 'encryption_key', None)
        )

    @classmethod
    def _from_generated(cls, skillset):
        custom_skills = []
        for skill in skillset.skills:
            skill_cls = type(skill)
            if skill_cls in [_EntityRecognitionSkillV1, _EntityRecognitionSkillV3]:
                custom_skills.append(EntityRecognitionSkill._from_generated(skill)) # pylint:disable=protected-access
            elif skill_cls in [_SentimentSkillV1, _SentimentSkillV3]:
                custom_skills.append(SentimentSkill._from_generated(skill)) # pylint:disable=protected-access
            else:
                custom_skills.append(skill)
        assert len(skillset.skills) == len(custom_skills)
        kwargs = skillset.as_dict()
        kwargs['skills'] = custom_skills
        return cls(**kwargs)


class EntityRecognitionSkillVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the Entity Recognition skill version to use."""

    #: Use Entity Recognition skill V1.
    V1 = "#Microsoft.Skills.Text.EntityRecognitionSkill"
    #: Use Entity Recognition skill V3.
    V3 = "#Microsoft.Skills.Text.V3.EntityRecognitionSkill"
    #: Use latest version of Entity Recognition skill.
    LATEST = "#Microsoft.Skills.Text.V3.EntityRecognitionSkill"


class EntityRecognitionSkill(SearchIndexerSkill):
    """Using the Text Analytics API, extracts entities of different types from text.

    All required parameters must be populated in order to send to Azure.

    :keyword odata_type: Required. Identifies the concrete type of the skill.Constant filled by
     server.
    :paramtype odata_type: str
    :keyword name: The name of the skill which uniquely identifies it within the skillset. A skill
     with no name defined will be given a default name of its 1-based index in the skills array,
     prefixed with the character '#'.
    :paramtype name: str
    :keyword description: The description of the skill which describes the inputs, outputs, and usage
     of the skill.
    :paramtype description: str
    :keyword context: Represents the level at which operations take place, such as the document root
     or document content (for example, /document or /document/content). The default is /document.
    :paramtype context: str
    :keyword inputs: Required. Inputs of the skills could be a column in the source data set, or the
     output of an upstream skill.
    :paramtype inputs: list[~azure.search.documents.indexes.models.InputFieldMappingEntry]
    :keyword outputs: Required. The output of a skill is either a field in a search index, or a value
     that can be consumed as an input by another skill.
    :paramtype outputs: list[~azure.search.documents.indexes.models.OutputFieldMappingEntry]
    :keyword categories: A list of entity categories that should be extracted.
    :paramtype categories: list[str or ~azure.search.documents.indexes.models.EntityCategory]
    :keyword default_language_code: A value indicating which language code to use. Default is en.
     Possible values include: "ar", "cs", "zh-Hans", "zh-Hant", "da", "nl", "en", "fi", "fr", "de",
     "el", "hu", "it", "ja", "ko", "no", "pl", "pt-PT", "pt-BR", "ru", "es", "sv", "tr".
    :paramtype default_language_code: str or
     ~azure.search.documents.indexes.models.EntityRecognitionSkillLanguage
    :keyword include_typeless_entities: Determines whether or not to include entities which are well
     known but don't conform to a pre-defined type. If this configuration is not set (default), set
     to null or set to false, entities which don't conform to one of the pre-defined types will not
     be surfaced. Only valid for skill version 1.
    :paramtype include_typeless_entities: bool
    :keyword minimum_precision: A value between 0 and 1 that be used to only include entities whose
     confidence score is greater than the value specified. If not set (default), or if explicitly
     set to null, all entities will be included.
    :paramtype minimum_precision: float
    :keyword model_version: The version of the model to use when calling the Text Analytics service.
     It will default to the latest available when not specified. We recommend you do not specify
     this value unless absolutely necessary. Only valid from skill version 3.
    :paramtype model_version: str
    :keyword skill_version: The version of the skill to use when calling the Text Analytics service.
     It will default to V1 when not specified.
    :paramtype skill_version: ~azure.search.documents.indexes.models.EntityRecognitionSkillVersion
    """

    _validation = {
        'odata_type': {'required': True},
        'inputs': {'required': True},
        'outputs': {'required': True},
        'minimum_precision': {'maximum': 1, 'minimum': 0},
    }

    _attribute_map = {
        'odata_type': {'key': '@odata\\.type', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'context': {'key': 'context', 'type': 'str'},
        'inputs': {'key': 'inputs', 'type': '[InputFieldMappingEntry]'},
        'outputs': {'key': 'outputs', 'type': '[OutputFieldMappingEntry]'},
        'categories': {'key': 'categories', 'type': '[str]'},
        'default_language_code': {'key': 'defaultLanguageCode', 'type': 'str'},
        'include_typeless_entities': {'key': 'includeTypelessEntities', 'type': 'bool'},
        'minimum_precision': {'key': 'minimumPrecision', 'type': 'float'},
        'model_version': {'key': 'modelVersion', 'type': 'str'},
        'skill_version': {'key': 'skillVersion', 'type': 'str'}
    }

    def __init__(
        self,
        **kwargs
    ):
        # pop skill_version from kwargs to avoid warning in msrest
        skill_version = kwargs.pop('skill_version', EntityRecognitionSkillVersion.V1)

        super(EntityRecognitionSkill, self).__init__(**kwargs)
        self.skill_version = skill_version
        self.odata_type = self.skill_version  # type: str
        self.categories = kwargs.get('categories', None)
        self.default_language_code = kwargs.get('default_language_code', None)
        self.minimum_precision = kwargs.get('minimum_precision', None)
        self.include_typeless_entities = kwargs.get('include_typeless_entities', None)
        self.model_version = kwargs.get('model_version', None)


    def _to_generated(self):
        if self.skill_version == EntityRecognitionSkillVersion.V1:
            return _EntityRecognitionSkillV1(
                inputs=self.inputs,
                outputs=self.outputs,
                name=self.name,
                odata_type=self.odata_type,
                categories=self.categories,
                default_language_code=self.default_language_code,
                include_typeless_entities=self.include_typeless_entities,
                minimum_precision=self.minimum_precision
            )
        if self.skill_version in [EntityRecognitionSkillVersion.V3, EntityRecognitionSkillVersion.LATEST]:
            return _EntityRecognitionSkillV3(
                inputs=self.inputs,
                outputs=self.outputs,
                name=self.name,
                odata_type=self.odata_type,
                categories=self.categories,
                default_language_code=self.default_language_code,
                minimum_precision=self.minimum_precision,
                model_version=self.model_version
            )
        return None

    @classmethod
    def _from_generated(cls, skill):
        if not skill:
            return None
        kwargs = skill.as_dict()
        if isinstance(skill, _EntityRecognitionSkillV1):
            return EntityRecognitionSkill(
                skill_version=EntityRecognitionSkillVersion.V1,
                **kwargs
            )
        if isinstance(skill, _EntityRecognitionSkillV3):
            return EntityRecognitionSkill(
                skill_version=EntityRecognitionSkillVersion.V3,
                **kwargs
            )
        return None


class SentimentSkillVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """ Specifies the Sentiment Skill version to use."""

    #: Use Sentiment skill V1.
    V1 = "#Microsoft.Skills.Text.SentimentSkill"
    #: Use Sentiment skill V3.
    V3 = "#Microsoft.Skills.Text.V3.SentimentSkill"
    #: Use latest version of Sentiment skill.
    LATEST = "#Microsoft.Skills.Text.V3.SentimentSkill"


class SentimentSkill(SearchIndexerSkill):
    """V1: Text analytics positive-negative sentiment analysis, scored as a floating point value in a range of zero
    to 1.
    V3: Using the Text Analytics API, evaluates unstructured text and for each record, provides sentiment labels
    (such as "negative", "neutral" and "positive") based on the highest confidence score found by the service at
    a sentence and document-level.

    All required parameters must be populated in order to send to Azure.

    :keyword odata_type: Required. Identifies the concrete type of the skill.Constant filled by
     server.
    :paramtype odata_type: str
    :keyword name: The name of the skill which uniquely identifies it within the skillset. A skill
     with no name defined will be given a default name of its 1-based index in the skills array,
     prefixed with the character '#'.
    :paramtype name: str
    :keyword description: The description of the skill which describes the inputs, outputs, and usage
     of the skill.
    :paramtype description: str
    :keyword context: Represents the level at which operations take place, such as the document root
     or document content (for example, /document or /document/content). The default is /document.
    :paramtype context: str
    :keyword inputs: Required. Inputs of the skills could be a column in the source data set, or the
     output of an upstream skill.
    :paramtype inputs: list[~azure.search.documents.indexes.models.InputFieldMappingEntry]
    :keyword outputs: Required. The output of a skill is either a field in a search index, or a value
     that can be consumed as an input by another skill.
    :paramtype outputs: list[~azure.search.documents.indexes.models.OutputFieldMappingEntry]
    :keyword default_language_code: A value indicating which language code to use. Default is en.
     Possible values include: "da", "nl", "en", "fi", "fr", "de", "el", "it", "no", "pl", "pt-PT",
     "ru", "es", "sv", "tr".
    :paramtype default_language_code: str or
     ~azure.search.documents.indexes.models.SentimentSkillLanguage
    :keyword include_opinion_mining: If set to true, the skill output will include information from
     Text Analytics for opinion mining, namely targets (nouns or verbs) and their associated
     assessment (adjective) in the text. Default is false.
    :paramtype include_opinion_mining: bool
    :keyword model_version: The version of the model to use when calling the Text Analytics service.
     It will default to the latest available when not specified. We recommend you do not specify
     this value unless absolutely necessary.
    :paramtype model_version: str
    :keyword skill_version: The version of the skill to use when calling the Text Analytics service.
     It will default to V1 when not specified.
    :paramtype skill_version: ~azure.search.documents.indexes.models.SentimentSkillVersion
    """

    _validation = {
        'odata_type': {'required': True},
        'inputs': {'required': True},
        'outputs': {'required': True},
    }

    _attribute_map = {
        'odata_type': {'key': '@odata\\.type', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'context': {'key': 'context', 'type': 'str'},
        'inputs': {'key': 'inputs', 'type': '[InputFieldMappingEntry]'},
        'outputs': {'key': 'outputs', 'type': '[OutputFieldMappingEntry]'},
        'default_language_code': {'key': 'defaultLanguageCode', 'type': 'str'},
        'include_opinion_mining': {'key': 'includeOpinionMining', 'type': 'bool'},
        'model_version': {'key': 'modelVersion', 'type': 'str'},
        'skill_version': {'key': 'skillVersion', 'type': 'str'}
    }

    def __init__(
        self,
        **kwargs
    ):
        # pop skill_version from kwargs to avoid warning in msrest
        skill_version = kwargs.pop('skill_version', SentimentSkillVersion.V1)

        super(SentimentSkill, self).__init__(**kwargs)
        self.skill_version = skill_version
        self.odata_type = self.skill_version  # type: str
        self.default_language_code = kwargs.get('default_language_code', None)
        self.include_opinion_mining = kwargs.get('include_opinion_mining', None)
        self.model_version = kwargs.get('model_version', None)

    def _to_generated(self):
        if self.skill_version == SentimentSkillVersion.V1:
            return _SentimentSkillV1(
                inputs=self.inputs,
                outputs=self.outputs,
                name=self.name,
                odata_type=self.odata_type,
                default_language_code=self.default_language_code
        )
        if self.skill_version in [SentimentSkillVersion.V3, SentimentSkillVersion.LATEST]:
            return _SentimentSkillV3(
                inputs=self.inputs,
                outputs=self.outputs,
                name=self.name,
                odata_type=self.odata_type,
                default_language_code=self.default_language_code,
                include_opinion_mining=self.include_opinion_mining,
                model_version=self.model_version
            )
        return None

    @classmethod
    def _from_generated(cls, skill):
        if not skill:
            return None
        kwargs = skill.as_dict()
        if isinstance(skill, _SentimentSkillV1):
            return SentimentSkill(
                skill_version=SentimentSkillVersion.V1,
                **kwargs
            )
        if isinstance(skill, _SentimentSkillV3):
            return SentimentSkill(
                skill_version=SentimentSkillVersion.V3,
                **kwargs
            )
        return None


class AnalyzeTextOptions(msrest.serialization.Model):
    """Specifies some text and analysis components used to break that text into tokens.

    All required parameters must be populated in order to send to Azure.

    :keyword text: Required. The text to break into tokens.
    :paramtype text: str
    :keyword analyzer_name: The name of the analyzer to use to break the given text. If this parameter is
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
    :paramtype analyzer_name: str or ~azure.search.documents.indexes.models.LexicalAnalyzerName
    :keyword tokenizer_name: The name of the tokenizer to use to break the given text. If this parameter
     is not specified, you must specify an analyzer instead. The tokenizer and analyzer parameters
     are mutually exclusive. Possible values include: "classic", "edgeNGram", "keyword_v2",
     "letter", "lowercase", "microsoft_language_tokenizer", "microsoft_language_stemming_tokenizer",
     "nGram", "path_hierarchy_v2", "pattern", "standard_v2", "uax_url_email", "whitespace".
    :paramtype tokenizer_name: str or ~azure.search.documents.indexes.models.LexicalTokenizerName
    :keyword normalizer_name: The name of the normalizer to use to normalize the given text. Possible
     values include: "asciifolding", "elision", "lowercase", "standard", "uppercase".
    :paramtype normalizer_name: str or ~azure.search.documents.indexes.models.LexicalNormalizerName
    :keyword token_filters: An optional list of token filters to use when breaking the given text.
     This parameter can only be set when using the tokenizer parameter.
    :paramtype token_filters: list[str or ~azure.search.documents.indexes.models.TokenFilterName]
    :keyword char_filters: An optional list of character filters to use when breaking the given text.
     This parameter can only be set when using the tokenizer parameter.
    :paramtype char_filters: list[str]
    """

    _validation = {
        "text": {"required": True},
    }

    _attribute_map = {
        "text": {"key": "text", "type": "str"},
        "analyzer_name": {"key": "analyzerName", "type": "str"},
        "tokenizer_name": {"key": "tokenizerName", "type": "str"},
        "normalizer_name": {"key": "normalizerName", "type": "str"},
        "token_filters": {"key": "tokenFilters", "type": "[str]"},
        "char_filters": {"key": "charFilters", "type": "[str]"},
    }

    def __init__(self, **kwargs):
        super(AnalyzeTextOptions, self).__init__(**kwargs)
        self.text = kwargs["text"]
        self.analyzer_name = kwargs.get("analyzer_name", None)
        self.tokenizer_name = kwargs.get("tokenizer_name", None)
        self.normalizer_name = kwargs.get("normalizer_name", None)
        self.token_filters = kwargs.get("token_filters", None)
        self.char_filters = kwargs.get("char_filters", None)

    def _to_analyze_request(self):
        return AnalyzeRequest(
            text=self.text,
            analyzer=self.analyzer_name,
            tokenizer=self.tokenizer_name,
            normalizer=self.normalizer_name,
            token_filters=self.token_filters,
            char_filters=self.char_filters,
        )


class CustomAnalyzer(LexicalAnalyzer):
    """Allows you to take control over the process of converting text into indexable/searchable tokens.
    It's a user-defined configuration consisting of a single predefined tokenizer and one or more filters.
    The tokenizer is responsible for breaking text into tokens, and the filters for modifying tokens
    emitted by the tokenizer.

    All required parameters must be populated in order to send to Azure.

    :keyword odata_type: Required. Identifies the concrete type of the analyzer.Constant filled by
     server.
    :paramtype odata_type: str
    :keyword name: Required. The name of the analyzer. It must only contain letters, digits, spaces,
     dashes or underscores, can only start and end with alphanumeric characters, and is limited to
     128 characters.
    :paramtype name: str
    :keyword tokenizer_name: Required. The name of the tokenizer to use to divide continuous text into a
     sequence of tokens, such as breaking a sentence into words. Possible values include: "classic",
     "edgeNGram", "keyword_v2", "letter", "lowercase", "microsoft_language_tokenizer",
     "microsoft_language_stemming_tokenizer", "nGram", "path_hierarchy_v2", "pattern",
     "standard_v2", "uax_url_email", "whitespace".
    :paramtype tokenizer_name: str or ~azure.search.documents.indexes.models.LexicalTokenizerName
    :keyword token_filters: A list of token filters used to filter out or modify the tokens generated
     by a tokenizer. For example, you can specify a lowercase filter that converts all characters to
     lowercase. The filters are run in the order in which they are listed.
    :paramtype token_filters: list[str or ~azure.search.documents.indexes.models.TokenFilterName]
    :keyword char_filters: A list of character filters used to prepare input text before it is
     processed by the tokenizer. For instance, they can replace certain characters or symbols. The
     filters are run in the order in which they are listed.
    :paramtype char_filters: list[str]
    """

    _validation = {
        "odata_type": {"required": True},
        "name": {"required": True},
        "tokenizer_name": {"required": True},
    }

    _attribute_map = {
        "odata_type": {"key": "@odata\\.type", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "tokenizer_name": {"key": "tokenizerName", "type": "str"},
        "token_filters": {"key": "tokenFilters", "type": "[str]"},
        "char_filters": {"key": "charFilters", "type": "[str]"},
    }

    def __init__(self, **kwargs):
        super(CustomAnalyzer, self).__init__(**kwargs)
        self.odata_type = "#Microsoft.Azure.Search.CustomAnalyzer"
        self.tokenizer_name = kwargs["tokenizer_name"]
        self.token_filters = kwargs.get("token_filters", None)
        self.char_filters = kwargs.get("char_filters", None)

    def _to_generated(self):
        return _CustomAnalyzer(
            name=self.name,
            odata_type=self.odata_type,
            tokenizer=self.tokenizer_name,
            token_filters=self.token_filters,
            char_filters=self.char_filters,
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
            char_filters=custom_analyzer.char_filters,
        )


class PatternAnalyzer(LexicalAnalyzer):
    """Flexibly separates text into terms via a regular expression.
    This analyzer is implemented using Apache Lucene.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the analyzer. It must only contain letters, digits, spaces,
     dashes or underscores, can only start and end with alphanumeric characters, and is limited to
     128 characters.
    :paramtype name: str
    :keyword lower_case_terms: A value indicating whether terms should be lower-cased. Default is
     true.
    :paramtype lower_case_terms: bool
    :keyword pattern: A regular expression to match token separators. Default is an
     expression that matches one or more white space characters.
    :paramtype pattern: str
    :keyword flags: List of regular expression flags. Possible values of each flag include: 'CANON_EQ',
     'CASE_INSENSITIVE', 'COMMENTS', 'DOTALL', 'LITERAL', 'MULTILINE', 'UNICODE_CASE', 'UNIX_LINES'.
    :paramtype flags: list[str] or list[~search_service_client.models.RegexFlags]
    :keyword stopwords: A list of stopwords.
    :paramtype stopwords: list[str]
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

    :keyword name: Required. The name of the tokenizer. It must only contain letters, digits, spaces,
     dashes or underscores, can only start and end with alphanumeric characters, and is limited to
     128 characters.
    :paramtype name: str
    :keyword pattern: A regular expression to match token separators. Default is an
     expression that matches one or more white space characters.
    :paramtype pattern: str
    :keyword flags: List of regular expression flags. Possible values of each flag include: 'CANON_EQ',
     'CASE_INSENSITIVE', 'COMMENTS', 'DOTALL', 'LITERAL', 'MULTILINE', 'UNICODE_CASE', 'UNIX_LINES'.
    :paramtype flags: list[str] or list[~search_service_client.models.RegexFlags]
    :keyword group: The zero-based ordinal of the matching group in the regular expression to
     extract into tokens. Use -1 if you want to use the entire pattern to split the input into
     tokens, irrespective of matching groups. Default is -1.
    :paramtype group: int
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

    :keyword key_name: Required. The name of your Azure Key Vault key to be used to encrypt your data
     at rest.
    :paramtype key_name: str
    :keyword key_version: Required. The version of your Azure Key Vault key to be used to encrypt
     your data at rest.
    :paramtype key_version: str
    :keyword vault_uri: Required. The URI of your Azure Key Vault, also referred to as DNS name, that
     contains the key to be used to encrypt your data at rest. An example URI might be https://my-
     keyvault-name.vault.azure.net.
    :paramtype vault_uri: str
    :keyword application_id: Required. An AAD Application ID that was granted the required access
     permissions to the Azure Key Vault that is to be used when encrypting your data at rest. The
     Application ID should not be confused with the Object ID for your AAD Application.
    :paramtype application_id: str
    :keyword application_secret: The authentication key of the specified AAD application.
    :paramtype application_secret: str
    """

    _validation = {
        "key_name": {"required": True},
        "key_version": {"required": True},
        "vault_uri": {"required": True},
    }

    _attribute_map = {
        "key_name": {"key": "keyVaultKeyName", "type": "str"},
        "key_version": {"key": "keyVaultKeyVersion", "type": "str"},
        "vault_uri": {"key": "keyVaultUri", "type": "str"},
        "application_id": {"key": "applicationId", "type": "str"},
        "application_secret": {"key": "applicationSecret", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(SearchResourceEncryptionKey, self).__init__(**kwargs)
        self.key_name = kwargs["key_name"]
        self.key_version = kwargs["key_version"]
        self.vault_uri = kwargs["vault_uri"]
        self.application_id = kwargs.get("application_id", None)
        self.application_secret = kwargs.get("application_secret", None)

    def _to_generated(self):
        if self.application_id and self.application_secret:
            access_credentials = AzureActiveDirectoryApplicationCredentials(
                application_id=self.application_id,
                application_secret=self.application_secret,
            )
        else:
            access_credentials = None
        return _SearchResourceEncryptionKey(
            key_name=self.key_name,
            key_version=self.key_version,
            vault_uri=self.vault_uri,
            access_credentials=access_credentials,
        )

    @classmethod
    def _from_generated(cls, search_resource_encryption_key):
        if not search_resource_encryption_key:
            return None
        if search_resource_encryption_key.access_credentials:
            application_id = (
                search_resource_encryption_key.access_credentials.application_id
            )
            application_secret = (
                search_resource_encryption_key.access_credentials.application_secret
            )
        else:
            application_id = None
            application_secret = None
        return cls(
            key_name=search_resource_encryption_key.key_name,
            key_version=search_resource_encryption_key.key_version,
            vault_uri=search_resource_encryption_key.vault_uri,
            application_id=application_id,
            application_secret=application_secret,
        )


class SynonymMap(msrest.serialization.Model):
    """Represents a synonym map definition.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the synonym map.
    :paramtype name: str
    :ivar format: Required. The format of the synonym map. Only the 'solr' format is currently
     supported. Default value: "solr".
    :vartype format: str
    :keyword synonyms: Required. A series of synonym rules in the specified synonym map format. The
     rules must be separated by newlines.
    :paramtype synonyms: list[str]
    :keyword encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your data when you
     want full assurance that no one, not even Microsoft, can decrypt your data in Azure Cognitive
     Search. Once you have encrypted your data, it will always remain encrypted. Azure Cognitive
     Search will ignore attempts to set this property to null. You can change this property as
     needed if you want to rotate your encryption key; Your data will be unaffected. Encryption with
     customer-managed keys is not available for free search services, and is only available for paid
     services created on or after January 1, 2019.
    :paramtype encryption_key: ~azure.search.documents.indexes.models.SearchResourceEncryptionKey
    :keyword e_tag: The ETag of the synonym map.
    :paramtype e_tag: str
    """

    _validation = {
        "name": {"required": True},
        "format": {"required": True, "constant": True},
        "synonyms": {"required": True},
    }

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "format": {"key": "format", "type": "str"},
        "synonyms": {"key": "synonyms", "type": "[str]"},
        "encryption_key": {
            "key": "encryptionKey",
            "type": "SearchResourceEncryptionKey",
        },
        "e_tag": {"key": "@odata\\.etag", "type": "str"},
    }

    format = "solr"

    def __init__(self, **kwargs):
        super(SynonymMap, self).__init__(**kwargs)
        self.name = kwargs["name"]
        self.synonyms = kwargs["synonyms"]
        self.encryption_key = kwargs.get("encryption_key", None)
        self.e_tag = kwargs.get("e_tag", None)

    def _to_generated(self):
        return _SynonymMap(
            name=self.name,
            synonyms="\n".join(self.synonyms),
            encryption_key=self.encryption_key._to_generated()  # pylint:disable=protected-access
            if self.encryption_key
            else None,
            e_tag=self.e_tag,
        )

    @classmethod
    def _from_generated(cls, synonym_map):
        if not synonym_map:
            return None
        return cls(
            name=synonym_map.name,
            synonyms=synonym_map.synonyms.split("\n"),
            # pylint:disable=protected-access
            encryption_key=SearchResourceEncryptionKey._from_generated(
                synonym_map.encryption_key
            ),
            e_tag=synonym_map.e_tag,
        )


class SearchIndexerDataSourceConnection(msrest.serialization.Model):
    """Represents a datasource connection definition, which can be used to configure an indexer.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the datasource connection.
    :paramtype name: str
    :keyword description: The description of the datasource connection.
    :paramtype description: str
    :keyword type: Required. The type of the datasource connection. Possible values include: "azuresql",
     "cosmosdb", "azureblob", "azuretable", "mysql", "adlsgen2".
    :paramtype type: str or ~azure.search.documents.indexes.models.SearchIndexerDataSourceType
    :keyword connection_string: The connection string for the datasource connection.
    :paramtype connection_string: str
    :keyword container: Required. The data container for the datasource connection.
    :paramtype container: ~azure.search.documents.indexes.models.SearchIndexerDataContainer
    :keyword data_change_detection_policy: The data change detection policy for the datasource connection.
    :paramtype data_change_detection_policy: ~azure.search.documents.models.DataChangeDetectionPolicy
    :keyword data_deletion_detection_policy: The data deletion detection policy for the datasource connection.
    :paramtype data_deletion_detection_policy:
     ~azure.search.documents.models.DataDeletionDetectionPolicy
    :keyword e_tag: The ETag of the data source.
    :paramtype e_tag: str
    :keyword identity: An explicit managed identity to use for this datasource. If not specified and
     the connection string is a managed identity, the system-assigned managed identity is used. If
     not specified, the value remains unchanged. If "none" is specified, the value of this property
     is cleared.
    :paramtype identity: ~azure.search.documents.indexes.models.SearchIndexerDataIdentity
    :keyword encryption_key: A description of an encryption key that you create in Azure Key Vault.
     This key is used to provide an additional level of encryption-at-rest for your datasource
     definition when you want full assurance that no one, not even Microsoft, can decrypt your data
     source definition in Azure Cognitive Search. Once you have encrypted your data source
     definition, it will always remain encrypted. Azure Cognitive Search will ignore attempts to set
     this property to null. You can change this property as needed if you want to rotate your
     encryption key; Your datasource definition will be unaffected. Encryption with customer-managed
     keys is not available for free search services, and is only available for paid services created
     on or after January 1, 2019.
    :paramtype encryption_key: ~azure.search.documents.indexes.models.SearchResourceEncryptionKey
    """

    _validation = {
        "name": {"required": True},
        "type": {"required": True},
        "connection_string": {"required": True},
        "container": {"required": True},
    }

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "description": {"key": "description", "type": "str"},
        "type": {"key": "type", "type": "str"},
        "connection_string": {"key": "connectionString", "type": "str"},
        "container": {"key": "container", "type": "SearchIndexerDataContainer"},
        "data_change_detection_policy": {
            "key": "dataChangeDetectionPolicy",
            "type": "DataChangeDetectionPolicy",
        },
        "data_deletion_detection_policy": {
            "key": "dataDeletionDetectionPolicy",
            "type": "DataDeletionDetectionPolicy",
        },
        'encryption_key': {'key': 'encryptionKey', 'type': 'SearchResourceEncryptionKey'},
        "e_tag": {"key": "@odata\\.etag", "type": "str"},
        'identity': {'key': 'identity', 'type': 'SearchIndexerDataIdentity'},
    }

    def __init__(self, **kwargs):
        super(SearchIndexerDataSourceConnection, self).__init__(**kwargs)
        self.name = kwargs["name"]
        self.description = kwargs.get("description", None)
        self.type = kwargs["type"]
        self.connection_string = kwargs["connection_string"]
        self.container = kwargs["container"]
        self.data_change_detection_policy = kwargs.get(
            "data_change_detection_policy", None
        )
        self.data_deletion_detection_policy = kwargs.get(
            "data_deletion_detection_policy", None
        )
        self.e_tag = kwargs.get("e_tag", None)
        self.encryption_key = kwargs.get("encryption_key", None)
        self.identity = kwargs.get("identity", None)

    def _to_generated(self):
        if self.connection_string is None or self.connection_string == "":
            connection_string = "<unchanged>"
        else:
            connection_string = self.connection_string
        credentials = DataSourceCredentials(connection_string=connection_string)
        return _SearchIndexerDataSource(
            name=self.name,
            description=self.description,
            type=self.type,
            credentials=credentials,
            container=self.container,
            data_change_detection_policy=self.data_change_detection_policy,
            data_deletion_detection_policy=self.data_deletion_detection_policy,
            e_tag=self.e_tag,
            encryption_key=self.encryption_key,
            identity=self.identity
        )

    @classmethod
    def _from_generated(cls, search_indexer_data_source):
        if not search_indexer_data_source:
            return None
        connection_string = (
            search_indexer_data_source.credentials.connection_string
            if search_indexer_data_source.credentials
            else None
        )
        return cls(
            name=search_indexer_data_source.name,
            description=search_indexer_data_source.description,
            type=search_indexer_data_source.type,
            connection_string=connection_string,
            container=search_indexer_data_source.container,
            data_change_detection_policy=search_indexer_data_source.data_change_detection_policy,
            data_deletion_detection_policy=search_indexer_data_source.data_deletion_detection_policy,
            e_tag=search_indexer_data_source.e_tag,
            encryption_key=search_indexer_data_source.encryption_key,
            identity=search_indexer_data_source.identity
        )


def pack_analyzer(analyzer):
    if not analyzer:
        return None
    if isinstance(analyzer, (PatternAnalyzer, CustomAnalyzer)):
        return analyzer._to_generated()  # pylint:disable=protected-access
    return analyzer


def unpack_analyzer(analyzer):
    if not analyzer:
        return None
    if isinstance(analyzer, _PatternAnalyzer):
        return PatternAnalyzer._from_generated(  # pylint:disable=protected-access
            analyzer
        )
    if isinstance(analyzer, _CustomAnalyzer):
        return CustomAnalyzer._from_generated(  # pylint:disable=protected-access
            analyzer
        )
    return analyzer
