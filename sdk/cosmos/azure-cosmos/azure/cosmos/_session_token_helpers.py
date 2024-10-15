# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal Helper functions for manipulating session tokens.
"""
from typing import Tuple, List

from azure.cosmos._routing.routing_range import Range
from azure.cosmos._vector_session_token import VectorSessionToken
from ._feed_range import FeedRange

# pylint: disable=protected-access


# ex inputs:
# 1. "1:1#51", "1:1#55" -> "1:1#55"
# 2. "0:1#57", "1:1#52" -> "0:1#57"
def merge_session_tokens_with_same_range(session_token1: str, session_token2: str) -> str:
    pk_range_id1, vector_session_token1 = parse_session_token(session_token1)
    pk_range_id2, vector_session_token2 = parse_session_token(session_token2)
    pk_range_id = pk_range_id1
    # The pkrangeid could be different in this scenario
    # Ex. get_updated_session_token([("AA", "BB"), "1:1#51"], ("AA", "DD")) -> "1:1#51"
    # Then we input this back into get_updated_session_token after a merge happened
    # get_updated_session_token([("AA", "DD"), "1:1#51", ("AA", "DD"), "0:1#55"], ("AA", "DD")) -> "0:1#55"
    if pk_range_id1 != pk_range_id2:
        pk_range_id = pk_range_id1 \
            if vector_session_token1.global_lsn > vector_session_token2.global_lsn else pk_range_id2
    vector_session_token = vector_session_token1.merge(vector_session_token2)
    return pk_range_id + ":" +  vector_session_token.session_token

def is_compound_session_token(session_token: str) -> bool:
    return "," in session_token

def parse_session_token(session_token: str) -> Tuple[str, VectorSessionToken]:
    tokens = session_token.split(":")
    return tokens[0], VectorSessionToken.create(tokens[1])

def split_compound_session_tokens(compound_session_tokens: List[Tuple[Range, str]]) -> List[str]:
    session_tokens = []
    for _, session_token in compound_session_tokens:
        if is_compound_session_token(session_token):
            tokens = session_token.split(",")
            for token in tokens:
                session_tokens.append(token)
        else:
            session_tokens.append(session_token)
    return session_tokens

# ex inputs:
# ["1:1#51", "1:1#55", "1:1#57"] -> ["1:1#57"]
def merge_session_tokens_for_same_partition(session_tokens: List[str]) -> List[str]:
    i = 0
    while i < len(session_tokens):
        j = i + 1
        while j < len(session_tokens):
            pk_range_id1, vector_session_token1 = parse_session_token(session_tokens[i])
            pk_range_id2, vector_session_token2 = parse_session_token(session_tokens[j])
            if pk_range_id1 == pk_range_id2:
                vector_session_token = vector_session_token1.merge(vector_session_token2)
                session_tokens.append(pk_range_id1 + ":" + vector_session_token.session_token)
                remove_session_tokens = [session_tokens[i], session_tokens[j]]
                for token in remove_session_tokens:
                    session_tokens.remove(token)
                i = -1
                break
            j += 1
        i += 1

    return session_tokens

# ex inputs:
# 1. [(("AA", "BB"), "1:1#51"), (("BB", "DD"), "2:1#51"), (("AA", "DD"), "0:1#55")] ->
# [("AA", "DD"), "0:1#55"]
# 2. [(("AA", "BB"), "1:1#57"), (("BB", "DD"), "2:1#58"), (("AA", "DD"), "0:1#55")] ->
# [("AA", "DD"), "1:1#57,2:1#58"]
# 3. [(("AA", "BB"), "1:1#57"), (("BB", "DD"), "2:1#52"), (("AA", "DD"), "0:1#55")] ->
# [("AA", "DD"), "1:1#57,2:1#52,0:1#55"]
# compound session tokens are not considered will just pass them along
def merge_ranges_with_subsets(overlapping_ranges: List[Tuple[Range, str]]) -> List[Tuple[Range, str]]:
    processed_ranges = []
    while len(overlapping_ranges) != 0: # pylint: disable=too-many-nested-blocks
        feed_range_cmp, session_token_cmp = overlapping_ranges[0]
        # compound session tokens are not considered for merging
        if is_compound_session_token(session_token_cmp):
            processed_ranges.append(overlapping_ranges[0])
            overlapping_ranges.remove(overlapping_ranges[0])
            continue
        _, vector_session_token_cmp = parse_session_token(session_token_cmp)
        subsets = []
        # finding the subset feed ranges of the current feed range
        for j in range(1, len(overlapping_ranges)):
            feed_range = overlapping_ranges[j][0]
            if not is_compound_session_token(overlapping_ranges[j][1]) and \
                    feed_range.is_subset(feed_range_cmp):
                subsets.append(overlapping_ranges[j] + (j,))

        # go through subsets to see if can create current feed range from the subsets
        not_found = True
        j = 0
        while not_found and j < len(subsets):
            merged_range = subsets[j][0]
            session_tokens = [subsets[j][1]]
            merged_indices = [subsets[j][2]]
            if len(subsets) == 1:
                _, vector_session_token = parse_session_token(session_tokens[0])
                if vector_session_token_cmp.global_lsn > vector_session_token.global_lsn:
                    overlapping_ranges.remove(overlapping_ranges[merged_indices[0]])
            else:
                for k, subset in enumerate(subsets):
                    if j == k:
                        continue
                    if merged_range.can_merge(subset[0]):
                        merged_range = merged_range.merge(subset[0])
                        session_tokens.append(subset[1])
                        merged_indices.append(subset[2])
                    if feed_range_cmp == merged_range:
                        # if feed range can be created from the subsets
                        # take the subsets if their global lsn is larger
                        # else take the current feed range
                        children_more_updated = True
                        parent_more_updated = True
                        for session_token in session_tokens:
                            _, vector_session_token = parse_session_token(session_token)
                            if vector_session_token_cmp.global_lsn > vector_session_token.global_lsn:
                                children_more_updated = False
                            else:
                                parent_more_updated = False
                        feed_ranges_to_remove = [overlapping_ranges[i] for i in merged_indices]
                        for feed_range_to_remove in feed_ranges_to_remove:
                            overlapping_ranges.remove(feed_range_to_remove)
                        if children_more_updated:
                            overlapping_ranges.append((merged_range, ','.join(map(str, session_tokens))))
                            overlapping_ranges.remove(overlapping_ranges[0])
                        elif not parent_more_updated and not children_more_updated:
                            session_tokens.append(session_token_cmp)
                            overlapping_ranges.append((merged_range, ','.join(map(str, session_tokens))))
                        not_found = False
                        break

            j += 1

        processed_ranges.append(overlapping_ranges[0])
        overlapping_ranges.remove(overlapping_ranges[0])
    return processed_ranges

def get_updated_session_token(feed_ranges_to_session_tokens: List[Tuple[FeedRange, str]], target_feed_range: FeedRange,
                              container_link: str):

    if target_feed_range._feed_range_internal._container_link != container_link:
        raise ValueError('The target feed range does not belong to the container.')
    target_feed_range_normalized = target_feed_range._feed_range_internal.get_normalized_range()
    # filter out tuples that overlap with target_feed_range and normalizes all the ranges
    overlapping_ranges = []
    for feed_range_to_session_token in feed_ranges_to_session_tokens:
        if feed_range_to_session_token[0]._feed_range_internal._container_link != container_link:
            raise ValueError('The feed range does not belong to the container.')
        if Range.overlaps(target_feed_range_normalized,
                          feed_range_to_session_token[0]._feed_range_internal.get_normalized_range()):
            overlapping_ranges.append((feed_range_to_session_token[0]._feed_range_internal.get_normalized_range(),
                                       feed_range_to_session_token[1]))

    if len(overlapping_ranges) == 0:
        raise ValueError('There were no overlapping feed ranges with the target.')

    # merge any session tokens that are the same exact feed range
    i = 0
    j = 1
    while i < len(overlapping_ranges) and j < len(overlapping_ranges):
        cur_feed_range = overlapping_ranges[i][0]
        session_token = overlapping_ranges[i][1]
        session_token_1 = overlapping_ranges[j][1]
        if (not is_compound_session_token(session_token) and
                not is_compound_session_token(overlapping_ranges[j][1]) and
                cur_feed_range == overlapping_ranges[j][0]):
            session_token = merge_session_tokens_with_same_range(session_token, session_token_1)
            feed_ranges_to_remove = [overlapping_ranges[i], overlapping_ranges[j]]
            for feed_range_to_remove in feed_ranges_to_remove:
                overlapping_ranges.remove(feed_range_to_remove)
            overlapping_ranges.append((cur_feed_range, session_token))
            i, j = 0, 1
        else:
            j += 1
            if j == len(overlapping_ranges):
                i += 1
                j = i + 1

    # checking for merging of feed ranges that can be created from other feed ranges
    processed_ranges = merge_ranges_with_subsets(overlapping_ranges)

    # break up session tokens that are compound
    remaining_session_tokens = split_compound_session_tokens(processed_ranges)

    if len(remaining_session_tokens) == 1:
        return remaining_session_tokens[0]
    # merging any session tokens with same physical partition key range id
    remaining_session_tokens = merge_session_tokens_for_same_partition(remaining_session_tokens)

    updated_session_token = ""
    # compound the remaining session tokens
    for i, remaining_session_token in enumerate(remaining_session_tokens):
        if i == len(remaining_session_tokens) - 1:
            updated_session_token += remaining_session_token
        else:
            updated_session_token += remaining_session_token + ","

    return updated_session_token
