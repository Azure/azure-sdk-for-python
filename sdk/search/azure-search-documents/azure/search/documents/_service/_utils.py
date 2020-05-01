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
    Index,
    PatternAnalyzer as _PatternAnalyzer,
    PatternTokenizer as _PatternTokenizer,
    AccessCondition
)
from ._models import PatternAnalyzer, PatternTokenizer

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Optional
    from ._generated.models import Skillset

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


def delistize_flags_for_pattern_analyzer(pattern_analyzer):
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


def listize_flags_for_pattern_analyzer(pattern_analyzer):
    # type: (PatternAnalyzer) -> PatternAnalyzer
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


def delistize_flags_for_pattern_tokenizer(pattern_tokenizer):
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


def listize_flags_for_pattern_tokenizer(pattern_tokenizer):
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


def delistize_flags_for_index(index):
    # type: (Index) -> Index
    if index.analyzers:
        index.analyzers = [
            delistize_flags_for_pattern_analyzer(x)  # type: ignore
            if isinstance(x, PatternAnalyzer)
            else x
            for x in index.analyzers
        ]  # mypy: ignore
    if index.tokenizers:
        index.tokenizers = [
            delistize_flags_for_pattern_tokenizer(x)  # type: ignore
            if isinstance(x, PatternTokenizer)
            else x
            for x in index.tokenizers
        ]
    return index


def listize_flags_for_index(index):
    # type: (Index) -> Index
    if index.analyzers:
        index.analyzers = [
            listize_flags_for_pattern_analyzer(x)  # type: ignore
            if isinstance(x, _PatternAnalyzer)
            else x
            for x in index.analyzers
        ]
    if index.tokenizers:
        index.tokenizers = [
            listize_flags_for_pattern_tokenizer(x)  # type: ignore
            if isinstance(x, _PatternTokenizer)
            else x
            for x in index.tokenizers
        ]
    return index


def listize_synonyms(synonym_map):
    # type: (dict) -> dict
    synonym_map["synonyms"] = synonym_map["synonyms"].split("\n")
    return synonym_map

def get_access_conditions(model, match_condition=MatchConditions.Unconditionally):
    # type: (Any, MatchConditions) -> Tuple[Dict[int, Any], AccessCondition]
    error_map = {
        401: ClientAuthenticationError,
        404: ResourceNotFoundError
    }

    if isinstance(model, six.string_types):
        if match_condition is not MatchConditions.Unconditionally:
            raise ValueError("A model must be passed to use access conditions")
        return (error_map, None)

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
        return (error_map, AccessCondition(if_match=if_match, if_none_match=if_none_match))
    except AttributeError:
        raise ValueError("Unable to get e_tag from the model")
