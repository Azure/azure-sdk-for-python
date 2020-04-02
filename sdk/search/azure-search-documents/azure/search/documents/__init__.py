# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

from ._version import VERSION

__version__ = VERSION

from ._index import (
    AutocompleteQuery,
    IndexAction,
    IndexDocumentsBatch,
    IndexingResult,
    SearchIndexClient,
    SearchQuery,
    SearchItemPaged,
    SuggestQuery,
    odata,
)

from ._service import SearchServiceClient
from ._service._models import PatternAnalyzer, PatternTokenizer
from ._service._generated.models import(
    Field,
    TextWeights,
    ScoringFunction,
    DistanceScoringFunction,
    FreshnessScoringFunction,
    MagnitudeScoringFunction,
    TagScoringFunction,
    DistanceScoringParameters,
    FreshnessScoringParameters,
    MagnitudeScoringParameters,
    TagScoringParameters,
    ScoringProfile,
    CorsOptions,
    Suggester,
    RegexFlags,
    Analyzer,
    CustomAnalyzer,
    StandardAnalyzer,
    StopAnalyzer,
    Tokenizer,
    ClassicTokenizer,
    EdgeNGramTokenizer,
    KeywordTokenizer,
    MicrosoftLanguageStemmingTokenizer,
    MicrosoftLanguageTokenizer,
    NGramTokenizer,
    StandardTokenizer,
    UaxUrlEmailTokenizer,
    TokenFilter,
    AsciiFoldingTokenFilter,
    CjkBigramTokenFilter,
    CommonGramTokenFilter,
    DictionaryDecompounderTokenFilter,
    EdgeNGramTokenFilter,
    ElisionTokenFilter,
    KeepTokenFilter,
    KeywordMarkerTokenFilter,
    LengthTokenFilter,
    LimitTokenFilter,
    NGramTokenFilter,
    PatternCaptureTokenFilter,
    PatternReplaceTokenFilter,
    PhoneticTokenFilter,
    ShingleTokenFilter,
    SnowballTokenFilter,
    StemmerOverrideTokenFilter,
    StemmerTokenFilter,
    StopwordsTokenFilter,
    SynonymTokenFilter,
    TruncateTokenFilter,
    UniqueTokenFilter,
    WordDelimiterTokenFilter,
    CharFilter,
    MappingCharFilter,
    PatternReplaceCharFilter,
    AzureActiveDirectoryApplicationCredentials,
    EncryptionKey,
    Index,
    GetIndexStatisticsResult,
    AnalyzeRequest,
    AnalyzeResult,
    TokenInfo,
)

__all__ = (
    "AutocompleteQuery",
    "IndexAction",
    "IndexDocumentsBatch",
    "IndexingResult",
    "SearchIndexClient",
    "SearchItemPaged",
    "SearchQuery",
    "SearchServiceClient",
    "SuggestQuery",
    "odata",
    "Field",
    "TextWeights",
    "ScoringFunction",
    "DistanceScoringFunction",
    "FreshnessScoringFunction",
    "MagnitudeScoringFunction",
    "TagScoringFunction",
    "DistanceScoringParameters",
    "FreshnessScoringParameters",
    "MagnitudeScoringParameters",
    "TagScoringParameters",
    "ScoringProfile",
    "CorsOptions",
    "Suggester",
    "RegexFlags",
    "Analyzer",
    "CustomAnalyzer",
    "PatternAnalyzer",
    "StandardAnalyzer",
    "StopAnalyzer",
    "Tokenizer",
    "ClassicTokenizer",
    "EdgeNGramTokenizer",
    "KeywordTokenizer",
    "MicrosoftLanguageStemmingTokenizer",
    "MicrosoftLanguageTokenizer",
    "NGramTokenizer",
    "PatternTokenizer",
    "StandardTokenizer",
    "UaxUrlEmailTokenizer",
    "TokenFilter",
    "AsciiFoldingTokenFilter",
    "CjkBigramTokenFilter",
    "CommonGramTokenFilter",
    "DictionaryDecompounderTokenFilter",
    "EdgeNGramTokenFilter",
    "ElisionTokenFilter",
    "KeepTokenFilter",
    "KeywordMarkerTokenFilter",
    "LengthTokenFilter",
    "LimitTokenFilter",
    "NGramTokenFilter",
    "PatternCaptureTokenFilter",
    "PatternReplaceTokenFilter",
    "PhoneticTokenFilter",
    "ShingleTokenFilter",
    "SnowballTokenFilter",
    "StemmerOverrideTokenFilter",
    "StemmerTokenFilter",
    "StopwordsTokenFilter",
    "SynonymTokenFilter",
    "TruncateTokenFilter",
    "UniqueTokenFilter",
    "WordDelimiterTokenFilter",
    "CharFilter",
    "MappingCharFilter",
    "PatternReplaceCharFilter",
    "AzureActiveDirectoryApplicationCredentials",
    "EncryptionKey",
    "Index",
    "GetIndexStatisticsResult",
    "AnalyzeRequest",
    "AnalyzeResult",
    "TokenInfo",
)
