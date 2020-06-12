# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.search.documents.indexes.models import SearchIndex, RegexFlags, PatternAnalyzer, PatternTokenizer
from azure.search.documents.indexes._internal._generated.models import (
    PatternAnalyzer as _PatternAnalyzer,
    PatternTokenizer as _PatternTokenizer,
)
from azure.search.documents.indexes._internal._utils import unpack_search_index, pack_search_index

def test_unpack_search_index():
    pattern_analyzer = _PatternAnalyzer(
            name="test_analyzer",
            flags="CANON_EQ"
        )
    analyzers = []
    analyzers.append(pattern_analyzer)
    pattern_tokenizer = _PatternTokenizer(
        name="test_tokenizer",
        flags="CANON_EQ"
    )
    tokenizers = []
    tokenizers.append(pattern_tokenizer)
    index = SearchIndex(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = unpack_search_index(index)
    assert isinstance(result.analyzers[0], PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, list)
    assert result.analyzers[0].flags[0] == "CANON_EQ"
    assert isinstance(result.tokenizers[0], PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, list)
    assert result.tokenizers[0].flags[0] == "CANON_EQ"

def test_multi_unpack_search_index():
    pattern_analyzer = _PatternAnalyzer(
            name="test_analyzer",
            flags="CANON_EQ|MULTILINE"
        )
    analyzers = []
    analyzers.append(pattern_analyzer)
    pattern_tokenizer = _PatternTokenizer(
        name="test_tokenizer",
        flags="CANON_EQ|MULTILINE"
    )
    tokenizers = []
    tokenizers.append(pattern_tokenizer)
    index = SearchIndex(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = unpack_search_index(index)
    assert isinstance(result.analyzers[0], PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, list)
    assert result.analyzers[0].flags[0] == "CANON_EQ"
    assert result.analyzers[0].flags[1] == "MULTILINE"
    assert isinstance(result.tokenizers[0], PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, list)
    assert result.tokenizers[0].flags[0] == "CANON_EQ"
    assert result.tokenizers[0].flags[1] == "MULTILINE"

def test_unpack_search_index_enum():
    pattern_analyzer = _PatternAnalyzer(
            name="test_analyzer",
            flags=RegexFlags.canon_eq
        )
    analyzers = []
    analyzers.append(pattern_analyzer)
    pattern_tokenizer = _PatternTokenizer(
        name="test_tokenizer",
        flags=RegexFlags.canon_eq
    )
    tokenizers = []
    tokenizers.append(pattern_tokenizer)
    index = SearchIndex(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = unpack_search_index(index)
    assert isinstance(result.analyzers[0], PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, list)
    assert result.analyzers[0].flags[0] == "CANON_EQ"
    assert isinstance(result.tokenizers[0], PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, list)
    assert result.tokenizers[0].flags[0] == "CANON_EQ"

def test_pack_search_index():
    pattern_analyzer = PatternAnalyzer(
            name="test_analyzer",
            flags=["CANON_EQ"]
        )
    analyzers = []
    analyzers.append(pattern_analyzer)
    pattern_tokenizer = PatternTokenizer(
        name="test_tokenizer",
        flags=["CANON_EQ"]
    )
    tokenizers = []
    tokenizers.append(pattern_tokenizer)
    index = SearchIndex(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = pack_search_index(index)
    assert isinstance(result.analyzers[0], _PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, str)
    assert result.analyzers[0].flags == "CANON_EQ"
    assert isinstance(result.tokenizers[0], _PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, str)
    assert result.tokenizers[0].flags == "CANON_EQ"

def test_multi_pack_search_index():
    pattern_analyzer = PatternAnalyzer(
            name="test_analyzer",
            flags=["CANON_EQ", "MULTILINE"]
        )
    analyzers = []
    analyzers.append(pattern_analyzer)
    pattern_tokenizer = PatternTokenizer(
        name="test_analyzer",
        flags=["CANON_EQ", "MULTILINE"]
    )
    tokenizers = []
    tokenizers.append(pattern_tokenizer)
    index = SearchIndex(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = pack_search_index(index)
    assert isinstance(result.analyzers[0], _PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, str)
    assert result.analyzers[0].flags == "CANON_EQ|MULTILINE"
    assert isinstance(result.tokenizers[0], _PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, str)
    assert result.tokenizers[0].flags == "CANON_EQ|MULTILINE"
