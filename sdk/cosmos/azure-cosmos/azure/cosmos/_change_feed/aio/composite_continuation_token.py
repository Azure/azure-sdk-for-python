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

"""Internal class for change feed composite continuation token in the Azure Cosmos
database service.
"""
from azure.cosmos._routing.routing_range import Range


class CompositeContinuationToken(object):
    _token_property_name = "token"
    _feed_range_property_name = "range"

    def __init__(self, feed_range: Range, token):
        if range is None:
            raise ValueError("range is missing")

        self._token = token
        self._feed_range = feed_range

    def to_dict(self):
        return {
            self._token_property_name: self._token,
            self._feed_range_property_name: self._feed_range.to_dict()
        }

    @property
    def feed_range(self):
        return self._feed_range

    @property
    def token(self):
        return self._token

    def update_token(self, etag):
        self._token = etag

    @classmethod
    def from_json(cls, data):
        token = data.get(cls._token_property_name)
        if token is None:
            raise ValueError(f"Invalid composite token [Missing {cls._token_property_name}]")

        feed_range_data = data.get(cls._feed_range_property_name)
        if feed_range_data is None:
            raise ValueError(f"Invalid composite token [Missing {cls._feed_range_property_name}]")

        feed_range = Range.ParseFromDict(feed_range_data)
        return cls(feed_range=feed_range, token=token)

    def __repr__(self):
        return f"CompositeContinuationToken(token={self.token}, range={self._feed_range})"
