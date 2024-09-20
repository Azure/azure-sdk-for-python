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
            if vector_session_token1.global_lsn > vector_session_token2.global_lsn else pk_range_id2
    vector_session_token = vector_session_token1.merge(vector_session_token2)
    return pk_range_id + ":" +  vector_session_token.session_token

def is_compound_session_token(session_token):
    return "," in session_token



