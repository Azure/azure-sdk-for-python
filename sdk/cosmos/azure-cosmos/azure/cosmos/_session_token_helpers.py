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
from azure.cosmos._routing.routing_range import Range
from azure.cosmos._vector_session_token import VectorSessionToken


def merge_session_tokens_with_same_range(session_token1, session_token2):
    pk_range_id1, vector_session_token1 = create_vector_session_token_and_pkrangeid(session_token1)
    pk_range_id2, vector_session_token2 = create_vector_session_token_and_pkrangeid(session_token2)
    pk_range_id = pk_range_id1
    if pk_range_id1 != pk_range_id2:
        pk_range_id = pk_range_id1 \
            if vector_session_token1.is_greater(vector_session_token2) else pk_range_id2
    vector_session_token = vector_session_token1.merge(vector_session_token2)
    return pk_range_id + ":" +  vector_session_token.session_token

def is_compound_session_token(session_token):
    return "," in session_token

def create_vector_session_token_and_pkrangeid(session_token):
    tokens = session_token.split(":")
    return tokens[0], VectorSessionToken.create(tokens[1])

def split_compound_session_tokens(compound_session_tokens):
    session_tokens = []
    for _, session_token in compound_session_tokens:
            if is_compound_session_token(session_token):
                tokens = session_token.split(",")
                for token in tokens:
                    session_tokens.append(token)
            else:
                session_tokens.append(session_token)
    return session_tokens

def merge_session_tokens_with_same_pkrangeid(session_tokens):
    i = 0
    while i < len(session_tokens):
        j = i + 1
        while j < len(session_tokens):
            pk_range_id1, vector_session_token1 = create_vector_session_token_and_pkrangeid(session_tokens[i])
            pk_range_id2, vector_session_token2 = create_vector_session_token_and_pkrangeid(session_tokens[j])
            if pk_range_id1 == pk_range_id2:
                vector_session_token = vector_session_token1.merge(vector_session_token2)
                session_tokens.append(pk_range_id1 + ":" + vector_session_token.session_token)
                remove_session_tokens = [session_tokens[i], session_tokens[j]]
                for token in remove_session_tokens:
                    session_tokens.remove(token)
                i = -1
            j += 1
        i += 1

    return session_tokens

def get_updated_session_token(feed_ranges_to_session_tokens, target_feed_range):
    target_feed_range_normalized = target_feed_range._feed_range_internal.get_normalized_range()
    # filter out tuples that overlap with target_feed_range and normalizes all the ranges
    overlapping_ranges = [(feed_range_to_session_token[0]._feed_range_internal.get_normalized_range(), feed_range_to_session_token[1])
                          for feed_range_to_session_token in feed_ranges_to_session_tokens if Range.overlaps(
            target_feed_range_normalized, feed_range_to_session_token[0]._feed_range_internal.get_normalized_range())]
    # Is there a feed_range that is a superset of some of the other feed_ranges excluding tuples
    # with compound session tokens?
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
        else:
            j += 1
            if j == len(overlapping_ranges):
                i += 1
                j = i + 1


    done_overlapping_ranges = []
    # checking for merging of feed ranges that can be created from other feed ranges
    while len(overlapping_ranges) != 0:
        feed_range_cmp, session_token_cmp = overlapping_ranges[0]
        # compound session tokens are not considered for merging
        if is_compound_session_token(session_token_cmp):
            done_overlapping_ranges.append(overlapping_ranges[0])
            overlapping_ranges.remove(overlapping_ranges[0])
            continue
        tokens_cmp = session_token_cmp.split(":")
        vector_session_token_cmp = VectorSessionToken.create(tokens_cmp[1])
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
                _, vector_session_token = create_vector_session_token_and_pkrangeid(session_tokens[0])
                if vector_session_token_cmp.is_greater(vector_session_token):
                    overlapping_ranges.remove(overlapping_ranges[merged_indices[0]])
            else:
                for k in range(len(subsets)):
                    if j == k:
                        continue
                    if merged_range.can_merge(subsets[k][0]):
                        merged_range = merged_range.merge(subsets[k][0])
                        session_tokens.append(subsets[k][1])
                        merged_indices.append(subsets[k][2])
                    if feed_range_cmp == merged_range:
                        # if feed range can be created from the subsets
                        # take the subsets if their global lsn is larger
                        # else take the current feed range
                        children_more_updated = True
                        for session_token in session_tokens:
                            _, vector_session_token = create_vector_session_token_and_pkrangeid(session_token)
                            if vector_session_token_cmp.is_greater(vector_session_token):
                                children_more_updated = False
                        feed_ranges_to_remove = [overlapping_ranges[i] for i in merged_indices]
                        for feed_range_to_remove in feed_ranges_to_remove:
                            overlapping_ranges.remove(feed_range_to_remove)
                        if children_more_updated:
                            overlapping_ranges.append((merged_range, ','.join(map(str, session_tokens))))
                            overlapping_ranges.remove(overlapping_ranges[0])
                        not_found = False
                        break

            j += 1

        done_overlapping_ranges.append(overlapping_ranges[0])
        overlapping_ranges.remove(overlapping_ranges[0])

    # break up session tokens that are compound
    remaining_session_tokens = split_compound_session_tokens(done_overlapping_ranges)

    if len(remaining_session_tokens) == 1:
        return remaining_session_tokens[0]
    # merging any session tokens with same physical partition key range id
    remaining_session_tokens = merge_session_tokens_with_same_pkrangeid(remaining_session_tokens)

    updated_session_token = ""
    # compound the remaining session tokens
    for i in range(len(remaining_session_tokens)):
        if i == len(remaining_session_tokens) - 1:
            updated_session_token += remaining_session_tokens[i]
        else:
            updated_session_token += remaining_session_tokens[i] + ","

    return updated_session_token
