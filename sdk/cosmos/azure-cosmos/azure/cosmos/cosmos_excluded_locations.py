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

"""A class which encapsulates a set of excluded regions.
"""

from typing import Set

class CosmosExcludedLocations:
    """Represents the CosmosExcludedLocations ConnectionPolicy.

    Use this class to encapsulate a set of CosmosExcludedLocations to filter endpoint locations to skip.

    :param Set[str] excluded_locations: The set of excluded locations. None value is not allowed.
    :raises ValueError: Raised if the excluded_locations was None.
    """
    def __init__(self, excluded_locations: Set[str]) -> None:
        if excluded_locations is None:
            raise ValueError("Excluded locations cannot be None. "
                             "Try passing an empty set, if you want to remove all excluded locations.")

        self._excluded_locations = frozenset(excluded_locations)

    def is_configured(self) -> bool:
        return len(self._excluded_locations) > 0

    def get(self) -> Set[str]:
        return set(self._excluded_locations)
