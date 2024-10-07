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

from azure.cosmos._vector_session_token import VectorSessionToken


def merge_session_tokens(session_token1, session_token2):
    # TODO method for splitting the session token into pk_range_id and vector_session_token
    token_pairs1 = session_token1.split(":")
    pk_range_id1 = token_pairs1[0]
    vector_session_token1 = VectorSessionToken.create(token_pairs1[1])
    token_pairs2 = session_token2.split(":")
    pk_range_id2 = token_pairs2[0]
    vector_session_token2 = VectorSessionToken.create(token_pairs2[1])
    pk_range_id = pk_range_id1
    if pk_range_id1 != pk_range_id2:
        pk_range_id = pk_range_id1 \
            if vector_session_token1.is_greater(vector_session_token2) else pk_range_id2
    vector_session_token = vector_session_token1.merge(vector_session_token2)
    return pk_range_id + ":" +  vector_session_token.session_token

def is_compound_session_token(session_token):
    return "," in session_token

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
    new_session_tokens = []
    i = 0
    while i < len(session_tokens):
        j = i + 1
        while j < len(session_tokens):
            tokens1 = session_tokens[i].split(":")
            tokens2 = session_tokens[j].split(":")
            pk_range_id1 = tokens1[0]
            pk_range_id2 = tokens2[0]
            if pk_range_id1 == pk_range_id2:
                vector_session_token1 = VectorSessionToken.create(tokens1[1])
                vector_session_token2 = VectorSessionToken.create(tokens2[1])
                vector_session_token = vector_session_token1.merge(vector_session_token2)
                new_session_tokens.append(pk_range_id1 + ":" + vector_session_token.session_token)
                remove_session_tokens = [session_tokens[i], session_tokens[j]]
                for token in remove_session_tokens:
                    session_tokens.remove(token)
                i = -1
            j += 1
        i += 1

    new_session_tokens.extend(session_tokens)
    return new_session_tokens
