# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.search.documents import Index, RegexFlags, PatternAnalyzer, PatternTokenizer
from azure.search.documents._service._generated.models import (
    PatternAnalyzer as _PatternAnalyzer,
    PatternTokenizer as _PatternTokenizer,
)
from azure.search.documents._service._utils import delistize_flags_for_index, listize_flags_for_index

def test_listize_flags_for_index():
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
    index = Index(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = listize_flags_for_index(index)
    assert isinstance(result.analyzers[0], PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, list)
    assert result.analyzers[0].flags[0] == "CANON_EQ"
    assert isinstance(result.tokenizers[0], PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, list)
    assert result.tokenizers[0].flags[0] == "CANON_EQ"

def test_listize_multi_flags_for_index():
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
    index = Index(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = listize_flags_for_index(index)
    assert isinstance(result.analyzers[0], PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, list)
    assert result.analyzers[0].flags[0] == "CANON_EQ"
    assert result.analyzers[0].flags[1] == "MULTILINE"
    assert isinstance(result.tokenizers[0], PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, list)
    assert result.tokenizers[0].flags[0] == "CANON_EQ"
    assert result.tokenizers[0].flags[1] == "MULTILINE"

def test_listize_flags_for_index_enum():
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
    index = Index(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = listize_flags_for_index(index)
    assert isinstance(result.analyzers[0], PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, list)
    assert result.analyzers[0].flags[0] == "CANON_EQ"
    assert isinstance(result.tokenizers[0], PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, list)
    assert result.tokenizers[0].flags[0] == "CANON_EQ"

def test_delistize_flags_for_index():
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
    index = Index(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = delistize_flags_for_index(index)
    assert isinstance(result.analyzers[0], _PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, str)
    assert result.analyzers[0].flags == "CANON_EQ"
    assert isinstance(result.tokenizers[0], _PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, str)
    assert result.tokenizers[0].flags == "CANON_EQ"

def test_delistize_multi_flags_for_index():
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
    index = Index(
        name="test",
        fields=None,
        analyzers=analyzers,
        tokenizers=tokenizers
    )
    result = delistize_flags_for_index(index)
    assert isinstance(result.analyzers[0], _PatternAnalyzer)
    assert isinstance(result.analyzers[0].flags, str)
    assert result.analyzers[0].flags == "CANON_EQ|MULTILINE"
    assert isinstance(result.tokenizers[0], _PatternTokenizer)
    assert isinstance(result.tokenizers[0].flags, str)
    assert result.tokenizers[0].flags == "CANON_EQ|MULTILINE"
