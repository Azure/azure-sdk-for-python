# The MIT License (MIT)
# Copyright (c) 2018 Microsoft Corporation

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

"""Session Consistency Tracking in the Azure Cosmos database service.
"""

from . import exceptions
from .http_constants import StatusCodes as _StatusCodes


class VectorSessionToken(object):
    segment_separator = "#"
    region_progress_separator = "="

    def __init__(self, version, global_lsn, local_lsn_by_region, session_token=None):

        self.version = version
        self.global_lsn = global_lsn
        self.local_lsn_by_region = local_lsn_by_region
        self.session_token = session_token

        if self.session_token is None:
            region_and_local_lsn = []

            for key in self.local_lsn_by_region:
                region_and_local_lsn.append(
                    str(key) + self.region_progress_separator + str(self.local_lsn_by_region[key])
                )

            region_progress = self.segment_separator.join(region_and_local_lsn)
            if not region_progress:
                self.session_token = "%s%s%s" % (self.version, self.segment_separator, self.global_lsn)
            else:
                self.session_token = "%s%s%s%s%s" % (
                    self.version,
                    self.segment_separator,
                    self.global_lsn,
                    self.segment_separator,
                    region_progress,
                )

    @classmethod
    def create(cls, session_token):  # pylint: disable=too-many-return-statements
        """Parses session token and creates the vector session token

        :param str session_token:
        :return: A Vector session Token
        :rtype: VectorSessionToken
        """

        version = None
        global_lsn = None
        local_lsn_by_region = {}

        if not session_token:
            return None

        segments = session_token.split(cls.segment_separator)

        if len(segments) < 2:
            return None

        try:
            version = int(segments[0])
        except ValueError as _:
            return None

        try:
            global_lsn = int(segments[1])
        except ValueError as _:
            return None

        for i in range(2, len(segments)):
            region_segment = segments[i]
            region_id_with_lsn = region_segment.split(cls.region_progress_separator)

            if len(region_id_with_lsn) != 2:
                return None

            try:
                region_id = int(region_id_with_lsn[0])
                local_lsn = int(region_id_with_lsn[1])
            except ValueError as _:
                return None
            local_lsn_by_region[region_id] = local_lsn

        return VectorSessionToken(version, global_lsn, local_lsn_by_region, session_token)

    def equals(self, other):
        if other is None:
            return False
        return (
            self.version == other.version
            and self.global_lsn == other.global_lsn
            and self.are_region_progress_equal(other.local_lsn_by_region)
        )

    def merge(self, other):
        if other is None:
            raise ValueError("Invalid Session Token (should not be None)")

        if self.version == other.version and len(self.local_lsn_by_region) != len(other.local_lsn_by_region):
            raise exceptions.CosmosHttpResponseError(
                status_code=_StatusCodes.INTERNAL_SERVER_ERROR,
                message=("Compared session tokens '%s' and '%s' have unexpected regions."
                         % (self.session_token, other.session_token))
            )

        if self.version < other.version:
            session_token_with_lower_version = self
            session_token_with_higher_version = other
        else:
            session_token_with_lower_version = other
            session_token_with_higher_version = self

        highest_local_lsn_by_region = {}

        for key in session_token_with_higher_version.local_lsn_by_region:
            region_id = key
            local_lsn1 = session_token_with_higher_version.local_lsn_by_region[key]
            local_lsn2 = (
                session_token_with_lower_version.local_lsn_by_region[region_id]
                if region_id in session_token_with_lower_version.local_lsn_by_region
                else None
            )

            if local_lsn2 is not None:
                highest_local_lsn_by_region[region_id] = max(local_lsn1, local_lsn2)
            elif self.version == other.version:
                raise exceptions.CosmosHttpResponseError(
                    status_code=_StatusCodes.INTERNAL_SERVER_ERROR,
                    message=("Compared session tokens '%s' and '%s' have unexpected regions."
                             % (self.session_token, other.session_token))
                )
            else:
                highest_local_lsn_by_region[region_id] = local_lsn1

        return VectorSessionToken(
            max(self.version, other.version), max(self.global_lsn, other.global_lsn), highest_local_lsn_by_region
        )

    def convert_to_string(self):
        return self.session_token

    def are_region_progress_equal(self, other):
        if len(self.local_lsn_by_region) != len(other):
            return False

        for key in self.local_lsn_by_region:
            region_id = key
            local_lsn1 = self.local_lsn_by_region[region_id]
            local_lsn2 = other[region_id] if region_id in other else None

            if local_lsn2 is not None:
                if local_lsn1 != local_lsn2:
                    return False
        return True
